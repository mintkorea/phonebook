import streamlit as st
import pandas as pd

# 1. 디자인 설정
st.set_page_config(page_title="성의교정 통합 연락처", layout="wide")
st.markdown("""
    <style>
    .contact-card { border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: white; }
    .main-title { font-size: 1.2rem; font-weight: bold; color: #000; }
    .sub-title { font-size: 0.9rem; color: #666; margin-bottom: 10px; }
    .info-text { font-size: 0.9rem; margin-bottom: 3px; }
    .tag { background-color: #eee; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 구글 시트 데이터 로드 (시트 ID를 입력하세요)
SHEET_ID = "YOUR_SPREADSHEET_ID" 
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(URL).fillna("")

df = load_data()

# 3. 통합 검색 인터페이스
st.title("📞 성의교정 연락처 관리 시스템")
query = st.text_input("검색어를 입력하세요 (부서, 담당자, 전화, 업무 전체 검색 가능)", "")

if query:
    mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
    df = df[mask]

# 4. 6개 카테고리 탭 생성
categories = ["시설관리", "보안팀", "미화팀", "행정지원", "협력업체", "비상연락"]
tabs = st.tabs(categories)

for i, cat in enumerate(categories):
    with tabs[i]:
        cat_df = df[df['카테고리'] == cat]
        if cat_df.empty:
            st.info("조회된 자료가 없습니다.")
        else:
            for _, row in cat_df.iterrows():
                with st.container():
                    st.markdown('<div class="contact-card">', unsafe_allow_html=True)
                    
                    # 담당자 유무에 따른 메인 포맷 결정
                    if row['담당자']:
                        st.markdown(f'<div class="main-title">👤 {row["담당자"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="sub-title">{row["부서명"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="main-title">🏢 {row["부서명"]}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="sub-title">담당자 없음</div>', unsafe_allow_html=True)
                    
                    # 상세 정보 (데이터가 있는 경우만 표출)
                    if row['전화'] or row['휴대폰']:
                        tel = f"📞 내선: {row['전화']}" if row['전화'] else ""
                        hp = f" 📱 HP: {row['휴대폰']}" if row['휴대폰'] else ""
                        st.markdown(f'<div class="info-text">{tel}{hp}</div>', unsafe_allow_html=True)
                    
                    if row['업무']:
                        st.markdown(f'<div class="info-row"><span class="tag">업무</span> {row["업무"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
