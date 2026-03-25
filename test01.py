import streamlit as st
import pandas as pd

# 1. 모바일 최적화: 여백 제거 및 한 줄 레이아웃 설정
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    /* 상단 기본 여백 제거 */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 0.5rem; padding-right: 0.5rem; }
    
    /* 카드 디자인: 한 화면 노출 극대화 (세로 여백 최소화) */
    .contact-row {
        border-bottom: 1px solid #eee;
        padding: 8px 0px;
        display: flex;
        flex-direction: column;
    }
    
    /* 헤드라인: 이름(또는 부서) 강조 */
    .title-line { display: flex; align-items: center; justify-content: space-between; }
    .main-text { font-size: 1rem; font-weight: 700; color: #000; }
    .sub-text { font-size: 0.8rem; color: #666; margin-left: 5px; }
    
    /* 버튼: 한 줄에 여러 개 배치 */
    .btn-group { display: flex; gap: 5px; margin-top: 5px; }
    .call-btn {
        flex: 1;
        text-align: center;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 6px 0;
        border-radius: 4px;
        color: white !important;
    }
    .btn-tel { background-color: #007bff; } /* 내선: 파랑 */
    .btn-hp { background-color: #28a745; }  /* 직통: 초록 */
    
    /* 업무내용: 아주 작게 표시 */
    .work-text { font-size: 0.75rem; color: #888; margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 불러오기 (파일 업로드 없이 로직 유지)
@st.cache_data
def load_data():
    # 실제 업로드하신 CSV 파일명 사용
    try:
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        return df.fillna('')
    except:
        return pd.DataFrame(columns=["구분", "부서명", "담당자", "전화", "휴대폰", "비고/업무"])

df = load_data()

# 3. 검색창 (공간 절약을 위해 레이블 생략)
search = st.text_input("", placeholder="🔍 성함, 부서, 번호 검색")

if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 카테고리 탭
tab_list = ["전체", "총무", "지원", "시설", "보안/미화", "기타"]
tabs = st.tabs(tab_list)

def render_compact_list(target_df):
    if target_df.empty:
        st.caption("정보가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        name = str(row['담당자']).strip()
        dept = str(row['부서명']).strip()
        tel = "".join(filter(str.isdigit, str(row['전화'])))
        hp = "".join(filter(str.isdigit, str(row['휴대폰'])))
        work = str(row['비고/업무']).strip()
        
        with st.container():
            # [가변형 헤드라인 로직]
            header_html = f'<div class="contact-row">'
            header_html += '<div class="title-line">'
            if name:
                header_html += f'<div><span class="main-text">{name}</span><span class="sub-text">{dept}</span></div>'
            else:
                header_html += f'<div><span class="main-text">{dept}</span></div>'
            header_html += '</div>'
            
            # [업무내용 한 줄 요약]
            if work:
                header_html += f'<div class="work-text">{work}</div>'
            
            # [원터치 전화 버튼]
            header_html += '<div class="btn-group">'
            if tel:
                header_html += f'<a href="tel:{tel}" class="call-btn btn-tel">내선 연결</a>'
            if hp:
                header_html += f'<a href="tel:{hp}" class="call-btn btn-hp">직통 연결</a>'
            header_html += '</div></div>'
            
            st.markdown(header_html, unsafe_allow_html=True)

# 5. 탭별 출력
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        if cat == "전체":
            render_compact_list(df)
        elif cat == "보안/미화":
            render_compact_list(df[df['구분'].isin(['보안', '미화'])])
        else:
            render_compact_list(df[df['구분'] == cat])
