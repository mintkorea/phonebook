import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 고급스러운 Light Navy & Minimal UI (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    .block-container { padding: 1rem 2rem !important; background-color: #fcfcfc; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 부드러운 네이비 포커스 */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 10px 15px !important;
        font-size: 0.95rem !important;
    }
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    }

    /* 연락처 카드: 연한 네이비 포인트 */
    .contact-card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* 업무 태그: 연한 네이비 (요청 사항 반영) */
    .work-tag {
        display: inline-block;
        background-color: #eff6ff; /* 매우 연한 파랑/네이비 */
        color: #1e40af; /* 신뢰감 있는 네이비 */
        padding: 3px 10px;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 10px;
        border: 1px solid #dbeafe;
    }

    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.2rem; font-weight: 800; color: #1e293b; }
    .dept-text { font-size: 0.85rem; color: #64748b; margin-left: 5px; }

    /* 버튼 그룹: 미니멀 네이비 스타일 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 8px 14px;
        border-radius: 8px;
        text-decoration: none !important;
        font-size: 0.82rem;
        font-weight: 700;
        transition: 0.2s;
    }
    .btn-tel { background-color: #f8fafc; color: #475569 !important; border: 1px solid #e2e8f0; }
    .btn-hp { background-color: #1e293b; color: #ffffff !important; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [aria-selected="true"] { color: #1e40af !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (오타 수정: except Exception)
@st.cache_data(ttl=300)
def get_live_data():
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(SHEET_URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        # 열 이름 강제 매핑
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except Exception as e: # [수정완료] 공백 추가
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 검색
q = st.text_input("", placeholder="🔍 담당자, 부서, 업무 검색...", label_visibility="collapsed")

# 5. 메인 UI
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df):
    if target_df.empty:
        st.info("검색 결과가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        # 번호 정제
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        st.markdown(f"""
            <div class="contact-card">
                {f'<div class="work-tag">{wk}</div>' if wk else ''}
                <div class="info-row">
                    <div>
                        <span class="name-text">{nm}</span>
                        <span class="dept-text">{dp}</span>
                    </div>
                    <div class="btn-group">
                        {f'<a href="tel:{tel_link}" class="c-btn btn-tel">내선</a>' if tel_link else ''}
                        {f'<a href="tel:{hp_link}" class="c-btn btn-hp">직통</a>' if hp_link else ''}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 6. 필터 및 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        if category == "전체":
            filtered = df
        else:
            filtered = df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_ui(filtered)
