import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. UI 디자인 (CSS) - 버튼 크기 축소 및 텍스트 정렬
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1.5rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    .stTextInput input { border-radius: 10px !important; border: 1px solid #f0f0f0 !important; background-color: #fafafa !important; }
    
    .contact-item { padding: 12px 5px; border-bottom: 1px solid #f8faf9; display: flex; justify-content: space-between; align-items: center; }
    .info-group { display: flex; flex-direction: column; flex: 1; }
    
    .name-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    
    /* 시설 전용 내선번호 (0.95rem, 괄호 없음) */
    .facility-tel { font-size: 0.95rem; color: #64748b; font-weight: 500; margin-left: 2px; }
    
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; margin-top: 2px; }

    /* 버튼 크기 축소 및 T, M 변경 */
    .btn-group { display: flex; gap: 4px; flex-shrink: 0; }
    .c-btn { 
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 8px; 
        text-decoration: none !important; font-size: 0.85rem; font-weight: 800; 
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        df = df.replace('nan', '').apply(lambda x: x.str.strip())
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df.sort_values(by=['c_dept', 'c_name'], ascending=True)
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 검색
q = st.text_input("", placeholder="🔍 성함 또는 부서 검색", label_visibility="collapsed")
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df, is_facility=False):
    if target_df.empty:
        st.caption("결과가 없습니다. 🌱")
        return
        
    for _, row in target_df.iterrows():
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        raw_tel = str(row['c_tel'])
        raw_hp = str(row['c_hp'])

        # 국번 맵핑
        if raw_tel.startswith('*1'):
            dial_tel = "022258" + raw_tel.replace('*1', '')
        elif raw_tel:
            dial_tel = "023147" + raw_tel
        else:
            dial_tel = ""

        dial_hp = re.sub(r'[^0-9]', '', raw_hp)

        # UI 요소 생성
        tel_disp = f'<span class="facility-tel">{raw_tel}</span>' if is_facility and raw_tel else ''
        t_btn = f'<a href="tel:{dial_tel}" class="c-btn btn-tel">T</a>' if dial_tel else ''
        m_btn = f'<a href="tel:{dial_hp}" class="c-btn btn-hp">M</a>' if dial_hp else ''
        work_div = f'<div class="work-desc">{wk}</div>' if wk else ''

        # 한 줄 렌더링 (HTML 깨짐 방지)
        st.markdown(f'<div class="contact-item"><div class="info-group"><div class="name-row"><span class="name-text">{nm}</span><span class="dept-text">{dp}</span>{tel_disp}</div>{work_div}</div><div class="btn-group">{t_btn}{m_btn}</div></div>', unsafe_allow_html=True)

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        filtered = df if category == "전체" else df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered, is_facility=(category == "시설"))
