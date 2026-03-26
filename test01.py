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

# 2. 데이터 로드 및 정렬 로직
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(url).astype(str)
        df = df.replace('nan', '').apply(lambda x: x.str.strip())
        # 컬럼명 강제 지정
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = cols[:len(df.columns)]
        
        # [정렬] c_cat에서 숫자 추출 (없으면 999)
        df['sort_order'] = df['c_cat'].apply(lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
        # [표시용] c_cat에서 숫자 제거
        df['c_cat_display'] = df['c_cat'].apply(lambda x: re.sub(r'\d+', '', x).strip())
        # [초성] 검색용 초성 키 생성
        df['chosung_key'] = (df['c_name'] + df['c_dept']).apply(get_chosung)
        
        return df.sort_values(by=['sort_order', 'c_dept', 'c_name'], ascending=[True, True, True])
    except:
        return pd.DataFrame()

df_origin = load_data()

# 3. 검색어 초기화 로직 (Session State)
if 'q' not in st.session_state:
    st.session_state.q = ""

def clear_search():
    st.session_state.q = ""

# 4. 상단 UI (제목 및 검색창)
st.title("성의교정 주요전화")

col1, col2 = st.columns([8, 2])

with col1:
    # 검색창: value를 session_state.q와 동기화
    q = st.text_input("🔍 성함, 부서 또는 초성 검색", value=st.session_state.q, key="search_input", label_visibility="collapsed")
    st.session_state.q = q # 입력 시 상태 업데이트

with col2:
    if st.button("초기화", on_click=clear_search):
        st.rerun()

# 5. 검색 필터링 적용
q_final = st.session_state.q
if q_final:
    # 초성만 입력되었는지 확인
    is_chosung = all('ㄱ' <= char <= 'ㅎ' for char in q_final.replace(" ", ""))
    if is_chosung:
        df = df_origin[df_origin['chosung_key'].str.contains(q_final.replace(" ", ""), case=False, na=False)]
    else:
        df = df_origin[df_origin.apply(lambda r: r.str.contains(q_final, case=False).any(), axis=1)]
else:
    df = df_origin

# 6. 전화번호 처리 함수
def make_tel(x):
    nums = re.sub(r'[^0-9]', '', str(x))
    if not nums or len(nums) < 4:
        return "", x
    if len(nums) == 4:
        return "023147" + nums, nums
    if nums.startswith("02"):
        return nums, x
    return "02" + nums, x

# 7. 탭 구성 및 렌더링
tabs = st.tabs(["전체", "보안", "시설", "미화", "총무", "지원", "기타"])

def render(data):
    if data.empty:
        st.caption("검색 결과가 없습니다. 🌱")
        return
        
    for _, r in data.iterrows():
        name = r['c_name']
        dept = r['c_dept']
        tel_raw = r['c_tel']
        work = r['c_work']
        
        dial, tel_display = make_tel(tel_raw)

        # 특수 처리 (주간/야간 문구가 포함된 경우)
        if "주간" in tel_raw or "야간" in tel_raw:
            work = f"[{tel_raw}] {work}".strip()
            tel_display = ""
            dial = ""

        with st.container():
            c1, c2 = st.columns([8, 2])
            with c1:
                # 이름이 없으면 부서를 강조
                main_text = f"**{name}**" if name else f"**{dept}**"
                sub_text = f"({dept})" if name else ""
                st.markdown(f"{main_text} {sub_text}")
                
                if tel_display:
                    st.write(f"📞 {tel_display}")
                if work:
                    st.caption(work)
            with c2:
                if dial:
                    st.link_button("전화", f"tel:{dial}", use_container_width=True)
            st.divider() # 가독성을 위한 구분선

# 8. 메인 실행
for i, tab in enumerate(tabs):
    with tab:
        if i == 0:
            render(df)
        else:
            keyword = ["보안", "시설", "미화", "총무", "지원", "기타"][i-1]
            # 숫자 제거된 카테고리명 또는 부서명에서 키워드 필터링
            filtered_df = df[
                df['c_cat_display'].str.contains(keyword, na=False) | 
                df['c_dept'].str.contains(keyword, na=False)
            ]
            render(filtered_df)
