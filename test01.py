import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 배경색 제거 및 민트 포인트 UI (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 전체 배경: 순백색 (배경색 제거) */
    .block-container { padding: 1.5rem 2rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 은은한 민트 라이트 그레이 */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #f0f0f0 !important;
        padding: 12px 18px !important;
        background-color: #fcfcfc !important;
    }
    .stTextInput input:focus {
        border-color: #6ee7b7 !important;
        box-shadow: 0 0 0 3px rgba(110, 231, 183, 0.1) !important;
    }

    /* 리스트 아이템: 배경 없이 선으로만 구분 */
    .contact-item {
        padding: 20px 10px;
        border-bottom: 1px solid #f8faf9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .info-group { display: flex; flex-direction: column; gap: 4px; }
    .name-row { display: flex; align-items: center; gap: 8px; }
    .name-text { font-size: 1.2rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    
    /* 업무내용: 이름 아래, 배경 없이 텍스트로만 (파스텔 민트색) */
    .work-desc { 
        font-size: 0.85rem; 
        color: #10b981; /* 파릇파릇한 민트색 */
        font-weight: 600;
        margin-top: 2px;
    }

    /* 버튼: 깔끔한 라운드 스타일 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 8px 16px;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 0.82rem;
        font-weight: 700;
        transition: 0.2s;
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    
    /* 탭 디자인: 민트색 강조 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        # 열 매핑: 구분, 부서, 성함, 내선, 직통, 업무
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except Exception:
        return pd.DataFrame()

df = get_live_data()

# 4. 검색창
q = st.text_input("", placeholder="🔍 성함 또는 부서로 검색하세요", label_visibility="collapsed")

# 5. 메인 UI
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다. 🌱")
        return
        
    for _, row in target_df.iterrows():
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 리스트 아이템 렌더링
        st.markdown(f"""
            <div class="contact-item">
                <div class="info-group">
                    <div class="name-row">
                        <span class="name-text">{nm}</span>
                        <span class="dept-text">{dp}</span>
                    </div>
                    {f'<div class="work-desc">{wk}</div>' if wk else ''}
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel_link}" class="c-btn btn-tel">내선</a>' if tel_link else ''}
                    {f'<a href="tel:{hp_link}" class="c-btn btn-hp">직통</a>' if hp_link else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)

# 6. 필터 및 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_names[i]
        filtered = df if cat == "전체" else df[df['c_cat'].str.contains(cat, na=False) | df['c_dept'].str.contains(cat, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered)
