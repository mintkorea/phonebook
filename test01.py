import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. CSS 주입 (unsafe_allow_html=True 필수)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    .block-container { padding: 1.5rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창 */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #f0f0f0 !important;
        background-color: #fafafa !important;
    }

    /* 리스트 아이템 */
    .contact-item {
        padding: 15px 5px;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .info-group { display: flex; flex-direction: column; }
    .name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
    .name-text { font-size: 1.15rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    
    /* 업무내용: 배경 없이 파릇파릇 민트색 텍스트 */
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; }

    /* 버튼 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 8px 15px; border-radius: 8px;
        text-decoration: none !important; font-size: 0.8rem; font-weight: 700;
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        # 데이터 내의 특수기호나 따옴표가 HTML을 깨뜨리지 않도록 정제
        df = df.apply(lambda x: x.str.strip().replace('"', '').replace("'", "").replace('nan', ''))
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 검색 및 탭
q = st.text_input("", placeholder="🔍 성함 또는 부서 검색", label_visibility="collapsed")
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
        
        # 전화번호 정제 (특수문자 제거)
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # [핵심] f-string 내부에 HTML 태그가 섞일 때 에러 방지
        html_code = f"""
            <div class="contact-item">
                <div class="info-group">
                    <div class="name-row">
                        <span class="name-text">{nm}</span>
                        <span class="dept-text">{dp}</span>
                    </div>
                    <div class="work-desc">{wk}</div>
                </div>
                <div class="btn-group">
                    <a href="tel:{tel_link}" class="c-btn btn-tel">내선</a>
                    <a href="tel:{hp_link}" class="c-btn btn-hp">직통</a>
                </div>
            </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_names[i]
        filtered = df if cat == "전체" else df[df['c_cat'].str.contains(cat, na=False) | df['c_dept'].str.contains(cat, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered)
