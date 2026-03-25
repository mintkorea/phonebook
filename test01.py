import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 디자인 (고급스러운 화이트 & 블루 포인트)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 0.6rem !important; background-color: #f5f7f9; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 테두리 강조 */
    .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #007bff !important;
        height: 45px !important;
    }

    /* 탭: 활성화된 탭 강조 */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { height: 38px; font-size: 0.85rem; font-weight: 600; }

    /* 카드 디자인: 업무 내용을 최상단으로 올림 */
    .contact-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 4px solid #007bff;
    }
    
    /* 업무 내용(비고) 강조 영역 */
    .work-box {
        background-color: #f0f7ff;
        color: #0056b3;
        padding: 8px 10px;
        border-radius: 6px;
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 10px;
        line-height: 1.4;
        border-left: 3px solid #007bff;
    }

    .card-main { display: flex; justify-content: space-between; align-items: center; }
    .info-text { flex: 1; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #111; margin-right: 6px; }
    .dept-text { font-size: 0.8rem; color: #777; }

    /* 버튼 스타일 */
    .btn-group { display: flex; gap: 8px; }
    .action-btn {
        display: flex; align-items: center; justify-content: center;
        width: 52px; height: 38px; border-radius: 8px;
        text-decoration: none !important; font-size: 0.8rem; font-weight: 700;
    }
    .btn-tel { background-color: #fff; color: #007bff !important; border: 1.5px solid #007bff; }
    .btn-hp { background-color: #007bff; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: '이름'이 아닌 '순서'로 읽기 (KeyError 해결)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        # 어떤 인코딩이든 읽을 수 있도록 설정
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig') 
        
        # [핵심] 열 이름이 무엇이든 상관없이 순서대로 강제 재설정
        # 열 개수가 6개라고 가정 (구분, 부서명, 담당자, 전화, 휴대폰, 비고)
        new_cols = ['cat', 'dept', 'name', 'tel', 'hp', 'work']
        df.columns = [new_cols[i] for i in range(len(df.columns))]
        
        return df.fillna('')
    except:
        return pd.DataFrame()

df = load_data()

# 3. 통합 검색 (모든 열 대상)
search = st.text_input("", placeholder="🔍 이름, 부서, 업무 내용(대관, 미화 등) 검색", label_visibility="collapsed")

if search and not df.empty:
    # 데이터프레임의 모든 값을 문자열로 바꾸고 검색어가 포함된 행만 필터링
    filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
else:
    filtered_df = df

# 4. 탭 구성
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_cards(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 순서 기반으로 데이터 할당 (KeyError 방지)
        r_name = str(row['name']).strip()
        r_dept = str(row['dept']).strip()
        r_work = str(row['work']).strip()
        r_tel = re.sub(r'[^0-9*]', '', str(row['tel']))
        r_hp = re.sub(r'[^0-9]', '', str(row['hp']))
        
        display_name = r_name if r_name else r_dept
        display_dept = r_dept if r_name else ""

        # 카드 렌더링
        st.markdown(f'''
            <div class="contact-card">
                {"<div class='work-box'>" + r_work + "</div>" if r_work else ""}
                <div class="card-main">
                    <div class="info-text">
                        <span class="name-text">{display_name}</span>
                        <span class="dept-text">{display_dept}</span>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:" + r_tel + "' class='action-btn btn-tel'>내선</a>" if r_tel else ""}
                        {"<a href='tel:" + r_hp + "' class='action-btn btn-hp'>직통</a>" if r_hp else ""}
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

# 5. 탭별 필터링 실행
for i, tab in enumerate(tabs):
    with tab:
        current_tab = tab_titles[i]
        if current_tab == "전체":
            render_cards(filtered_df)
        else:
            # 검색 결과 내에서 현재 탭 키워드가 포함된 행만 표시
            tab_data = filtered_df[filtered_df.apply(lambda x: x.astype(str).str.contains(current_tab, na=False)).any(axis=1)]
            render_cards(tab_data)
