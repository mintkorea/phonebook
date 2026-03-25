import streamlit as st
import pandas as pd

# 1. 디자인 최적화 (블랙 & 화이트 미니멀 테마)
st.set_page_config(page_title="성의교정 연락처 Hub", layout="wide")
st.markdown("""
    <style>
    .contact-card {
        border-bottom: 1px solid #eee;
        padding: 10px 5px;
        margin-bottom: 5px;
    }
    .main-text { font-size: 1.1rem; font-weight: 700; color: #000; }
    .sub-text { font-size: 0.85rem; color: #666; }
    .detail-text { font-size: 0.9rem; color: #333; margin-top: 4px; }
    .label { color: #999; margin-right: 5px; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (구글 시트 게시판 URL 또는 로컬 파일)
@st.cache_data
def load_data():
    # 파일명을 실제 환경에 맞춰 수정하세요
    df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv') 
    return df.fillna('')

df = load_data()

# 3. 다중 키워드 검색 UI
search = st.text_input("🔍 전체 데이터 실시간 검색", placeholder="이름, 부서, 번호, 업무 등 키워드 입력")

if search:
    # 전체 컬럼에서 키워드가 포함된 행 필터링
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 6개 카테고리 탭 (데이터의 '구분' 값 기준)
category_list = ["전체", "총무", "지원", "시설", "연구", "기타"]
tabs = st.tabs(category_list)

for i, cat_name in enumerate(category_list):
    with tabs[i]:
        # 카테고리별 필터링
        display_df = df if cat_name == "전체" else df[df['구분'] == cat_name]
        
        if display_df.empty:
            st.caption("검색 결과가 없습니다.")
        
        for _, row in display_df.iterrows():
            with st.container():
                st.markdown('<div class="contact-card">', unsafe_allow_html=True)
                
                # [로직 1] 가변형 헤드라인
                if row['담당자']:
                    st.markdown(f'<div class="main-text">{row["담당자"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="sub-text">{row["부서명"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="main-text">{row["부서명"]}</div>', unsafe_allow_html=True)
                
                # [로직 2] 포맷 최적화 (데이터가 있을 때만 노출)
                contact_line = []
                if row['전화']: contact_line.append(f"<span class='label'>내선</span>{row['전화']}")
                if row['휴대폰']: contact_line.append(f"<span class='label'>직통</span>{row['휴대폰']}")
                
                if contact_line:
                    st.markdown(f'<div class="detail-text">{" | ".join(contact_line)}</div>', unsafe_allow_html=True)
                
                if row['비고/업무']:
                    st.markdown(f'<div class="detail-text"><span class="label">업무</span>{row["비고/업무"]}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
