# from app.utils.graph import FoodGraph, nutrient_search_node, FoodGraph_test, nutrient_identify_agent
import base64
from app.utils.graph import get_all_node
from app.utils.prompt_zero import image_prompt
from app.utils.tools import NutrientSearch, NutrientCalculate
import asyncio
from langchain_core.tools import StructuredTool

file_path = r"C:\Users\PJ-Lin\Documents\LLM\multi_tool\food_eva.jpg"
with open(file_path, 'rb') as file:
    image_data = base64.b64encode(file.read()).decode("utf-8")

user_message = image_prompt(image_data)
prompt = {"messages": user_message, "image_url": image_data}

prompt_tools = {
    "messages": [{
        'name': 'nutrient_search',
        'args': {
            'food_name': 'French fries',
            'weight': 150
        },
        'id': 'call_a04e670e72dd420291545c3a17de31b7',
        'type': 'tool_call'
    }]
}

# async def test():
#     calculator = StructuredTool.from_function(coroutine=NutrientSearch)
#     print(await calculator.ainvoke({
#         'food_name': 'French fries',
#         'weight': 150
#     }))

#     multiply = NutrientSearchTool()
#     print("multiply.name", multiply.name)
#     print("multiply.description", multiply.description)
#     result = await multiply.ainvoke({'food_name': 'French fries'})
#     print('result', result)

if __name__ == "__main__":
    # print(prompt)
    graph_result = get_all_node(prompt)
    # graph_result = nutrient_search_node.invoke(prompt_tools)
    # graph_result = FoodGraph_test.invoke(prompt)
    # agent_action = nutrient_identify_agent.invoke(prompt)
    # agent_action.tool_calls[-1]['name'] = "NutrientSearch"
    # print('agent_action', agent_action)
    # graph_result = nutrient_search_node.invoke({"messages": [agent_action]})
    # print("graph_result", graph_result)

    # asyncio.run(test())
