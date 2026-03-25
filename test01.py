import streamlit as st
import pandas as pd
import os
import re

# 1. 페이지 설정 및 모바일 최적화 디자인
st.set_page_config(page_title="성의 연락처 Hub", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #fff; }
    header, footer { visibility: hidden; }
    
    /* 검색창: 테두리 강조 */
    .stTextInput input { border: 2px solid #000 !important; border-radius: 4px !important; height: 45px !important; }

    /* 연락처 아이템 레이아웃 */
    .item-box { padding: 10px 0; border-bottom: 1px solid #eee; }
    
    /* 업무 내용(비고): 가장 눈에 띄는 빨간색 강조 */
    .work-highlight { 
        color: #d32f2f; font-weight: 800; font-size: 0.95rem; 
        margin-bottom: 4px; line-height: 1.3;
    }
    
    .name-row { display: flex; justify-content: space-between; align-items: center; }
    .name-txt { font-size: 1.1rem; font-weight: 800; color: #000; }
    .dept-txt { font-size: 0.82rem; color: #777; margin-left: 5px; }

    /* 버튼 스타일 */
    .btn-wrap { display: flex; gap: 6px; }
    .c-btn {
        display: flex; align-items: center; justify-content: center;
        width: 50px; height: 36px; border-radius: 4px;
        text-decoration: none !important; font-size: 0.8rem; font-weight: 700;
    }
    .btn-tel { background-color: #f8f9fa; color: #333 !important; border: 1px solid #ccc; }
    .btn-hp { background-color: #000; color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 "강력 세척" (공백/유령문자 제거)
@st.cache_data
def get_clean_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not files: return pd.DataFrame()
        
        # 데이터 읽기 & 모든 칸의 공백/줄바꿈 무조건 제거
        df = pd.read_csv(files[0], encoding='utf-8-sig').astype(str)
        df = df.apply(lambda x: x.str.strip().replace('nan', ''))
        
        # 열 이름을 번호 순서대로 강제 매핑 (KeyError 방지)
        # 0:구분, 1:부서, 2:성함, 3:내선, 4:직통, 5:업무(비고)
        cols = ['v_cat', 'v_dept', 'v_name', 'v_tel', 'v_hp', 'v_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), 6))]
        
        return df
    except:
        return pd.DataFrame()

df = get_clean_data()

# 3. 통합 검색
q = st.text_input("", placeholder="🔍 성함, 부서, 담당 업무(대관, 보안, 주차 등) 검색", label_visibility="collapsed")

# 4. 탭 구성
tab_list = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_list)

def render_contact(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 추출 및 정제
        nm = row.get('v_name', '').strip()
        dp = row.get('v_dept', '').strip()
        wk = row.get('v_work', '').strip()
        tl = re.sub(r'[^0-9*]', '', str(row.get('v_tel', '')))
        hp = re.sub(r'[^0-9]', '', str(row.get('v_hp', '')))
        
        # [수정 사항 1] 담당자 없으면 부서명을 제목으로
        display_name = nm if nm else dp
        display_dept = dp if nm else ""

        with st.container():
            # [수정 사항 2] 업무 내용이 있을 때만 최상단 노출
            if wk:
                st.markdown(f"<div class='work-highlight'>{wk}</div>", unsafe_allow_html=True)
            
            # 이름 및 버튼 행
            st.markdown(f'''
                <div class="name-row">
                    <div>
                        <span class="name-txt">{display_name}</span>
                        <span class="dept-txt">{display_dept}</span>
                    </div>
                    <div class="btn-wrap">
                        {"<a href='tel:"+tl+"' class='c-btn btn-tel'>내선</a>" if tl else ""}
                        {"<a href='tel:"+hp+"' class='c-btn btn-hp'>직통</a>" if hp else ""}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            st.divider()

# 5. 탭/검색 필터링
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        d = df if cat == "전체" else df[df['v_cat'].str.contains(cat) | df['v_dept'].str.contains(cat)]
        if q:
            d = d[d.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_contact(d)
