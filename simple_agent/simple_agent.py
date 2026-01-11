import os
from agents import OpenAIChatCompletionsModel, Agent
from openai import AsyncOpenAI
from typing import Any, Optional, Dict
from langchain_openai import ChatOpenAI
from autogen_ext.models.openai import OpenAIChatCompletionClient

_PROVIDER_DEFAULTS = {
    "deepseek": (os.getenv("DEEPSEEK_API_KEY"), "https://api.deepseek.com/v1"),
    "gemini": (os.getenv("GEMINI_API_KEY"), "https://generativelanguage.googleapis.com/v1beta/openai/")
}

def agent(
        *,
        name: str,
        instructions: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any
) -> Agent:
    model_lower = model.lower()

    # 如果是 GPT 模型，直接使用OPENAI SDK
    if model_lower.startswith("gpt"):
        return Agent(
            model=model,
            name=name,
            instructions=instructions,
            **kwargs
        )
    # 反之则在提供商中查找
    else:
        if api_key is None or base_url is None:
            for provider in ["deepseek", "gemini"]:
                if model_lower.startswith(provider):
                    api_key, base_url = _PROVIDER_DEFAULTS[provider]
                    break

        if api_key and base_url:
            client = AsyncOpenAI(api_key=api_key,base_url=base_url)
            model_instance = OpenAIChatCompletionsModel(openai_client=client, model=model)
            return Agent(
                model=model_instance,
                name=name,
                instructions=instructions,
                **kwargs
            )
        else:
            raise ValueError(f"现有的api_key和base_url下，模型名称 '{model}' 不支持。")
        

        
def chatopenai(
        *,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any
) -> ChatOpenAI:
    model_lower = model.lower()

    # 如果是 GPT 模型，直接使用OPENAI SDK
    if model_lower.startswith("gpt"):
        return ChatOpenAI(
            model=model,
            **kwargs
        )
    # 反之则在提供商中查找
    else:
        if api_key is None or base_url is None:
            for provider in ["deepseek", "gemini"]:
                if model_lower.startswith(provider):
                    api_key, base_url = _PROVIDER_DEFAULTS[provider]
                    break
        if api_key and base_url:
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url,
                **kwargs
            )
        else:
            raise ValueError(f"现有的api_key和base_url下，模型名称 '{model}' 不支持。")
        
def openaichatcompletionsclient(
        *,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_info: Optional[Dict[str, Any]] = None,
        **kwargs: Any
) -> OpenAIChatCompletionClient:
    """
    创建一个 OpenAIChatCompletionClient，支持 GPT 与兼容提供商（如 DeepSeek、Gemini）。

    扩展点：
    - api_key/base_url 可显式传入以覆盖环境默认值（适配自定义网关）。
    - model_info 可覆盖/自定义模型能力声明（如 function_calling/structured_output/json_output）。

    示例（DeepSeek 强化函数调用/结构化输出）：
        client = openaichatcompletionsclient(
            model="deepseek-chat",
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "family": "deepseek",
                "structured_output": True,
            },
        )
    """

    model_lower = model.lower()

    # 如果是 GPT 模型，直接使用 OPENAI 客户端（兼容原有 **kwargs）
    if model_lower.startswith("gpt"):
        return OpenAIChatCompletionClient(
            model=model,
            **kwargs
        )
    # 反之则在提供商中查找
    else: 
        if  api_key is None or base_url is None:
            if model_lower.startswith("deepseek"):
                api_key, base_url = _PROVIDER_DEFAULTS["deepseek"]
                model_info: Dict[str, Any] = {
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                    "family": "deepseek",
                    "structured_output": False,
                }

        if api_key and base_url:
            return OpenAIChatCompletionClient(
                model=model,
                api_key=api_key,
                base_url=base_url,
                model_info=model_info,
                **kwargs
            )
        else:
            raise ValueError(f"现有的api_key和base_url下，模型名称 '{model}' 不支持。")