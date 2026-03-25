import streamlit as st
import pandas as pd
import io

# 1. 데이터 로드 및 강제 교정
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    # 우리가 사용할 표준 컬럼 순서
    fixed_columns = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # 쉼표가 너무 많거나 적어서 밀리는 현상을 방지하기 위해 header=0으로 읽은 후 컬럼 강제 재지정
        df = pd.read_csv(file_path).fillna('')
        
        # 만약 실제 파일의 컬럼 수가 우리가 정의한 것보다 많으면 앞부분만 사용
        if len(df.columns) >= len(fixed_columns):
            df = df.iloc[:, :len(fixed_columns)]
            df.columns = fixed_columns
        else:
            # 컬럼 수가 부족할 경우 에러 방지용 재정의
            df = pd.read_csv(file_path, names=fixed_columns, header=0).fillna('')
            
        # 모든 텍스트의 앞뒤 공백 제거
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except Exception as e:
        st.error(f"⚠️ 데이터 정렬 오류: {e}")
        return None

df = load_data()

# 2. UI 및 카드형 검색 결과
st.set_page_config(page_title="성의교정 연락처 검색", layout="wide")
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    search_term = st.text_input("🔍 부서, 성함 또는 업무 키워드(누수, 전기 등)를 입력하세요", "")

    if search_term:
        # 전체 행 검색
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        result_df = df[mask]
        
        if not result_df.empty:
            st.success(f"✅ 총 {len(result_df)}건의 결과를 찾았습니다.")
            for _, row in result_df.iterrows():
                # 데이터 밀림 현상을 고려하여 명확하게 변수 할당
                dept = row['부서_업체명']
                name = f"{row['성명']} {row['직함']}".strip()
                
                # 카드 상단: 부서명 강조
                with st.container():
                    st.markdown(f"### 📍 {dept}")
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1:
                        st.write(f"👤 **담당자**: {name if name else '정보 없음'}")
                    with c2:
                        st.write(f"📞 **내선**: {row['내선_일반']}")
                    with c3:
                        st.write(f"📱 **휴대폰**: {row['휴대폰']}")
                    
                    # 담당업무를 시각적으로 분리하여 강조
                    st.info(f"📝 **담당 업무**: {row['담당업무_비고']}")
                    st.divider()
        else:
            st.warning("검색 결과가 없습니다.")
    else:
        st.info("검색어를 입력하면 상세 연락처 카드가 나타납니다.")
        st.dataframe(df, use_container_width=True)
