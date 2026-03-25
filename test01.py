import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 모바일 극한 최적화
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    /* 상단 여백 및 헤더 제거 */
    .block-container { padding: 0.4rem 0.6rem !important; }
    header, footer { visibility: hidden; }
    
    /* 탭 디자인: 글자 크기 및 간격 축소 */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { height: 32px; font-size: 0.8rem; padding: 0 6px; font-weight: 600; }

    /* 리스트: 한 화면 노출 극대화 (최소 높이 42px) */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #f2f2f2;
        min-height: 42px;
    }
    .info-section { flex: 1; min-width: 0; line-height: 1.1; }
    .title-line { display: flex; align-items: baseline; gap: 5px; }
    .main-text { font-size: 0.95rem; font-weight: 700; color: #111; }
    .sub-text { font-size: 0.75rem; color: #777; white-space: nowrap; }
    .work-desc { font-size: 0.7rem; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 1px; }
    
    /* 텍스트 액션 버튼 (아이콘 제거) */
    .btn-group { display: flex; gap: 4px; }
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 10px;
        height: 30px;
        border-radius: 4px;
        text-decoration: none !important;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .btn-tel { background-color: #fff; color: #007bff !important; border: 1px solid #007bff; }
    .btn-hp { background-color: #007bff; color: #fff !important; border: 1px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 열 이름 강제 정규화 (KeyError 해결 핵심)
@st.cache_data
def load_data():
    try:
        # 파일 읽기
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        
        # [핵심] 컬럼명이 깨졌을 경우를 대비해 위치(index) 기반으로 강제 이름 부여
        # 열이 6개라고 가정하고 강제로 덮어씌웁니다.
        new_cols = ['구분', '부서명', '담당자', '전화', '휴대폰', '비고/업무']
        df.columns = new_cols[:len(df.columns)]
        
        # 각 셀의 앞뒤 공백 제거
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df.fillna('')
    except:
        return pd.DataFrame(columns=['구분', '부서명', '담당자', '전화', '휴대폰', '비고/업무'])

df = load_data()

# 3. 검색 (공간 절약)
search = st.text_input("", placeholder="성함, 부서, 업무 검색", label_visibility="collapsed")
if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 요청하신 탭 순서 (보안 -> 시설 -> 미화 -> 총무 -> 지원 -> 기타 -> 전체)
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_row(target_df):
    if target_df.empty:
        st.caption("내용 없음")
        return
    
    for _, row in target_df.iterrows():
        name = str(row['담당자']).strip()
        dept = str(row['부서명']).strip()
        tel_raw = str(row['전화']).strip()
        hp_raw = str(row['휴대폰']).strip()
        work = str(row['비고/업무']).strip()
        
        # 전화 연결 번호 정제 (* 및 숫자 유지)
        tel_link = re.sub(r'[^0-9*]', '', tel_raw)
        hp_link = re.sub(r'[^0-9]', '', hp_raw)
        
        # 가변 헤드라인
        title = name if name else dept
        sub = dept if name else ""
        
        st.markdown(f'''
        <div class="list-row">
            <div class="info-section">
                <div class="title-line">
                    <span class="main-text">{title}</span>
                    <span class="sub-text">{sub}</span>
                </div>
                {"<div class='work-desc'>" + work + "</div>" if work else ""}
            </div>
            <div class="btn-group">
                {"<a href='tel:" + tel_link + "' class='action-btn btn-tel'>내선</a>" if tel_link else ""}
                {"<a href='tel:" + hp_link + "' class='action-btn btn-hp'>직통</a>" if hp_link else ""}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# 5. 탭별 매핑 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        if cat == "전체":
            render_row(df)
        else:
            # '구분' 열의 위치를 기반으로 필터링 (iloc[0]이 '구분' 열임을 보장)
            filtered_df = df[df.iloc[:, 0].str.contains(cat, na=False)]
            render_row(filtered_df)
