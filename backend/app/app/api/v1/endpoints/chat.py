from app.core.config import settings
from app.utils.interface import chatllm as defaultllm
import logging
from app.core.config import settings as p

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.uuid6 import uuid7
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from app.utils.prompt_zero import zero_agent_prompt, image_prompt
import json
import time
# import httpx
import requests
import base64
from app.utils.graph import get_all_node, a_get_all_node
from app.utils.prompt_zero import image_prompt
from app.utils.agents import huanik
import asyncio
from app.utils.common import extract_translation

# from langgraph.prebuilt import create_react_agent

router = APIRouter()

@router.websocket("/tools")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def process_data(data):
        user_message = data["message"]
        user_img = data["image"]
        user_message = image_prompt(user_img)
        prompt = {"messages": user_message, "image_url": user_img}
        async for result in a_get_all_node(prompt):
            await asyncio.sleep(1) #需要加上此，ws的msg才能一個接一個
            if 'processing' in result:
                print('yield result', len(result), "time", datetime.now())
                await websocket.send_text(json.dumps(result))
            else:
                if not isinstance(result.get('END'), str):
                    print('yield result', len(result), "time", datetime.now())
                    await websocket.send_text(json.dumps({"Processing":{"nutrient_calculate_agent":result.get('END').content}}))
                    res = huanik("English", "Traditional chinese",
                                 result.get('END').content, "Taiwan", 5000)
                    print('yield result', len(result), "time", datetime.now())
                    res = extract_translation(res)
                    await websocket.send_text(json.dumps({"END":res}))
                else:
                    print('yield result', len(result), "time", datetime.now())
                    await websocket.send_text(json.dumps(result))

    while True:
        try:
            data = await websocket.receive_json()
            asyncio.create_task(process_data(data))
            # await process_data(data)
            
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            await asyncio.sleep(20)
            break

