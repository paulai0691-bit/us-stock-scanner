import os
import json
import requests
import streamlit as st
from datetime import datetime

def check_endpoint_debug(provider_name: str, secret_key_name: str, url_template: str) -> dict:
    key_value = st.secrets.get(secret_key_name, "").strip()
    
    # 1. 키 존재 여부 검사
    if not key_value:
        return {
            "provider": provider_name,
            "status": "FAILED",
            "http_status_code": None,
            "error": f"Streamlit Secrets에 '{secret_key_name}' 설정이 없거나 빈 값입니다."
        }
        
    url = url_template.format(key=key_value)
    
    try:
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                "provider": provider_name,
                "status": "VERIFIED",
                "http_status_code": 200,
                "response_keys": list(data.keys()) if isinstance(data, dict) else ["List Response"],
                "error": None
            }
        else:
            return {
                "provider": provider_name,
                "status": "FAILED",
                "http_status_code": resp.status_code,
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}"
            }
            
    except Exception as e:
        return {
            "provider": provider_name,
            "status": "FAILED",
            "http_status_code": None,
            "error": f"요청 예외 발생: {str(e)}"
        }

def render_data_status_page():
    st.subheader("API Data Providers Health & Detailed Debug")
    st.write("각 API Key의 로드 여부와 서버 응답 메시지를 디버깅합니다.")

    if st.button("상세 진단 테스트 실행"):
        with st.spinner("API Key 및 통신 상태를 종합 점검 중입니다..."):
            
            endpoints = {
                "FMP": ("FMP_API_KEY", "https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={key}"),
                "AlphaVantage": ("ALPHAVANTAGE_API_KEY", "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={key}"),
                "EODHD": ("EODHD_API_TOKEN", "https://eodhd.com/api/real-time/AAPL.US?api_token={key}&fmt=json"),
                "FRED": ("FRED_API_KEY", "https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={key}&file_type=json"),
                "Massive": ("MASSIVE_API_KEY", "https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={key}")
            }
            
            results = {}
            for name, (secret_name, url_tmpl) in endpoints.items():
                results[name] = check_endpoint_debug(name, secret_name, url_tmpl)
                
            st.session_state["debug_results"] = results
            st.success("진단이 완료되었습니다.")

    if "debug_results" in st.session_state:
        results = st.session_state["debug_results"]
        
        st.markdown("### API별 진단 결과")
        for name, info in results.items():
            if info["status"] == "VERIFIED":
                st.success(f"**{name}**: VERIFIED (HTTP 200)")
            else:
                st.error(f"**{name}**: FAILED | 원인: {info['error']}")

        st.markdown("### 전체 JSON 디버그 결과")
        st.json(results)
