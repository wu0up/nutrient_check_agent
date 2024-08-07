# from langchain_openai import AzureOpenAIEmbeddings
# from langchain_openai import AzureChatOpenAI, ChatOpenAI
from app.core.config import settings as p
from langchain_community.llms import Ollama
# from langchain_community.embeddings import OllamaEmbeddings
from langchain_experimental.llms.ollama_functions import OllamaFunctions

__all__ = ["chatllm", "embeddings"]

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

chatllm = OllamaFunctions(model=p.OLLAMA_BASE_MODEL,
                          base_url=p.OLLAMA_BASE_URL,
                          request_timeout=1800,
                          temperature=0,
                          format="json")

llama31 = OllamaFunctions(model="llama3.1",
                          base_url=p.OLLAMA_BASE_URL,
                          request_timeout=1800,
                          temperature=0,
                          format="json")

gemma = OllamaFunctions(model="gemma",
                        base_url=p.OLLAMA_BASE_URL,
                        request_timeout=1800,
                        temperature=0,
                        format="json")
