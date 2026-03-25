import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정
st.set_page_config(page_title="현장 연락처 Hub", layout="wide")

# 2. UI 디자인 (CSS)
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1rem !important; background-color: #ffffff; font-family: 'Pretendard', sans-serif; }
    header, footer { visibility: hidden; }
    
    .stTextInput input { border-radius: 10px !important; border: 1px solid #f0f0f0 !important; background-color: #fafafa !important; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] { font-size: 1.15rem !important; font-weight: 700 !important; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 900 !important; }

    .contact-item { padding: 10px 5px; border-bottom: 1px solid #f8faf9; display: flex; justify-content: space-between; align-items: center; }
    .info-group { display: flex; flex-direction: column; flex: 1; }
    
    .name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    
    /* [요청사항] 노출되는 전화번호 스타일: 2pt 키우고(약 1.15rem) 진하게 */
    .highlight-tel { 
        font-size: 1.15rem; 
        color: #475569; 
        font-weight: 800; 
        margin-left: 4px;
    }
    
    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; margin-top: 2px; }

    /* 버튼 사이즈 초소형화 */
    .btn-group { display: flex; gap: 3px; flex-shrink: 0; }
    .c-btn { 
        display: inline-flex; align-items: center; justify-content: center;
        width: 28px; height: 28px; border-radius: 6px; 
        text-decoration: none !important; font-size: 0.75rem; font-weight: 800; 
    }
    .btn-tel { background-color: #f1f5f9; color: #475569 !important; }
    .btn-hp { background-color: #ecfdf5; color: #059669 !important; border: 1px solid #d1fae5; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=300)
def get_live_data():
    URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(URL).astype(str)
        df = df.replace('nan', '').apply(lambda x: x.str.strip())
        cols = ['c_cat', 'c_dept', 'c_name', 'c_tel', 'c_hp', 'c_work']
        df.columns = [cols[i] for i in range(min(len(df.columns), len(cols)))]
        return df.sort_values(by=['c_dept', 'c_name'], ascending=True)
    except:
        return pd.DataFrame()

df = get_live_data()

# 4. 상단 검색 및 탭
q = st.text_input("", placeholder="🔍 성함 또는 부서 검색", label_visibility="collapsed")
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def render_ui(target_df, current_tab):
    if target_df.empty:
        st.caption("결과가 없습니다. 🌱")
        return
        
    for _, row in target_df.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        raw_tel, raw_hp = str(row['c_tel']), str(row['c_hp'])

        # [수정] 전화 연결 로직: 추가 국번 없이 데이터 그대로 사용 (특수문자만 제거)
        dial_tel = re.sub(r'[^0-9*]', '', raw_tel)
        dial_hp = re.sub(r'[^0-9]', '', raw_hp)

        # 부서별 노출 로직 및 폰트 강조 적용
        tel_html = f'<span class="highlight-tel">{raw_tel}</span>' if raw_tel else ''
        
        if current_tab == "보안" and ("보안" in dp) and not nm:
            # 보안팀 이름 없을 때 번호를 이름 자리에 (highlight-tel 적용)
            display_name = f'<span class="highlight-tel" style="margin-left:0; font-size:1.3rem;">{raw_tel}</span>' if raw_tel else dp
            display_dept = dp if raw_tel else ""
            tel_inline = ""
        elif (current_tab == "시설") or ("총무" in dp):
            display_name = nm if nm else dp
            display_dept = dp if nm else ""
            tel_inline = tel_html
        else:
            display_name = nm if nm else dp
            display_dept = dp if nm else ""
            tel_inline = ""

        # 버튼 생성
        t_btn = f'<a href="tel:{dial_tel}" class="c-btn btn-tel">T</a>' if dial_tel else ''
        m_btn = f'<a href="tel:{dial_hp}" class="c-btn btn-hp">M</a>' if dial_hp else ''
        work_div = f'<div class="work-desc">{wk}</div>' if wk else ''

        # 전체 행 렌더링
        st.markdown(f'<div class="contact-item"><div class="info-group"><div class="name-row"><span class="name-text">{display_name}</span><span class="dept-text">{display_dept}</span>{tel_inline}</div>{work_div}</div><div class="btn-group">{t_btn}{m_btn}</div></div>', unsafe_allow_html=True)

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        filtered = df if category == "전체" else df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered, category)
