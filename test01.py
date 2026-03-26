import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 주요전화", layout="wide")

# 초성 추출 함수
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

# 2. UI 디자인 (CSS)
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');

.block-container { padding: 1rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
header, footer { visibility: hidden; }

.main-title {
    font-size: 1.8rem;
    font-weight: 900;
    color: #1e293b;
    margin-bottom: 1.2rem;
    padding-left: 10px;
    border-left: 5px solid #10b981;
}

/* 검색 영역 */
.search-container { margin-bottom: 10px; }

/* 탭 */
.stTabs [data-baseweb="tab"] {
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: #94a3b8 !important;
}
.stTabs [aria-selected="true"] {
    color: #10b981 !important;
    font-weight: 900 !important;
}

/* 리스트 */
.contact-item {
    padding: 10px 5px;
    border-bottom: 1px solid #f8faf9;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.info-group { display: flex; flex-direction: column; flex: 1; }

.name-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.name-text { font-size: 1.1rem; font-weight: 800; color: #334155; }
.dept-text { font-size: 0.85rem; color: #94a3b8; }

.highlight-tel {
    font-size: 1.4rem;
    color: #475569;
    font-weight: 800;
}

.navy-tel {
    color: #000080 !important;
    font-weight: 900 !important;
    font-style: italic;
}

.highlight-hp {
    font-size: 1.3rem;
    color: #059669;
    font-weight: 800;
}

.work-desc {
    font-size: 0.85rem;
    color: #10b981;
    font-weight: 600;
}

/* 버튼 */
.btn-group { display: flex; gap: 6px; }

.c-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    border-radius: 8px;
    text-decoration: none !important;
    font-weight: 800;
}

.btn-tel { background-color: #f1f5f9; }
.btn-hp { background-color: #ecfdf5; border: 1px solid #d1fae5; }

/* 초기화 버튼 안정화 */
div[data-testid="column"] > div button {
    height: 45px;
    width: 100%;
    border-radius: 10px;
}
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
        df.columns = cols[:len(df.columns)]

        df['sort_order'] = df['c_cat'].apply(lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
        df['c_cat_display'] = df['c_cat'].apply(lambda x: re.sub(r'\d+', '', x).strip())
        df['chosung_key'] = (df['c_name'] + df['c_dept']).apply(get_chosung)

        return df.sort_values(by=['sort_order', 'c_dept', 'c_name'])

    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 검색창
def clear_search():
    st.session_state.global_search_input = ""

col_search, col_clear = st.columns([8, 2])

with col_search:
    st.text_input(
        "",
        placeholder="🔍 성함, 부서 또는 초성 검색",
        key="global_search_input",
        label_visibility="collapsed"
    )

with col_clear:
    st.button("초기화", on_click=clear_search)

q_final = st.session_state.get("global_search_input", "")

# 검색 필터
if q_final:
    is_chosung = all('ㄱ' <= c <= 'ㅎ' for c in q_final.replace(" ", ""))
    if is_chosung:
        filtered_base = df[df['chosung_key'].str.contains(q_final, na=False)]
    else:
        filtered_base = df[df.apply(lambda r: r.str.contains(q_final, case=False).any(), axis=1)]
else:
    filtered_base = df

# 5. 탭
tab_names = ["전체", "보안", "시설", "미화", "총무", "지원", "기타"]
tabs = st.tabs(tab_names)

def get_dial_number(num):
    clean = re.sub(r'[^0-9*]', '', str(num))
    if not clean: return ""
    if clean.startswith('*1'): return "022258" + clean.replace('*1', '')
    if len(clean) >= 7: return "02" + clean
    return "023147" + clean

def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return

    for _, row in target_df.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        tel, hp = str(row['c_tel']), str(row['c_hp'])

        tel_html = f'<span class="highlight-tel">{tel}</span>' if tel else ''
        hp_html = f'<span class="highlight-hp">{hp}</span>' if hp else ''

        dial = get_dial_number(tel)
        t_btn = f'<a href="tel:{dial}" class="c-btn btn-tel">T</a>' if dial else ''
        m_btn = f'<a href="tel:{re.sub(r"[^0-9]", "", hp)}" class="c-btn btn-hp">M</a>' if hp else ''

        work = f'<div class="work-desc">{wk}</div>' if wk else ''

        st.markdown(f"""
        <div class="contact-item">
            <div class="info-group">
                <div class="name-row">
                    <span class="name-text">{nm}</span>
                    <span class="dept-text">{dp}</span>
                    {tel_html}{hp_html}
                </div>
                {work}
            </div>
            <div class="btn-group">{t_btn}{m_btn}</div>
        </div>
        """, unsafe_allow_html=True)

for i, tab in enumerate(tabs):
    with tab:
        name = tab_names[i]
        if name == "전체":
            render_ui(filtered_base)
        else:
            render_ui(filtered_base[
                filtered_base['c_cat_display'].str.contains(name, na=False) |
                filtered_base['c_dept'].str.contains(name, na=False)
            ])
