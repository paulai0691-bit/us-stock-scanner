import os
import json
import requests
import streamlit as st

def check_fmp_multi_fallback(api_key: str) -> dict:
    """FMP의 신규 `/stable` 규격 및 구버전 `/api/v3` 규격을 순차적으로 테스트합니다."""
    targets = [
        ("v3_standard", f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={api_key}", {}),
        ("stable_param", f"https://financialmodelingprep.com/stable/profile?symbol=AAPL&apikey={api_key}", {}),
        ("v3_header", "https://financialmodelingprep.com/api/v3/profile/AAPL", {"apikey": api_key}),
    ]
    
    last_error = ""
    for name, url, headers in targets:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                keys = list(data[0].keys()) if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) else []
                return {
                    "provider": "FMP",
                    "status": "VERIFIED",
                    "http_status_code": 200,
                    "endpoint_used": name,
                    "response_keys": keys,
                    "error": None
                }
            else:
                last_error = f"[{name}] HTTP {resp.status_code}: {resp.text[:100]}"
        except Exception as e:
            last_error = f"[{name}] Exception: {str(e)}"
            
    return {
        "provider": "FMP",
        "status": "FAILED",
        "http_status_code": None,
        "error": last_error
    }

def check_endpoint(provider_name: str, secret_key_name: str, url_template: str) -> dict:
    key_value = st.secrets.get(secret_key_name, "").strip()
    
    if not key_value:
        return {
            "provider": provider_name,
            "status": "FAILED",
            "http_status_code": None,
            "error": f"'{secret_key_name}' 값이 설정되지 않았습니다."
        }

    # FMP일 경우 다각도 엔드포인트 테스트 적용
    if provider_name == "FMP":
        return check_fmp_multi_fallback(key_value)
        
    url = url_template.format(key=key_value)
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            response_keys = []
            if isinstance(data, dict):
                response_keys = list(data.keys())
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                response_keys = list(data[0].keys())
                
            return {
                "provider": provider_name,
                "status": "VERIFIED",
                "http_status_code": 200,
                "response_keys": response_keys,
                "error": None
            }
        else:
            return {
                "provider": provider_name,
                "status": "FAILED",
                "http_status_code": resp.status_code,
                "error": f"HTTP {resp.status_code}: {resp.text[:150]}"
            }
            
    except Exception as e:
        return {
            "provider": provider_name,
            "status": "FAILED",
            "http_status_code": None,
            "error": str(e)
        }

def render_data_status_page():
    st.subheader("📊 API Data Providers Health & Validation")
    st.write("Streamlit Secrets에 등록된 API 키를 사용하여 전체 데이터 제공자의 연결 상태를 검증합니다.")

    if st.button("전체 API 연결 재검증 실행"):
        with st.spinner("5개 API 연결 상태를 검증 중입니다..."):
            endpoints = {
                "FMP": ("FMP_API_KEY", "https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={key}"),
                "AlphaVantage": ("ALPHAVANTAGE_API_KEY", "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={key}"),
                "EODHD": ("EODHD_API_TOKEN", "https://eodhd.com/api/real-time/AAPL.US?api_token={key}&fmt=json"),
                "FRED": ("FRED_API_KEY", "https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={key}&file_type=json"),
                "Massive": ("MASSIVE_API_KEY", "https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={key}")
            }
            
            results = {}
            for name, (secret_name, url_tmpl) in endpoints.items():
                results[name] = check_endpoint(name, secret_name, url_tmpl)
                
            os.makedirs("data/raw", exist_ok=True)
            report_path = "data/raw/api_validation_report.json"
            
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
                
            st.session_state["validation_results"] = results
            st.success("검증이 완료되었습니다!")

    if "validation_results" in st.session_state:
        results = st.session_state["validation_results"]
        
        st.markdown("### 검증 결과 요약")
        cols = st.columns(len(results))
        for idx, (provider, info) in enumerate(results.items()):
            with cols[idx]:
                if info["status"] == "VERIFIED":
                    st.success(f"**{provider}**\n\nVERIFIED")
                else:
                    st.error(f"**{provider}**\n\nFAILED")

        st.markdown("### 상세 응답 데이터 리포트")
        st.json(results)
