from fastapi import FastAPI, HTTPException, Request, APIRouter, status, UploadFile, Query, File
from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
from app.templates.chat import chat_html
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from app.utils.graph import get_all_node, a_get_all_node


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("startup fastapi")
    yield
    # shutdown
    print("shutdown fastapi")


# Core Application Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS origins enabled
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    """
    An example "Hello world" FastAPI route.
    """
    # if oso.is_allowed(user, "read", message):
    return {"message": "Hello World"}


async def send_message(content: str):
    # callback = AsyncIteratorCallbackHandler()
    # model = ChatOpenAI(
    #     streaming=True,
    #     verbose=True,
    #     callbacks=[callback],
    # )

    # task = asyncio.create_task(
    #     model.agenerate(messages=[[HumanMessage(content=content)]])
    # )

    try:
        for token in content:
            yield token
    except Exception as e:
        print(f"Caught exception: {e}")


class Message(BaseModel):
    content: str


@app.post("/stream_chat/")
async def stream_chat(message: Message, file: UploadFile = File(...)):
    generator = send_message(message.content)
    return StreamingResponse(generator, media_type="text/event-stream")


# @app.get("/chat", response_class=HTMLResponse)
# async def chat(*,image: UploadFile = File(...),request: Request):

#     async def process_data(data):
#         user_message = data["message"]
#         user_img = data["image"]
#         user_message = image_prompt(user_img)
#         prompt = {"messages": user_message, "image_url": user_img}

#         async for result in a_get_all_node(prompt):
#             print('yield result', result)
#             if 'processing' in result:
#                 await websocket.send_text(json.dumps(result))
#             else:
#                 if not isinstance(result.get('END'), str):
#                     res = huanik("English", "Traditional chinese",
#                                  result.get('END').content, "Taiwan", 5000)
#                     await websocket.send_text(json.dumps(res))
#                 else:
#                     await websocket.send_text(json.dumps(result.get('END')))

#     while True:
#         try:
#             data = await websocket.receive_json()
#             asyncio.create_task(process_data(data))
#         except WebSocketDisconnect:
#             logging.info("websocket disconnect")
#             break

# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
