import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 여백 극한 최적화
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    /* 상단 및 좌우 여백 제거 */
    .block-container { padding: 0.5rem 0.7rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { height: 35px; font-size: 0.85rem; padding: 0 10px; }
    
    /* 한 줄 리스트 디자인 (뱅킹 앱 스타일) */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #f1f1f1;
    }
    .info-section { flex: 1; min-width: 0; }
    .title-line { display: flex; align-items: baseline; gap: 6px; }
    .main-text { font-size: 1rem; font-weight: 700; color: #111; white-space: nowrap; }
    .sub-text { font-size: 0.8rem; color: #888; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .work-desc { font-size: 0.75rem; color: #999; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    
    /* 전화 버튼 그룹 */
    .btn-group { display: flex; gap: 4px; margin-left: 10px; }
    .call-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 36px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 1.1rem;
    }
    .btn-tel { background-color: #e7f1ff; color: #007bff !important; } /* 내선: 연파랑 */
    .btn-hp { background-color: #e9f7ef; color: #28a745 !important; }  /* 직통: 연초록 */
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 처리 함수 (숫자만 추출 로직 포함)
def clean_phone(phone_str):
    if not phone_str: return ""
    return re.sub(r'[^0-9]', '', str(phone_str))

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        return df.fillna('')
    except:
        return pd.DataFrame(columns=["구분", "부서명", "담당자", "전화", "휴대폰", "비고/업무"])

df = load_data()

# 3. 검색 UI (레이블 없이 입력창만)
search = st.text_input("", placeholder="🔍 이름, 부서, 번호 검색 (167개 전체)")

if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 카테고리 탭 (총무, 지원, 시설, 보안/미화, 기타)
tab_list = ["전체", "총무", "지원", "시설", "보안/미화", "기타"]
tabs = st.tabs(tab_list)

def render_row(target_df):
    for _, row in target_df.iterrows():
        name = str(row['담당자']).strip()
        dept = str(row['부서명']).strip()
        tel = clean_phone(row['전화'])
        hp = clean_phone(row['휴대폰'])
        work = str(row['비고/업무']).strip()
        
        # 가변형 헤드라인 로직: 이름 유무에 따른 타이틀 결정
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
                {"<a href='tel:" + tel + "' class='call-btn btn-tel' title='내선'>📞</a>" if tel else ""}
                {"<a href='tel:" + hp + "' class='call-btn btn-hp' title='직통'>📱</a>" if hp else ""}
            </div>
        </div>
        '''
        st.markdown(row_html, unsafe_allow_html=True)

# 5. 탭별 출력 로직
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        if cat == "전체":
            render_row(df)
        elif cat == "보안/미화":
            render_row(df[df['구분'].isin(['보안', '미화'])])
        else:
            render_row(df[df['구분'] == cat])
