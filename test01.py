import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 모바일 초슬림 디자인
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.4rem 0.6rem !important; }
    header, footer { visibility: hidden; }
    
    /* 탭 간격 및 글자 크기 최적화 */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { height: 32px; font-size: 0.8rem; padding: 0 6px; font-weight: 600; }

    /* 리스트 행 높이 극한으로 줄임 (한 화면 최대 노출) */
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
    
    /* 텍스트 기반 액션 버튼 (아이콘 제거) */
    .btn-group { display: flex; gap: 4px; }
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 12px;
        height: 30px;
        border-radius: 4px;
        text-decoration: none !important;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .btn-tel { background-color: #ffffff; color: #007bff !important; border: 1px solid #007bff; }
    .btn-hp { background-color: #007bff; color: #ffffff !important; border: 1px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 열 이름 강제 정규화 (KeyError 해결 핵심)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        # 열 이름의 앞뒤 공백을 제거하고, 모든 열 이름을 새로 정의 (순서 보장)
        df.columns = [c.strip() for c in df.columns]
        # 만약 열 이름이 다르더라도 위치(인덱스) 기반으로 강제 이름 부여
        df.columns = ['구분', '부서명', '담당자', '전화', '휴대폰', '비고/업무']
        return df.fillna('')
    except:
        return pd.DataFrame(columns=['구분', '부서명', '담당자', '전화', '휴대폰', '비고/업무'])

df = load_data()

# 3. 검색 기능
search = st.text_input("", placeholder="성함, 부서, 업무 검색", label_visibility="collapsed")
if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 요청하신 순서대로 탭 배치
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_row(target_df):
    if target_df.empty:
        st.caption("내용 없음")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 추출
        name = str(row['담당자']).strip()
        dept = str(row['부서명']).strip()
        tel_raw = str(row['전화']).strip()
        hp_raw = str(row['휴대폰']).strip()
        work = str(row['비고/업무']).strip()
        
        # 전화연결 번호 정리 (숫자 및 내선 특수문자 유지)
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

# 5. 탭별 데이터 매핑
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        if cat == "전체":
            render_row(df)
        else:
            # '구분' 열에서 해당 탭 텍스트가 포함된 데이터 필터링
            render_row(df[df['구분'].str.contains(cat, na=False)])
