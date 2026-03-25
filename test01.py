import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub - 봄 에디션", layout="wide")

# 2. 봄 테마 UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 전체 배경: 아주 연한 벚꽃 핑크색 */
    .block-container { padding: 1.5rem 2rem !important; background-color: #fff9fb; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 둥글고 화사하게 */
    .stTextInput input {
        border-radius: 20px !important;
        border: 1px solid #ffd1dc !important;
        padding: 10px 20px !important;
        background-color: white !important;
    }

    /* 연락처 카드: 그림자 대신 은은한 선 */
    .contact-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid #ffe4e6;
        box-shadow: 0 2px 8px rgba(255, 209, 220, 0.2);
    }

    .info-row { display: flex; justify-content: space-between; align-items: center; }
    
    /* 성함과 부서 */
    .name-text { font-size: 1.25rem; font-weight: 800; color: #4a5568; }
    .dept-text { font-size: 0.9rem; color: #a0aec0; margin-left: 6px; font-weight: 400; }

    /* [요청사항 반영] 업무내용: 배경 없이 이름 아래에 텍스트로만 */
    .work-desc {
        font-size: 0.85rem;
        color: #718096; /* 차분한 그레이 */
        margin-top: 6px;
        line-height: 1.4;
        font-weight: 500;
    }

    /* 버튼: 연한 네이비와 핑크 포인트 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 8px 16px;
        border-radius: 12px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 700;
        transition: 0.2s;
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; border: 1px solid #e2e8f0; }
    .btn-hp { background-color: #64748b; color: #ffffff !important; } /* 연한 네이비 계열 */
    
    /* 탭 스타일: 핑크 포인트 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] { color: #ff69b4 !important; font-weight: 800 !important; border-bottom-color: #ff69b4 !important; }
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
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 검색
q = st.text_input("", placeholder="🔍 봄바람 타고 누구를 찾으시나요?", label_visibility="collapsed")

# 5. 메인 UI
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df):
    if target_df.empty:
        st.info("찾으시는 연락처가 없네요. 🌸")
        return
        
    for _, row in target_df.iterrows():
        # 데이터 정리
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 카드 렌더링 (순서 변경: 이름/부서 -> 업무내용)
        st.markdown(f"""
            <div class="contact-card">
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
