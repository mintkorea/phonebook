@st.cache_data
def get_clean_data():
    try:
        # 파일 확인
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        
        # 1. 데이터 읽기 (원본 컬럼명 무시하고 읽기 위해 header=0 권장)
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        
        # 2. 데이터 청소 (공백, 줄바꿈 제거)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', '', regex=True).replace(r'\r', '', regex=True))
        df = df.replace('nan', '')

        # 3. [핵심] 컬럼 개수 맞추기 (KeyError 방지)
        # 필요한 표준 컬럼 리스트
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        
        # 현재 데이터프레임의 열 개수가 부족하면 빈 열을 추가
        for i, col_name in enumerate(cols):
            if i < len(df.columns):
                # 기존 열이 있으면 이름만 변경
                df.rename(columns={df.columns[i]: col_name}, inplace=True)
            else:
                # 부족한 열은 빈 값으로 생성
                df[col_name] = ""
        
        # 4. 혹시 모를 열 순서 고정 및 초과 열 제거
        df = df[cols]
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()
