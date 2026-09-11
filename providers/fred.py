import requests
import pandas as pd
import streamlit as st

class FREDProvider:
    def __init__(self):
        self.api_key = st.secrets.get("FRED_API_KEY", "")
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"

    def get_series_data(self, series_id: str = "UNRATE") -> pd.DataFrame:
        """FRED 시리즈 데이터 수집 (예: UNRATE - 실업률)"""
        if not self.api_key:
            return pd.DataFrame()
            
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        try:
            resp = requests.get(self.base_url, params=params, timeout=10)
            if resp.status_code == 200:
                obs = resp.json().get("observations", [])
                df = pd.DataFrame(obs)
                if not df.empty:
                    df = df[['date', 'value']]
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                return df
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()
