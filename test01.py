import streamlit as st
import pandas as pd
import re

# 1. 모바일 극한 최적화 (아이콘 없이 텍스트 중심 디자인)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 0.6rem !important; }
    header, footer { visibility: hidden; }
    
    /* 탭 디자인: 텍스트 강조 및 간격 조정 */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { height: 34px; font-size: 0.82rem; padding: 0 8px; font-weight: 600; }

    /* 리스트: 한 줄당 높이를 최소화 (뱅킹 앱 슬림 리스트 스타일) */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid #f2f2f2;
    }
    .info-section { flex: 1; min-width: 0; line-height: 1.2; }
    .title-line { display: flex; align-items: baseline; gap: 6px; }
    .main-text { font-size: 0.95rem; font-weight: 700; color: #111; }
    .sub-text { font-size: 0.78rem; color: #777; white-space: nowrap; }
    .work-desc { font-size: 0.72rem; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 1px; }
    
    /* 액션 버튼: 아이콘 대신 직관적인 텍스트 버튼 */
    .btn-group { display: flex; gap: 4px; }
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 10px;
        height: 32px;
        border-radius: 4px;
        text-decoration: none !important;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid #ddd;
    }
    .btn-tel { background-color: #fff; color: #007bff !important; border-color: #007bff; }
    .btn-hp { background-color: #007bff; color: #fff !important; border-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리 (KeyError 방지)
def clean_phone(phone_str):
    if not phone_str: return ""
    # 내선번호 중 *1 등 특수문자 포함 숫자를 위해 정규식 수정
    return re.sub(r'[^0-9*]', '', str(phone_str))

@st.cache_data
def load_data():
    try:
        # 파일이 없을 경우를 대비해 업로드된 파일명 확인
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        df.columns = df.columns.str.strip()
        return df.fillna('')
    except:
        # 파일 에러 시 빈 데이터프레임 반환
        return pd.DataFrame(columns=["구분", "부서명", "담당자", "전화", "휴대폰", "비고/업무"])

df = load_data()

# 3. 검색 (레이블 제거)
search = st.text_input("", placeholder="검색어 입력 (이름, 부서, 업무 등)", label_visibility="collapsed")
if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 탭 순서 강제 지정 (보안, 시설, 미화, 총무, 지원, 기타, 전체)
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_compact_row(target_df):
    if target_df.empty:
        st.caption("결과 없음")
        return
    for _, row in target_df.iterrows():
        name = str(row.get('담당자', '')).strip()
        dept = str(row.get('부서명', '')).strip()
        tel_raw = str(row.get('전화', '')).strip()
        hp_raw = str(row.get('휴대폰', '')).strip()
        work = str(row.get('비고/업무', '')).strip()
        
        # 전화 연결용 번호 정리
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
                {"<a href='tel:" + tel + "' class='action-btn btn-tel'>내선</a>" if tel else ""}
                {"<a href='tel:" + hp + "' class='action-btn btn-hp'>직통</a>" if hp else ""}
            </div>
        </div>
        '''
        st.markdown(row_html, unsafe_allow_html=True)

# 5. 각 탭에 데이터 매핑
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        if cat == "전체":
            render_compact_row(df)
        else:
            # 해당 구분이 포함된 데이터만 필터링
            render_compact_row(df[df['구분'].str.contains(cat, na=False)])
