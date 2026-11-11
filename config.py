import os
from typing import Optional

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def get_tavily_api_key() -> Optional[str]:
    try:
        api_key = st.secrets.get("TAVILY_API_KEY")
    except StreamlitSecretNotFoundError:
        api_key = None
    return api_key or os.getenv("TAVILY_API_KEY")
