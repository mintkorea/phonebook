import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="성의교정 연락처 검색", layout="wide")

# 2. 데이터 로드 및 강제 교정 함수
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    # 데이터 밀림 방지를 위한 표준 7개 컬럼 정의
    fixed_columns = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # header=0으로 기존 헤더를 무시하고, names로 우리가 정의한 컬럼명을 강제 할당합니다.
        # engine='python'과 on_bad_lines='skip'은 쉼표 오류로 인한 실행 중단을 방지합니다.
        df = pd.read_csv(file_path, names=fixed_columns, header=0, engine='python', on_bad_lines='skip').fillna('')
        
        # 데이터가 오른쪽으로 밀리는 것을 방지하기 위해 앞의 7개 열만 선택
        df = df.iloc[:, :7]
        
        # 모든 텍스트의 앞뒤 공백 제거
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 중 오류 발생: {e}")
        return None

df = load_data()

# 3. 메인 UI
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    # 검색창
    search_term = st.text_input("🔍 검색어(부서명, 성함, 업무 키워드)를 입력하세요", "")

    if search_term:
        # 검색어가 있을 경우 전체 데이터에서 필터링
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        res = df[mask]
        st.subheader(f"✅ '{search_term}' 검색 결과 ({len(res)}건)")
        
        # 검색 결과 카드 출력
        for _, row in res.iterrows():
            with st.container():
                st.markdown(f"### 📍 {row['부서_업체명']}")
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1: st.write(f"👤 **담당**: {row['성명']} {row['직함']}")
                with c2: st.write(f"📞 **내선**: {row['내선_일반']}")
                with c3: st.write(f"📱 **휴대폰**: {row['휴대폰']}")
                st.info(f"📝 **업무**: {row['담당업무_비고']}")
                st.divider()
    else:
        # 검색어가 없을 경우 카테고리별 탭 표시
        categories = df['카테고리'].unique().tolist()
        if categories:
            tabs = st.tabs(categories)
            for i, cat in enumerate(categories):
                with tabs[i]:
                    cat_df = df[df['카테고리'] == cat]
                    for _, row in cat_df.iterrows():
                        with st.container():
                            # 부서명 강조
                            st.markdown(f"### 📍 {row['부서_업체명']}")
                            c1, c2, c3 = st.columns([1, 1, 2])
                            with c1: st.write(f"👤 **담당**: {row['성명']} {row['직함']}")
                            with c2: st.write(f"📞 **내선**: {row['내선_일반']}")
                            with c3: st.write(f"📱 **휴대폰**: {row['휴대폰']}")
                            st.info(f"📝 **업무**: {row['담당업무_비고']}")
                            st.divider()
        else:
            st.warning("표시할 데이터가 없습니다. CSV 파일을 확인해주세요.")
