import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 고급스러운 모던 리스트 UI (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 배경 및 기본 폰트 */
    .block-container { padding: 1.5rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 얇은 보더와 아이콘 느낌 */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #f0f0f0 !important;
        background-color: #f8f9fa !important;
        padding: 12px 15px !important;
        font-size: 1rem !important;
    }

    /* 리스트 스타일 (카드 대신 선으로 구분) */
    .contact-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 5px;
        border-bottom: 1px solid #f1f1f1;
    }
    
    .info-group { display: flex; flex-direction: column; gap: 4px; }
    
    /* 업무 내용: 이름 위에 작고 단정하게 */
    .work-text {
        font-size: 0.75rem;
        font-weight: 700;
        color: #e11d48; /* 세련된 레드 포인트 */
        margin-bottom: -2px;
    }
    
    .name-text { font-size: 1.15rem; font-weight: 700; color: #1a1a1a; }
    .dept-text { font-size: 0.85rem; color: #888; margin-left: 6px; font-weight: 400; }

    /* 버튼: 미니멀한 라운드 스타일 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 8px 16px;
        border-radius: 20px; /* 알약 모양 */
        text-decoration: none !important;
        font-size: 0.8rem;
        font-weight: 600;
        transition: 0.2s;
    }
    .btn-tel { background-color: #f1f3f5; color: #495057 !important; }
    .btn-hp { background-color: #212529; color: #ffffff !important; }
    
    /* 탭 메뉴 커스텀 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; color: #adb5bd; }
    .stTabs [aria-selected="true"] { color: #000 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (구글 시트 연동)
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        # 열 매핑 고정
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 검색창
q = st.text_input("", placeholder="🔍 성함 또는 부서 검색", label_visibility="collapsed")

# 5. 메인 UI
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        # [해결] 변수명 오타 수정 완료
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        st.markdown(f"""
            <div class="contact-item">
                <div class="info-group">
                    {f'<span class="work-text">{wk}</span>' if wk else ''}
                    <div>
                        <span class="name-text">{nm if nm else dp}</span>
                        <span class="dept-text">{dp if nm else ""}</span>
                    </div>
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel_link}" class="c-btn btn-tel">내선</a>' if tel_link else ''}
                    {f'<a href="tel:{hp_link}" class="c-btn btn-hp">직통</a>' if hp_link else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)

# 6. 필터 및 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        filtered = df if category == "전체" else df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered)
