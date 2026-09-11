import requests
import streamlit as st

class FMPProvider:
    def __init__(self):
        self.api_key = st.secrets.get("FMP_API_KEY", "")
        self.base_url_v3 = "https://financialmodelingprep.com/api/v3"
        self.base_url_v4 = "https://financialmodelingprep.com/api/v4"

    def test_fmp_connection(self) -> dict:
        """FMP 주요 엔드포인트를 다각도로 테스트하여 수신 여부를 확인합니다."""
        if not self.api_key:
            return {"status": "FAILED", "error": "FMP_API_KEY 가 설정되지 않았습니다."}
            
        test_endpoints = {
            "v3_profile": f"{self.base_url_v3}/profile/AAPL?apikey={self.api_key}",
            "v3_quote": f"{self.base_url_v3}/quote/AAPL?apikey={self.api_key}",
            "v3_market_cap": f"{self.base_url_v3}/market-capitalization/AAPL?apikey={self.api_key}",
        }
        
        results = {}
        for name, url in test_endpoints.items():
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    results[name] = {
                        "status": "VERIFIED",
                        "http_code": 200,
                        "data_sample": resp.json()[:1] if isinstance(resp.json(), list) else resp.json()
                    }
                else:
                    results[name] = {
                        "status": "FAILED",
                        "http_code": resp.status_code,
                        "error_text": resp.text[:200]
                    }
            except Exception as e:
                results[name] = {"status": "FAILED", "error": str(e)}
                
        return results

    def get_company_profile(self, ticker: str) -> dict:
        """기업 기본 정보(Profile) 조회"""
        if not self.api_key:
            return {"error": "FMP_API_KEY 가 설정되지 않았습니다."}
            
        url = f"{self.base_url_v3}/profile/{ticker.upper()}?apikey={self.api_key}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data[0] if isinstance(data, list) and len(data) > 0 else {}
            return {"error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"error": str(e)}
