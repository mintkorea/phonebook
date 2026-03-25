import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 (가장 먼저 실행되어야 함)
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. CSS 디자인 설정
st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #fff; }
    header, footer { visibility: hidden; }
    .stTextInput input { border: 2px solid #000 !important; border-radius: 4px !important; height: 45px !important; }

    /* 업무 내용(비고): 빨간색 박스로 최상단 노출 */
    .work-tag {
        background-color: #fff0f0; color: #d32f2f; padding: 4px 8px;
        border-radius: 4px; font-size: 0.95rem; font-weight: 800;
        margin-bottom: 8px; display: inline-block; border: 1px solid #ffcccc;
    }

    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.15rem; font-weight: 800; color: #000; }
    .dept-text { font-size: 0.85rem; color: #666; margin-left: 5px; }

    /* 버튼 스타일 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        width: 55px; height: 38px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.85rem; font-weight: 700;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 및 가공 (KeyError 방지 로직 포함)
@st.cache_data
def get_clean_data():
    try:
        # 현재 폴더 내 CSV 파일 찾기
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files:
            return pd.DataFrame(columns=['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work'])
        
        # 데이터 읽기 및 전처리
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        
        # 유령 공백 및 줄바꿈 제거
        df = df.apply(lambda x: x.str.strip().replace(r'\n', '', regex=True).replace(r'\r', '', regex=True))
        df = df.replace('nan', '')

        # [해결 핵심] 컬럼 개수와 이름을 강제로 일치시킴
        target_cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        new_df = pd.DataFrame()

        for i, col_name in enumerate(target_cols):
            if i < len(df.columns):
                new_df[col_name] = df.iloc[:, i]
            else:
                new_df[col_name] = "" # 부족한 열은 빈 값으로 생성
        
        return new_df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df = get_clean_data()

# 4. 통합 검색창
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용(전기, 보안, 대관 등) 검색", label_visibility="collapsed")

# 5. 탭 구성
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

# 6. UI 렌더링 함수
def render_ui(target_df):
    # 실제 데이터가 있는 행만 필터링
    valid = target_df[(target_df['c_name'] != "") | (target_df['c_dept'] != "") | (target_df['c_work'] != "")]
    
    if valid.empty:
        st.info("검색 결과가 없거나 표시할 내용이 없습니다.")
        return
    
    for _, row in valid.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        # 전화번호에서 숫자와 특정 기호만 추출
        tl = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp = re.sub(r'[^0-9]', '', str(row['c_hp']))
        
        # 담당자가 없으면 부서명을 제목으로
        d_title = nm if nm else dp
        d_sub = dp if nm else ""

        with st.container():
            # 업무 내용(비고) 최상단 노출
            if wk:
                st.markdown(f"<div class='work-tag'>업무: {wk}</div>", unsafe_allow_html=True)
            
            # 정보 행 (이름, 부서, 버튼)
            st.markdown(f'''
                <div class="info-row">
                    <div>
                        <span class="name-text">{d_title}</span>
                        <span class="dept-text">{d_sub}</span>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:"+tl+"' class='c-btn btn-tel'>내선</a>" if tl else ""}
                        {"<a href='tel:"+hp+"' class='c-btn btn-hp'>직통</a>" if hp else ""}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            st.divider()

# 7. 탭별 데이터 필터링 및 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_list[i]
        
        # 카테고리 필터링
        if category == "전체":
            filtered_df = df
        else:
            # 구분(c_cat)이나 부서(c_dept)에 카테고리 명이 포함된 경우
            filtered_df = df[df['c_cat'].str.contains(category) | df['c_dept'].str.contains(category)]
        
        # 검색어 필터링
        if q:
            filtered_df = filtered_df[filtered_df.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_ui(filtered_df)
