import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 이미지 스타일 반영 (Black & White 미니멀)
st.set_page_config(page_title="성의교정 통합 연락처", layout="wide")
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px; border-radius: 5px 5px 0 0; background-color: #f0f2f6;
    }
    .contact-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        background-color: #ffffff;
    }
    .main-title { font-size: 1.15rem; font-weight: bold; color: #000; margin-bottom: 2px; }
    .sub-title { font-size: 0.85rem; color: #666; margin-bottom: 8px; }
    .info-row { font-size: 0.9rem; color: #333; margin-top: 3px; display: flex; align-items: center; }
    .label { font-weight: bold; color: #888; width: 45px; font-size: 0.75rem; }
    .tag { background: #eee; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-bottom: 5px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (구글 시트 게시판 URL 또는 로컬 CSV)
@st.cache_data
def load_data():
    # 파일명은 실제 저장된 이름으로 확인 필요
    df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
    return df.fillna('')

df = load_data()

# 3. 다중 키워드 검색 (단일 입력창)
st.title("📞 성의교정 연락처 검색")
search_query = st.text_input("", placeholder="부서, 담당자, 내선, 업무 중 하나만 입력하세요")

if search_query:
    mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
    df = df[mask]

# 4. 6개 카테고리 탭 (데이터의 '구분' 기준 자동 배정)
# 구글 시트의 '구분' 열에 있는 값들로 6개 탭 구성
tabs = st.tabs(["전체", "총무", "지원", "시설", "연구", "기타"])

def display_list(target_df):
    if target_df.empty:
        st.write("해당하는 정보가 없습니다.")
        return
    for _, row in target_df.iterrows():
        with st.container():
            st.markdown('<div class="contact-card">', unsafe_allow_html=True)
            
            # [가변형 헤드라인 로직]
            if row['담당자'].strip():
                # 이름이 있는 경우: 이름이 제목, 부서가 소제목
                st.markdown(f'<div class="main-title">{row["담당자"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="sub-title">{row["부서명"]}</div>', unsafe_allow_html=True)
            else:
                # 이름이 없는 경우: 부서명이 제목으로 격상
                st.markdown(f'<div class="main-title">{row["부서명"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="sub-text" style="height:15px;"></div>', unsafe_allow_html=True)
            
            # [포맷 최적화: 데이터가 있는 항목만 노출]
            if row['전화'].strip():
                st.markdown(f'<div class="info-row"><span class="label">내선</span>{row["전화"]}</div>', unsafe_allow_html=True)
            if row['휴대폰'].strip():
                st.markdown(f'<div class="info-row"><span class="label">H.P</span>{row["휴대폰"]}</div>', unsafe_allow_html=True)
            if row['비고/업무'].strip():
                st.markdown(f'<div class="info-row" style="margin-top:8px; border-top:1px solid #f5f5f5; padding-top:5px;">'
                            f'<span class="label">업무</span>{row["비고/업무"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# 5. 각 탭별 로직 실행
for i, tab in enumerate(tabs):
    with tab:
        cat_names = ["전체", "총무", "지원", "시설", "연구", "기타"]
        if cat_names[i] == "전체":
            display_list(df)
        else:
            display_list(df[df['구분'] == cat_names[i]])
