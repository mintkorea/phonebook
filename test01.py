import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 모던 엔터프라이즈 UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    /* 전체 배경 및 폰트 설정 */
    .block-container { padding: 2rem 5rem !important; background-color: #fcfcfc; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 미니멀 스타일 */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 12px 18px !important;
        background-color: white !important;
        font-size: 0.95rem !important;
        transition: all 0.2s;
    }
    .stTextInput input:focus {
        border-color: #1e3a8a !important;
        box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.1) !important;
    }

    /* 리스트 컨테이너 */
    .contact-list {
        background: white;
        border-radius: 12px;
        border: 1px solid #eaeaea;
        overflow: hidden;
        margin-top: 1rem;
    }

    /* 리스트 아이템 (행) */
    .contact-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 25px;
        border-bottom: 1px solid #f0f0f0;
        transition: background-color 0.1s;
    }
    .contact-item:last-child { border-bottom: none; }
    .contact-item:hover { background-color: #f9fafb; }

    /* 이름 및 부서 섹션 */
    .name-section { display: flex; align-items: center; gap: 12px; }
    .name-text { font-size: 1.15rem; font-weight: 700; color: #111; letter-spacing: -0.02em; }
    .dept-text { font-size: 0.85rem; color: #777; font-weight: 400; }

    /* 업무 태그 (세련된 그레이 배지) */
    .work-badge {
        display: inline-block;
        background-color: #f3f4f6;
        color: #555;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
    }

    /* 버튼 그룹 (아웃라인 스타일) */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px 15px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 0.82rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* 내선 버튼: 그레이 아웃라인 */
    .btn-tel { 
        background-color: white; 
        color: #555 !important; 
        border: 1px solid #d1d5db; 
    }
    .btn-tel:hover { background-color: #f9fafb; border-color: #c1c5cb; }
    
    /* 직통 버튼: 네이비 아웃라인 */
    .btn-hp { 
        background-color: white; 
        color: #1e3a8a !important; 
        border: 1px solid #1e3a8a; 
    }
    .btn-hp:hover { background-color: #eff6ff; }
    
    /* SVG 아이콘 스타일 */
    .btn-icon { width: 14px; height: 14px; fill: currentColor; }

    /* 탭 디자인 살짝 보정 */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; border-bottom: 1px solid #eaeaea; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        color: #666;
        font-size: 0.95rem;
    }
    .stTabs [aria-selected="true"] {
        color: #1e3a8a !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (매핑 로직 유지)
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

# 4. 상단 검색창 (Placeholder 문구 수정)
q = st.text_input("", placeholder="🔍 성함, 부서, 주요 업무로 검색...", label_visibility="collapsed")

# 5. 메인 UI 탭 구성
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

# SVG 아이콘 정의 (수화기)
icon_phone = '<svg class="btn-icon" viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.26 1.12.32 2.33.5 3.57.5.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.18 2.45.5 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>'

def render_ui(target_df):
    if target_df.empty:
        st.info("검색 조건에 맞는 연락처가 없습니다.")
        return
    
    # 리스트 시작 컨테이너
    st.markdown('<div class="contact-list">', unsafe_allow_html=True)
    
    for _, row in target_df.iterrows():
        # 데이터 매핑
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        # 전화번호 정제
        tel_link = re.sub(r'[^0-9*]', '', str(row['c_tel']))
        hp_link = re.sub(r'[^0-9]', '', str(row['c_hp']))

        # 리스트 아이템 (행) 렌더링
        item_html = f"""
            <div class="contact-item">
                <div class="name-section">
                    <div>
                        <span class="name-text">{nm}</span>
                        <span class="dept-text">{dp}</span>
                    </div>
                    {f'<span class="work-badge">{wk}</span>' if wk else ''}
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel_link}" class="c-btn btn-tel">{icon_phone}내선</a>' if tel_link else ''}
                    {f'<a href="tel:{hp_num}" class="c-btn btn-hp">{icon_phone}직통전화</a>' if hp_num else ''}
                </div>
            </div>
        """
        st.markdown(item_html, unsafe_allow_html=True)
        
    # 리스트 종료 컨테이너
    st.markdown('</div>', unsafe_allow_html=True)

# 6. 필터링 및 출력
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
