import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="성의 연락처 Hub", layout="wide")

# 2. 강력한 디자인 시스템 (업무 내용 강조 및 모바일 최적화)
st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #fcfcfc; }
    header, footer { visibility: hidden; }
    
    /* 검색창 스타일 */
    .stTextInput input {
        border: 2px solid #000 !important;
        border-radius: 8px !important;
        height: 48px !important;
        font-size: 1.1rem !important;
    }

    /* 연락처 카드 디자인 */
    .contact-card {
        background: white;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #eee;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* 업무 내용(비고) 박스: 무엇을 하는 사람인지 최우선 노출 */
    .work-tag {
        background-color: #fff0f0;
        color: #d32f2f;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.92rem;
        font-weight: 800;
        margin-bottom: 8px;
        display: inline-block;
        border: 1px solid #ffcdd2;
    }

    .main-info { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.15rem; font-weight: 800; color: #111; }
    .dept-text { font-size: 0.85rem; color: #666; margin-left: 5px; }

    /* 버튼 디자인 */
    .btn-row { display: flex; gap: 8px; margin-top: 5px; }
    .call-btn {
        flex: 1; display: flex; align-items: center; justify-content: center;
        height: 40px; border-radius: 6px; text-decoration: none !important;
        font-size: 0.85rem; font-weight: 700;
    }
    .btn-tel { background-color: #f1f3f5; color: #333 !important; border: 1px solid #dee2e6; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 및 "강제 세척" 로직
@st.cache_data
def get_processed_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        
        # 데이터 읽기 및 모든 칸의 유령 공백 제거
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        df = df.apply(lambda x: x.str.strip()) 
        
        # [핵심] 열 이름이 무엇이든 '순서'대로 강제 재설정 (KeyError 완전 방지)
        # 0:구분, 1:부서, 2:성함, 3:내선, 4:직통, 5:업무
        standard_cols = ['cat', 'dept', 'name', 'tel', 'hp', 'work']
        df.columns = [standard_cols[i] for i in range(min(len(df.columns), 6))]
        
        return df.replace('nan', '')
    except Exception as e:
        st.error(f"데이터 세척 중 오류: {e}")
        return pd.DataFrame()

df = get_processed_data()

# 4. 통합 검색창
q = st.text_input("", placeholder="🔍 성함, 부서, 담당 업무(대관, 주차, 보안 등) 검색", label_visibility="collapsed")

# 5. 탭 구성
tabs = st.tabs(["보안", "시설", "미화", "총무", "지원", "기타", "전체"])

def render_ui(data):
    if data.empty:
        st.caption("검색 결과가 없습니다.")
        return
    
    for _, row in data.iterrows():
        # 데이터 매핑
        nm, dp, wk = row['name'], row['dept'], row['work']
        tl, hp = row['tel'], row['hp']
        
        # 전화번호 정제
        tl_link = re.sub(r'[^0-9*]', '', tl)
        hp_link = re.sub(r'[^0-9]', '', hp)
        
        title = nm if nm else dp
        sub = dp if nm else ""

        st.markdown(f'''
            <div class="contact-card">
                {"<div class='work-tag'>업무: " + wk + "</div>" if wk else ""}
                <div class="main-info">
                    <div>
                        <span class="name-text">{title}</span>
                        <span class="dept-text">{sub}</span>
                    </div>
                </div>
                <div class="btn-row">
                    {"<a href='tel:"+tl_link+"' class='call-btn btn-tel'>내선 호출</a>" if tl_link else ""}
                    {"<a href='tel:"+hp_link+"' class='call-btn btn-hp'>직통 연결</a>" if hp_link else ""}
                </div>
            </div>
        ''', unsafe_allow_html=True)

# 6. 필터링 로직 (탭 + 검색)
for i, tab in enumerate(tabs):
    with tab:
        category = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"][i]
        
        # 탭 필터링
        if category == "전체":
            d_tab = df
        else:
            # 첫 번째(구분)나 두 번째(부서) 열에서 카테고리 확인
            d_tab = df[df['cat'].str.contains(category) | df['dept'].str.contains(category)]
        
        # 검색어 필터링
        if q:
            d_tab = d_tab[d_tab.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
            
        render_ui(d_tab)
