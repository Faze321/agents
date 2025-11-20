import os
from agents import OpenAIChatCompletionsModel, Agent, InputGuardrail, OutputGuardrail
from openai import AsyncOpenAI
from typing import Any

_PROVIDER_DEFAULTS = {
    "deepseek": (os.getenv("DEEPSEEK_API_KEY"), "https://api.deepseek.ai/v1"),
    "gemini": (os.getenv("GOOGLE_API_KEY"), "https://generativelanguage.googleapis.com/v1beta/openai/"),
    "gpt": (os.getenv("OPENAI_API_KEY"), None)
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
        for provider in ["deepseek", "gpt", "gemini"]:
            if model_lower.startswith(provider):
                api_key, base_url = _PROVIDER_DEFAULTS[provider]
                break

        if api_key is None:
            raise ValueError(f"模型名称 '{model}' 不支持。")
        
        # 创建客户端
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        model_instance = OpenAIChatCompletionsModel(openai_client=client, model=model)

        super().__init__(
            model=model_instance,
            name=name,
            instructions=instructions,
            **kwargs
        )