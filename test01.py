import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="성의교정 주요전화", layout="wide")

st.title("성의교정 주요전화")

# 데이터
@st.cache_data
def load():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?output=csv"
    df = pd.read_csv(url).astype(str)
    df = df.replace('nan','')
    df.columns = ['c_cat','c_dept','c_name','c_tel','c_hp','c_work'][:len(df.columns)]
    return df

df = load()

# 검색
def clear():
    st.session_state.q = ""

col1, col2 = st.columns([8,2])

with col1:
    st.text_input("검색", key="q")

with col2:
    st.button("초기화", on_click=clear)

q = st.session_state.get("q","")

if q:
    df = df[df.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]

# 전화 처리
def make_tel(x):
    nums = re.sub(r'[^0-9]', '', str(x))
    if len(nums) < 4:
        return "", x
    if len(nums) == 4:
        return "023147"+nums, nums
    if nums.startswith("02"):
        return nums, nums
    return "02"+nums, nums

# UI (HTML 없음 → 절대 안 깨짐)
tabs = st.tabs(["전체","보안","시설","미화","총무","지원","기타"])

def render(data):
    for _, r in data.iterrows():
        name = r['c_name']
        dept = r['c_dept']
        tel_raw = r['c_tel']
        work = r['c_work']

        dial, tel = make_tel(tel_raw)

        # 주간/야간 처리
        if "주간" in tel_raw or "야간" in tel_raw:
            work = f"{tel_raw} {work}"
            tel = ""
            dial = ""

        with st.container():
            col1, col2 = st.columns([8,2])

            with col1:
                st.markdown(f"**{name}** ({dept})")
                if tel:
                    st.write(f"📞 {tel}")
                if work:
                    st.caption(work)

            with col2:
                if dial:
                    st.link_button("전화", f"tel:{dial}")

for i, tab in enumerate(tabs):
    with tab:
        if i == 0:
            render(df)
        else:
            keyword = ["보안","시설","미화","총무","지원","기타"][i-1]
            render(df[
                df['c_dept'].str.contains(keyword, na=False) |
                df['c_cat'].str.contains(keyword, na=False)
            ])
