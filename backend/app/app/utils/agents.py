from langchain.agents import AgentExecutor, create_json_chat_agent
import requests
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import Ollama
from langchain_core.messages import (BaseMessage, AIMessage, HumanMessage,
                                     FunctionMessage)
import operator
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain import hub
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation, ToolExecutor
from numpy import random
from typing import Optional, TypedDict, Annotated, Sequence, Dict
import json
from app.utils.tools import NutrientSearchTool, NutrientCalTool, FoodIdentifyTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import functools

from langchain_core.messages import AIMessage
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langgraph.prebuilt import ToolNode
"""
使用langgraph的原因:
langchain直接call ollamafunction帶image的prompt會報錯

因此拆成3個agent:

"""


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    image: Optional[str]


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful AI assistant, collaborating with other assistants."
            " Use the provided tools to progress towards answering the question."
            " If you are unable to fully answer, that's OK, another assistant with different tools "
            " will help where you left off. Execute what you can to make progress."
            " If you or any of the other assistants have the final answer or deliverable,"
            " prefix your response with FINAL ANSWER so the team knows to stop."
            " You have access to the following tools: {tool_names}.\n{system_message}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ])
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name
                                                  for tool in tools]))
    return prompt | llm.bind_tools(tools)


def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


# state definition for langgraph agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    image: Optional[str]


food_system_prompt = """
You are a highly knowledgeable and professional nutritionist with expertise in analyzing meal components and evaluating their caloric content.
as reciving an image, you need to identify the items in the image is food or not. 
if the image is food, you need to identify food name and food weight.  
When answering, your answers Must be fit into format.
format: {food:str, weight:float (grams)}
"""


def node_generate(system_prompt, tools, agent_name):
    node = create_agent(
        ChatOllama,
        tools,
        system_message=system_prompt,
    )
    return functools.partial(agent_node, agent=node, name=agent_name)


food_identify_node = node_generate(food_system_prompt, [FoodIdentifyTool()],
                                   food_identify_agent)
food_search_node = ToolNode([NutrientSearchTool])
food_calculate_node = node_generate()

workflow = StateGraph(AgentState)

workflow.add_node("Researcher", research_node)
workflow.add_node("chart_generator", chart_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "Researcher",
    router,
    {
        "continue": "chart_generator",
        "call_tool": "call_tool",
        "__end__": END
    },
)
workflow.add_conditional_edges(
    "chart_generator",
    router,
    {
        "continue": "Researcher",
        "call_tool": "call_tool",
        "__end__": END
    },
)

workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {
        "Researcher": "Researcher",
        "chart_generator": "chart_generator",
    },
)
workflow.add_edge(START, "Researcher")
graph = workflow.compile()
