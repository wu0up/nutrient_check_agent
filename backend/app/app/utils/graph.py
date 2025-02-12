from langchain_core.prompts import ChatPromptTemplate

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

from app.utils.tools import NutrientSearch, NutrientCalculate
from app.utils.interface import chatllm
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field
from langfuse.callback import CallbackHandler
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.tools import StructuredTool

from langchain.globals import set_debug
from app.core.config import settings as p
set_debug(True)

tools = [NutrientCalculate, NutrientSearch]
llm = chatllm

import os

langfuse_handler = CallbackHandler(
            public_key=p.LANGFUSE_PUBLIC_KEY,
            secret_key=p.LANGFUSE_SECRET_KEY, 
            host=p.LANGFUSE_HOST
        )
config = {"callbacks": [langfuse_handler]}


# use
class FoodInfo(BaseModel):
    """Always use this tool to structure your response to the user."""
    food_name: str = Field(description="name of image's food")
    weight: float = Field(description="the weight estimate from food")
    is_food: bool = Field(
        description=
        "can detect food and is_food value is True; if can not determine or detect food, the value of is_food is False"
    )

# use
def create_agent_no_tool(llm, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages([
        # (
        #     "system",
        #     # "You are a highly knowledgeable and professional nutritionist with expertise in analyzing meal components and evaluating their caloric content.as reciving an image, you need to identify the items in the image is food or not. if the image is food, you need to identify food name and food weight.",
        system_message,
        # ),
        # MessagesPlaceholder(variable_name="messages"),
        (
            "human",
            [{
                "type": "text",
                "text": f"{system_message}"
            }, {
                "type": "image_url",
                "image_url": "data:image/jpeg;base64,{image_url}"
            }],
        ),
    ])
    prompt = prompt.partial(system_message=system_message)

    return prompt | llm.bind_tools([FoodInfo])


#use
async def agent_identify_node(prompt, agent):
    
    result = agent.invoke(prompt ,config)
    print(f"result in agent_identify:{result}")
    # print(f"result in agent_identify:{result.tool_calls}")

    food_info = result.tool_calls[-1]["args"]
    name = food_info["food_name"]
    weight = food_info["weight"]
    is_food = food_info['is_food']
    tool_call = result.tool_calls.copy()
    tool_call[-1]['name'] = "NutrientSearchTool"

    if is_food:
        weight = float(weight)

    return {

        "food_name": name,
        "weight": weight,
        "is_food": is_food
    }


#use
async def tool_agent(state, tool):
    calculator = StructuredTool.from_function(func=tool)
    input = {
        'food_name': state.get('food_name'),
        'weight': state.get('weight')
    }
    result = calculator.invoke(input)
    # print('result in tool agent', result)

    return result

#use
async def tool_agent_cal(state, tool):
    # print("tool_agent_cal state", state)
    calculator = StructuredTool.from_function(func=tool)
    input = {
        'weight': state.get('weight'),
        'nutrient_dict': state.get("nutrient_dict")
    }
    result = calculator.invoke(input)
    print('result in tool agent', result)
    # return ""
    return result


# use
nutrient_identify_agent = create_agent_no_tool(
    llm,
    system_message=
    #     """as reciving an image, you need to identify the items in the image is food or not.
    # if the image is food, you need to identify food name and food weight. """,
    """You are a highly knowledgeable and professional nutritionist with expertise in 
    analyzing meal components and evaluating their caloric content.
    as reciving an image, you need to identify the items in the image is food or not. 
    if image is food, make is_food value to True.
    if the image is food, you need to identify food name and food weight(grams). 
    if image is not food or can not detect food, make is_food to False""",
)



def get_all_node(prompt):
    food_info = agent_identify_node(prompt, nutrient_identify_agent)
    # print('food_info', food_info)
    if not food_info['is_food']:
        return "圖片中沒有食物"
    nutriend_dict = tool_agent(food_info, NutrientSearch)

    food_info['nutrient_dict'] = nutriend_dict

    res = tool_agent_cal(food_info, NutrientCalculate)

    return res

async def a_get_all_node(prompt):
    food_info =await agent_identify_node(prompt, nutrient_identify_agent)
    yield {"processing": {"nutrient_identify_agent": food_info}}

    if not food_info['is_food']:
        yield {"END":"圖片中沒有食物"}
        return
    
    nutriend_dict =await tool_agent(food_info, NutrientSearch)
    yield {"processing": {"nutrient_search_agent":nutriend_dict}}

    food_info['nutrient_dict'] = nutriend_dict

    res =await tool_agent_cal(food_info, NutrientCalculate)

    yield {"END":res}


