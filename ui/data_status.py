import os
import json
import requests
import streamlit as st
from datetime import datetime
from providers.fmp import FMPProvider

def check_endpoint(provider_name: str, url: str) -> dict:
    report = {
        "provider": provider_name,
        "timestamp": datetime.now().isoformat(),
        "url_tested": url.split("?")[0],
        "status": "UNKNOWN",
        "http_status_code": None,
        "response_keys": [],
        "sample_data": None,
        "error": None
    }
    
    try:
        resp = requests.get(url, timeout=10)
        report["http_status_code"] = resp.status_code
        
        if resp.status_code == 200:
            data = resp.json()
            report["status"] = "VERIFIED"
            
            if isinstance(data, dict):
                report["response_keys"] = list(data.keys())
                report["sample_data"] = {k: str(v)[:80] for k, v in list(data.items())[:3]}
            elif isinstance(data, list) and len(data) > 0:
                report["response_keys"] = list(data[0].keys()) if isinstance(data[0], dict) else ["List"]
                report["sample_data"] = data[0] if isinstance(data[0], dict) else str(data[:2])
        else:
            report["status"] = "FAILED"
            report["error"] = f"HTTP {resp.status_code}: {resp.text[:200]}"
            
    except Exception as e:
        report["status"] = "FAILED"
        report["error"] = str(e)
        
    return report

def render_data_status_page():
    st.subheader("API Data Providers Health & Validation")
    st.write("Streamlit Secrets에 등록된 API 키를 사용하여 데이터 제공자의 연결 상태를 검증합니다.")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("전체 API 연결 상태 테스트"):
            with st.spinner("API 연결을 검증 중입니다..."):
                fmp_key = st.secrets.get("FMP_API_KEY", "")
                av_key = st.secrets.get("ALPHAVANTAGE_API_KEY", "")
                eod_key = st.secrets.get("EODHD_API_TOKEN", "")
                fred_key = st.secrets.get("FRED_API_KEY", "")
                massive_key = st.secrets.get("MASSIVE_API_KEY", "")
                
                targets = {
                    "FMP": f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={fmp_key}",
                    "AlphaVantage": f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={av_key}",
                    "EODHD": f"https://eodhd.com/api/real-time/AAPL.US?api_token={eod_key}&fmt=json",
                    "FRED": f"https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={fred_key}&file_type=json",
                    "Massive": f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={massive_key}"
                }
                
                results = {}
                for name, url in targets.items():
                    results[name] = check_endpoint(name, url)
                    
                os.makedirs("data/raw", exist_ok=True)
                report_path = "data/raw/api_validation_report.json"
                
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
                    
                st.success("검증이 완료되었습니다!")

    with col2:
        if st.button("FMP Endpoint 다각도 진단 실행"):
            with st.spinner("FMP 엔드포인트를 진단 중입니다..."):
                fmp = FMPProvider()
                fmp_results = fmp.test_fmp_connection()
                st.session_state["fmp_diag"] = fmp_results

    # FMP 진단 결과 출력
    if "fmp_diag" in st.session_state:
        st.markdown("### FMP 상세 진단 결과")
        st.json(st.session_state["fmp_diag"])

    # 기존 검증 결과 리포트 출력
    report_path = "data/raw/api_validation_report.json"
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            
        st.markdown("### 최근 검증 결과")
        cols = st.columns(len(report_data))
        for idx, (provider, info) in enumerate(report_data.items()):
            with cols[idx]:
                status = info.get("status", "UNKNOWN")
                if status == "VERIFIED":
                    st.success(f"**{provider}**\n\nVERIFIED")
                else:
                    st.error(f"**{provider}**\n\nFAILED")
                    
        st.markdown("### 상세 JSON 응답 리포트")
        st.json(report_data)
