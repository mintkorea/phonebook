import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 디자인 시스템 (일관성 있는 블랙&화이트 톤)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    /* 기본 여백 제거 및 배경 설정 */
    .block-container { padding: 0.5rem 0.6rem !important; background-color: #ffffff; }
    header, footer { visibility: hidden; }
    
    /* 탭 디자인: 하단 라인 강조 및 글자 크기 최적화 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #f0f0f0; }
    .stTabs [data-baseweb="tab"] { 
        height: 40px; font-size: 0.85rem; padding: 0 4px; 
        font-weight: 600; color: #888; border: none !important;
    }
    .stTabs [aria-selected="true"] { color: #000 !important; border-bottom: 2px solid #000 !important; }

    /* 리스트 디자인: 업무 내용이 주인공이 되도록 배치 */
    .list-row {
        display: flex;
        flex-direction: column;
        padding: 12px 0;
        border-bottom: 1px solid #f5f5f5;
    }
    .main-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        width: 100%;
    }
    .info-section { flex: 1; min-width: 0; }
    
    /* 텍스트 레이어링 */
    .title-line { display: flex; align-items: baseline; gap: 6px; margin-bottom: 4px; }
    .main-text { font-size: 1.05rem; font-weight: 800; color: #111; }
    .sub-text { font-size: 0.8rem; color: #666; font-weight: 400; }
    
    /* 업무 내용: 가장 잘 보이게 강조 */
    .work-desc { 
        font-size: 0.85rem; 
        color: #007bff; /* 업무 내용은 블루 톤으로 강조 */
        background-color: #f0f7ff; 
        padding: 4px 8px; 
        border-radius: 4px;
        display: inline-block;
        margin-top: 4px;
        line-height: 1.3;
    }
    
    /* 버튼: 불필요한 색상 제거, 깔끔한 외곽선 스타일 */
    .btn-group { display: flex; gap: 8px; margin-top: 2px; }
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 34px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 0.75rem;
        font-weight: 700;
        transition: 0.2s;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ddd; }
    .btn-hp { background-color: #333; color: #fff !important; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (에러 방지용 위치 기반 매핑)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        df = pd.read_csv(csv_files[0])
        cols = ['구분', '부서명', '담당자', '전화', '휴대폰', '비고']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df.fillna('')
    except:
        return pd.DataFrame()

raw_df = load_data()

# 3. 검색 필터링 (탭에 상관없이 '전체'에서 먼저 검색)
search = st.text_input("", placeholder="🔍 이름, 부서, 업무 키워드로 검색", label_visibility="collapsed")
if search:
    filtered_df = raw_df[raw_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
else:
    filtered_df = raw_df

# 4. 탭 구성
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_list(target_df):
    if target_df.empty:
        st.info("해당하는 연락처가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        name = str(row.get('담당자', '')).strip()
        dept = str(row.get('부서명', '')).strip()
        tel_raw = str(row.get('전화', '')).strip()
        hp_raw = str(row.get('휴대폰', '')).strip()
        work = str(row.get('비고', '')).strip()
        
        tel_link = re.sub(r'[^0-9*]', '', tel_raw)
        hp_link = re.sub(r'[^0-9]', '', hp_raw)
        
        title = name if name else dept
        sub = dept if name else ""
        
        # 디자인 개선된 HTML 구조
        st.markdown(f'''
            <div class="list-row">
                <div class="main-container">
                    <div class="info-section">
                        <div class="title-line">
                            <span class="main-text">{title}</span>
                            <span class="sub-text">{sub}</span>
                        </div>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:" + tel_link + "' class='action-btn btn-tel'>내선</a>" if tel_link else ""}
                        {"<a href='tel:" + hp_link + "' class='action-btn btn-hp'>직통</a>" if hp_link else ""}
                    </div>
                </div>
                {"<div class='work-desc'>" + work + "</div>" if work else ""}
            </div>
        ''', unsafe_allow_html=True)

# 5. 탭별 필터링 실행 (전체 검색 결과 내에서 분류)
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_titles[i]
        if cat == "전체":
            render_list(filtered_df)
        else:
            # 검색 결과 중 해당 카테고리가 포함된 행만 추출
            tab_filtered = filtered_df[filtered_df.apply(lambda x: x.astype(str).str.contains(cat, na=False)).any(axis=1)]
            render_list(tab_filtered)
