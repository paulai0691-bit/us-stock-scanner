import requests
import streamlit as st

class AlphaVantageProvider:
    def __init__(self):
        self.api_key = st.secrets.get("ALPHAVANTAGE_API_KEY", "")
        self.base_url = "https://www.alphavantage.co/query"

    def get_global_quote(self, ticker: str) -> dict:
        """Global Quote (최신 시세 요약) 조회"""
        if not self.api_key:
            return {"error": "ALPHAVANTAGE_API_KEY 가 설정되지 않았습니다."}
            
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker.upper(),
            "apikey": self.api_key
        }
        
        try:
            resp = requests.get(self.base_url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("Global Quote", {})
            return {"error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"error": str(e)}
