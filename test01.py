import streamlit as st
import pandas as pd

# 1. 데이터 로드 및 강제 교정 (에러 방지용)
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    # 우리가 사용할 표준 7개 컬럼 순서
    fixed_columns = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # engine='python'과 on_bad_lines='warn'으로 줄 수 불일치 에러를 방지합니다.
        df = pd.read_csv(file_path, engine='python', on_bad_lines='skip').fillna('')
        
        # 데이터가 밀리는 것을 방지하기 위해 강제로 7개 열만 선택하고 이름을 붙입니다.
        if len(df.columns) >= len(fixed_columns):
            df = df.iloc[:, :len(fixed_columns)]
            df.columns = fixed_columns
        
        # 텍스트 정제 (앞뒤 공백 제거)
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except Exception as e:
        st.error(f"⚠️ 데이터 읽기 오류: {e}")
        return None

df = load_data()

# 2. UI 및 카드형 검색 결과
st.set_page_config(page_title="성의교정 연락처", layout="wide")
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    search_term = st.text_input("🔍 부서, 성함 또는 업무 키워드(누수, 전기 등)를 입력하세요", "")

    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        res = df[mask]
        
        if not res.empty:
            for _, row in res.iterrows():
                with st.container():
                    # 부서명(2번째 칸)을 제목으로 강조
                    st.markdown(f"### 📍 {row['부서_업체명']}")
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1: st.write(f"👤 **담당**: {row['성명']} {row['직함']}")
                    with c2: st.write(f"📞 **내선**: {row['내선_일반']}")
                    with c3: st.write(f"📱 **휴대폰**: {row['휴대폰']}")
                    st.info(f"📝 **업무**: {row['담당업무_비고']}")
                    st.divider()
        else:
            st.warning("검색 결과가 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)
