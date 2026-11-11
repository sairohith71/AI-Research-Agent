import os

import streamlit as st
from langchain_ollama import ChatOllama
from streamlit.errors import StreamlitSecretNotFoundError


def get_setting(name, default=None):
    value = os.getenv(name)
    if value:
        return value

    try:
        return st.secrets.get(name, default)
    except StreamlitSecretNotFoundError:
        return default


def get_llm(temperature=0.2):
    model_name = get_setting(
        "OLLAMA_MODEL",
        "qwen2.5:0.5b"
    )
    ollama_url = get_setting(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    headers = {}
    if "ngrok-free.dev" in ollama_url or "ngrok-free.app" in ollama_url:
        headers["ngrok-skip-browser-warning"] = "true"

    return ChatOllama(
        model=model_name,
        base_url=ollama_url,
        temperature=temperature,
        num_ctx=1024,
        client_kwargs={"headers": headers}
    )
