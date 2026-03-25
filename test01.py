import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 비즈니스 다크/화이트 테마
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 0.6rem !important; background-color: #f8f9fa; }
    header, footer { visibility: hidden; }
    
    /* 검색창 디자인 개선 */
    .stTextInput input {
        border-radius: 8px !important;
        border: 2px solid #007bff !important;
        padding: 10px !important;
    }

    /* 탭 디자인: 깔끔한 상단 바 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background-color: #fff; padding: 5px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { height: 36px; font-size: 0.85rem; font-weight: 600; }

    /* 리스트 카드 디자인 (일관성 및 가독성 확보) */
    .contact-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff; /* 카테고리 구분선 */
    }
    .card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
    .name-dept { flex: 1; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #111; display: block; }
    .dept-text { font-size: 0.8rem; color: #666; }
    
    /* 업무 내용 (가장 중요) */
    .work-tag {
        font-size: 0.85rem;
        color: #444;
        background-color: #e9ecef;
        padding: 6px 10px;
        border-radius: 5px;
        line-height: 1.4;
        display: block;
        margin-top: 5px;
        border: 1px dashed #ccc;
    }

    /* 버튼 디자인 */
    .btn-group { display: flex; gap: 6px; }
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 55px;
        height: 38px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .btn-tel { background-color: #fff; color: #007bff !important; border: 1px solid #007bff; }
    .btn-hp { background-color: #007bff; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        df = pd.read_csv(csv_files[0])
        df.columns = ['구분', '부서명', '담당자', '전화', '휴대폰', '비고']
        return df.fillna('')
    except:
        return pd.DataFrame()

raw_df = load_data()

# 3. 검색 필터 (오류 방지용 명시적 검색)
search = st.text_input("", placeholder="🔍 이름, 부서, '업무 내용'을 입력하세요", label_visibility="collapsed")

if search:
    # 모든 열을 문자열로 변환 후 검색어 포함 여부 확인
    mask = (
        raw_df['담당자'].str.contains(search, case=False, na=False) |
        raw_df['부서명'].str.contains(search, case=False, na=False) |
        raw_df['비고'].str.contains(search, case=False, na=False) |
        raw_df['구분'].str.contains(search, case=False, na=False)
    )
    filtered_df = raw_df[mask]
else:
    filtered_df = raw_df

# 4. 탭 구성
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_cards(target_df):
    if target_df.empty:
        st.info("검색 결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        name = str(row['담당자']).strip()
        dept = str(row['부서명']).strip()
        tel = re.sub(r'[^0-9*]', '', str(row['전화']))
        hp = re.sub(r'[^0-9]', '', str(row['휴대폰']))
        work = str(row['비고']).strip()
        
        title = name if name else dept
        sub = dept if name else ""

        st.markdown(f'''
            <div class="contact-card">
                <div class="card-top">
                    <div class="name-dept">
                        <span class="name-text">{title}</span>
                        <span class="dept-text">{sub}</span>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:" + tel + "' class='action-btn btn-tel'>내선</a>" if tel else ""}
                        {"<a href='tel:" + hp + "' class='action-btn btn-hp'>직통</a>" if hp else ""}
                    </div>
                </div>
                {"<div class='work-tag'><b>업무:</b> " + work + "</div>" if work else ""}
            </div>
        ''', unsafe_allow_html=True)

# 5. 탭별 로직 (전체 검색 결과 내에서 카테고리 분류)
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_titles[i]
        if cat == "전체":
            render_cards(filtered_df)
        else:
            # 탭에 해당하는 데이터만 필터링
            tab_data = filtered_df[filtered_df['구분'].str.contains(cat, na=False)]
            render_cards(tab_data)
