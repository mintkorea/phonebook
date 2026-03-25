import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 여백 극한 최적화 (한 화면 최대 노출)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    /* 상단 여백 및 기본 패딩 제거 */
    .block-container { padding: 0.5rem 0.5rem !important; }
    header {visibility: hidden;}
    
    /* 탭 디자인 슬림화 */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { height: 32px; font-size: 0.8rem; padding: 0 8px; }

    /* 리스트 디자인: 높이를 최소화하여 한 화면 노출 극대화 */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #f2f2f2;
        min-height: 45px;
    }
    .info-section { flex: 1; min-width: 0; line-height: 1.2; }
    .title-line { display: flex; align-items: center; gap: 5px; }
    .main-text { font-size: 0.95rem; font-weight: 700; color: #000; }
    .sub-text { font-size: 0.75rem; color: #888; }
    .work-desc { font-size: 0.7rem; color: #aaa; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 1px; }
    
    /* 원터치 버튼 슬림화 */
    .btn-group { display: flex; gap: 3px; }
    .call-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 34px;
        border-radius: 4px;
        text-decoration: none !important;
        font-size: 1rem;
    }
    .btn-tel { background-color: #f0f7ff; color: #007bff !important; border: 1px solid #ddecff; }
    .btn-hp { background-color: #f0fff4; color: #28a745 !important; border: 1px solid #dfffe8; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 처리 및 KeyError 방지 로직
def clean_phone(phone_str):
    if not phone_str: return ""
    return re.sub(r'[^0-9]', '', str(phone_str))

@st.cache_data
def load_data():
    try:
        # 파일 읽기 및 컬럼명 양끝 공백 제거 (KeyError 방지 핵심)
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        df.columns = df.columns.str.strip() 
        
        # 만약 '구분' 컬럼이 없다면 첫 번째 컬럼을 '구분'으로 강제 지정
        if '구분' not in df.columns:
            df.rename(columns={df.columns[0]: '구분'}, inplace=True)
            
        return df.fillna('')
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = load_data()

# 3. 검색 UI (검색창 높이 줄임)
search = st.text_input("", placeholder="🔍 성함/부서/번호 검색", label_visibility="collapsed")

if search and not df.empty:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 탭 구성 (KeyError 방지를 위해 실제 데이터에 있는 값만 사용)
available_cats = ["전체"] + (df['구분'].unique().tolist() if not df.empty else [])
# 중복 제거 및 순서 정리 (원하시는 순서대로)
tab_list = ["전체", "총무", "지원", "시설", "보안", "미화", "기타"]
# 실제 데이터에 있는 카테고리만 필터링
tab_list = [c for c in tab_list if c in available_cats or c == "전체"]

tabs = st.tabs(tab_list)

def render_row(target_df):
    for _, row in target_df.iterrows():
        # 컬럼 존재 여부 확인하며 데이터 추출
        name = str(row.get('담당자', '')).strip()
        dept = str(row.get('부서명', '')).strip()
        tel_raw = str(row.get('전화', ''))
        hp_raw = str(row.get('휴대폰', ''))
        work = str(row.get('비고/업무', '')).strip()
        
        tel = clean_phone(tel_raw)
        hp = clean_phone(hp_raw)
        
        # 가변형 헤드라인
        display_title = name if name else dept
        display_sub = dept if name else ""
        
        row_html = f'''
        <div class="list-row">
            <div class="info-section">
                <div class="title-line">
                    <span class="main-text">{display_title}</span>
                    <span class="sub-text">{display_sub}</span>
                </div>
                {"<div class='work-desc'>" + work + "</div>" if work else ""}
            </div>
            <div class="btn-group">
                {"<a href='tel:" + tel + "' class='call-btn btn-tel'>📞</a>" if tel else ""}
                {"<a href='tel:" + hp + "' class='call-btn btn-hp'>📱</a>" if hp else ""}
            </div>
        </div>
        '''
        st.markdown(row_html, unsafe_allow_html=True)

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        if cat == "전체":
            render_row(df)
        else:
            render_row(df[df['구분'] == cat])
