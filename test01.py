import streamlit as st
import pandas as pd

# 1. 화면 설정 및 CSS (블랙 & 화이트 미니멀)
st.set_page_config(page_title="성의교정 통합 연락처", layout="wide")
st.markdown("""
    <style>
    .contact-card {
        border-bottom: 1px solid #eee;
        padding: 12px 5px;
        margin-bottom: 2px;
    }
    .main-text { font-size: 1.15rem; font-weight: 800; color: #000; margin-bottom: 2px; }
    .sub-text { font-size: 0.85rem; color: #666; margin-bottom: 5px; }
    .detail-text { font-size: 0.95rem; color: #333; }
    .label { color: #888; margin-right: 6px; font-weight: 500; font-size: 0.8rem; }
    .work-box { background: #f8f9fa; padding: 5px 8px; border-radius: 4px; margin-top: 5px; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 함수 (업로드한 파일명을 정확히 기입하세요)
@st.cache_data
def load_data():
    try:
        # 실제 파일명으로 수정 필요
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        return df.fillna('')
    except:
        st.error("데이터 파일을 찾을 수 없습니다. 파일명을 확인해 주세요.")
        return pd.DataFrame()

df = load_data()

# 3. 검색 UI (다중 키워드 즉시 필터링)
search = st.text_input("🔍 검색어 입력", placeholder="이름, 부서명, 내선번호, 업무내용 중 입력")

if search:
    mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    df = df[mask]

# 4. 6개 카테고리 탭 자동 분류
categories = ["전체", "총무", "지원", "시설", "보안/미화", "기타"]
tabs = st.tabs(categories)

for i, cat_name in enumerate(categories):
    with tabs[i]:
        # 카테고리 필터링 (보안/미화는 '보안' 또는 '미화' 포함 항목)
        if cat_name == "전체":
            display_df = df
        elif cat_name == "보안/미화":
            display_df = df[df['구분'].isin(['보안', '미화'])]
        else:
            display_df = df[df['구분'] == cat_name]

        if display_df.empty:
            st.caption("해당하는 정보가 없습니다.")
        
        for _, row in display_df.iterrows():
            with st.container():
                st.markdown('<div class="contact-card">', unsafe_allow_html=True)
                
                # [로직 1] 가변형 헤드라인: 담당자 이름 유무에 따른 처리
                if row['담당자'].strip():
                    st.markdown(f'<div class="main-text">{row["담당자"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="sub-text">{row["부서명"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="main-text">{row["부서명"]}</div>', unsafe_allow_html=True)
                
                # [로직 2] 연락처 포맷 최적화
                contacts = []
                if row['전화'].strip(): contacts.append(f"<span class='label'>내선</span>{row['전화']}")
                if row['휴대폰'].strip(): contacts.append(f"<span class='label'>직통</span>{row['휴대폰']}")
                
                if contacts:
                    st.markdown(f'<div class="detail-text">{" | ".join(contacts)}</div>', unsafe_allow_html=True)
                
                # [로직 3] 업무 내용 생략 로직
                if row['비고/업무'].strip():
                    st.markdown(f'<div class="work-box"><span class="label">업무</span>{row["비고/업무"]}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
