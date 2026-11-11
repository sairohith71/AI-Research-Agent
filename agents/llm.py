import os
from langchain_ollama import ChatOllama


def get_llm(temperature=0.2):
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

    return ChatOllama(
        model=model_name,
        temperature=temperature,
        num_ctx=1024
    )