import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    # CSV 파일을 불러올 때 헤더 이름을 강제로 지정하여 KeyError를 방지합니다.
    column_names = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    try:
        # header=0은 파일의 첫 줄을 무시하고 names에 지정된 이름을 사용한다는 뜻입니다.
        df = pd.read_csv('contacts.csv', names=column_names, header=0).fillna('')
        return df
    except Exception as e:
        st.error(f"파일 로딩 중 오류 발생: {e}")
        return None

df = load_data()

if df is not None:
    st.title("🏢 성의교정 통합 연락처 검색")
    search_term = st.text_input("부서, 성명 또는 키워드(예: 누수, 정수기)를 입력하세요", "")

    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        result_df = df[mask]
        
        if not result_df.empty:
            st.success(f"총 {len(result_df)}건의 검색 결과가 있습니다.")
            for i, row in result_df.iterrows():
                # 열 이름을 안전하게 가져오기 위해 인덱스 번호를 사용할 수도 있습니다.
                title = f"📌 {row.iloc[1]} - {row.iloc[2]} {row.iloc[3]}"
                with st.expander(title):
                    st.write(f"**📞 내선/일반:** {row.iloc[4]}")
                    st.write(f"**📱 휴대폰:** {row.iloc[5]}")
                    # 오류가 났던 '담당업무_비고' 부분
                    st.info(f"**📝 담당업무:** {row.iloc[6]}") 
        else:
            st.warning("검색 결과가 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)
