import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 주요전화", layout="wide")

# 초성 추출
def get_chosung(text):
    CHOSUNG_LIST = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
    result = ""
    for char in str(text):
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            result += CHOSUNG_LIST[(code - 0xAC00) // 588]
        else:
            result += char
    return result

# 2. CSS
st.markdown("""
<style>
.block-container { padding: 1rem !important; font-family: 'Pretendard', sans-serif; }
header, footer { visibility: hidden; }

.main-title {
    font-size: 1.8rem;
    font-weight: 900;
    margin-bottom: 1rem;
    border-left: 5px solid #10b981;
    padding-left: 10px;
}

/* 검색창 */
div[data-testid="column"] > div button {
    height: 45px;
    width: 100%;
}

/* 리스트 */
.contact-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 5px;
    border-bottom: 1px solid #eee;
}

.info-group { flex: 1; }

.name-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
}

.name-text { font-weight: 800; font-size: 1.1rem; }
.dept-text { font-size: 0.85rem; color: #888; }

.highlight-tel { font-size: 1.2rem; font-weight: 800; }
.highlight-hp { font-size: 1.1rem; color: #059669; font-weight: 800; }

.work-desc {
    font-size: 0.85rem;
    color: #10b981;
}

.btn-group { display: flex; gap: 6px; }

.c-btn {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-decoration: none;
    font-weight: 800;
}

.btn-tel { background: #f1f5f9; }
.btn-hp { background: #ecfdf5; border: 1px solid #d1fae5; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">성의교정 주요전화</div>', unsafe_allow_html=True)

# 3. 데이터
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?output=csv"
    try:
        df = pd.read_csv(url).astype(str)
        df = df.replace('nan','').apply(lambda x: x.str.strip())

        cols = ['c_cat','c_dept','c_name','c_tel','c_hp','c_work']
        df.columns = cols[:len(df.columns)]

        df['chosung_key'] = (df['c_name'] + df['c_dept']).apply(get_chosung)
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 4. 검색창
def clear_search():
    st.session_state.global_search_input = ""

col1, col2 = st.columns([8,2])

with col1:
    st.text_input(
        "",
        placeholder="🔍 성함, 부서 또는 초성 검색",
        key="global_search_input",
        label_visibility="collapsed"
    )

with col2:
    st.button("초기화", on_click=clear_search)

q = st.session_state.get("global_search_input", "")

# 검색 필터
if q:
    is_chosung = all('ㄱ' <= c <= 'ㅎ' for c in q.replace(" ",""))
    if is_chosung:
        df_filtered = df[df['chosung_key'].str.contains(q, na=False)]
    else:
        df_filtered = df[df.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
else:
    df_filtered = df

# 전화 변환
def get_tel(num):
    num = re.sub(r'[^0-9*]', '', str(num))
    if not num: return ""
    if len(num) >= 7: return "02" + num
    return "023147" + num

# UI 렌더
def render(df):
    if df.empty:
        st.caption("결과 없음")
        return

    for _, row in df.iterrows():
        nm = row['c_name']
        dp = row['c_dept']
        tel = row['c_tel']
        hp = row['c_hp']
        wk = row['c_work']

        name_html = f'<span class="name-text">{nm}</span>' if nm else ''
        dept_html = f'<span class="dept-text">{dp}</span>' if dp else ''
        tel_html = f'<span class="highlight-tel">{tel}</span>' if tel else ''
        hp_html = f'<span class="highlight-hp">{hp}</span>' if hp else ''
        work_html = f'<div class="work-desc">{wk}</div>' if wk else ''

        dial = get_tel(tel)
        t_btn = f'<a href="tel:{dial}" class="c-btn btn-tel">T</a>' if dial else ''
        m_btn = f'<a href="tel:{re.sub(r"[^0-9]", "", hp)}" class="c-btn btn-hp">M</a>' if hp else ''

        st.markdown(f"""
        <div class="contact-item">
            <div class="info-group">
                <div class="name-row">
                    {name_html}
                    {dept_html}
                    {tel_html}
                    {hp_html}
                </div>
                {work_html}
            </div>
            <div class="btn-group">{t_btn}{m_btn}</div>
        </div>
        """, unsafe_allow_html=True)

# 5. 탭
tabs = st.tabs(["전체","보안","시설","미화","총무","지원","기타"])

for i, tab in enumerate(tabs):
    with tab:
        if i == 0:
            render(df_filtered)
        else:
            keyword = ["보안","시설","미화","총무","지원","기타"][i-1]
            render(df_filtered[
                df_filtered['c_dept'].str.contains(keyword, na=False) |
                df_filtered['c_cat'].str.contains(keyword, na=False)
            ])
