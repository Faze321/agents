import os
from agents import OpenAIChatCompletionsModel, Agent
from openai import AsyncOpenAI
from typing import Any

_PROVIDER_DEFAULTS = {
    "deepseek": (os.getenv("DEEPSEEK_API_KEY"), "https://api.deepseek.ai/v1"),
    "gemini": (os.getenv("GEMINI_API_KEY"), "https://generativelanguage.googleapis.com/v1beta/openai/")
}

class SimpleAgent(Agent):
    def __init__(
        self,
        *,
        name: str,
        instructions: str,
        model: str,
        **kwargs: Any
    ):        
        # 检测模型名称中包含的提供商
        api_key = None
        base_url = None
        model_lower = model.lower()

        # 如果是 GPT 模型，直接使用OPENAI SDK
        if model_lower.startswith("gpt"):
            model_instance = model
        # 反之则在提供商中查找
        else:
            for provider in ["deepseek", "gemini"]:
                if model_lower.startswith(provider):
                    api_key, base_url = _PROVIDER_DEFAULTS[provider]
                    client = AsyncOpenAI(api_key=api_key,base_url=base_url)
                    model_instance = OpenAIChatCompletionsModel(openai_client=client, model=model)
                    break
            if api_key is None:
                raise ValueError(f"模型名称 '{model}' 不支持。")

        super().__init__(
            model=model_instance,
            name=name,
            instructions=instructions,
            **kwargs
        )