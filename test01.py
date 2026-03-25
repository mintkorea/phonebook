import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 및 디자인 (불필요한 HTML 제거, 안전한 CSS만 사용)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    header, footer { visibility: hidden; }
    /* 검색창 가독성 향상 */
    .stTextInput input { border: 2px solid #000 !important; }
    /* 업무 내용(비고) 강조 */
    .work-highlight { color: #d32f2f; font-weight: bold; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (열 이름 무관, 위치 기반 매핑)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        # 모든 데이터를 텍스트로 읽고 결측치 제거
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig').astype(str)
        df = df.replace('nan', '')
        # 열 이름을 표준화 (0:구분, 1:부서, 2:담당, 3:내선, 4:휴대폰, 5:업무)
        new_cols = ['cat', 'dept', 'name', 'tel', 'hp', 'work']
        df.columns = [new_cols[i] for i in range(min(len(df.columns), 6))]
        return df
    except Exception as e:
        st.error(f"데이터 로드 에러: {e}")
        return pd.DataFrame()

df = load_data()

# 3. 통합 검색 (전체 데이터 대상)
search_q = st.text_input("", placeholder="🔍 이름, 부서, 업무(대관, 보안 등)를 입력하세요", label_visibility="collapsed")

# 4. 탭 구성 (보안 -> 시설 -> 미화 -> 총무 -> 지원 -> 기타 -> 전체)
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_secure_ui(target_df):
    if target_df.empty:
        st.info("표시할 연락처가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 안전하게 가져오기
        name, dept, work = row['name'].strip(), row['dept'].strip(), row['work'].strip()
        tel, hp = row['tel'].strip(), row['hp'].strip()
        
        # 이름이 없으면 부서를 제목으로 사용
        display_name = name if name else dept
        display_dept = dept if name else ""

        # [디자인] Streamlit 기본 위젯을 사용하여 깨짐 방지
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # 이름과 부서
                st.markdown(f"**{display_name}** <small style='color:#666'>{display_dept}</small>", unsafe_allow_html=True)
                # 업무 내용 (빨간색 강조)
                if work:
                    st.markdown(f"<span class='work-highlight'> 업무: {work}</span>", unsafe_allow_html=True)
            
            with col2:
                # 버튼 레이아웃
                btn_cols = st.columns(2)
                if tel:
                    clean_tel = re.sub(r'[^0-9*]', '', tel)
                    btn_cols[0].markdown(f'<a href="tel:{clean_tel}" style="text-decoration:none;"><button style="width:100%; height:40px; border:1px solid #ccc; border-radius:4px; background:#f8f9fa; font-weight:bold; cursor:pointer;">내선</button></a>', unsafe_allow_html=True)
                if hp:
                    clean_hp = re.sub(r'[^0-9]', '', hp)
                    btn_cols[1].markdown(f'<a href="tel:{clean_hp}" style="text-decoration:none;"><button style="width:100%; height:40px; border:none; border-radius:4px; background:#000; color:#fff; font-weight:bold; cursor:pointer;">직통</button></a>', unsafe_allow_html=True)
            
            st.divider() # 행 구분선

# 5. 검색 및 탭 필터링 로직 (완벽하게 작동하도록 보정)
for i, tab in enumerate(tabs):
    with tab:
        current_cat = tab_list[i]
        
        # 1. 탭 필터링
        if current_cat == "전체":
            filtered = df
        else:
            # 'cat'(구분) 또는 'dept'(부서)에 탭 이름이 포함된 행 추출
            filtered = df[df['cat'].str.contains(current_cat) | df['dept'].str.contains(current_cat)]
        
        # 2. 검색어 필터링 (탭 필터링된 결과 내에서 수행)
        if search_q:
            # 모든 열을 합쳐서 검색어가 있는지 확인
            search_mask = filtered.apply(lambda r: r.str.contains(search_q, case=False).any(), axis=1)
            filtered = filtered[search_mask]
            
        render_secure_ui(filtered)
