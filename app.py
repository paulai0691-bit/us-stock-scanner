import streamlit as st
from ui.data_status import render_data_status_page

st.set_page_config(
    page_title="US Stock Structural Opportunity Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("US Stock Structural Opportunity Scanner")
st.caption("구조적 수급 및 경제적 메커니즘 기반 미국 주식 탐색 및 추천 시스템")

# 탭 메뉴 구성
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Market Overview", 
    "Stock Screener", 
    "Stock Detail", 
    "Recommendation", 
    "Data Status", 
    "Research / Model Status"
])

with tab1:
    st.header("Market Regime")
    st.info("데이터 파이프라인 연동 대기 중입니다.")

with tab5:
    render_data_status_page()
