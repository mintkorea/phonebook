import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 고품격 현대적 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .block-container { padding: 1.5rem !important; background-color: #f8f9fa; font-family: 'Inter', sans-serif; }
    header, footer { visibility: hidden; }
    .stTextInput input { border-radius: 12px !important; border: 1px solid #e0e0e0 !important; padding: 12px 20px !important; }
    .contact-card { background: white; border-radius: 16px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }
    .work-tag { display: inline-block; background-color: #fef2f2; color: #ef4444; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; margin-bottom: 12px; }
    .info-row { display: flex; justify-content: space-between; align-items: flex-end; }
    .name-text { font-size: 1.25rem; font-weight: 800; color: #1a1a1a; }
    .dept-text { font-size: 0.9rem; color: #6b7280; margin-top: 2px; }
    .btn-group { display: flex; gap: 10px; }
    .c-btn { padding: 10px 18px; border-radius: 10px; text-decoration: none !important; font-size: 0.85rem; font-weight: 600; text-align: center; }
    .btn-tel { background-color: #ffffff; color: #4b5563 !important; border: 1px solid #d1d5db; }
    .btn-hp { background-color: #1e293b; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (구글 시트 URL 연동)
@st.cache_data(ttl=600) # 10분마다 데이터 자동 갱신
def get_google_sheet_data():
    # ⚠️ 여기에 구글 시트 [웹에 게시] 후 생성된 CSV 링크를 넣으세요
    # 테스트용으로 파일명을 넣었지만, 나중에 URL로 교체만 하면 됩니다.
    url = "성의교정 연락처.xlsx - Sheet1.csv" 
    
    try:
        df = pd.read_csv(url).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', '', regex=True).replace('nan', ''))
        
        # 열 이름 매핑 (업무내용, 성함 등 자동 찾기)
        mapping = {}
        for c in df.columns:
            if '구분' in c: mapping['cat'] = c
            elif '부서' in c: mapping['dept'] = c
            elif '성함' in c: mapping['name'] = c
            elif '내선' in c: mapping['tel'] = c
            elif '직통' in c or '휴대폰' in c: mapping['hp'] = c
            elif '업무' in c: mapping['work'] = c

        new_df = pd.DataFrame()
        new_df['c_cat'] = df[mapping.get('cat', df.columns[0])]
        new_df['c_dept'] = df[mapping.get('dept', df.columns[1])]
        new_df['c_name'] = df[mapping.get('name', df.columns[2])]
        new_df['c_tel'] = df[mapping.get('tel', df.columns[3])]
        new_df['c_hp'] = df[mapping.get('hp', df.columns[4])]
        new_df['c_work'] = df[mapping.get('work', df.columns[5])]
        return new_df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = get_google_sheet_data()

# 4. 상단 검색창
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용을 검색하세요", label_visibility="collapsed")

# 5. 메인 UI
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_ui(target_df):
    if target_df.empty:
        st.caption("표시할 연락처가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        # 데이터 추출 및 전화번호 정제
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        tel_num = re.sub(r'[^0-9]', '', str(row['c_tel']))
        hp_num = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 카드 렌더링
        card_html = f"""
        <div class="contact-card">
            {f'<div class="work-tag">{wk}</div>' if wk else ''}
            <div class="info-row">
                <div>
                    <span class="name-text">{nm if nm else dp}</span>
                    <span class="dept-text">{dp if nm else ""}</span>
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel_num}" class="c-btn btn-tel">내선</a>' if tel_num else ''}
                    {f'<a href="tel:{hp_num}" class="c-btn btn-hp">직통전화</a>' if hp_num else ''}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

for i, tab in enumerate(tabs):
    with tab:
        cat_name = tab_list[i]
        # 카테고리 필터링
        if cat_name == "전체":
            d = df
        else:
            d = df[df['c_cat'].str.contains(cat_name) | df['c_dept'].str.contains(cat_name)]
        
        # 검색 필터링
        if q:
            d = d[d.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
            
        render_ui(d)
