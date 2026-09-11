import requests
import pandas as pd
import streamlit as st

class EODHDProvider:
    def __init__(self):
        self.api_token = st.secrets.get("EODHD_API_TOKEN", "")
        self.base_url = "https://eodhd.com/api"

    def get_realtime_price(self, ticker: str) -> dict:
        """단일 종목 실시간 시세 조회"""
        if not self.api_token:
            return {"error": "EODHD_API_TOKEN 이 설정되지 않았습니다."}
            
        symbol = f"{ticker.upper()}.US"
        url = f"{self.base_url}/real-time/{symbol}?api_token={self.api_token}&fmt=json"
        
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"error": str(e)}
