import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1.5rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창 */
    .stTextInput input { border-radius: 10px !important; border: 1px solid #f0f0f0 !important; background-color: #fafafa !important; }
    
    /* 리스트 아이템 */
    .contact-item { padding: 15px 5px; border-bottom: 1px solid #f8faf9; display: flex; justify-content: space-between; align-items: center; }
    .info-group { display: flex; flex-direction: column; flex: 1; }
    
    /* 텍스트 스타일 */
    .name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .name-text { font-size: 1.15rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    
    /* 시설 전용 내선번호 표기 (중간 크기) */
    .facility-tel { font-size: 0.95rem; color: #64748b; font-weight: 500; margin-left: 4px; }
    
    /* 업무내용 */
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; margin-top: 3px; }

    /* 버튼 */
    .btn-group { display: flex; gap: 6px; flex-shrink: 0; }
    .c-btn { display: inline-flex; align-items: center; justify-content: center; min-width: 55px; height: 36px; padding: 0 12px; border-radius: 8px; text-decoration: none !important; font-size: 0.8rem; font-weight: 700; }
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

        # 국번 자동 완성 (전화 연결용)
        if raw_tel.startswith('*1'):
            dial_tel = "022258" + raw_tel.replace('*1', '')
        elif raw_tel:
            dial_tel = "023147" + raw_tel
        else:
            dial_tel = ""

        dial_hp = re.sub(r'[^0-9]', '', raw_hp)

        # 시설 전용 내선 노출 (괄호 없이, 중간 크기)
        tel_display = f'<span class="facility-tel">{raw_tel}</span>' if is_facility and raw_tel else ''

        # 버튼 및 업무내용 HTML
        tel_btn = f'<a href="tel:{dial_tel}" class="c-btn btn-tel">내선</a>' if dial_tel else ''
        hp_btn = f'<a href="tel:{dial_hp}" class="c-btn btn-hp">직통</a>' if dial_hp else ''
        work_div = f'<div class="work-desc">{wk}</div>' if wk else ''

        # 메인 렌더링 (한 줄로 결합하여 깨짐 방지)
        st.markdown(f'<div class="contact-item"><div class="info-group"><div class="name-row"><span class="name-text">{nm}</span><span class="dept-text">{dp}</span>{tel_display}</div>{work_div}</div><div class="btn-group">{tel_btn}{hp_btn}</div></div>', unsafe_allow_html=True)

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        is_fac = (category == "시설")
        
        if category == "전체":
            filtered = df
        else:
            filtered = df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_ui(filtered, is_facility=is_fac)
