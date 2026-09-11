import requests
import streamlit as st

class MassiveProvider:
    def __init__(self):
        self.api_key = st.secrets.get("MASSIVE_API_KEY", "")
        self.base_url = "https://api.polygon.io"

    def get_previous_close(self, ticker: str) -> dict:
        """전일 종가/거래량 데이터 조회"""
        if not self.api_key:
            return {"error": "MASSIVE_API_KEY 가 설정되지 않았습니다."}
            
        url = f"{self.base_url}/v2/aggs/ticker/{ticker.upper()}/prev?apiKey={self.api_key}"
        
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"error": str(e)}
