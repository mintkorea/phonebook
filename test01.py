import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 파스텔 민트 & 화이트 미니멀 UI (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 배경 및 폰트 */
    .block-container { padding: 1rem 2rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 은은한 민트 포인트 */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 12px 18px !important;
        background-color: #f9fafb !important;
    }
    .stTextInput input:focus {
        border-color: #6ee7b7 !important;
        box-shadow: 0 0 0 3px rgba(110, 231, 183, 0.2) !important;
    }

    /* 리스트 아이템: 배경색 없이 선으로만 구분 */
    .contact-item {
        padding: 22px 10px;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .name-section { display: flex; flex-direction: column; gap: 4px; }
    .name-box { display: flex; align-items: center; gap: 8px; }
    .name-text { font-size: 1.25rem; font-weight: 800; color: #1e293b; }
    .dept-text { font-size: 0.9rem; color: #64748b; font-weight: 500; }
    
    /* [요청사항] 업무내용: 이름 아래 텍스트로만 배치 */
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; }

    /* 버튼: 파릇파릇한 파스텔 민트 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 10px 18px;
        border-radius: 12px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 700;
        transition: 0.2s;
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    
    /* 탭 디자인: 민트 포인트 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (매핑 로직 고정)
@st.cache_data(ttl=300)
def get_live_data():
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(SHEET_URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        # 열 순서: 구분, 부서, 성함, 내선, 직통, 업무
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except Exception:
        return pd.DataFrame()

df = get_live_data()

# 4. 검색창
q = st.text_input("", placeholder="🔍 누구를 찾으시나요?", label_visibility="collapsed")

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
        
        # 전화번호 정제
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 리스트 렌더링
        st.markdown(f"""
            <div class="contact-item">
                <div class="name-section">
                    <div class="name-box">
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
        category = tab_names[i]
        if category == "전체":
            filtered = df
        else:
            filtered = df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_ui(filtered)
