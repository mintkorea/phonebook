import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 및 디자인 (가장 심플하고 강력한 방식)
st.set_page_config(page_title="성의 연락처 Hub", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #fff; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 시인성 강화 */
    .stTextInput input { border: 2px solid #000 !important; border-radius: 4px !important; height: 45px !important; }

    /* 업무 내용(비고): 빨간색 굵게 상단 노출 */
    .work-tag { color: #d32f2f; font-weight: 800; font-size: 0.95rem; margin-bottom: 2px; }
    .name-txt { font-size: 1.1rem; font-weight: 800; color: #000; }
    .dept-txt { font-size: 0.85rem; color: #666; margin-left: 6px; }

    /* 버튼 스타일 */
    .btn-wrap { display: flex; gap: 8px; }
    .call-btn {
        display: flex; align-items: center; justify-content: center;
        width: 55px; height: 38px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.85rem; font-weight: 700;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: "사람 눈에 안 보이는 모든 것" 강제 세척
@st.cache_data
def get_clean_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        
        # 데이터 읽기 (모든 데이터를 문자열로 변환)
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        
        # [핵심] 모든 셀의 앞뒤 공백, 줄바꿈(\n, \r), 'nan' 글자를 싹 다 지웁니다.
        df = df.apply(lambda x: x.str.strip().replace(r'\n', '', regex=True).replace(r'\r', '', regex=True).replace('nan', ''))
        
        # [해결책] 열 이름에 절대 의존하지 않고 '순서'로 강제 고정 (KeyError 박멸)
        # 0:구분, 1:부서, 2:성함, 3:내선, 4:직통, 5:비고
        standard_cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        num_actual = len(df.columns)
        df.columns = [standard_cols[i] for i in range(min(num_actual, 6))] + [f'extra_{i}' for i in range(max(0, num_actual-6))]
        
        return df
    except:
        return pd.DataFrame()

df = get_clean_data()

# 3. 통합 검색 (상단 고정)
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용(주차, 보안 등) 검색", label_visibility="collapsed")

# 4. 탭 구성
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_list(target_df):
    # 의미 있는 데이터(이름, 부서, 업무 중 하나라도 있는 경우)만 필터링
    valid_df = target_df[
        (target_df['c_name'] != "") | 
        (target_df['c_dept'] != "") | 
        (target_df['c_work'] != "")
    ]
    
    if valid_df.empty:
        st.caption("표시할 내용이 없습니다.")
        return
    
    for _, row in valid_df.iterrows():
        nm, dp, wk = row.get('c_name', ''), row.get('c_dept', ''), row.get('c_work', '')
        tl = re.sub(r'[^0-9*]', '', str(row.get('c_tel', '')))
        hp = re.sub(r'[^0-9]', '', str(row.get('c_hp', '')))
        
        # [사용자 요청] 담당자가 없으면 부서명을 제목으로
        d_name = nm if nm else dp
        d_dept = dp if nm else ""

        with st.container():
            # 업무 내용이 있으면 가장 먼저 빨간색으로 노출
            if wk:
                st.markdown(f"<div class='work-tag'>{wk}</div>", unsafe_allow_html=True)
            
            c_info, c_btn = st.columns([3, 1.3])
            with c_info:
                st.markdown(f"<span class='name-txt'>{d_name}</span> <span class='dept-txt'>{d_dept}</span>", unsafe_allow_html=True)
            
            with c_btn:
                b_cols = st.columns(2)
                if tl:
                    b_cols[0].markdown(f'<a href="tel:{tl}" class="call-btn btn-tel">내선</a>', unsafe_allow_html=True)
                if hp:
                    b_cols[1].markdown(f'<a href="tel:{hp}" class="call-btn btn-hp">직통</a>', unsafe_allow_html=True)
            st.divider()

# 5. 탭/검색 연동 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        # 탭 필터링 (구분 또는 부서 열 기준)
        d = df if cat == "전체" else df[df['c_cat'].str.contains(cat) | df['c_dept'].str.contains(cat)]
        # 검색 필터링 (모든 열 대상)
        if q:
            d = d[d.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_list(d)
