from app.core.config import settings as p
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.tools import BaseTool
from typing import Any, Optional, Annotated
from langchain_core.tools import tool
import httpx
# from app.utils import t5_pipe
# from fastapi.concurrency import run_in_threadpool
from app.utils.interface import chatllm, llama31, gemma
from app.utils.prompt_zero import text_prompt, image_system_prompt
import re, base64, requests, json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


def NutrientSearch(food_name: str):
    """ Useful when asked to answer nutrient data about food"""
    api_key = p.FOOD_DATABASE_API_KEY
    base_url = p.FOOD_DATABASE_URL
    nutrient_lst = [
        'Protein', "Total lipid (fat)", "Carbohydrate, by difference",
        "Energy", "Total Sugars"
    ]
    # Make a request to the API to search for the food
    params = {
        'api_key': api_key,
        'query': food_name,
        "pageSize": 3,
        "pageNumber": 1
    }
    response = requests.request(
        "get",
        base_url,
        params=params,
        timeout=600,
        #  headers=headers,
        #  verify=verify
    )

    # response = json.loads(r.text)

    if response.status_code == 200:
        # Parse the response to get the first food item
        food_item = response.json()['foods'][0]

        # Extract relevant nutrient information
        nutrient_info = {'Food': food_item['description']}
        nutrient_info['servingSize'] = 100
        nutrient_info['servingSizeUnit'] = 'g'
        if 'servingSize' in food_item:
            nutrient_info['servingSize'] = food_item['servingSize']

        if 'servingSizeUnit' in food_item:
            nutrient_info['servingSizeUnit'] = food_item['servingSizeUnit']
        # Check if 'foodNutrients' key is present
        if 'foodNutrients' in food_item:
            # Extract nutrient information based on the available keys
            for nutrient in food_item['foodNutrients']:
                nutrient_name = nutrient.get('nutrientName', '')

                if nutrient_name in nutrient_lst:

                    nutrient_amount = nutrient.get('value', '')
                    nutrient_info[nutrient_name] = nutrient_amount

        return nutrient_info
    else:
        # Handle API request failure
        return {'error': 'Unable to fetch nutrient information'}


def NutrientCalculate(weight: float, nutrient_dict: dict):
    """Useful when asked to estimate nutrient information about food, by use weight and nutrient data to calculate the nutrient information about food"""

    nutrient_dict_str = json.dumps(nutrient_dict)
    query = f"""you are good at math.you know the weight of food is {weight}, and each nutrient per serving size in nutrient info: {nutrient_dict_str}, 
    you also know serving size is servingSize in nutrient_dict_str, 
    your task is to calculate the food nutrient based on weight {weight} and nutrient info {nutrient_dict_str} and provide the food nutrient. 
    display the reference {nutrient_dict_str} from usda and answer you calculated in response.
    """
    response = llama31.invoke(query)
    print('response', response)

    return response


def create_agent(llm):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are good at math",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ])
    # prompt = prompt.partial(system_message=system_message)
    # prompt = prompt.partial(tool_names=", ".join([tool.name
    #                                               for tool in tools]))
    return prompt | llm

