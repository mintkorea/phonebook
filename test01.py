import streamlit as st
import pandas as pd

# 1. 데이터 로드 및 강제 교정
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    fixed_columns = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # 쉼표 밀림 방지를 위해 engine='python' 사용
        df = pd.read_csv(file_path, engine='python', on_bad_lines='skip').fillna('')
        
        # 데이터가 밀리는 것을 방지하기 위해 7개 열만 선택
        if len(df.columns) >= len(fixed_columns):
            df = df.iloc[:, :len(fixed_columns)]
            df.columns = fixed_columns
        
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 오류: {e}")
        return None

df = load_data()

# 2. UI 설정
st.set_page_config(page_title="성의교정 연락처", layout="wide")
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    # 검색 기능
    search_term = st.text_input("🔍 검색어(부서, 성함, 업무 등)를 입력하세요", "")

    if search_term:
        # 검색 모드: 검색어가 있을 때는 탭 무시하고 결과 출력
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        res = df[mask]
        st.subheader(f"🔍 '{search_term}' 검색 결과 ({len(res)}건)")
    else:
        # 탭 모드: 검색어가 없을 때 카테고리별로 분류
        categories = df['카테고리'].unique().tolist()
        tabs = st.tabs(categories)
        
        for i, cat in enumerate(categories):
            with tabs[i]:
                res = df[df['카테고리'] == cat]
                
    # 카드형 출력 로직
    if 'res' in locals() and not res.empty:
        for _, row in res.iterrows():
            with st.container():
                # 부서명을 상단에 크게 배치하여 가독성 확보
                st.markdown(f"### 📍 {row['부서_업체명']}")
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1: st.write(f"👤 **담당**: {row['성명']} {row['직함']}")
                with c2: st.write(f"📞 **내선**: {row['내선_일반']}")
                with c3: st.write(f"📱 **휴대폰**: {row['휴대폰']}")
                st.info(f"📝 **업무**: {row['담당업무_비고']}")
                st.divider()
    elif search_term:
        st.warning("검색 결과가 없습니다.")
