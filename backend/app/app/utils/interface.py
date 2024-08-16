# from langchain_openai import AzureOpenAIEmbeddings
# 研華的Azure Open ai沒有佈署gpt-4o mini
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from app.core.config import settings as p
from langchain_community.llms import Ollama
# from langchain_community.embeddings import OllamaEmbeddings
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.chat_models import ChatOpenAI
import os
from langchain_community.chat_models import ChatLiteLLM
from typing import Optional

__all__ = ["chatllm", "embeddings"]

key_id = "sk-1234"
os.environ["AZURE_OPENAI_API_KEY"] =key_id # 👈 Team's Key
os.environ["OPENAI_API_VERSION"] ="2024-02-15-preview" # 👈 Team's Key

api_endpoint = "http://127.0.0.1:4000"
azure_model =  "azure/gpt-35-turbo-0613"
ollama_model =  "ollama_chat/llava"

ollama_endpoint =  "https://8174-35-204-20-90.ngrok-free.app"

# if p.OPENAI_API_TYPE == "azure":
#     chatllm = AzureChatOpenAI(azure_deployment=p.OPENAI_API_DEPLOYMENT,
#                               openai_api_version=p.OPENAI_API_VERSION,
#                               temperature=0)
#     embeddings = AzureOpenAIEmbeddings(deployment=p.OPENAI_API_DEPLOYMENT_ADA,
#                                        chunk_size=16)
# elif p.OPENAI_API_TYPE == "openai":
#     chatllm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
#     #embeddings = FakeEmbeddings(size=1352)
# elif p.OPENAI_API_TYPE == "nvidia":
#     pass
#     #chatllm = ChatNVIDIA(model="mixtral_8x7b",temperature=0)
#     #embeddings = NVIDIAEmbeddings(model="nvolveqa_40k")
# elif p.OPENAI_API_TYPE == "local":
# chatllm = OllamaFunctions(model=p.OLLAMA_BASE_MODEL,
#                           base_url=p.OLLAMA_BASE_URL,
#                           request_timeout=1800,
#                           format="json")
# embeddings = OllamaEmbeddings(model=p.OLLAMA_BASE_MODEL,
#                               base_url=p.OLLAMA_BASE_URL)
# embeddings = AzureOpenAIEmbeddings(deployment=p.OPENAI_API_DEPLOYMENT_ADA,
#                                    chunk_size=16)

# key_id = "sk-6FUP6K8TWIxOQMxNGHt30w"
# os.environ["OPENAI_API_KEY"] =key_id # 👈 Team's Key

# model_name = "llava_test"

# chatllm =ChatOpenAI(
#     openai_api_base="http://127.0.0.1:4000",
#     api_key = "sk-1234",
#     model = model_name,
#     temperature=0.1,
# )

class CustomLiteLLM(ChatLiteLLM):
    """Override the default LiteLLM model to allow setting infinity max_tokens"""

    max_tokens: Optional[int] = None

def load_language_model(model_name: str, endpoint:str) -> CustomLiteLLM:
    """
    Helper method for loading language model
    """
    try:
        llm_model = CustomLiteLLM(model_name=model_name, api_base = endpoint)
        # Attempts to use the provider to capture any potential missing configuration error
        llm_model.invoke("respond in 20 words. who are you?")
    except Exception as e:
        print(
            f"Error initializing the language model '{model_name}'. Please check all required variables are set. "
            "Provider docs here - https://litellm.vercel.app/docs/providers \n"
        )
        raise e
    else:
        # logger.info(f"Loaded the language model {model_name}")
        print(f"Loaded the language model {model_name}")
    # return llm_model
    return llm_model
    


# chatllm = OllamaFunctions(model=p.OLLAMA_BASE_MODEL,
#                           base_url=p.OLLAMA_BASE_URL,
#                           request_timeout=1800,
#                           temperature=0,
#                           format="json")
chatllm = load_language_model(model_name= ollama_model, endpoint =ollama_endpoint )

llama31 = OllamaFunctions(model="llama3.1",
                          base_url=p.OLLAMA_BASE_URL,
                          request_timeout=1800,
                          temperature=0,
                          format="json")
# llama31 = load_language_model(model_name = azure_model, endpoint = api_endpoint)

gemma = OllamaFunctions(model="gemma",
                        base_url=p.OLLAMA_BASE_URL,
                        request_timeout=1800,
                        temperature=0,
                        format="json")
