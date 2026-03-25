import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="성의 연락처 Hub", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #fff; }
    header, footer { visibility: hidden; }
    .stTextInput input { border: 2px solid #000 !important; border-radius: 4px !important; height: 45px !important; }
    
    /* 업무 내용(비고) 빨간색 강조 */
    .work-highlight { color: #d32f2f; font-weight: 800; font-size: 0.95rem; margin-bottom: 4px; }
    .name-txt { font-size: 1.1rem; font-weight: 800; color: #000; }
    .dept-txt { font-size: 0.82rem; color: #777; margin-left: 5px; }

    /* 버튼 스타일 */
    .btn-wrap { display: flex; gap: 6px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        width: 50px; height: 36px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.8rem; font-weight: 700;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: "사람 눈에 안 보이는 모든 것" 제거
@st.cache_data
def get_clean_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        
        # 데이터 읽기 및 모든 칸의 공백/줄바꿈/nan 강제 제거
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        # 모든 셀의 앞뒤 공백 제거 및 'nan' 문자열 처리
        df = df.apply(lambda x: x.str.strip().replace('nan', ''))
        
        # 열 이름을 위치 번호로 강제 고정 (KeyError 절대 방지)
        # 0:구분, 1:부서, 2:성함, 3:내선, 4:직통, 5:업무(비고)
        standard_cols = ['v_cat', 'v_dept', 'v_name', 'v_tel', 'v_hp', 'v_work']
        df.columns = [standard_cols[i] for i in range(min(len(df.columns), 6))]
        
        return df
    except:
        return pd.DataFrame()

df = get_clean_data()

# 3. 검색 및 탭
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용 검색", label_visibility="collapsed")
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_list(target_df):
    # 실제 내용이 있는 행만 필터링 (이름, 부서, 업무 중 하나라도 있어야 함)
    valid_df = target_df[
        (target_df['v_name'] != "") | 
        (target_df['v_dept'] != "") | 
        (target_df['v_work'] != "")
    ]
    
    if valid_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in valid_df.iterrows():
        nm, dp, wk = row['v_name'], row['v_dept'], row['v_work']
        tl = re.sub(r'[^0-9*]', '', row['v_tel'])
        hp = re.sub(r'[^0-9]', '', row['v_hp'])
        
        # [요청사항] 담당자가 없으면 부서명을 제목으로
        display_name = nm if nm else dp
        display_dept = dp if nm else ""

        with st.container():
            # 업무 내용이 있으면 최상단 노출
            if wk:
                st.markdown(f"<div class='work-highlight'>{wk}</div>", unsafe_allow_html=True)
            
            # 이름/부서 및 버튼 행
            col_info, col_btn = st.columns([3, 1.2])
            with col_info:
                st.markdown(f"<span class='name-txt'>{display_name}</span> <span class='dept-txt'>{display_dept}</span>", unsafe_allow_html=True)
            
            with col_btn:
                btn_cols = st.columns(2)
                if tl:
                    btn_cols[0].markdown(f'<a href="tel:{tl}" class="c-btn btn-tel">내선</a>', unsafe_allow_html=True)
                if hp:
                    btn_cols[1].markdown(f'<a href="tel:{hp}" class="c-btn btn-hp">직통</a>', unsafe_allow_html=True)
            st.divider()

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        d = df if cat == "전체" else df[df['v_cat'].str.contains(cat) | df['v_dept'].str.contains(cat)]
        if q:
            d = d[d.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_list(d)
