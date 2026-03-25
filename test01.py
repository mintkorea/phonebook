import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub - Mint Spring", layout="wide")

# 2. 고급스러운 파스텔톤 UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 전체 배경: 아주 연한 파스텔 민트/크림 */
    .block-container { padding: 1rem 3rem !important; background-color: #f7faf9; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 부드러운 그린 포커스 */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
        padding: 12px 20px !important;
        background-color: white !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .stTextInput input:focus {
        border-color: #a7f3d0 !important; /* Mint Green Focus */
        box-shadow: 0 0 0 3px rgba(167, 243, 208, 0.4) !important;
    }

    /* 연락처 카드: 그림자 대신 은은한 선과 파스텔 배경 */
    .contact-card {
        background: white;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* 업무 내용 태그: 연한 파스텔 그린으로 변경 */
    .work-tag {
        display: inline-block;
        background-color: #ecfdf5; /* 연한 파스텔 그린 배경 */
        color: #059669; /* 짙은 민트 그린 글씨 */
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: -0.01em;
        border: 1px solid #d1fae5;
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
    /* 내선 버튼: 그레이 아웃라인 */
    .btn-tel { background-color: white; color: #374151 !important; border: 1px solid #d1d5db; }
    .btn-tel:hover { background-color: #f9fafb; border-color: #c1c5cb; }
    
    /* 직통 버튼: 파스텔 그린 계열 */
    .btn-hp { background-color: #10b981; color: #ffffff !important; box-shadow: 0 4px 6px rgba(16,185,129,0.2); }
    .btn-hp:hover { background-color: #059669; }
    
    /* 탭 메뉴 디자인 정돈 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #eaeaea; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 8px; color: #6b7280; padding: 10px 16px; font-weight: 500; }
    .stTabs [aria-selected="true"] {
        background-color: #ecfdf5 !important;
        color: #059669 !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 4px rgba(16,185,129,0.1) !important;
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
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 검색창
q = st.text_input("", placeholder="🔍 성함, 부서, 주요 업무로 검색...", label_visibility="collapsed")

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
        # 데이터 정리
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        # 전화번호 정제
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 카드 렌더링
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
                    {f'<a href="tel:{hp_link}" class="c-btn btn-hp">{icon_phone}직통</a>' if hp_link else ''}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# 6. 필터링 및 출력
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        
        # 카테고리 필터링
        if category == "전체":
            filtered = df
        else:
            filtered = df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        
        # 검색어 필터링
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_ui(filtered)
