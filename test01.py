import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    file_path = 'contacts.csv'
    # 우리가 사용할 표준 7개 컬럼
    fixed_columns = ['카테고리', '부서_업체명', '성명', '직함', '내선_일반', '휴대폰', '담당업무_비고']
    
    try:
        # on_bad_lines='skip'을 추가하여 형식이 틀린 줄은 건너뜁니다.
        # 혹은 engine='python'을 사용하여 유연하게 읽어옵니다.
        df = pd.read_csv(file_path, on_bad_lines='warn', engine='python').fillna('')
        
        # 데이터가 오른쪽으로 밀리는 것을 방지하기 위해 앞의 7개 열만 선택
        if len(df.columns) > len(fixed_columns):
            df = df.iloc[:, :len(fixed_columns)]
        
        df.columns = fixed_columns
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    except Exception as e:
        st.error(f"⚠️ 데이터 읽기 오류: {e}")
        return None

df = load_data()

# 이하 UI 및 카드 출력 로직 (동일)
