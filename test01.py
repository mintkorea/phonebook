import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 모바일 극한 최적화 (여백 최소화)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    /* 배경 및 컨테이너 설정 */
    .block-container { padding: 0.3rem 0.5rem !important; background-color: #ffffff; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 상단 고정 느낌으로 디자인 */
    .stTextInput > div > div > input {
        border-radius: 4px !important;
        border: 1px solid #333 !important;
        height: 42px !important;
        font-size: 1rem !important;
    }

    /* 탭: 세분화된 카테고리를 위해 간격 조정 */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { 
        height: 34px; font-size: 0.78rem; padding: 0 6px; 
        font-weight: 600; color: #666; 
    }
    .stTabs [aria-selected="true"] { color: #000 !important; border-bottom: 2px solid #000 !important; }

    /* 리스트: 한 줄에 이름-부서-업무를 밀집 배치 */
    .contact-item {
        padding: 10px 0;
        border-bottom: 1px solid #eee;
        display: flex;
        flex-direction: column;
        gap: 3px;
    }
    .top-line { display: flex; justify-content: space-between; align-items: flex-start; }
    .name-info { flex: 1; }
    .name-tag { font-size: 1rem; font-weight: 800; color: #000; margin-right: 5px; }
    .dept-tag { font-size: 0.75rem; color: #888; }
    
    /* 업무 내용: 이름 바로 아래에 가장 잘 보이도록 강조 */
    .work-tag { 
        font-size: 0.82rem; color: #d32f2f; /* 업무는 붉은 계열로 강조 */
        font-weight: 600; line-height: 1.2;
    }

    /* 버튼: 실용적인 텍스트 버튼 */
    .btn-group { display: flex; gap: 5px; }
    .action-btn {
        display: flex; align-items: center; justify-content: center;
        width: 46px; height: 34px; border-radius: 3px;
        text-decoration: none !important; font-size: 0.75rem; font-weight: 700;
    }
    .btn-tel { background-color: #f1f3f5; color: #333 !important; border: 1px solid #ced4da; }
    .btn-hp { background-color: #212529; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: 열 이름 무관하게 순서로 강제 매핑 (KeyError 해결)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig')
        # 열 이름을 순서대로 강제 지정 (구분, 부서, 담당, 내선, 휴대폰, 비고)
        new_names = ['cat', 'dept', 'name', 'tel', 'hp', 'work']
        df.columns = [new_names[i] for i in range(min(len(df.columns), len(new_names)))]
        return df.fillna('')
    except:
        return pd.DataFrame()

raw_df = load_data()

# 3. 검색: 탭과 무관하게 전체 데이터에서 실시간 필터링
search_q = st.text_input("", placeholder="🔍 이름, 부서, 업무(대관, 보안 등) 통합 검색", label_visibility="collapsed")

if search_q:
    # 모든 열에서 검색어가 포함된 행을 찾음
    filtered_df = raw_df[raw_df.apply(lambda row: row.astype(str).str.contains(search_q, case=False).any(), axis=1)]
else:
    filtered_df = raw_df

# 4. 탭 세분화 (보안, 시설, 미화, 총무, 지원, 기타, 전체)
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_list(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 안전 추출
        r_name = str(row.get('name', '')).strip()
        r_dept = str(row.get('dept', '')).strip()
        r_work = str(row.get('work', '')).strip()
        r_tel = re.sub(r'[^0-9*]', '', str(row.get('tel', '')))
        r_hp = re.sub(r'[^0-9]', '', str(row.get('hp', '')))
        
        d_name = r_name if r_name else r_dept
        d_dept = r_dept if r_name else ""

        # UI 렌더링
        st.markdown(f'''
            <div class="contact-item">
                <div class="top-line">
                    <div class="name-info">
                        <span class="name-tag">{d_name}</span>
                        <span class="dept-tag">{d_dept}</span>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:" + r_tel + "' class='action-btn btn-tel'>내선</a>" if r_tel else ""}
                        {"<a href='tel:" + r_hp + "' class='action-btn btn-hp'>직통</a>" if r_hp else ""}
                    </div>
                </div>
                {"<div class='work-tag'>" + r_work + "</div>" if r_work else ""}
            </div>
        ''', unsafe_allow_html=True)

# 5. 탭별 실행 (검색 결과 내에서 카테고리 매칭)
for i, tab in enumerate(tabs):
    with tab:
        current_cat = tab_titles[i]
        if current_cat == "전체":
            render_list(filtered_df)
        else:
            # 탭 키워드가 '구분' 또는 행 전체에 포함된 데이터만 표시
            tab_data = filtered_df[filtered_df.apply(lambda x: x.astype(str).str.contains(current_cat, na=False)).any(axis=1)]
            render_list(tab_data)
