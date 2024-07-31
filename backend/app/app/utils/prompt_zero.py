# flake8: noqa
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class IZeroPrompt(BaseModel):
    prefix: str
    suffix: str
    format_instructions: str
    input_variables: list[str]


PREFIX = """Answer the following questions as best and complete you can. You have access to the following tools:"""
FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer; if the input is food image, describe exactly what food this is, including its taste in one short sentence.
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""
SUFFIX = """When answering, your answers should be with markdown format.

Question: {input}
Thought:{agent_scratchpad}"""

# Question: What is the topic of the question?
# Thought: I now know the partial answer
# Action: the action to take, should be determinate the topic of the question with GeneralKnowledgeTool tool
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat 1 time)
# If you detect this answer topic is about Greetings append this to the end of the answer: "Greetings" : [BOOL_VALUE]
zero_agent_prompt = IZeroPrompt(
    prefix=PREFIX,
    suffix=SUFFIX,
    format_instructions=FORMAT_INSTRUCTIONS,
    input_variables=["input", "agent_scratchpad"],
)


def image_prompt(image_data: str):
    message = HumanMessage(content=[
        {
            "type": "text",
            "text": "estimate the nutrient of this image"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_data}"
            },
        },
    ], )
    return message


image_system_prompt = """
You are a highly knowledgeable and professional nutritionist with expertise in analyzing meal components and evaluating their caloric content.
as reciving an image, you need to identify the items in the image is food or not. 
if the image is food, you need to identify food name and food weight. 
"""

# image_prompt_template = ChatPromptTemplate.from_messages([
#     (
#         "system",
#         system_prompt,
#     ),
#     (
#         "human",
#         [
#             {
#                 "type": "text",
#                 "text": "{user_msg}"
#             },
#             {
#                 "type": "image_url",
#                 "image_url": {
#                     "url": f"data:image/jpeg;base64,{image_data}"
#                 },
#             },
#         ],
#     ),
# ])


def text_prompt(user_msg: str):
    # region: Identifying the items in the image
    system_prompt = """
    You are a highly knowledgeable and professional nutritionist.
    you can estimate the food nutrient data by food weight and nutrient info.
    """

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            system_prompt,
        ),
        (
            "human",
            [
                {
                    "type": "text",
                    "text": "{user_msg}"
                },
            ],
        ),
    ])

    return prompt_template


# endregion

# region: Answering question on what items are recyclable, and providing instructions
# recycling_question = """
# For each of the image_items, is the item recyclable in Singapore? If so, provide the recycling instructions. If the item is not recyclable. If the item is not recyclable, answer why the item(s) are not recyclable and how to properly dispose it.

# """

# template = """Answer the question referring to the following context.
# Context: {context}

# Question: {question}
# """
