import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 디자인(CSS)
st.set_page_config(page_title="성의교정 연락처 검색", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 16px;
        font-family: 'Pretendard', sans-serif;
    }
    .dept-title {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .name-text {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #374151;
    }
    /* 안내 문구 스타일 */
    .info-box {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #3B82F6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (컬럼 강제 고정 및 밀림 방지)
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    fixed_columns = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    try:
        df = pd.read_csv(file_path, names=fixed_columns, header=0, engine='python', on_bad_lines='skip').fillna('')
        df = df.iloc[:, :7] 
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 오류: {e}")
        return None

df = load_data()

# 3. 카드 렌더링 함수 (휴대폰 유무 로직 포함)
def render_contact_cards(data):
    for _, row in data.iterrows():
        with st.container():
            # 부서명 출력 (2폰트 크게)
            st.markdown(f'<div class="dept-title">📍 {row["부서_업체명"]}</div>', unsafe_allow_html=True)
            
            has_mobile = str(row['휴대폰']).strip() != ""
            
            if has_mobile:
                # 휴대폰이 있는 경우: 기존 3단 배열
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    name_label = f"{row['성명']} {row['직함']}".strip()
                    st.markdown(f'👤 <span class="name-text">{name_label if name_label else "담당자"}</span>', unsafe_allow_html=True)
                with c2:
                    st.write(f"📞 **내선**: {row['내선_일반']}")
                with c3:
                    st.write(f"📱 **휴대폰**: {row['휴대폰']}")
            else:
                # 휴대폰이 없는 경우: 내선과 업무만 강조하는 2단 배열
                c1, c2 = st.columns([1, 3])
                with c1:
                    name_label = f"{row['성명']} {row['직함']}".strip()
                    st.markdown(f'👤 <span class="name-text">{name_label if name_label else "담당부서"}</span>', unsafe_allow_html=True)
                with c2:
                    st.write(f"📞 **내선 연락처**: {row['내선_일반']}")
            
            # 담당 업무 (항상 강조)
            st.info(f"📝 **담당 업무**: {row['담당업무_비고']}")
            st.divider()

# 4. 메인 UI 출력
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    search_term = st.text_input("🔍 부서, 성함 또는 업무 키워드를 입력하세요", "")

    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        res = df[mask]
        st.subheader(f"✅ 검색 결과 ({len(res)}건)")
        render_contact_cards(res)
    else:
        # 카테고리별 탭 구성
        categories = df['카테고리'].unique().tolist()
        if categories:
            tabs = st.tabs(categories)
            for i, cat in enumerate(categories):
                with tabs[i]:
                    render_contact_cards(df[df['카테고리'] == cat])
