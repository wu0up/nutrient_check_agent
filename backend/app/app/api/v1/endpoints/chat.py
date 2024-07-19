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
# from app.utils.tools import (GeneralKnowledgeTool, ImageSearchTool,
#                              PokemonSearchTool, YoutubeSearchTool,
#                              GeneralWeatherTool, NutrientCalTool,
#                              NutrientSearchTool)
from app.utils.tools import NutrientSearchTool
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
from langchain.agents import ZeroShotAgent, AgentExecutor, create_react_agent
from app.utils.prompt_zero import zero_agent_prompt, image_prompt
import json

# from langgraph.prebuilt import create_react_agent

router = APIRouter()

memory = ConversationBufferMemory(memory_key="chat_history",
                                  return_messages=True)


def run_llm(question, image_b64):
    print('run_llm')
    llm_with_image_context = defaultllm.bind(images=image_b64)
    res = llm_with_image_context.invoke(question)
    return res


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

    # if not settings.OPENAI_API_KEY.startswith("sk-"):
    #     await websocket.send_json({"error": "OPENAI_API_KEY is not set"})
    #     return
    """
    直接串Ollama的post api
    """

    while True:
        try:
            data = await websocket.receive_json()
            user_message = data["message"]
            user_img = data["image"]
            user_message = image_prompt(user_img)
            # user_message_card = create_adaptive_card(user_message)

            # resp = IChatResponse(
            #     sender="you",
            #     # message=user_message_card.to_dict(),
            #     message=user_message,
            #     type="start",
            #     message_id=str(uuid7()),
            #     id=str(uuid7()),
            # )

            # await websocket.send_json(resp.dict())
            # message_id: str = str(uuid7())
            # custom_handler = CustomFinalStreamingStdOutCallbackHandler(
            #     websocket, message_id=message_id)

            # tools = [
            #     # GeneralKnowledgeTool(),
            #     # PokemonSearchTool(),
            #     # ImageSearchTool(),
            #     # YoutubeSearchTool(),
            #     # GeneralWeatherTool(),
            #     NutrientSearchTool(),
            #     # NutrientCalTool()
            # ]

            # # llm = ChatOpenAI(
            # #     streaming=True,
            # #     temperature=0,
            # # )

            # #TODO: handle memory
            # agent = create_react_agent(
            #     llm=defaultllm,
            #     tools=tools,
            #     prompt=image_prompt,
            #     # checkpointer=memory
            # )
            # agent_executor = AgentExecutor(agent=agent, tools=tools)
            # await agent_executor.arun(input=user_img,
            #                           callbacks=[custom_handler])
            queestion = "describe exactly what food this is, including its taste in one short sentence"
            res = run_llm(queestion, user_img)
            response = {"result": res}

            await websocket.send(json.dumps(response))
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
