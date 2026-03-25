import streamlit as st
import pandas as pd

# 1. 데이터 로드 (에러 방지를 위해 열 이름을 강제로 지정)
@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    # CSV 파일의 헤더 순서와 일치해야 합니다.
    column_names = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # header=0은 파일의 첫 줄을 무시하고 names에 지정된 이름을 사용한다는 뜻입니다.
        df = pd.read_csv(file_path, names=column_names, header=0).fillna('')
        return df
    except FileNotFoundError:
        st.error(f"⚠️ '{file_path}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"⚠️ 데이터 로딩 중 오류 발생: {e}")
        return None

df = load_data()

# 2. UI 구성
st.set_page_config(page_title="성의교정 연락처", page_icon="🏢")
st.title("🏢 성의교정 통합 연락처 검색")

if df is not None:
    # 검색창
    search_term = st.text_input("부서, 성명 또는 키워드(예: 누수, 정수기)를 입력하세요", "")

    # 3. 검색 로직 (전체 텍스트 검색)
    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        result_df = df[mask]
        
        # 4. 결과 출력 (카드형 레이아웃)
        if not result_df.empty:
            st.success(f"총 {len(result_df)}건의 검색 결과가 있습니다.")
            
            # 각 행을 카드로 시각화
            for i, row in result_df.iterrows():
                # iloc를 사용하여 열 이름 오류 방지 (1:부서, 2:성명, 3:직함)
                department = row.iloc[1] 
                name = row.iloc[2]
                position = row.iloc[3]
                
                # 카드 제목 구성 (부서명 - 성명 직함)
                card_title = f"📌 {department} - {name} {position}" if name else f"📌 {department}"
                
                with st.expander(card_title, expanded=True): # expanded=True로 기본으로 펼쳐둠
                    # 내부 콘텐츠 구성 (4:내선, 5:휴대폰, 6:업무)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**📞 내선/일반:** {row.iloc[4]}")
                    with c2:
                        st.write(f"**📱 휴대폰:** {row.iloc[5]}")
                    
                    # 담당업무 및 비고 (가장 중요한 키워드)
                    st.info(f"**📝 담당업무 및 비고:** {row.iloc[6]}")
                    
        else:
            st.warning("검색 결과가 없습니다. 키워드를 확인해 주세요.")
    else:
        st.info("검색어를 입력하시면 상세 연락처를 확인하실 수 있습니다.")
        # 초기 화면에는 전체 데이터프레임을 보여줌
        st.dataframe(df, use_container_width=True)

else:
    st.warning("데이터를 불러올 수 없습니다. CSV 파일을 확인해 주세요.")
