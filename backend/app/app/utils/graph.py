from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_community.chat_models import ChatOllama

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import ToolMessage
from app.utils.tools import NutrientSearchTool, NutrientCalTool, FoodIdentifyTool
from app.utils.interface import chatllm
from typing import Optional

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import END, StateGraph

from langgraph.prebuilt import create_react_agent

import functools

from langchain_core.messages import AIMessage

tools = [NutrientSearchTool, NutrientCalTool, FoodIdentifyTool]
llm = chatllm


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    image_url: Optional[str] = None
    nutrient_dict: Optional[dict] = None
    food_name: Optional[str] = None
    weight: Optional[float] = None


def create_agent(llm, tools_name, tools, system_message: str):
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
    prompt = prompt.partial(tool_names=", ".join([tool
                                                  for tool in tools_name]))
    return prompt | llm.bind_tools(tools)


def create_agent_no_tool(llm, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a highly knowledgeable and professional nutritionist with expertise in analyzing meal components and evaluating their caloric content.",
        ),
        # MessagesPlaceholder(variable_name="messages"),
        (
            "human",
            [{
                "type": "text",
                "text": "estimate the nutrient of this image"
            }, {
                "type": "image_url",
                "image_url": "data:image/jpeg;base64,{image_url}"
            }],
        ),
    ])
    prompt = prompt.partial(system_message=system_message)

    return prompt | llm.bind_tools(tools)


# Helper function to create a node for a given agent
def agent_search_node(state: StateGraph, agent):
    food_name = state.get('food_name')
    result = agent.invoke({"food_name": food_name})
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        # result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        result = HumanMessage(content=result)
    return {
        "messages": [result],
        "nutrient_dict": result
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
    }


def agent_cal_node(state: StateGraph, agent):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        # result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        result = HumanMessage(content=result)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        # "nutrient_dict":
    }


def agent_identify_node(state: StateGraph, agent):
    result = agent.invoke(state.get('messages'))
    print(f"result in agent_identify:{result}")
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        # result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        result = HumanMessage(content=result)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        # "food_name": name,
        # "weight":
    }


nutrient_search_agent = create_agent(
    llm,
    ["NutrientSearch"],
    [NutrientSearchTool],
    system_message="input food name to tool to return the nutrient info",
)
nutrient_search_node = functools.partial(
    agent_search_node,
    agent=nutrient_search_agent,
)

nutrient_cal_agent = create_agent(
    llm,
    ["NutrientCalculate"],
    [NutrientCalTool],
    system_message=
    "input weight and nutrient dict to tool  and calculate the nutrient base on weight and nutrient_dict.",
)
nutrient_cal_node = functools.partial(
    agent_cal_node,
    agent=nutrient_cal_agent,
)

nutrient_identify_agent = create_agent_no_tool(
    llm,
    system_message=
    """as reciving an image, you need to identify the items in the image is food or not. 
if the image is food, you need to identify food name and food weight. """,
)
nutrient_identify_node = functools.partial(
    agent_identify_node,
    agent=nutrient_identify_agent,
)

workflow = StateGraph(AgentState)

workflow.add_node("Nutrient_Identify_Agent", nutrient_identify_node)
workflow.add_node("Nutrient_Search_Agent", nutrient_search_node)
workflow.add_node("Nutrient_Cal_Agent", nutrient_cal_node)
workflow.set_entry_point("Nutrient_Identify_Agent")

workflow.add_edge("Nutrient_Identify_Agent", "Nutrient_Search_Agent")
workflow.add_edge("Nutrient_Search_Agent", "Nutrient_Cal_Agent")
workflow.add_edge("Nutrient_Cal_Agent", END)

FoodGraph = workflow.compile()
"""
no tool agent to build langgraph
"""
workflow_test = StateGraph(AgentState)

workflow_test.add_node("Nutrient_Identify_Agent", nutrient_identify_node)
# workflow.add_node("Nutrient_Search_Agent", nutrient_search_node)
# workflow.add_node("Nutrient_Cal_Agent", nutrient_cal_node)
workflow_test.set_entry_point("Nutrient_Identify_Agent")

# workflow_test.add_edge("Nutrient_Identify_Agent", "Nutrient_Search_Agent")
# workflow_test.add_edge("Nutrient_Search_Agent", "Nutrient_Cal_Agent")
workflow_test.add_edge("Nutrient_Identify_Agent", END)

FoodGraph_test = workflow_test.compile()
