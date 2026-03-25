import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 및 디자인 (가장 심플하고 강력한 방식)
st.set_page_config(page_title="성의 연락처 Hub", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    header, footer { visibility: hidden; }
    /* 검색창 시인성 강화 */
    .stTextInput input { border: 2px solid #000 !important; border-radius: 4px !important; height: 45px !important; }
    /* 업무 내용(비고) 빨간색 강조 */
    .work-txt { color: #d32f2f; font-weight: bold; font-size: 0.92rem; margin-top: 2px; }
    .dept-txt { color: #666; font-size: 0.82rem; margin-left: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: 유령 문자 자동 제거 및 '위치 기반' 강제 매핑
@st.cache_data
def load_and_clean_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        # 데이터를 읽어오면서 모든 칸의 앞뒤 공백(유령 문자)을 즉시 제거
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig').astype(str)
        df = df.apply(lambda x: x.str.strip())
        
        # [해결책] 스크린샷의 'Length mismatch' 에러 방지
        # 실제 데이터의 열 개수가 몇 개든 상관없이 앞의 6개만 사용하여 이름 강제 부여
        # 0:구분, 1:부서, 2:성함, 3:내선, 4:직통, 5:비고
        standard_cols = ['v_cat', 'v_dept', 'v_name', 'v_tel', 'v_hp', 'v_work']
        num_cols = len(df.columns)
        df.columns = [standard_cols[i] for i in range(min(num_cols, 6))] + [f'extra_{i}' for i in range(max(0, num_cols-6))]
        
        return df.replace('nan', '')
    except Exception as e:
        st.error(f"데이터 세척 중 오류 발생: {e}")
        return pd.DataFrame()

df_clean = load_and_clean_data()

# 3. 통합 검색 (상단 고정)
q = st.text_input("", placeholder="🔍 성함, 부서, 담당 업무(보안, 주차, 대관 등) 검색", label_visibility="collapsed")

# 4. 탭 구성 (보안 -> 시설 -> 미화 -> 총무 -> 지원 -> 기타 -> 전체)
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_row(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 안전하게 추출 (KeyError 방지)
        nm, dp, wk = row.get('v_name', ''), row.get('v_dept', ''), row.get('v_work', '')
        tl, hp = row.get('v_tel', ''), row.get('v_hp', '')
        
        # 전화번호 정제
        t_link = re.sub(r'[^0-9*]', '', str(tl))
        h_link = re.sub(r'[^0-9]', '', str(hp))
        
        display_name = nm if nm else dp
        display_dept = dp if nm else ""

        # [해결책] HTML 태그 노출 방지를 위해 Streamlit 고유 위젯 사용
        with st.container():
            c1, c2 = st.columns([3, 1.2])
            with c1:
                st.markdown(f"**{display_name}** <span class='dept-txt'>{display_dept}</span>", unsafe_allow_html=True)
                if wk:
                    st.markdown(f"<p class='work-txt'>{wk}</p>", unsafe_allow_html=True)
            with c2:
                btn_c1, btn_c2 = st.columns(2)
                if t_link:
                    btn_c1.markdown(f'<a href="tel:{t_link}" target="_self" style="text-decoration:none;"><button style="width:100%; height:38px; background:#f1f3f5; border:1px solid #ccc; border-radius:5px; font-weight:bold; cursor:pointer;">내선</button></a>', unsafe_allow_html=True)
                if h_link:
                    btn_c2.markdown(f'<a href="tel:{h_link}" target="_self" style="text-decoration:none;"><button style="width:100%; height:38px; background:#000; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">직통</button></a>', unsafe_allow_html=True)
            st.divider()

# 5. 탭 필터링 및 검색 연동
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        
        # 1차: 탭 필터링 (구분 혹은 부서 열 기준)
        if cat == "전체":
            d_tab = df_clean
        else:
            d_tab = df_clean[df_clean['v_cat'].str.contains(cat) | df_clean['v_dept'].str.contains(cat)]
        
        # 2차: 검색어 필터링 (모든 열 대상)
        if q:
            d_final = d_tab[d_tab.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        else:
            d_final = d_tab
            
        render_row(d_final)
