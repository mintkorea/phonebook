import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. 고급스러운 Enterprise UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    
    .block-container { padding: 1rem !important; background-color: #f9fafb; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 모던한 스타일 */
    .stTextInput input {
        border-radius: 14px !important;
        border: 1px solid #e5e7eb !important;
        padding: 12px 20px !important;
        background-color: white !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }

    /* 연락처 카드: 그림자와 라운드 강조 */
    .contact-card {
        background: white;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid #f3f4f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* 업무 태그: 유치하지 않은 파스텔 톤 */
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
    .name-section { display: flex; flex-direction: column; }
    .name-text { font-size: 1.3rem; font-weight: 800; color: #111827; }
    .dept-text { font-size: 0.9rem; color: #6b7280; font-weight: 500; }

    /* 버튼 그룹: Deep Navy & Soft Gray */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 10px 16px;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 700;
        min-width: 65px;
        transition: all 0.2s ease;
    }
    .btn-tel { background-color: #f3f4f6; color: #374151 !important; border: 1px solid #e5e7eb; }
    .btn-hp { background-color: #0f172a; color: #ffffff !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* 탭 스타일 조정 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 8px;
        color: #6b7280;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 (구글 시트 실시간 연동)
@st.cache_data(ttl=300) # 5분마다 자동 갱신
def get_live_data():
    # ⚠️ [중요] 여기에 웹에 게시한 CSV URL을 넣으세요.
    # 복사한 주소가 "https://docs.google.com/spreadsheets/d/e/.../pub?output=csv" 형태여야 합니다.
    SHEET_URL = "복사한_CSV_주소를_여기에_붙여넣으세요"
    
    try:
        # URL에서 직접 읽기
        df = pd.read_csv(SHEET_URL).astype(str)
        # 전처리: 줄바꿈 제거 및 공백 정리
        df = df.apply(lambda x: x.str.strip().replace(r'\n', ' ', regex=True).replace('nan', ''))
        return df
    except:
        # 오류 발생 시 빈 프레임 반환
        return pd.DataFrame()

df = get_live_data()

# 4. 통합 검색
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용으로 검색하세요...", label_visibility="collapsed")

# 5. 메인 UI 탭 구성
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_cards(target_df):
    if target_df.empty:
        st.info("조건에 맞는 연락처가 없습니다.")
        return
        
    for _, row in target_df.iterrows():
        # 데이터 매핑 (사용자 시트 컬럼 기준)
        cat = row.get('구분', '')
        dept = row.get('부서', '')
        name = row.get('성함', '')
        tel = re.sub(r'[^0-9*]', '', str(row.get('내선', '')))
        hp = re.sub(r'[^0-9]', '', str(row.get('직통', '')))
        work = row.get('업무내용', '')

        # 제목 결정 (성함이 없으면 부서를 제목으로)
        display_name = name if name else dept
        display_dept = dept if name else ""

        card_html = f"""
        <div class="contact-card">
            {f'<div class="work-tag">{work}</div>' if work else ''}
            <div class="info-row">
                <div class="name-section">
                    <span class="name-text">{display_name}</span>
                    <span class="dept-text">{display_dept}</span>
                </div>
                <div class="btn-group">
                    {f'<a href="tel:{tel}" class="c-btn btn-tel">내선</a>' if tel else ''}
                    {f'<a href="tel:{hp}" class="c-btn btn-hp">직통전화</a>' if hp else ''}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# 6. 필터링 로직 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        
        # 1차 필터: 카테고리(구분)
        if category == "전체":
            filtered = df
        else:
            filtered = df[df['구분'].str.contains(category, na=False) | df['부서'].str.contains(category, na=False)]
        
        # 2차 필터: 검색어
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        
        render_cards(filtered)
