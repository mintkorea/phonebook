import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 디자인 (CSS) - 생략 없이 유지
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    .block-container { padding: 1rem !important; background-color: #f9fafb; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    .stTextInput input { border-radius: 14px !important; border: 1px solid #e5e7eb !important; padding: 12px 20px !important; }
    .contact-card { background: white; border-radius: 18px; padding: 20px; margin-bottom: 12px; border: 1px solid #f3f4f6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .work-tag { display: inline-block; background-color: #fef2f2; color: #dc2626; padding: 4px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; margin-bottom: 12px; border: 1px solid #fee2e2; }
    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.3rem; font-weight: 800; color: #111827; }
    .dept-text { font-size: 0.9rem; color: #6b7280; font-weight: 500; }
    .btn-group { display: flex; gap: 8px; }
    .c-btn { display: flex; align-items: center; justify-content: center; padding: 10px 16px; border-radius: 10px; text-decoration: none !important; font-size: 0.85rem; font-weight: 700; min-width: 65px; }
    .btn-tel { background-color: #f3f4f6; color: #374151 !important; border: 1px solid #e5e7eb; }
    .btn-hp { background-color: #0f172a; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (인덱스 기반 안전 장치 추가)
@st.cache_data(ttl=300)
def get_live_data():
    # ⚠️ 여기에 구글 시트 웹에 게시(CSV) 주소를 꼭 넣으세요!
    SHEET_URL = "https://docs.google.com/spreadsheets/d/19OdXrE8_CmLxBLeohVLFi8sFZIznfoKFRQAVZBH_6fE/edit?usp=sharing" 
    
    try:
        df = pd.read_csv(SHEET_URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))

        # [해결책] 열 이름이 '구분', '부서'가 아닐 경우를 대비해 표준화
        # 0:구분, 1:부서, 2:성함, 3:내선, 4:직통, 5:업무내용 순서라고 가정
        new_cols = ['구분', '부서', '성함', '내선', '직통', '업무내용']
        
        # 현재 읽어온 데이터프레임의 열 개수만큼 이름을 강제로 바꿈
        temp_dict = {df.columns[i]: new_cols[i] for i in range(min(len(df.columns), len(new_cols)))}
        df = df.rename(columns=temp_dict)
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = get_live_data()

# 4. 검색창
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용 검색", label_visibility="collapsed")

# 5. 탭 구성
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_cards(target_df):
    if target_df.empty:
        st.info("조건에 맞는 연락처가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        # 열 이름을 못 찾아도 에러 안 나게 .get() 사용
        cat = row.get('구분', '')
        dept = row.get('부서', '')
        name = row.get('성함', '')
        tel = re.sub(r'[^0-9*]', '', str(row.get('내선', '')))
        hp = re.sub(r'[^0-9]', '', str(row.get('직통', '')))
        work = row.get('업무내용', '')

        nm = name if name else dept
        dp = dept if name else ""

        st.markdown(f"""
        <div class="contact-card">
            {f'<div class="work-tag">{work}</div>' if work else ''}
            <div class="info-row">
                <div><span class="name-text">{nm}</span><span class="dept-text">{dp}</span></div>
                <div class="btn-group">
                    {f'<a href="tel:{tel}" class="c-btn btn-tel">내선</a>' if tel else ''}
                    {f'<a href="tel:{hp}" class="c-btn btn-hp">직통전화</a>' if hp else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 6. 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        
        # '구분' 또는 '부서' 열이 존재하는지 확인 후 필터링
        if category == "전체":
            filtered = df
        else:
            # 안전한 필터링 (열 이름 체크)
            col_list = df.columns.tolist()
            mask = pd.Series([False] * len(df))
            if '구분' in col_list: mask |= df['구분'].str.contains(category, na=False)
            if '부서' in col_list: mask |= df['부서'].str.contains(category, na=False)
            filtered = df[mask]
        
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_cards(filtered)
