import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 고품격 현대적 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .block-container { padding: 1.5rem !important; background-color: #f8f9fa; font-family: 'Inter', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창 스타일링 */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 12px 20px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }

    /* 카드 컨테이너 */
    .contact-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #f0f0f0;
    }

    /* 업무 태그 (세련된 스타일) */
    .work-tag {
        display: inline-block;
        background-color: #fef2f2;
        color: #ef4444;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }

    .info-row { display: flex; justify-content: space-between; align-items: flex-end; }
    
    .name-text { font-size: 1.25rem; font-weight: 800; color: #1a1a1a; display: block; }
    .dept-text { font-size: 0.9rem; color: #6b7280; font-weight: 400; margin-top: 2px; }

    /* 버튼 그룹 */
    .btn-group { display: flex; gap: 10px; }
    .c-btn {
        padding: 10px 18px;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.2s;
        text-align: center;
    }
    .btn-tel { 
        background-color: #ffffff; 
        color: #4b5563 !important; 
        border: 1px solid #d1d5db; 
    }
    .btn-hp { 
        background-color: #1e293b; 
        color: #ffffff !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 탭 메뉴 스타일 살짝 보정 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 8px 16px;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-weight: 700;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (매핑 로직 유지)
@st.cache_data
def get_clean_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', '', regex=True).replace('nan', ''))
        
        mapping = {}
        for c in df.columns:
            if '구분' in c or '분류' in c: mapping['cat'] = c
            elif '부서' in c or '팀' in c: mapping['dept'] = c
            elif '성함' in c or '이름' in c or '성명' in c: mapping['name'] = c
            elif '내선' in c: mapping['tel'] = c
            elif '직통' in c or '휴대폰' in c or '전화' in c: mapping['hp'] = c
            elif '업무' in c or '비고' in c: mapping['work'] = c

        new_df = pd.DataFrame()
        new_df['c_cat'] = df[mapping.get('cat')] if 'cat' in mapping else pd.Series([""]*len(df))
        new_df['c_dept'] = df[mapping.get('dept')] if 'dept' in mapping else pd.Series([""]*len(df))
        new_df['c_name'] = df[mapping.get('name')] if 'name' in mapping else pd.Series([""]*len(df))
        new_df['c_tel'] = df[mapping.get('tel')] if 'tel' in mapping else pd.Series([""]*len(df))
        new_df['c_hp'] = df[mapping.get('hp')] if 'hp' in mapping else pd.Series([""]*len(df))
        new_df['c_work'] = df[mapping.get('work')] if 'work' in mapping else pd.Series([""]*len(df))
        return new_df
    except: return pd.DataFrame()

df = get_clean_data()

# 4. 검색창
q = st.text_input("", placeholder="🔍 찾으시는 담당자나 업무를 입력하세요", label_visibility="collapsed")

# 5. 메인 UI 렌더링
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_ui(target_df):
    if target_df.empty:
        st.caption("표시할 연락처가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        tel_num = re.sub(r'[^0-9]', '', row['c_tel'])
        hp_num = re.sub(r'[^0-9]', '', row['c_hp'])

        card_html = f"""
        <div class="contact-card">
            {f'<div class="work-tag">{wk}</div>' if wk else ''}
            <div class="info-row">
                <div>
                    <span class="name-text">{nm}</span>
                    <span class="dept-text">{dp}</span>
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
        cat = tab_list[i]
        d = df if cat == "전체" else df[df['c_cat'].str.contains(cat) | df['c_dept'].str.contains(cat)]
        if q:
            d = d[d.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(d)
