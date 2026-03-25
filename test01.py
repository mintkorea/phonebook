import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. CSS 주입 (배경 빼고 민트 포인트만)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1.5rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    .stTextInput input { border-radius: 10px !important; border: 1px solid #f0f0f0 !important; background-color: #fafafa !important; }
    
    /* 리스트 아이템 레이아웃 */
    .contact-item { 
        padding: 15px 5px; 
        border-bottom: 1px solid #f8faf9; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        min-height: 60px;
    }
    
    .info-group { display: flex; flex-direction: column; flex: 1; margin-right: 10px; }
    .name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    
    /* 업무내용 파스텔 민트 텍스트 */
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; margin-top: 3px; }

    /* 버튼 스타일 */
    .btn-group { display: flex; gap: 6px; flex-shrink: 0; }
    .c-btn { 
        display: inline-flex; align-items: center; justify-content: center;
        min-width: 55px; height: 36px; padding: 0 12px;
        border-radius: 8px; text-decoration: none !important;
        font-size: 0.8rem; font-weight: 700;
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 및 정렬
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        # 데이터 클리닝: nan 제거 및 공백 정리
        df = df.replace('nan', '').apply(lambda x: x.str.strip())
        
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        
        # 부서 -> 이름순 정렬
        df = df.sort_values(by=['c_dept', 'c_name'], ascending=True)
        return df
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 UI
q = st.text_input("", placeholder="🔍 성함 또는 부서 검색", label_visibility="collapsed")
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다. 🌱")
        return
        
    for _, row in target_df.iterrows():
        # 데이터가 없을 경우를 대비한 방어 로직
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        # 번호에서 특수문자 제거
        tel_val = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_val = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 버튼 생성 (데이터가 있을 때만 HTML 생성)
        tel_html = f'<a href="tel:{tel_val}" class="c-btn btn-tel">내선</a>' if tel_val else ''
        hp_html = f'<a href="tel:{hp_val}" class="c-btn btn-hp">직통</a>' if hp_val else ''
        work_html = f'<div class="work-desc">{wk}</div>' if wk else ''

        # 전체 카드 구조 (줄바꿈 없이 한 줄로 처리하여 파싱 오류 방지)
        card_html = (
            f'<div class="contact-item">'
            f'<div class="info-group">'
            f'<div class="name-row"><span class="name-text">{nm}</span><span class="dept-text">{dp}</span></div>'
            f'{work_html}'
            f'</div>'
            f'<div class="btn-group">{tel_html}{hp_html}</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_names[i]
        filtered = df if cat == "전체" else df[df['c_cat'].str.contains(cat, na=False) | df['c_dept'].str.contains(cat, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered)
