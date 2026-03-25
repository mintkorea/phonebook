import streamlit as st
import pandas as pd

# 1. UI 디자인: 모바일 앱 스타일 (이미지 반영)
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    /* 여백 및 배경 설정 */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 45px; font-weight: 600; }
    
    /* 카드 디자인: 이미지의 리스트 스타일 반영 */
    .contact-card {
        border-bottom: 1px solid #f0f0f0;
        padding: 15px 5px;
        background-color: transparent;
    }
    .header-group { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; }
    .main-title { font-size: 1.15rem; font-weight: 800; color: #1a1a1a; }
    .sub-title { font-size: 0.85rem; color: #888; font-weight: 400; }
    
    /* 상세 정보 스타일 */
    .info-row { font-size: 0.95rem; color: #444; margin-top: 2px; }
    .label { color: #aaa; margin-right: 8px; font-size: 0.75rem; width: 40px; display: inline-block; }
    .work-tag { 
        background-color: #f8f9fa; 
        padding: 6px 10px; 
        border-radius: 4px; 
        font-size: 0.85rem; 
        color: #555; 
        margin-top: 8px;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    # 파일명: 성의교정 연락처.xlsx - Sheet1.csv
    df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
    return df.fillna('')

df = load_data()

# 3. 검색 필터 (다중 키워드)
search = st.text_input("🔍 이름, 부서, 번호, 업무로 검색", placeholder="단어 하나만 입력해도 167개 전체에서 검색")

if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 6개 카테고리 자동 분류 탭
tab_titles = ["전체", "총무", "지원", "시설", "보안/미화", "연구/기타"]
tabs = st.tabs(tab_titles)

def render_cards(target_df):
    if target_df.empty:
        st.caption("검색 결과가 없습니다.")
        return
    for _, row in target_df.iterrows():
        with st.container():
            st.markdown('<div class="contact-card">', unsafe_allow_html=True)
            
            # [로직 1] 가변형 헤드라인 (Dynamic Header)
            if row['담당자'].strip():
                # 담당자 이름이 있는 경우
                st.markdown(f'''
                    <div class="header-group">
                        <div class="main-title">{row['담당자']}</div>
                        <div class="sub-title">{row['부서명']}</div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                # 담당자 이름이 없는 경우: 부서명을 제목으로 격상
                st.markdown(f'<div class="main-title">{row["부서명"]}</div>', unsafe_allow_html=True)
            
            # [로직 2] 연락처 포맷 최적화 (데이터 유무에 따라 표출)
            if row['전화'].strip():
                st.markdown(f'<div class="info-row"><span class="label">내선</span>{row["전화"]}</div>', unsafe_allow_html=True)
            if row['휴대폰'].strip():
                st.markdown(f'<div class="info-row"><span class="label">직통</span>{row["휴대폰"]}</div>', unsafe_allow_html=True)
            
            # [로직 3] 비고/업무 내용 (있는 경우만 디자인 박스로 노출)
            if row['비고/업무'].strip():
                st.markdown(f'<div class="work-tag"><b>업무:</b> {row["비고/업무"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# 5. 각 탭별 카테고리 매핑
for i, tab in enumerate(tabs):
    with tab:
        current_cat = tab_titles[i]
        if current_cat == "전체":
            render_cards(df)
        elif current_cat == "보안/미화":
            render_cards(df[df['구분'].isin(['보안', '미화'])])
        elif current_cat == "연구/기타":
            render_cards(df[df['구분'].isin(['연구', '기타'])])
        else:
            render_cards(df[df['구분'] == current_cat])
