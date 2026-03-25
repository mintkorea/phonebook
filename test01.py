import streamlit as st
import pandas as pd

# 1. 데이터 로드 및 강제 정렬
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    # 정확한 데이터 추출을 위한 표준 컬럼 정의
    column_names = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # 데이터가 밀리지 않도록 설정
        df = pd.read_csv(file_path, names=column_names, header=0).fillna('')
        # 모든 공백 제거하여 매칭 정확도 향상
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        st.error(f"⚠️ 파일 로딩 실패: {e}")
        return None

df = load_data()

# 2. UI 설정
st.set_page_config(page_title="성의교정 연락처", layout="wide")
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    # 검색창 강조
    search_term = st.text_input("🔍 찾으시는 부서, 성함 또는 업무 키워드를 입력하세요 (예: 누수, 전기, 총무)", "")

    if search_term:
        # 전체 행에서 검색어 포함 여부 확인
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        result_df = df[mask]
        
        if not result_df.empty:
            st.success(f"✅ 총 {len(result_df)}건의 연락처를 찾았습니다.")
            
            # 카드형 레이아웃 출력
            for _, row in result_df.iterrows():
                # 부서 이름과 성명을 제목으로 강조
                dept = row['부서_업체명']
                name_info = f"{row['성명']} {row['직함']}".strip()
                
                with st.container():
                    # 부서명을 상단에 크게 표시
                    st.markdown(f"### 📍 {dept}") 
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        st.write(f"👤 **담당자**: {name_info if name_info else '부서 공용'}")
                    with col2:
                        # 전화번호 하이퍼링크 처리 (모바일 클릭 시 바로 전화 연결)
                        tel = row['내선_일반']
                        st.write(f"📞 **내선**: [{tel}](tel:{tel})")
                    with col3:
                        mobile = row['휴대폰']
                        st.write(f"📱 **휴대폰**: [{mobile}](tel:{mobile})")
                    
                    # 업무 상세 내용 강조
                    st.info(f"📝 **담당 업무**: {row['담당업무_비고']}")
                    st.divider() # 카드 구분선
        else:
            st.warning("🧐 검색 결과가 없습니다. 다른 키워드로 검색해 보세요.")
    else:
        st.info("💡 키워드를 입력하면 상세 카드가 나타납니다. 아래는 전체 목록입니다.")
        st.dataframe(df, use_container_width=True)
