import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 주요전화", layout="wide")

# --- 초성 추출 함수 ---
def get_chosung(text):
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    result = ""
    for char in text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            chosung_index = (code - 0xAC00) // 588
            result += CHOSUNG_LIST[chosung_index]
        else:
            result += char
    return result

# 2. UI 디자인 (정렬 및 레이아웃 최적화)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    .main-title { font-size: 1.8rem; font-weight: 900; color: #1e293b; margin-bottom: 1.2rem; padding-left: 10px; border-left: 5px solid #10b981; }
    
    .stTabs [data-baseweb="tab"] { font-size: 1.2rem !important; font-weight: 700 !important; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 900 !important; }

    .contact-item { 
        display: flex; 
        align-items: center; 
        padding: 12px 0; 
        border-bottom: 1px solid #f1f5f9; 
        gap: 10px;
    }
    
    .info-group { flex: 1; min-width: 0; }
    .name-row { display: flex; align-items: baseline; gap: 6px; margin-bottom: 2px; }
    .name-text { font-size: 1.15rem; font-weight: 800; color: #1e293b; white-space: nowrap; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; line-height: 1.3; word-break: keep-all; }

    .tel-container { 
        display: flex; 
        flex-direction: column; 
        align-items: flex-end; 
        justify-content: center; 
        width: 140px; 
        flex-shrink: 0;
    }
    .highlight-tel { font-size: 1.15rem; font-weight: 700; color: #334155; line-height: 1.2; }
    .navy-tel { font-family: 'Times New Roman', serif; color: #000080 !important; font-weight: 900 !important; font-style: italic; }
    .highlight-hp { font-size: 1rem; color: #059669; font-weight: 700; line-height: 1.2; }

    .btn-group { 
        display: flex; 
        gap: 6px; 
        width: 80px; 
        justify-content: flex-end;
        flex-shrink: 0; 
    }
    .c-btn { 
        display: inline-flex; 
        align-items: center; 
        justify-content: center; 
        width: 34px; 
        height: 34px; 
        border-radius: 8px; 
        text-decoration: none !important; 
        font-size: 0.85rem; 
        font-weight: 800; 
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; border: 1px solid #e2e8f0; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">성의교정 주요전화</div>', unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        df = df.replace('nan', '').apply(lambda x: x.str.strip())
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        df['sort_order'] = df['c_cat'].apply(lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
        df['c_cat_display'] = df['c_cat'].apply(lambda x: re.sub(r'\d+', '', x).strip())
        df['chosung_key'] = (df['c_name'] + " " + df['c_dept'] + " " + df['c_work']).apply(get_chosung)
        return df.sort_values(by=['sort_order', 'c_dept', 'c_name'], ascending=[True, True, True])
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 검색 로직
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 초성 검색", key="global_search", label_visibility="collapsed")
if q:
    is_chosung = all('ㄱ' <= char <= 'ㅎ' or char == " " for char in q)
    filtered_base = df[df['chosung_key'].str.contains(q, case=False)] if is_chosung else df[df.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
else:
    filtered_base = df

# 5. 유틸리티 함수
def get_dial_number(raw_num):
    clean_num = re.sub(r'[^0-9*]', '', str(raw_num))
    if not clean_num: return ""
    if clean_num.startswith('*1'): return "022258" + clean_num.replace('*1', '')
    if len(clean_num) >= 7: return "02" + clean_num
    return "023147" + clean_num

# 6. UI 렌더링 함수
def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다. 🌱")
        return
        
    for _, row in target_df.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        raw_tel, raw_hp = str(row['c_tel']), str(row['c_hp'])
        
        display_name = nm if nm else dp
        display_dept = dp if nm else ""
        display_tel = raw_tel.replace("02-3147-", "").replace("02-3147", "") if "총무" in dp else raw_tel
        tel_class = "highlight-tel navy-tel" if display_tel.startswith('*1') else "highlight-tel"

        # 1. 업무 내용 영역 (비어있으면 빈 문자열, 있으면 태그 포함)
        work_html = f'<div class="work-desc">{wk}</div>' if wk and wk.strip() else ""

        # 2. 전화번호 영역 조립
        tel_inner = ""
        if raw_tel:
            tel_inner += f'<span class="{tel_class}">{display_tel}</span>'
        if raw_hp:
            tel_inner += f'<span class="highlight-hp">{raw_hp}</span>'
        tel_html = f'<div class="tel-container">{tel_inner}</div>'

        # 3. 버튼 영역 조립
        dial_tel = get_dial_number(raw_tel)
        t_btn = f'<a href="tel:{dial_tel}" class="c-btn btn-tel">T</a>' if dial_tel else ''
        m_btn = f'<a href="tel:{re.sub(r"[^0-9]", "", raw_hp)}" class="c-btn btn-hp">M</a>' if raw_hp else ''
        btn_html = f'<div class="btn-group">{t_btn}{m_btn}</div>'

        # 4. 전체 행 최종 조립 (중첩 중괄호 없이 깔끔하게 합침)
        final_item_html = (
            f'<div class="contact-item">'
            f'    <div class="info-group">'
            f'        <div class="name-row">'
            f'            <span class="name-text">{display_name}</span>'
            f'            <span class="dept-text">{display_dept}</span>'
            f'        </div>'
            f'        {work_html}'
            f'    </div>'
            f'    {tel_html}'
            f'    {btn_html}'
            f'</div>'
        )
        
        st.markdown(final_item_html, unsafe_allow_html=True)
        

# 7. 실행
tab_names = ["전체", "보안", "시설", "미화", "총무", "지원", "기타"]
tabs = st.tabs(tab_names)

for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        if category == "전체":
            render_ui(filtered_base)
        else:
            tab_final = filtered_base[filtered_base['c_cat_display'].str.contains(category, na=False) | filtered_base['c_dept'].str.contains(category, na=False)]
            render_ui(tab_final)
