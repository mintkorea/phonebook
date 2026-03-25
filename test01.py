import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 배경색을 모두 제거한 미니멀 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 전체 배경을 완전 흰색으로 고정 */
    .block-container { padding: 1.5rem 2rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 배경 없이 선으로만 강조 */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #f0f0f0 !important;
        padding: 12px 18px !important;
        background-color: #fafafa !important;
    }

    /* 연락처 아이템: 카드 배경을 빼고 구분선으로만 처리 */
    .contact-item {
        padding: 20px 5px;
        border-bottom: 1px solid #f8f8f8; /* 아주 연한 구분선 */
        background: none;
    }
    
    .info-row { display: flex; justify-content: space-between; align-items: center; }
    
    /* 이름과 부서 */
    .name-text { font-size: 1.2rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; margin-left: 6px; font-weight: 400; }

    /* [요청사항] 업무내용: 이름 아래 배경 없이 텍스트로만 */
    .work-desc {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
        line-height: 1.4;
    }

    /* 버튼: 연한 네이비/그레이 조합 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 8px 16px;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #1e293b; color: #ffffff !important; }
    
    /* 탭 스타일: 핑크 포인트만 살짝 유지 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] { color: #f472b6 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=300)
def get_live_data():
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(SHEET_URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except Exception as e:
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 검색
q = st.text_input("", placeholder="🔍 성함 또는 부서 검색", label_visibility="collapsed")

# 5. 메인 UI
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 배경색 없이 선으로 구분된 리스트 아이템
        st.markdown(f"""
            <div class="contact-item">
                <div class="info-row">
                    <div>
                        <div>
                            <span class="name-text">{nm}</span>
                            <span class="dept-text">{dp}</span>
                        </div>
                        {f'<div class="work-desc">{wk}</div>' if wk else ''}
                    </div>
                    <div class="btn-group">
                        {f'<a href="tel:{tel_link}" class="c-btn btn-tel">내선</a>' if tel_link else ''}
                        {f'<a href="tel:{hp_link}" class="c-btn btn-hp">직통</a>' if hp_link else ''}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 6. 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_names[i]
        filtered = df if cat == "전체" else df[df['c_cat'].str.contains(cat, na=False) | df['c_dept'].str.contains(cat, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered)
