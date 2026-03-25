import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. CSS 디자인 (HTML 노출 방지를 위해 스타일 보강)
st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    header, footer { visibility: hidden; }
    .stTextInput input { border: 2px solid #000 !important; }
    
    .contact-card {
        border-bottom: 1px solid #eee;
        padding: 12px 0;
        margin-bottom: 5px;
    }
    .work-tag {
        background-color: #fff0f0; color: #d32f2f; padding: 2px 8px;
        border-radius: 4px; font-size: 0.85rem; font-weight: 800;
        margin-bottom: 6px; display: inline-block; border: 1px solid #ffcccc;
    }
    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #000; }
    .dept-text { font-size: 0.85rem; color: #666; margin-left: 5px; }
    
    .btn-group { display: flex; gap: 6px; }
    .c-btn {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 4px;
        text-decoration: none !important;
        font-size: 0.8rem;
        font-weight: 700;
        text-align: center;
        min-width: 50px;
    }
    .btn-tel { background-color: #f0f0f0; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (열 이름 자동 매핑)
@st.cache_data
def get_clean_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', '', regex=True).replace('nan', ''))

        # [수정] 열 이름을 순서가 아닌 '포함된 단어'로 찾기 (더 정확함)
        mapping = {}
        cols = df.columns.tolist()
        
        # 각 열의 의미를 유추해서 매핑
        for c in cols:
            if '구분' in c or '분류' in c: mapping['cat'] = c
            elif '부서' in c or '팀' in c: mapping['dept'] = c
            elif '성함' in c or '이름' in c or '성명' in c: mapping['name'] = c
            elif '내선' in c: mapping['tel'] = c
            elif '직통' in c or '휴대폰' in c or '전화' in c: mapping['hp'] = c
            elif '업무' in c or '비고' in c: mapping['work'] = c

        # 매핑된 대로 표준 컬럼명 적용
        new_df = pd.DataFrame()
        new_df['c_cat'] = df[mapping['cat']] if 'cat' in mapping else pd.Series([""]*len(df))
        new_df['c_dept'] = df[mapping['dept']] if 'dept' in mapping else pd.Series([""]*len(df))
        new_df['c_name'] = df[mapping['name']] if 'name' in mapping else pd.Series([""]*len(df))
        new_df['c_tel'] = df[mapping['tel']] if 'tel' in mapping else pd.Series([""]*len(df))
        new_df['c_hp'] = df[mapping['hp']] if 'hp' in mapping else pd.Series([""]*len(df))
        new_df['c_work'] = df[mapping['work']] if 'work' in mapping else pd.Series([""]*len(df))
        
        return new_df
    except:
        return pd.DataFrame()

df = get_clean_data()

# 4. 검색창
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용 검색", label_visibility="collapsed")

# 5. 메인 로직
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_ui(target_df):
    if target_df.empty:
        st.caption("데이터가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        # 데이터 정리
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        # 전화번호 정제 (숫자만 추출)
        tel_num = re.sub(r'[^0-9]', '', row['c_tel'])
        hp_num = re.sub(r'[^0-9]', '', row['c_hp'])

        # 카드 렌더링 (st.markdown 하나로 묶어서 렌더링 오류 방지)
        card_html = f"""
        <div class="contact-card">
            {f'<div class="work-tag">업무: {wk}</div>' if wk else ''}
            <div class="info-row">
                <div>
                    <span class="name-text">{nm}</span>
                    <span class="dept-text">{dp}</span>
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel_num}" class="c-btn btn-tel">내선</a>' if tel_num else ''}
                    {f'<a href="tel:{hp_num}" class="c-btn btn-hp">직통</a>' if hp_num else ''}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        d = df if cat == "전체" else df[df['c_cat'].str.contains(cat) | df['c_dept'].str.contains(cat)]
        if q:
            d = d[d.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(d)
