from app.utils.graph import FoodGraph, FoodGraph_test
import base64
from app.utils.prompt_zero import image_prompt

file_path = r"C:\Users\PJ-Lin\Documents\LLM\multi_tool\food_eva.jpg"
with open(file_path, 'rb') as file:
    image_data = base64.b64encode(file.read()).decode("utf-8")

user_message = image_prompt(image_data)
prompt = {"messages": user_message, "image_url": image_data}

if __name__ == "__main__":
    # print(prompt)
    graph_result = FoodGraph_test.invoke(prompt)
