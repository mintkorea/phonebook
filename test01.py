import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 고품격 현대적 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    
    .block-container { padding: 1rem !important; background-color: #f9fafb; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창 */
    .stTextInput input {
        border-radius: 14px !important;
        border: 1px solid #e5e7eb !important;
        padding: 12px 20px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }

    /* 연락처 카드 */
    .contact-card {
        background: white;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid #f3f4f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* 업무 태그 (세련된 레드/그레이 조합) */
    .work-tag {
        display: inline-block;
        background-color: #fef2f2;
        color: #dc2626;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 12px;
        border: 1px solid #fee2e2;
    }

    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.3rem; font-weight: 800; color: #111827; }
    .dept-text { font-size: 0.9rem; color: #6b7280; font-weight: 500; margin-left: 6px; }

    /* 버튼 그룹 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 10px 16px;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 700;
        min-width: 65px;
        transition: 0.2s;
    }
    .btn-tel { background-color: #f3f4f6; color: #374151 !important; border: 1px solid #e5e7eb; }
    .btn-hp { background-color: #0f172a; color: #ffffff !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (실시간 구글 시트 연동)
@st.cache_data(ttl=300) # 5분 간격 갱신
def get_live_data():
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(SHEET_URL).astype(str)
        # 공백 제거 및 nan 처리
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        
        # 열 이름 강제 매핑 (KeyError 방지)
        # 구글 시트 순서: 구분, 부서명, 담당자, 전화, 휴대폰, 비고/업무
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 검색창
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용(전기, 보안, 대관 등) 검색", label_visibility="collapsed")

# 5. 탭 구성
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df):
    if target_df.empty:
        st.info("조건에 맞는 연락처가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        # 데이터 매핑
        nm = row['c_name'] if row['c_name'] else row['c_dept']
        dp = row['c_dept'] if row['c_name'] else ""
        wk = row['c_work']
        
        # 전화번호 정제 (숫자 및 기호 추출)
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
                        {f'<a href="tel:{hp_link}" class="c-btn btn-hp">직통전화</a>' if hp_link else ''}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 6. 필터링 및 출력
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        
        # 카테고리 필터링
        if category == "전체":
            filtered = df
        else:
            # '구분' 또는 '부서' 열에서 카테고리 명 포함 확인
            filtered = df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        
        # 검색어 필터링
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_ui(filtered)
