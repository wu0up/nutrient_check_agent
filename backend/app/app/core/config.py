import os
from pydantic import AnyHttpUrl, field_validator
from pydantic import Field
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    PROJECT_NAME: str = "app"
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    OPENAI_API_KEY: str = ""
    UNSPLASH_API_KEY: str = ""
    SERP_API_KEY: str = ""

    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl] = ["*"]
    """LangSmith"""
    LANGCHAIN_TRACING_V2: str = Field("true", env="LANGCHAIN_TRACING_V2")
    # LANGCHAIN_API_KEY: str = Field("ls__17508d8a92ad40d0bdcecd12f5dea69b",
    #                                env="LANGCHAIN_API_KEY")
    LANGCHAIN_API_KEY: str = Field(
        "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",
        env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = Field("Multi_tool", env="LANGCHAIN_PROJECT")
    """LLM"""
    OPENAI_API_TYPE: Optional[str] = Field("local", env="OPENAI_API_TYPE")
    OPENAI_API_VERSION: Optional[str] = Field("2024-02-15-preview",
                                              env="OPENAI_API_VERSION")
    OPENAI_API_KEY: Optional[str] = Field("546c2da351d0469eb3d6f9b76b4702d0",
                                          env="OPENAI_API_KEY")
    OPENAI_ENDPOINT: Optional[str] = Field(
        "https://ifactory-openai.openai.azure.com", env="OPENAI_ENDPOINT")
    OPENAI_API_DEPLOYMENT: Optional[str] = Field("gpt-35-turbo-0613",
                                                 env="OPENAI_API_DEPLOYMENT")
    OPENAI_API_DEPLOYMENT_ADA: Optional[str] = Field(
        "text-embedding-ada-002", env="OPENAI_API_DEPLOYMENT_ADA")

    # """MILVUS"""
    # MILVUS_HOST: Optional[str] = Field("127.0.0.1", env="MILVUS_HOST")
    # MILVUS_PORT: Optional[str] = Field("19530", env="MILVUS_PORT")
    # MILVUS_COLLECTION: Optional[str] = Field("test_kdb_colleciotn",
    #                                          env="MILVUS_COLLECTION")
    # MILVUS_DATABASE: Optional[str] = Field("test_kdb", env="MILVUS_DATABASE")
    # """TAVILY"""
    # TAVILY_API_KEY: Optional[str] = Field(
    #     "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", env="TAVILY_API_KEY")
    """OLLMA"""
    OLLAMA_BASE_URL: Optional[str] = Field(
        "https://83c4-35-229-39-71.ngrok-free.app", env="OLLAMA_BASE_URL")
    # OLLAMA_BASE_MODEL: Optional[str] = Field("gemma2", env="OLLAMA_BASE_MODEL")
    OLLAMA_BASE_MODEL: Optional[str] = Field("llava", env="OLLAMA_BASE_MODEL")
    """FOOD DATABASE"""
    FOOD_DATABASE_URL: Optional[str] = Field(
        "https://api.nal.usda.gov/fdc/v1/foods/search",
        env="FOOD_DATABASE_URL")
    FOOD_DATABASE_API_KEY: Optional[str] = Field("",
                                                 env="FOOD_DATABASE_API_KEY")

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(case_sensitive=True,
                                      env_file=os.path.expanduser("~/.env"))


settings = Settings()
