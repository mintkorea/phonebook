import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 및 디자인 (가장 견고한 방식)
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #fff; }
    header, footer { visibility: hidden; }
    .stTextInput input { border: 2px solid #000 !important; border-radius: 4px !important; height: 45px !important; }

    /* 업무 내용(비고): 빨간색 박스로 최상단 노출 */
    .work-tag {
        background-color: #fff0f0; color: #d32f2f; padding: 4px 8px;
        border-radius: 4px; font-size: 0.95rem; font-weight: 800;
        margin-bottom: 8px; display: inline-block; border: 1px solid #ffcccc;
    }

    .info-row { display: flex; justify-content: space-between; align-items: center; }
    .name-text { font-size: 1.15rem; font-weight: 800; color: #000; }
    .dept-text { font-size: 0.85rem; color: #666; margin-left: 5px; }

    /* 버튼 스타일 */
    .btn-group { display: flex; gap: 8px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        width: 55px; height: 38px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.85rem; font-weight: 700;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드: "유령 공백" 및 "KeyError" 원천 차단
@st.cache_data
def get_clean_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        
        # [해결책 1] 모든 데이터를 문자로 읽고 앞뒤 공백/줄바꿈(\n, \r) 즉시 제거
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        df = df.apply(lambda x: x.str.strip().replace(r'\n', '', regex=True).replace(r'\r', '', regex=True).replace('nan', ''))
        
        # [해결책 2] 열 이름을 번호 순서대로 강제 할당 (KeyError 완전 방지)
        # 0:구분, 1:부서, 2:성함, 3:내선, 4:직통, 5:업무
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), 6))]
        return df
    except:
        return pd.DataFrame()

df = get_clean_data()

# 3. 통합 검색 (상단 고정)
q = st.text_input("", placeholder="🔍 성함, 부서, 업무 내용(전기, 보안, 대관 등) 검색", label_visibility="collapsed")

# 4. 탭 구성
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_ui(target_df):
    # 실제 내용이 있는 행만 필터링
    valid = target_df[(target_df['c_name'] != "") | (target_df['c_dept'] != "") | (target_df['c_work'] != "")]
    
    if valid.empty:
        st.caption("표시할 내용이 없습니다.")
        return
    
    for _, row in valid.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        tl = re.sub(r'[^0-9*]', '', row['c_tel'])
        hp = re.sub(r'[^0-9]', '', row['c_hp'])
        
        # [요청사항 1] 담당자가 없으면 부서명을 제목으로 사용
        d_title = nm if nm else dp
        d_sub = dp if nm else ""

        with st.container():
            # [요청사항 2] 업무 내용(비고)이 있으면 가장 먼저 노출
            if wk:
                st.markdown(f"<div class='work-tag'>업무: {wk}</div>", unsafe_allow_html=True)
            
            # 이름/부서 및 버튼
            st.markdown(f'''
                <div class="info-row">
                    <div>
                        <span class="name-text">{d_title}</span>
                        <span class="dept-text">{d_sub}</span>
                    </div>
                    <div class="btn-group">
                        {"<a href='tel:"+tl+"' class='c-btn btn-tel'>내선</a>" if tl else ""}
                        {"<a href='tel:"+hp+"' class='c-btn btn-hp'>직통</a>" if hp else ""}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            st.divider()

# 5. 탭 및 검색 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        d = df if cat == "전체" else df[df['c_cat'].str.contains(cat) | df['c_dept'].str.contains(cat)]
        if q:
            d = d[d.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(d)
