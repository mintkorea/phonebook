import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 폰트 로드
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 고급스러운 Enterprise UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 전체 배경 및 폰트 설정 */
    .block-container { padding: 1rem 3rem !important; background-color: #f9fafb; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창 디자인 (미니멀) */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 12px 20px !important;
        background-color: white !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    /* 연락처 카드 디자인 (전문가급) */
    .contact-card {
        background: white;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 14px;
        border: 1px solid #f0f1f4;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* [해결책] 업무 내용 태그: 연한 네이비로 변경 */
    .work-tag {
        display: inline-block;
        background-color: #e0f2fe; /* 연한 네이비 배경 */
        color: #1e3a8a; /* 짙은 네이비 글씨 */
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: -0.01em;
    }

    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.3rem; font-weight: 800; color: #111; display: block; }
    .dept-text { font-size: 0.9rem; color: #6b7280; font-weight: 400; margin-top: 1px; }

    /* 버튼 그룹 디자인 살짝 보정 */
    .btn-group { display: flex; gap: 9px; }
    .c-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 10px 18px;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 600;
        transition: 0.2s;
    }
    .btn-tel { background-color: white; color: #374151 !important; border: 1px solid #d1d5db; }
    .btn-hp { background-color: #0f172a; color: #ffffff !important; }
    
    /* 탭 메뉴 디자인 정돈 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #eaeaea; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 8px; color: #6b7280; padding: 10px 16px; }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (매핑 로직 유지)
@st.cache_data(ttl=300)
def get_live_data():
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(SHEET_URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    exceptException as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = get_live_data()

# 4. 검색창 (Placeholder 수정)
q = st.text_input("", placeholder="🔍 담당자, 부서, 주요 업무로 검색...", label_visibility="collapsed")

# 5. 메인 UI
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

# 아이콘 (수화기)
icon_phone = '<svg width="14" height="14" viewBox="0 0 24 24" style="fill: currentColor;"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.26 1.12.32 2.33.5 3.57.5.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.18 2.45.5 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>'

def render_ui(target_df):
    if target_df.empty:
        st.info("검색 조건에 맞는 연락처가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # [해결 핵심] 업무 태그 HTML 수정
        card_html = f"""
        <div class="contact-card">
            {f'<div class="work-tag">{wk}</div>' if wk else ''}
            <div class="info-row">
                <div>
                    <span class="name-text">{nm}</span>
                    <span class="dept-text">{dp}</span>
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel_link}" class="c-btn btn-tel">{icon_phone}내선</a>' if tel_link else ''}
                    {f'<a href="tel:{hp_link}" class="c-btn btn-hp">{icon_phone}직통전화</a>' if hp_link else ''}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# 6. 필터링 및 출력
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
