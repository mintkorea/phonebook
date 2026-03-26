import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 주요전화", layout="wide")

# --- 초성 추출 함수 추가 ---
def get_chosung(text):
    CHOSUNG_LIST = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 
        'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]
    result = ""
    for char in text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3: # 한글 범위
            chosung_index = (code - 0xAC00) // 588
            result += CHOSUNG_LIST[chosung_index]
        else:
            result += char
    return result

# 2. UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    .main-title { font-size: 1.8rem; font-weight: 900; color: #1e293b; margin-bottom: 1.2rem; padding-left: 10px; border-left: 5px solid #10b981; }
    .stTabs [data-baseweb="tab"] { font-size: 1.35rem !important; font-weight: 700 !important; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 900 !important; }
    .contact-item { padding: 10px 5px; border-bottom: 1px solid #f8faf9; display: flex; justify-content: space-between; align-items: center; }
    .info-group { display: flex; flex-direction: column; flex: 1; }
    .name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    .highlight-tel { font-family: 'Pretendard', sans-serif; font-size: 1.4rem; color: #475569; font-weight: 800; margin-left: 4px; }
    .navy-tel { font-family: 'Times New Roman', serif; color: #000080 !important; font-weight: 900 !important; font-style: italic; letter-spacing: 0.5px; text-decoration: none !important; }
    .highlight-hp { font-size: 1.3rem; color: #059669; font-weight: 800; margin-left: 4px; }
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; margin-top: 2px; }
    .btn-group { display: flex; gap: 6px; flex-shrink: 0; }
    .c-btn { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; border-radius: 8px; text-decoration: none !important; font-size: 0.9rem; font-weight: 800; }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">성의교정 주요전화</div>', unsafe_allow_html=True)

# 3. 데이터 로드 및 정렬 + 초성 인덱스 생성
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        df = df.replace('nan', '').apply(lambda x: x.str.strip())
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        
        # 정렬용 숫자 추출
        df['sort_order'] = df['c_cat'].apply(lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
        df['c_cat_display'] = df['c_cat'].apply(lambda x: re.sub(r'\d+', '', x).strip())
        
        # --- 검색용 초성 필드 생성 ---
        df['chosung_key'] = (df['c_name'] + df['c_dept']).apply(get_chosung)
        
        return df.sort_values(by=['sort_order', 'c_dept', 'c_name'], ascending=[True, True, True])
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 전역 검색창 (초성 검색 지원)
q = st.text_input("", placeholder="🔍 성함, 부서 또는 초성 검색 (예: ㅂㅇ)", key="global_search", label_visibility="collapsed")

if q:
    # 입력값이 초성으로만 구성되었는지 확인
    is_chosung_query = all('ㄱ' <= char <= 'ㅎ' for char in q.replace(" ", ""))
    
    if is_chosung_query:
        # 초성 검색: chosung_key에서 찾음
        filtered_base = df[df['chosung_key'].str.contains(q.replace(" ", ""), case=False, na=False)]
    else:
        # 일반 검색: 전체 컬럼 대조
        filtered_base = df[df.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
else:
    filtered_base = df

# 5. 탭 구성 및 렌더링 (기존과 동일)
tab_names = ["전체", "보안", "시설", "미화", "총무", "지원", "기타"]
tabs = st.tabs(tab_names)

def get_dial_number(raw_num):
    clean_num = re.sub(r'[^0-9*]', '', str(raw_num))
    if not clean_num: return ""
    if clean_num.startswith('*1'): return "022258" + clean_num.replace('*1', '')
    if len(clean_num) >= 7: return "02" + clean_num
    return "023147" + clean_num

def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다. 🌱")
        return
        
    for _, row in target_df.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        raw_tel, raw_hp = str(row['c_tel']), str(row['c_hp'])
        is_real_security = ("보안" in dp) and ("총무" not in dp)
        display_tel = raw_tel.replace("02-3147-", "").replace("02-3147", "") if "총무" in dp else raw_tel
        tel_class = "highlight-tel navy-tel" if display_tel.startswith('*1') else "highlight-tel"
        tel_html = f'<span class="{tel_class}">{display_tel}</span>' if display_tel else ''
        hp_html = f'<span class="highlight-hp">{raw_hp}</span>' if raw_hp else ''

        if is_real_security:
            display_name, display_dept, tel_inline = (nm if nm else dp), (dp if nm else ""), tel_html
            m_btn_html = f'<a href="tel:{re.sub(r"[^0-9]", "", raw_hp)}" class="c-btn btn-hp">M</a>' if raw_hp else ''
        else:
            display_name, display_dept = (nm if nm else dp), (dp if nm else "")
            tel_inline = tel_html if raw_tel else hp_html
            m_btn_html = f'<a href="tel:{re.sub(r"[^0-9]", "", raw_hp)}" class="c-btn btn-hp">M</a>' if raw_hp else ''

        dial_tel = get_dial_number(raw_tel)
        t_btn_html = f'<a href="tel:{dial_tel}" class="c-btn btn-tel">T</a>' if dial_tel else ''
        work_div = f'<div class="work-desc">{wk}</div>' if wk else ''

        st.markdown(f'<div class="contact-item"><div class="info-group"><div class="name-row"><span class="name-text">{display_name}</span><span class="dept-text">{display_dept}</span>{tel_inline}</div>{work_div}</div><div class="btn-group">{t_btn_html}{m_btn_html}</div></div>', unsafe_allow_html=True)

for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        if category == "전체":
            render_ui(filtered_base)
        else:
            tab_final = filtered_base[filtered_base['c_cat_display'].str.contains(category, na=False) | filtered_base['c_dept'].str.contains(category, na=False)]
            render_ui(tab_final)
