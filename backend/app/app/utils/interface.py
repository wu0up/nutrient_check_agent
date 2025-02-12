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
    


chatllm = OllamaFunctions(model=p.OLLAMA_BASE_MODEL,
                          base_url=p.OLLAMA_BASE_URL,
                          request_timeout=1800,
                          temperature=0,
                          format="json")
# chatllm = load_language_model(model_name= ollama_model, endpoint =ollama_endpoint )

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
