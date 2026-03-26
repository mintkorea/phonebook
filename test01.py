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
    
    .stTabs [data-baseweb="tab"] { font-size: 1.15rem !important; font-weight: 700 !important; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; font-weight: 900 !important; }

    .contact-item { padding: 10px 5px; border-bottom: 1px solid #f8faf9; display: flex; justify-content: space-between; align-items: center; }
    .info-group { display: flex; flex-direction: column; flex: 1; }
    .name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .name-text { font-size: 1.1rem; font-weight: 800; color: #334155; }
    .dept-text { font-size: 0.85rem; color: #94a3b8; font-weight: 400; }
    
    /* [스타일] 일반 내선 (고딕, 다크그레이) */
    .highlight-tel { font-family: 'Pretendard', sans-serif; font-size: 1.2rem; color: #475569; font-weight: 800; margin-left: 4px; }
    
    /* [스타일] *1 내선 (네이비, 명조체, 밑줄 제거) */
    .navy-tel { 
        font-family: 'Times New Roman', serif; 
        color: #000080 !important; 
        font-weight: 900 !important; 
        font-style: italic; 
        letter-spacing: 0.5px;
        text-decoration: none !important; /* 밑줄 제거 */
    }
    
    /* [스타일] 모바일 번호 (민트색 강조) */
    .highlight-hp { font-size: 1.1rem; color: #059669; font-weight: 800; margin-left: 4px; }

    .work-desc { font-size: 0.85rem; color: #10b981; font-weight: 600; margin-top: 2px; }

    /* 버튼 사이즈 초소형화 */
    .btn-group { display: flex; gap: 4px; flex-shrink: 0; }
    .c-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 6px; text-decoration: none !important; font-size: 0.75rem; font-weight: 800; }
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

# 4. 검색 및 탭
q = st.text_input("", placeholder="🔍 성함 또는 부서 검색", label_visibility="collapsed")
tab_names = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_names)

def get_dial_number(raw_num):
    """실제 전화 연결용 번호 생성 규칙 (02 국번 보정)"""
    clean_num = re.sub(r'[^0-9*]', '', str(raw_num))
    if not clean_num: return ""
    if clean_num.startswith('*1'): return "022258" + clean_num.replace('*1', '')
    if len(clean_num) >= 7: return "02" + clean_num
    return "023147" + clean_num

def render_ui(target_df, current_tab):
    if target_df.empty:
        st.caption("결과가 없습니다. 🌱")
        return
        
    for _, row in target_df.iterrows():
        nm, dp, wk = row['c_name'], row['c_dept'], row['c_work']
        raw_tel, raw_hp = str(row['c_tel']), str(row['c_hp'])

        # 총무부 국번 제거 텍스트 가공
        display_tel = raw_tel.replace("02-3147-", "").replace("02-3147", "") if "총무" in dp else raw_tel
        
        # 스타일 클래스 결정
        tel_class = "highlight-tel navy-tel" if display_tel.startswith('*1') else "highlight-tel"
        
        # UI 요소 생성 (내선 HTML / 모바일 HTML)
        tel_html = f'<span class="{tel_class}">{display_tel}</span>' if display_tel else ''
        hp_html = f'<span class="highlight-hp">{raw_hp}</span>' if raw_hp else ''

        # --- [노출 로직 통합] ---
        
        # 1. 보안팀 특수 처리 (보안 탭이면서 보안팀인 경우)
        if current_tab == "보안" and ("보안" in dp):
            if not nm and raw_tel: # 이름이 없으면 번호를 이름 자리에 크게
                display_name = f'<span class="{tel_class}" style="margin-left:0; font-size:1.4rem;">{display_tel}</span>'
                display_dept, tel_inline = dp, ""
            else: # 이름이 있으면 이름 옆에 내선 표출
                display_name, display_dept, tel_inline = (nm if nm else dp), (dp if nm else ""), tel_html
        
        # 2. 보안팀을 제외한 모든 경우: 내선 우선 -> 없으면 모바일
        else:
            display_name = nm if nm else dp
            display_dept = dp if nm else ""
            tel_inline = tel_html if raw_tel else hp_html

        # 실제 다이얼 번호 (T, M 버튼용)
        dial_tel = get_dial_number(raw_tel)
        dial_hp = re.sub(r'[^0-9]', '', raw_hp)

        # 버튼 생성
        t_btn = f'<a href="tel:{dial_tel}" class="c-btn btn-tel">T</a>' if dial_tel else ''
        m_btn = f'<a href="tel:{dial_hp}" class="c-btn btn-hp">M</a>' if dial_hp else ''
        work_div = f'<div class="work-desc">{wk}</div>' if wk else ''

        # 렌더링
        st.markdown(f'<div class="contact-item"><div class="info-group"><div class="name-row"><span class="name-text">{display_name}</span><span class="dept-text">{display_dept}</span>{tel_inline}</div>{work_div}</div><div class="btn-group">{t_btn}{m_btn}</div></div>', unsafe_allow_html=True)

# 5. 실행 루프
for i, tab in enumerate(tabs):
    with tab:
        category = tab_names[i]
        filtered = df if category == "전체" else df[df['c_cat'].str.contains(category, na=False) | df['c_dept'].str.contains(category, na=False)]
        if q:
            filtered = filtered[filtered.apply(lambda r: r.str.contains(q, case=False).any(), axis=1)]
        render_ui(filtered, category)
