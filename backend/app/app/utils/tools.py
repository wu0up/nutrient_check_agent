from app.core.config import settings as p
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.tools import BaseTool
from serpapi import GoogleSearch
from typing import Any, Optional, Annotated
from langchain_core.tools import tool
import httpx
# from app.utils import t5_pipe
# from fastapi.concurrency import run_in_threadpool
from app.utils.interface import chatllm
from app.utils.prompt_zero import text_prompt, image_system_prompt

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

pokemon_api_url = "https://pokeapi.co/api/v2/pokemon/"
# unsplash_api_url = f"https://api.unsplash.com/search/photos?client_id={settings.UNSPLASH_API_KEY}&query="
weather_api_url = "https://wttr.in"


class GeneralKnowledgeTool(BaseTool):
    name = "Search"
    description = "useful for when you need to answer questions about current events"

    def __init__(self):
        super().__init__()

    def _run(self, query: str, run_manager: Optional[Any] = None) -> str:
        """Use the tool."""
        pass

    async def _arun(self,
                    query: str,
                    run_manager: Optional[Any] = None) -> str:
        """Use the tool asynchronously."""
        chat = ChatOpenAI()
        response = await chat.agenerate([[HumanMessage(content=query)]])
        message = response.generations[0][0].text
        return message


class PokemonSearchTool(BaseTool):
    name = "search_pokemon"
    description = " Useful when asked to answer information about a pokemon"

    def __init__(self):
        super().__init__()

    def _run(self, query: str, run_manager: Optional[Any] = None) -> str:
        """Use the tool."""
        response = httpx.get(pokemon_api_url + query)
        body = response.json()
        pokemon_number = body["id"]
        pokemon_name = body["name"]
        return f"{pokemon_name} - #{pokemon_number} "

    async def _arun(self,
                    query: str,
                    run_manager: Optional[Any] = None) -> str:
        """Use the tool asynchronously."""
        async with httpx.AsyncClient() as client:
            pokemon_url = pokemon_api_url + query.lower()
            response = await client.get(pokemon_url)
            if response.status_code == 404:
                return "Pokemon not found"
            body = response.json()
            pokemon_number = body["id"]
            pokemon_name = body["name"]
            pokemon_image = body.get("sprites", {}).get(
                "front_default",
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
            )
            pokemon_types = body["types"]
            pokemon_type = pokemon_types[0].get("type",
                                                {}).get("name", "electric")
            abilities = body.get("abilities", [])
            abilities_list_names = []
            height = body["height"] / 10  # convert to meters
            weight = body["weight"] / 10  # convert to kg
            for ability in abilities:
                abilities_list_names.append(ability["ability"]["name"])
            abilities_names = ", ".join(abilities_list_names)
            return f"""{pokemon_image} \n
{pokemon_name} - #{pokemon_number} \n
Abilities: {abilities_names} \n
Type: {pokemon_type} \n
Height: {height} m \n
Weight: {weight} kg \n
Sprite: {pokemon_image} \n
"""


# class ImageSearchTool(BaseTool):
#     name = "search_image"
#     description = " Useful when asked to answer information about find images URL"
#     return_direct = True

#     def __init__(self):
#         super().__init__()

#     def _run(self, query: str, run_manager: Optional[Any] = None) -> str:
#         """Use the tool."""
#         pass

#     async def _arun(self,
#                     query: str,
#                     run_manager: Optional[Any] = None) -> str:
#         """Use the tool asynchronously."""
#         async with httpx.AsyncClient() as client:
#             if settings.UNSPLASH_API_KEY == "":
#                 return "You need to set a UNSPLASH_API_KEY"

#             unsplash_url = unsplash_api_url + query.lower()
#             response = await client.get(unsplash_url)
#             body = response.json()
#             results = body["results"]
#             images_urls = []
#             for result in results:
#                 image_url = result["urls"]["small"]
#                 images_urls.append(image_url)
#             image_list_string = "\n".join([
#                 f"{i+1}. ![Image {i+1}]({url})"
#                 for i, url in enumerate(images_urls)
#             ])
#             return image_list_string

# class YoutubeSearchTool(BaseTool):
#     name = "search_videos"
#     description = " Useful when asked to answer information about find videos"
#     return_direct = True

#     def __init__(self):
#         super().__init__()

#     def _run(self, query: str, run_manager: Optional[Any] = None) -> str:
#         """Use the tool."""
#         pass

#     async def _arun(self,
#                     query: str,
#                     run_manager: Optional[Any] = None) -> str:
#         """Use the tool asynchronously."""
#         async with httpx.AsyncClient() as client:
#             if not settings.SERP_API_KEY or settings.SERP_API_KEY == "":
#                 return "You need to set a SERP_API_KEY"

#             params = {
#                 "engine": "youtube",
#                 "search_query": query,
#                 "api_key": settings.SERP_API_KEY,
#             }
#             search = GoogleSearch(params)
#             results = search.get_dict()
#             videos = results["video_results"]
#             video_list_string = "\n".join([
#                 f"{i+1}. [{video['title']}]({video['link']})"
#                 for i, video in enumerate(videos)
#             ])
#             return video_list_string


class GeneralWeatherTool(BaseTool):
    name = "Weather"
    description = "useful for when you need to answer questions about weather"

    def __init__(self):
        super().__init__()
        # self.return_direct = True

    def _run(self, query: str, run_manager: Optional[Any] = None) -> str:
        """Use the tool."""
        pass

    async def _arun(self,
                    query: str,
                    run_manager: Optional[Any] = None) -> dict:
        """Use the tool asynchronously."""
        async with httpx.AsyncClient() as client:
            query = query.replace(" ", "+")
            query = query.replace(",", "")
            final_url = f"{weather_api_url}/{query}?format=j1"
            response = await client.get(final_url)
            if response.status_code == 404:
                return f"Could not find weather for {query}"
            weather = response.json()
            temperature = weather["current_condition"][0]
            return temperature


class NutrientSearchTool(BaseTool):
    name: str = "NutrientSearch"
    description: str = "Useful when asked to answer nutrient data about food"

    def __init__(self):
        super().__init__()
        # self.return_direct = True

    def _run(self, food: str, run_manager: Optional[Any] = None) -> str:
        """Use the tool."""
        pass

    async def _arun(self,
                    food_name: str,
                    run_manager: Optional[Any] = None) -> dict:
        """Use the tool asynchronously."""
        api_key = 'AJkI7imE8qiJN6F2a6F3kpdIlzogNsmCXDflzLTx'
        base_url = p.FOOD_DATABASE_URL
        nutrient_lst = [
            'Protein', "Total lipid (fat)", "Carbohydrate, by difference",
            "Energy", "Total Sugars"
        ]
        # Make a request to the API to search for the food
        params = {
            'api_key': api_key,
            'query': food_name,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)

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
                        nutrient_amount = nutrient.get('amount', '')
                        nutrient_info[nutrient_name] = nutrient_amount

            return nutrient_info
        else:
            # Handle API request failure
            return {'error': 'Unable to fetch nutrient information'}


# class NutrientSearchTool(BaseTool):

#     @tool("NutrientSearch")
#     async def nutrient_search(food_name: str):
#         """ Useful when asked to answer nutrient data about food"""
#         api_key = 'AJkI7imE8qiJN6F2a6F3kpdIlzogNsmCXDflzLTx'
#         base_url = p.FOOD_DATABASE_URL
#         nutrient_lst = [
#             'Protein', "Total lipid (fat)", "Carbohydrate, by difference",
#             "Energy", "Total Sugars"
#         ]
#         # Make a request to the API to search for the food
#         params = {
#             'api_key': api_key,
#             'query': food_name,
#         }
#         async with httpx.AsyncClient() as client:
#             response = await client.get(base_url, params=params)

#         if response.status_code == 200:
#             # Parse the response to get the first food item
#             food_item = response.json()['foods'][0]

#             # Extract relevant nutrient information
#             nutrient_info = {'Food': food_item['description']}
#             nutrient_info['servingSize'] = 100
#             nutrient_info['servingSizeUnit'] = 'g'
#             if 'servingSize' in food_item:
#                 nutrient_info['servingSize'] = food_item['servingSize']

#             if 'servingSizeUnit' in food_item:
#                 nutrient_info['servingSizeUnit'] = food_item['servingSizeUnit']
#             # Check if 'foodNutrients' key is present
#             if 'foodNutrients' in food_item:
#                 # Extract nutrient information based on the available keys
#                 for nutrient in food_item['foodNutrients']:
#                     nutrient_name = nutrient.get('nutrientName', '')
#                     if nutrient_name in nutrient_lst:
#                         nutrient_amount = nutrient.get('amount', '')
#                         nutrient_info[nutrient_name] = nutrient_amount

#             return nutrient_info
#         else:
#             # Handle API request failure
#             return {'error': 'Unable to fetch nutrient information'}


class FoodIdentifyTool(BaseTool):
    name: str = "FoodIdentifyTool"
    description = """"""

    def __init__(self):
        super().__init__()
        # self.return_direct = True

    def _run(self, image: str, run_manager: Optional[Any] = None) -> str:
        """Use the tool."""
        pass

    async def _arun(self,
                    image: str,
                    run_manager: Optional[Any] = None) -> dict:
        """Use the tool asynchronously."""
        chat = chatllm
        image_llm = chat.bind(images=[image])
        # response = await chat.agenerate([[HumanMessage(content=query)]])
        response = image_llm.invoke(image_system_prompt)
        print('response', response)
        message = response.generations[0][0].text
        return message


class NutrientCalTool(BaseTool):
    name: str = "NutrientCalculate"
    description = """Useful when asked to estimate nutrient information about food,
                    by use weight and nutrient data to calculate the nutrient information about food"""

    def __init__(self):
        super().__init__()
        # self.return_direct = True

    def _run(self,
             weight: float,
             nutrient_dict: dict,
             run_manager: Optional[Any] = None) -> str:
        """Use the tool."""
        pass

    async def _arun(self,
                    weight: float,
                    nutrient_dict: dict,
                    run_manager: Optional[Any] = None) -> dict:
        """Use the tool asynchronously."""
        chat = chatllm
        query = f"based on nutrient info:{nutrient_dict} and food weight {weight} to estimate calories from food. provide the reference {nutrient_dict}"
        prompt = text_prompt(query)
        # response = await chat.agenerate([[HumanMessage(content=query)]])
        agent = create_agent(chat, [], prompt)
        response = agent.invoke(query)
        print('response', response)
        message = response.generations[0][0].text
        return message


# class NutrientCalTool(BaseTool):

#     @tool("NutrientCalculate")
#     async def nutrient_calculate(weight: float, nutrient_dict: dict):
#         """Useful when asked to estimate nutrient information about food, by use weight and nutrient data to calculate the nutrient information about food"""
#         chat = chatllm
#         query = f"based on nutrient info:{nutrient_dict} and food weight {weight} to estimate calories from food. provide the reference {nutrient_dict}"
#         prompt = text_prompt(query)
#         # response = await chat.agenerate([[HumanMessage(content=query)]])
#         agent = create_agent(chat, [], prompt)
#         response = agent.invoke(query)
#         print('response', response)
#         message = response.generations[0][0].text
#         return message

# def create_agent(llm, tools, system_message: str):
#     """Create an agent."""
#     prompt = ChatPromptTemplate.from_messages([
#         (
#             "system",
#             "You are a helpful AI assistant, collaborating with other assistants."
#             " Use the provided tools to progress towards answering the question."
#             " If you are unable to fully answer, that's OK, another assistant with different tools "
#             " will help where you left off. Execute what you can to make progress."
#             " If you or any of the other assistants have the final answer or deliverable,"
#             " prefix your response with FINAL ANSWER so the team knows to stop."
#             " You have access to the following tools: {tool_names}.\n{system_message}",
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ])
#     prompt = prompt.partial(system_message=system_message)
#     prompt = prompt.partial(tool_names=", ".join([tool.name
#                                                   for tool in tools]))
#     return prompt | llm.bind_tools(tools)

# 目前無法使用
# class TranslationTool(BaseTool):
#     name = "translate_en_to_zh-TW"
#     description = "useful for changing English sentences into Chinese (Traditional)."
#     verbose = True

#     pipe = t5_pipe
#     fallback_msg = "None"

#     def _run(self, en_text: str) -> str:
#         # i.g. [{'translation_text': 'traduire cette déclaration'}]
#         result = self.pipe(en_text)
#         try:
#             translation_text = result[0].get("translation_text",
#                                              self.fallback_msg)
#         except IndexError:
#             return self.fallback_msg
#         return translation_text

#     async def _arun(self, en_text: str) -> list:
#         return await run_in_threadpool(func=self._run, en_text=en_text)
