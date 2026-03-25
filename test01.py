import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. UI 디자인 (미니멀 리스트 스타일)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1.5rem 2rem !important; background-color: #fcfcfc; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #e0e0e0 !important; padding: 10px 15px !important; }
    .contact-list { background: white; border-radius: 12px; border: 1px solid #eaeaea; margin-top: 1rem; }
    .contact-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; border-bottom: 1px solid #f0f0f0; }
    .contact-item:last-child { border-bottom: none; }
    .name-section { display: flex; align-items: center; gap: 10px; }
    .name-text { font-size: 1.1rem; font-weight: 700; color: #111; }
    .dept-text { font-size: 0.85rem; color: #777; }
    .work-badge { background-color: #f3f4f6; color: #555; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-left: 5px; }
    .btn-group { display: flex; gap: 8px; }
    .c-btn { display: flex; align-items: center; gap: 5px; padding: 7px 12px; border-radius: 6px; text-decoration: none !important; font-size: 0.8rem; font-weight: 600; }
    .btn-tel { background-color: white; color: #555 !important; border: 1px solid #d1d5db; }
    .btn-hp { background-color: white; color: #1e3a8a !important; border: 1px solid #1e3a8a; }
    .btn-icon { width: 14px; height: 14px; fill: currentColor; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (구글 시트 연동)
@st.cache_data(ttl=300)
def get_live_data():
    # 주신 구글 시트 주소
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(SHEET_URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        # 열 순서 강제 매핑
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 검색창
q = st.text_input("", placeholder="🔍 검색어 입력...", label_visibility="collapsed")

# 5. 탭 구성
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

# 아이콘 정의
icon_phone = '<svg class="btn-icon" viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.26 1.12.32 2.33.5 3.57.5.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.18 2.45.5 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>'

def render_ui(target_df):
    if target_df.empty:
        st.info("결과가 없습니다.")
        return
    
    st.markdown('<div class="contact-list">', unsafe_allow_html=True)
    for _, row in target_df.iterrows():
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        # [수정 포인트] 변수명을 hp_link로 통일
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        item_html = f"""
            <div class="contact-item">
                <div class="name-section">
                    <div><span class="name-text">{nm}</span> <span class="dept-text">{dp}</span></div>
                    {f'<span class="work-badge">{wk}</span>' if wk else ''}
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel_link}" class="c-btn btn-tel">{icon_phone}내선</a>' if tel_link else ''}
                    {f'<a href="tel:{hp_link}" class="c-btn btn-hp">{icon_phone}직통</a>' if hp_link else ''}
                </div>
            </div>
        """
        st.markdown(item_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 필터링 및 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        filtered = df if category == "전체" else df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered)
