import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="성의교정 주요전화", layout="wide")

# 초성
def get_chosung(text):
    CHO = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
    result = ""
    for ch in str(text):
        if '가' <= ch <= '힣':
            result += CHO[(ord(ch)-ord('가'))//588]
        else:
            result += ch
    return result

# CSS
st.markdown("""
<style>
.block-container {padding:1rem;font-family:sans-serif;}
.contact-item {
    display:flex;justify-content:space-between;align-items:center;
    border-bottom:1px solid #eee;padding:10px 5px;
}
.name-row {display:flex;flex-wrap:wrap;gap:6px;}
.name-text {font-weight:800;}
.dept-text {color:#888;font-size:0.9rem;}
.highlight-tel {font-weight:800;}
.work-desc {color:#10b981;font-size:0.85rem;}
.btn-group {display:flex;gap:6px;}
.c-btn {width:34px;height:34px;display:flex;align-items:center;justify-content:center;background:#f1f5f9;border-radius:8px;text-decoration:none;}
</style>
""", unsafe_allow_html=True)

st.title("성의교정 주요전화")

# 데이터
@st.cache_data
def load():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?output=csv"
    df = pd.read_csv(url).astype(str)
    df = df.replace('nan','')
    df.columns = ['c_cat','c_dept','c_name','c_tel','c_hp','c_work'][:len(df.columns)]
    df['chosung'] = (df['c_name']+df['c_dept']).apply(get_chosung)
    return df

df = load()

# 검색
def clear():
    st.session_state.q = ""

col1, col2 = st.columns([8,2])
with col1:
    st.text_input("", key="q", placeholder="검색")
with col2:
    st.button("초기화", on_click=clear)

q = st.session_state.get("q","")

if q:
    if all('ㄱ'<=c<='ㅎ' for c in q):
        df = df[df['chosung'].str.contains(q)]
    else:
        df = df[df.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]

# 전화번호 처리
def make_tel(raw):
    raw = str(raw)
    nums = re.sub(r'[^0-9]', '', raw)

    # "주간 2020" 같은 경우 필터
    if not nums or len(nums) < 3:
        return "", raw  # 버튼 없음, 텍스트 유지

    if len(nums) == 4:
        return "023147"+nums, nums

    if nums.startswith("02"):
        return nums, nums

    return "02"+nums, nums

# 렌더
def render(df):
    if df.empty:
        st.write("결과 없음")
        return

    for _, r in df.iterrows():
        nm = r['c_name']
        dp = r['c_dept']
        tel_raw = r['c_tel']
        hp = r['c_hp']
        wk = r['c_work']

        dial, tel_display = make_tel(tel_raw)

        # 주간/야간 처리
        if "주간" in tel_raw or "야간" in tel_raw:
            wk = (tel_raw + " " + wk).strip()
            tel_display = ""
            dial = ""

        name_html = f'<span class="name-text">{nm}</span>' if nm else ''
        dept_html = f'<span class="dept-text">{dp}</span>' if dp else ''
        tel_html = f'<span class="highlight-tel">{tel_display}</span>' if tel_display else ''
        work_html = f'<div class="work-desc">{wk}</div>' if wk else ''

        t_btn = f'<a href="tel:{dial}" class="c-btn">T</a>' if dial else ''

        st.markdown(f"""
        <div class="contact-item">
            <div>
                <div class="name-row">
                    {name_html}
                    {dept_html}
                    {tel_html}
                </div>
                {work_html}
            </div>
            <div class="btn-group">
                {t_btn}
            </div>
        </div>
        """, unsafe_allow_html=True)

render(df)
