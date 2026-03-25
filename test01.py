import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정: 모바일 화면에 꽉 차게 설정
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 0.7rem !important; background-color: #ffffff; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 테두리를 두껍게 하여 시인성 확보 */
    .stTextInput input {
        border: 2px solid #111 !important;
        border-radius: 4px !important;
        height: 45px !important;
    }

    /* 탭 디자인: 촘촘하게 배치 */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { height: 36px; font-size: 0.82rem; font-weight: 700; color: #555; }
    .stTabs [aria-selected="true"] { color: #000 !important; border-bottom: 2px solid #000 !important; }

    /* 리스트 디자인: 무엇을 하는 사람인지(업무)를 가장 강조 */
    .contact-row {
        padding: 12px 0;
        border-bottom: 1px solid #eee;
        display: flex;
        flex-direction: column;
    }
    .top-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #000; }
    .dept-text { font-size: 0.8rem; color: #777; margin-left: 5px; }
    
    /* 업무 내용(비고): 붉은색 굵은 글씨로 이름 바로 아래 배치 */
    .work-text { 
        font-size: 0.95rem; 
        color: #d32f2f; 
        font-weight: 700; 
        line-height: 1.4;
        margin-top: 2px;
    }

    /* 버튼 스타일: 직관적인 텍스트 버튼 */
    .btn-group { display: flex; gap: 6px; }
    .call-btn {
        display: flex; align-items: center; justify-content: center;
        width: 52px; height: 38px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.82rem; font-weight: 800;
    }
    .btn-sub { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-main { background-color: #222; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: '열 이름'을 무시하고 '순서'로 강제 매핑 (KeyError 완전 방지)
@st.cache_data
def load_data():
    try:
        # 폴더 내 첫 번째 CSV 파일 찾기
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        # 데이터 로드 (모든 데이터를 문자열로 변환하여 에러 방지)
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig').astype(str)
        
        # [해결책] 엑셀 헤더가 깨져도 상관없이 순서대로 이름을 새로 붙임
        # 0:구분, 1:부서명, 2:담당자, 3:전화, 4:휴대폰, 5:비고
        actual_cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [actual_cols[i] for i in range(min(len(df.columns), 6))]
        
        return df.replace('nan', '')
    except:
        return pd.DataFrame()

df_raw = load_data()

# 3. 통합 검색 (전체 데이터 대상)
search_q = st.text_input("", placeholder="🔍 이름, 부서, 업무(대관, 보안, 미화 등) 검색", label_visibility="collapsed")

# 4. 탭 구성 (보안 -> 시설 -> 미화 -> 총무 -> 지원 -> 기타 -> 전체)
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 순서 기반으로 저장한 열 이름 사용
        name, dept, work = row['c_name'].strip(), row['c_dept'].strip(), row['c_work'].strip()
        tel, hp = row['c_tel'].strip(), row['c_hp'].strip()
        
        # 전화번호 숫자만 추출
        t_link = re.sub(r'[^0-9*]', '', tel)
        h_link = re.sub(r'[^0-9]', '', hp)
        
        title = name if name else dept
        sub = dept if name else ""

        st.markdown(f'''
            <div class="contact-row">
                <div class="top-flex">
                    <div class="info-box">
                        <span class="name-text">{title}</span>
                        <span class="dept-text">{sub}</span>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:"+t_link+"' class='call-btn btn-sub'>내선</a>" if t_link else ""}
                        {"<a href='tel:"+h_link+"' class='call-btn btn-main'>직통</a>" if h_link else ""}
                    </div>
                </div>
                {"<div class='work-text'>" + work + "</div>" if work else ""}
            </div>
        ''', unsafe_allow_html=True)

# 5. 탭 필터링 및 검색 로직 (전체 검색 -> 탭 분류)
for i, tab in enumerate(tabs):
    with tab:
        current_cat = tab_list[i]
        
        # 1차 카테고리 필터링
        if current_cat == "전체":
            df_tab = df_raw
        else:
            # '구분' 또는 '부서' 열에서 탭 이름 찾기
            df_tab = df_raw[df_raw['c_cat'].str.contains(current_cat) | df_raw['c_dept'].str.contains(current_cat)]
        
        # 2차 검색어 필터링
        if search_q:
            # 모든 열을 합쳐서 검색어가 있는지 확인
            df_final = df_tab[df_tab.apply(lambda r: r.str.contains(search_q, case=False).any(), axis=1)]
        else:
            df_final = df_tab
            
        render_ui(df_final)
