import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 기본 디자인(CSS) 적용
st.set_page_config(page_title="성의교정 연락처 검색", layout="wide")

st.markdown("""
    <style>
    /* 전체 기본 폰트 사이즈 조정 */
    html, body, [class*="st-"] {
        font-size: 16px;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    /* 부서명 스타일: 기본보다 2단계 크게 (h3 수준) */
    .dept-title {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    /* 성명 스타일: 기본보다 크게 */
    .name-text {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #374151;
    }
    /* 카드 컨테이너 여백 */
    .contact-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 강제 교정 함수
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    # 7개 표준 컬럼 강제 정의
    fixed_columns = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # 데이터 밀림 방지를 위해 names 할당 및 iloc 슬라이싱
        df = pd.read_csv(file_path, names=fixed_columns, header=0, engine='python', on_bad_lines='skip').fillna('')
        df = df.iloc[:, :7] 
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 중 오류 발생: {e}")
        return None

df = load_data()

# 3. 메인 UI
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    search_term = st.text_input("🔍 검색어(부서명, 성함, 업무 키워드)를 입력하세요", "")

    # 검색 결과 또는 탭 데이터 추출
    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        display_df = df[mask]
        st.subheader(f"✅ '{search_term}' 검색 결과 ({len(display_df)}건)")
    else:
        categories = df['카테고리'].unique().tolist()
        if categories:
            tabs = st.tabs(categories)
            selected_tab_index = 0 # 기본값
            # 탭별 데이터 처리는 아래 루프에서 진행
        else:
            st.warning("표시할 데이터가 없습니다.")
            display_df = pd.DataFrame()

    # 데이터 출력 로직 (검색어 유무에 따른 분기)
    def render_cards(data):
        for _, row in data.iterrows():
            with st.container():
                # HTML을 사용하여 부서명과 성명 폰트 크기 조절
                st.markdown(f'<div class="dept-title">📍 {row["부서_업체명"]}</div>', unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    name_display = f"{row['성명']} {row['직함']}".strip()
                    st.markdown(f'👤 <span class="name-text">{name_display if name_display else "정보 없음"}</span>', unsafe_allow_html=True)
                with c2:
                    st.write(f"📞 **내선**: {row['내선_일반']}")
                with c3:
                    st.write(f"📱 **휴대폰**: {row['휴대폰']}")
                
                st.info(f"📝 **업무**: {row['담당업무_비고']}")
                st.divider()

    if search_term:
        render_cards(display_df)
    elif 'tabs' in locals():
        for i, cat in enumerate(categories):
            with tabs[i]:
                render_cards(df[df['카테고리'] == cat])
