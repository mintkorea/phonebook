import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 디자인 (실용성 극대화)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.4rem 0.6rem !important; background-color: #ffffff; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 직관적 디자인 */
    .stTextInput input {
        border: 2px solid #000 !important;
        border-radius: 4px !important;
        height: 45px !important;
        font-size: 1.1rem !important;
    }

    /* 리스트 디자인: 업무(비고)를 가장 먼저 보이게 */
    .contact-item {
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }
    
    /* 업무 내용(비고) 강조: 빨간색 박스형 */
    .work-tag {
        display: inline-block;
        background-color: #fff0f0;
        color: #d32f2f;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 6px;
        border: 1px solid #ffcccc;
    }

    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #111; }
    .dept-text { font-size: 0.8rem; color: #666; margin-left: 5px; }

    /* 버튼 스타일 */
    .btn-group { display: flex; gap: 6px; }
    .action-btn {
        display: flex; align-items: center; justify-content: center;
        width: 52px; height: 38px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.8rem; font-weight: 700;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: 이름 대신 '번호'로 읽기 (KeyError 완전 해결)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        # 모든 데이터를 일단 글자(str)로 읽어서 에러 방지
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig').astype(str)
        df = df.replace('nan', '')
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

# 3. 통합 검색 (상단 고정)
q = st.text_input("", placeholder="🔍 이름, 부서, 업무 내용 검색", label_visibility="collapsed")

# 4. 탭 구성 (보안, 시설, 미화, 총무, 지원, 기타, 전체)
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_list(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # [핵심] 컬럼명 대신 번호(iloc)로 접근하여 KeyError 차단
        # 0:구분, 1:부서명, 2:담당자, 3:전화, 4:휴대폰, 5:비고
        try:
            r_cat = str(row.iloc[0]).strip()
            r_dept = str(row.iloc[1]).strip()
            r_name = str(row.iloc[2]).strip()
            r_tel = re.sub(r'[^0-9*]', '', str(row.iloc[3]))
            r_hp = re.sub(r'[^0-9]', '', str(row.iloc[4]))
            r_work = str(row.iloc[5]).strip()
            
            title = r_name if r_name else r_dept
            sub = r_dept if r_name else ""

            st.markdown(f'''
                <div class="contact-item">
                    {"<div class='work-tag'>업무: " + r_work + "</div>" if r_work else ""}
                    <div class="info-row">
                        <div class="names">
                            <span class="name-text">{title}</span>
                            <span class="dept-text">{sub}</span>
                        </div>
                        <div class="btn-group">
                            {"<a href='tel:"+r_tel+"' class='action-btn btn-tel'>내선</a>" if r_tel else ""}
                            {"<a href='tel:"+r_hp+"' class='action-btn btn-hp'>직통</a>" if r_hp else ""}
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        except:
            continue

# 5. 탭 필터링 및 검색 로직 (전체 검색 -> 탭 분류)
for i, tab in enumerate(tabs):
    with tab:
        cat_name = tab_list[i]
        
        # 1차 필터링 (탭 선택)
        if cat_name == "전체":
            df_step1 = df_raw
        else:
            # 0번 열(구분) 또는 1번 열(부서)에서 카테고리 확인
            df_step1 = df_raw[df_raw.iloc[:, 0].str.contains(cat_name) | df_raw.iloc[:, 1].str.contains(cat_name)]
        
        # 2차 필터링 (검색어 입력)
        if q:
            # 모든 열(0~5번)에서 검색어 포함 여부 확인
            df_final = df_step1[df_step1.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        else:
            df_final = df_step1
            
        render_list(df_final)
