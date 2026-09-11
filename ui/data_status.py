import os
import json
import requests
import streamlit as st

def render_data_status_page():
    st.subheader("🛠️ Secrets (시크릿) 연동 문제 해결")
    st.write("스트림릿 시크릿에 입력하신 설정이 코드와 어떻게 다르게 연결되었는지 확인합니다.")

    # 1. 스트림릿이 실제로 인식한 시크릿 키 목록 출력
    try:
        loaded_keys = list(st.secrets.keys())
        if not loaded_keys:
            st.error("🚨 **스트림릿이 아무런 시크릿 키도 읽지 못했습니다!** 설정창 입력 양식(따옴표 등)에 오류가 있을 가능성이 높습니다.")
        else:
            st.info(f"✅ **현재 스트림릿이 인식한 키 목록:** {loaded_keys}")
    except Exception as e:
        st.error(f"시크릿을 읽는 중 에러 발생: {e}")

    st.markdown("---")
    
    if st.button("다시 API 연결 테스트 실행"):
        with st.spinner("테스트 중입니다..."):
            endpoints = {
                "FMP": ("FMP_API_KEY", "https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={key}"),
                "AlphaVantage": ("ALPHAVANTAGE_API_KEY", "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={key}"),
                "EODHD": ("EODHD_API_TOKEN", "https://eodhd.com/api/real-time/AAPL.US?api_token={key}&fmt=json"),
                "FRED": ("FRED_API_KEY", "https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key={key}&file_type=json"),
                "Massive": ("MASSIVE_API_KEY", "https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={key}")
            }
            
            results = {}
            for name, (secret_name, url_tmpl) in endpoints.items():
                key_val = st.secrets.get(secret_name, "").strip()
                if not key_val:
                    results[name] = {"status": "FAILED", "error": f"'{secret_name}' 값을 찾을 수 없습니다."}
                    continue
                    
                url = url_tmpl.format(key=key_val)
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        results[name] = {"status": "VERIFIED", "error": "정상 작동"}
                    else:
                        results[name] = {"status": "FAILED", "error": f"HTTP {resp.status_code}: {resp.text[:100]}"}
                except Exception as e:
                    results[name] = {"status": "FAILED", "error": str(e)}
                    
            st.session_state["debug_results"] = results

    if "debug_results" in st.session_state:
        st.markdown("### 🔍 상세 진단 결과")
        for name, info in st.session_state["debug_results"].items():
            if info["status"] == "VERIFIED":
                st.success(f"**{name}**: ✅ 정상 작동")
            else:
                st.error(f"**{name}**: ❌ 실패 | 원인: {info['error']}")
