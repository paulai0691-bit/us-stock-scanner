import streamlit as st

def get_secret(key_name: str, default: str = "") -> str:
    """Streamlit secrets에서 안전하게 API Key를 가져옵니다."""
    try:
        return st.secrets.get(key_name, default)
    except Exception:
        return default

# Provider별 API Key
FMP_API_KEY = get_secret("FMP_API_KEY")
ALPHAVANTAGE_API_KEY = get_secret("ALPHAVANTAGE_API_KEY")
EODHD_API_TOKEN = get_secret("EODHD_API_TOKEN")
FRED_API_KEY = get_secret("FRED_API_KEY")
MASSIVE_API_KEY = get_secret("MASSIVE_API_KEY")
