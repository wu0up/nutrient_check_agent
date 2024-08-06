from app.core.config import settings
from app.utils.interface import chatllm as defaultllm
from app.schemas.message_schema import (
    IChatResponse, )
import logging
from app.utils.adaptive_cards.cards import create_adaptive_card
from app.utils.callback import (
    CustomAsyncCallbackHandler,
    CustomFinalStreamingStdOutCallbackHandler,
)
from app.core.config import settings as p

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.uuid6 import uuid7
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from app.utils.prompt_zero import zero_agent_prompt, image_prompt
import json
# import httpx
import requests
import base64
from app.utils.graph import get_all_node
from app.utils.prompt_zero import image_prompt

# from langgraph.prebuilt import create_react_agent

router = APIRouter()

memory = ConversationBufferMemory(memory_key="chat_history",
                                  return_messages=True)


# use tool, use memory
async def run_llm(question, image_data):
    """Use the tool asynchronously."""
    payload = {
        "model": "llava",
        "stream": True,
        "prompt": question,
        "images": [image_data]
    }
    url = f"{p.OLLAMA_BASE_URL}/api/generate"
    headers = {"Content-Type": "application/json"}
    try:
        with requests.post(url, json=payload, headers=headers,
                           stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {line}")
            else:
                print(f"Error: {response.status_code}")
                yield {"response": "Error in generating response"}
    except requests.RequestException as e:
        print(f"Request error: {e}")
        yield {"response": "Error in generating response"}


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # if not settings.OPENAI_API_KEY.startswith("sk-"):
    #     await websocket.send_json({"error": "OPENAI_API_KEY is not set"})
    #     return

    while True:
        data = await websocket.receive_json()
        user_message = data["message"]
        user_message_card = create_adaptive_card(user_message)

        resp = IChatResponse(
            sender="you",
            message=user_message_card.to_dict(),
            type="start",
            message_id=str(uuid7()),
            id=str(uuid7()),
        )
        await websocket.send_json(resp.dict())

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content="You are a chatbot having a conversation with a human."
            ),  # The persistent system prompt
            MessagesPlaceholder(variable_name="chat_history"
                                ),  # Where the memory will be stored.
            HumanMessagePromptTemplate.from_template(
                "{human_input}"),  # Where the human input will injectd
        ])
        message_id: str = str(uuid7())
        custom_handler = CustomAsyncCallbackHandler(websocket=websocket,
                                                    message_id=message_id)
        llm = ChatOpenAI(streaming=True, callbacks=[custom_handler])

        chat_llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=False,
            memory=memory,
        )

        await chat_llm_chain.apredict(human_input=user_message, )


@router.websocket("/tools")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    """
    直接串Ollama的post api
    """

    while True:
        try:
            data = await websocket.receive_json()
            user_message = data["message"]

            user_img = data["image"]
            user_message = image_prompt(user_img)
            prompt = {"messages": user_message, "image_url": user_img}

            graph_result = get_all_node(prompt)
            print('graph_result', graph_result)
            result = graph_result.content

            await websocket.send_text(json.dumps(result))

        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
