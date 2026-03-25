import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 모바일 최적화 레이아웃
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.4rem 0.6rem !important; }
    header, footer { visibility: hidden; }
    
    /* 탭 간격 및 텍스트 설정 */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { height: 34px; font-size: 0.82rem; padding: 0 8px; font-weight: 600; }

    /* 리스트 행 디자인 */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;
        min-height: 48px;
    }
    .info-section { flex: 1; min-width: 0; padding-right: 8px; }
    .title-line { display: flex; align-items: baseline; gap: 6px; margin-bottom: 2px; }
    .main-text { font-size: 0.95rem; font-weight: 700; color: #111; }
    .sub-text { font-size: 0.78rem; color: #777; }
    .work-desc { font-size: 0.72rem; color: #999; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    /* 버튼 그룹 및 텍스트 버튼 스타일 */
    .btn-group { display: flex; gap: 6px; flex-shrink: 0; }
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 32px;
        border-radius: 4px;
        text-decoration: none !important;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .btn-tel { background-color: #ffffff; color: #007bff !important; border: 1px solid #007bff; }
    .btn-hp { background-color: #007bff; color: #ffffff !important; border: 1px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (파일명 자동 인식 및 강제 컬럼 매핑)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        df = pd.read_csv(csv_files[0])
        # 컬럼명이 깨졌을 경우를 대비해 위치 기반으로 강제 이름 부여
        cols = ['구분', '부서명', '담당자', '전화', '휴대폰', '비고']
        mapping = {df.columns[i]: cols[i] for i in range(min(len(df.columns), len(cols)))}
        df.rename(columns=mapping, inplace=True)
        return df.fillna('')
    except:
        return pd.DataFrame()

raw_df = load_data()

# 3. 검색 필터링 (전체 데이터 대상)
search = st.text_input("", placeholder="🔍 성함, 부서, 업무 검색", label_visibility="collapsed")
if search:
    # 모든 열을 검사하여 검색어가 포함된 행만 남김
    filtered_df = raw_df[raw_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
else:
    filtered_df = raw_df

# 4. 탭 구성 (보안 -> 시설 -> 미화 -> 총무 -> 지원 -> 기타 -> 전체)
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_list(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        name = str(row.get('담당자', '')).strip()
        dept = str(row.get('부서명', '')).strip()
        tel_raw = str(row.get('전화', '')).strip()
        hp_raw = str(row.get('휴대폰', '')).strip()
        work = str(row.get('비고', '')).strip()
        
        # 전화연결 링크 전처리
        tel_link = re.sub(r'[^0-9*]', '', tel_raw)
        hp_link = re.sub(r'[^0-9]', '', hp_raw)
        
        # 제목 및 부제목 설정
        title = name if name else dept
        sub = dept if name else ""
        
        # HTML 렌더링 (구조적 오류 방지를 위해 f-string 결합 최소화)
        row_html = f'<div class="list-row">'
        row_html += f'<div class="info-section">'
        row_html += f'<div class="title-line"><span class="main-text">{title}</span><span class="sub-text">{sub}</span></div>'
        if work: row_html += f'<div class="work-desc">{work}</div>'
        row_html += f'</div>' # info-section 끝
        
        row_html += f'<div class="btn-group">'
        if tel_link: row_html += f'<a href="tel:{tel_link}" class="action-btn btn-tel">내선</a>'
        if hp_link: row_html += f'<a href="tel:{hp_link}" class="action-btn btn-hp">직통</a>'
        row_html += f'</div></div>' # btn-group 및 list-row 끝
        
        st.markdown(row_html, unsafe_allow_html=True)

# 5. 탭별 로직 실행
for i, tab in enumerate(tabs):
    with tab:
        current_cat = tab_titles[i]
        if current_cat == "전체":
            render_list(filtered_df)
        else:
            # 검색된 결과(filtered_df) 중에서 현재 탭 카테고리에 맞는 데이터만 리스트업
            # '구분' 열 뿐만 아니라 행 전체에서 해당 카테고리 명이 있는지 확인하여 더 정확히 매칭
            tab_filtered = filtered_df[filtered_df.apply(lambda x: x.astype(str).str.contains(current_cat, na=False)).any(axis=1)]
            render_list(tab_filtered)
