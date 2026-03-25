import streamlit as st
import pandas as pd

# 1. 데이터 로드 (앞서 정리한 CSV 파일을 'contacts.csv'로 저장했다고 가정)
@st.cache_data
def load_data():
    # 데이터프레임을 불러오고 모든 컬럼을 문자열로 처리하여 검색 효율을 높임
    df = pd.read_csv('contacts.csv').fillna('')
    return df

df = load_data()

# 2. 검색 UI 구성
st.title("🏢 성의교정 통합 연락처 검색")
search_term = st.text_input("부서, 성명 또는 담당업무(예: 정수기, 승강기)를 입력하세요", "")

# 3. 검색 로직 (모든 열을 대상으로 검색)
if search_term:
    # 각 행에서 검색어가 포함된 데이터가 있는지 확인
    mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    result_df = df[mask]
    
    # 4. 결과 출력
    if not result_df.empty:
        st.success(f"총 {len(result_df)}건의 검색 결과가 있습니다.")
        
        # 모바일에서도 보기 편하도록 카드로 출력하거나 테이블로 출력
        for i, row in result_df.iterrows():
            with st.expander(f"📌 {row['부서_업체명']} - {row['성명']} {row['직함']}"):
                st.write(f"**📍 카테고리:** {row['카테고리']}")
                st.write(f"**📞 내선/일반:** {row['내선_일반']}")
                st.write(f"**📱 휴대폰:** {row['휴대폰']}")
                st.info(f"**📝 담당업무:** {row['담당업무_비고']}")
    else:
        st.warning("검색 결과가 없습니다. 키워드를 확인해 주세요.")
else:
    st.info("검색어를 입력하시면 상세 연락처를 확인하실 수 있습니다.")
    # 초기 화면에는 전체 표를 보여줌
    st.dataframe(df, use_container_width=True)
