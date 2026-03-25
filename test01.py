import streamlit as st
import pandas as pd
import re
import os

# 1. 페이지 설정 (최대한 넓고 깔끔하게)
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem 0.7rem !important; background-color: #fff; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 직관적으로 강조 */
    .stTextInput input {
        border: 2px solid #222 !important;
        border-radius: 4px !important;
        height: 45px !important;
        font-weight: 600 !important;
    }

    /* 리스트 스타일: 업무 내용 강조 */
    .item-container {
        padding: 12px 0;
        border-bottom: 1px solid #eee;
    }
    .line-1 { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
    .name-txt { font-size: 1.1rem; font-weight: 800; color: #000; }
    .dept-txt { font-size: 0.85rem; color: #666; margin-left: 6px; }
    
    /* 업무내용(비고): 붉은색 강조로 무엇을 하는 사람인지 바로 확인 */
    .work-txt { font-size: 0.92rem; color: #e63946; font-weight: 700; line-height: 1.4; }

    /* 버튼 스타일: 실용적 크기 */
    .btn-wrap { display: flex; gap: 8px; }
    .tel-btn {
        display: flex; align-items: center; justify-content: center;
        width: 55px; height: 38px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.85rem; font-weight: 800;
    }
    .btn-off { background-color: #f1f3f5; color: #333 !important; border: 1px solid #adb5bd; }
    .btn-on { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (KeyError/IndexError 원천 차단 로직)
@st.cache_data
def load_data():
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files: return pd.DataFrame()
        
        # BOM 문자 제거 및 문자열 강제 변환
        df = pd.read_csv(csv_files[0], encoding='utf-8-sig').astype(str)
        
        # 열 이름을 무조건 순서대로 강제 재설정 (파일명/헤더 깨짐 방지)
        # 구분[0], 부서[1], 담당[2], 내선[3], 휴대폰[4], 비고[5]
        new_cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [new_cols[i] for i in range(min(len(df.columns), 6))]
        
        return df.replace('nan', '')
    except:
        return pd.DataFrame()

df = load_data()

# 3. 통합 검색창 (상단 고정)
q = st.text_input("", placeholder="🔍 이름, 업무(대관, 보안, 미화 등) 검색", label_visibility="collapsed")

# 4. 탭 구성
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def show_list(target_df):
    if target_df.empty:
        st.caption("표시할 내용이 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 매핑
        nm, dp, wk = row.get('c_name', ''), row.get('c_dept', ''), row.get('c_work', '')
        t_raw, h_raw = row.get('c_tel', ''), row.get('c_hp', '')
        
        # 전화번호 정제
        t_link = re.sub(r'[^0-9*]', '', t_raw)
        h_link = re.sub(r'[^0-9]', '', h_raw)
        
        title = nm if nm else dp
        sub = dp if nm else ""

        st.markdown(f'''
            <div class="item-container">
                <div class="line-1">
                    <div class="info">
                        <span class="name-txt">{title}</span>
                        <span class="dept-txt">{sub}</span>
                    </div>
                    <div class="btn-wrap">
                        {"<a href='tel:"+t_link+"' class='tel-btn btn-off'>내선</a>" if t_link else ""}
                        {"<a href='tel:"+h_link+"' class='tel-btn btn-on'>직통</a>" if h_link else ""}
                    </div>
                </div>
                {"<div class='work-txt'>" + wk + "</div>" if wk else ""}
            </div>
        ''', unsafe_allow_html=True)

# 5. [핵심 로직] 검색과 탭 필터링 동시 적용
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_names[i]
        
        # 1차 필터링: 탭 카테고리 (전체 탭 제외)
        if cat == "전체":
            d_tab = df
        else:
            # '구분' 열이나 '부서' 열에 탭 이름이 포함된 경우
            d_tab = df[df['c_cat'].str.contains(cat) | df['c_dept'].str.contains(cat)]
        
        # 2차 필터링: 검색어 적용
        if q:
            # 모든 열을 합쳐서 검색어가 있는지 확인
            d_final = d_tab[d_tab.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        else:
            d_final = d_tab
            
        show_list(d_final)
