import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 및 디자인 (심플 & 실용성 강조)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 0.7rem !important; background-color: #ffffff; }
    header, footer { visibility: hidden; }
    
    /* 검색창 디자인: 테두리 강조 */
    .stTextInput input {
        border-radius: 8px !important;
        border: 2px solid #333 !important;
        height: 45px !important;
    }

    /* 리스트 아이템 디자인 */
    .contact-item {
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }
    .top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #000; }
    .dept-text { font-size: 0.85rem; color: #666; margin-left: 6px; }
    
    /* 업무 내용: 이름 바로 아래 빨간색으로 강조 */
    .work-text { font-size: 0.9rem; color: #d32f2f; font-weight: 700; line-height: 1.3; }

    /* 버튼 스타일 */
    .btn-group { display: flex; gap: 6px; }
    .action-btn {
        display: flex; align-items: center; justify-content: center;
        width: 50px; height: 36px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.8rem; font-weight: 700;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #212529; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: 열 이름 무관하게 '위치'로 강제 지정 (KeyError 방지)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        # utf-8-sig로 읽어서 한글 깨짐 방지
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig')
        
        # [중요] 열 이름을 우리가 정한 이름으로 강제 교체 (0번부터 5번 열까지)
        # 이 작업이 없으면 '구분'이라는 글자를 못 찾아서 에러가 납니다.
        new_cols = ['v_cat', 'v_dept', 'v_name', 'v_tel', 'v_hp', 'v_work']
        df.columns = [new_cols[i] for i in range(min(len(df.columns), len(new_names)))]
        
        return df.fillna('')
    except:
        return pd.DataFrame()

df_raw = load_data()

# 3. 통합 검색 (상단 고정)
search_input = st.text_input("", placeholder="🔍 이름, 부서, 업무(대관, 보안 등) 검색", label_visibility="collapsed")

# 검색 로직: 전체 데이터에서 검색어가 포함된 행만 필터링
if search_input:
    # 모든 열의 내용을 하나로 합쳐서 검색어가 있는지 확인 (가장 확실한 방법)
    search_mask = df_raw.apply(lambda x: x.astype(str).str.contains(search_input, case=False).any(), axis=1)
    df_filtered = df_raw[search_mask]
else:
    df_filtered = df_raw

# 4. 탭 구성 (보안, 시설, 미화, 총무, 지원, 기타, 전체)
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_list(target_df):
    if target_df.empty:
        st.caption("표시할 내용이 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 위치(열 이름)를 안전하게 가져오기
        name = str(row.get('v_name', '')).strip()
        dept = str(row.get('v_dept', '')).strip()
        work = str(row.get('v_work', '')).strip()
        tel = re.sub(r'[^0-9*]', '', str(row.get('v_tel', '')))
        hp = re.sub(r'[^0-9]', '', str(row.get('v_hp', '')))
        
        d_name = name if name else dept
        d_dept = dept if name else ""

        st.markdown(f'''
            <div class="contact-item">
                <div class="top-row">
                    <div class="info">
                        <span class="name-text">{d_name}</span>
                        <span class="dept-text">{d_dept}</span>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:" + tel + "' class='action-btn btn-tel'>내선</a>" if tel else ""}
                        {"<a href='tel:" + hp + "' class='action-btn btn-hp'>직통</a>" if hp else ""}
                    </div>
                </div>
                {"<div class='work-text'>" + work + "</div>" if work else ""}
            </div>
        ''', unsafe_allow_html=True)

# 5. 탭별 필터링 실행
for i, tab in enumerate(tabs):
    with tab:
        current_cat = tab_titles[i]
        
        if current_cat == "전체":
            render_list(df_filtered)
        else:
            # 1단계: 검색어로 필터링된 데이터(df_filtered) 중에서
            # 2단계: 탭 카테고리(보안, 시설 등)가 포함된 행만 추출
            # 'v_cat'(구분) 열에서만 찾지 않고 행 전체에서 찾으므로 훨씬 정확합니다.
            tab_mask = df_filtered.apply(lambda x: x.astype(str).str.contains(current_cat, na=False).any(), axis=1)
            render_list(df_filtered[tab_mask])
