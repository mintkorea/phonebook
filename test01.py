import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 모바일 극한 최적화
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.4rem 0.6rem !important; }
    header, footer { visibility: hidden; }
    
    /* 탭 디자인: 텍스트 강조 및 간격 축소 */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { height: 32px; font-size: 0.8rem; padding: 0 6px; font-weight: 600; }

    /* 리스트: 한 줄 높이 최소화 (한 화면 노출 극대화) */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #f2f2f2;
        min-height: 42px;
    }
    .info-section { flex: 1; min-width: 0; line-height: 1.1; }
    .title-line { display: flex; align-items: baseline; gap: 5px; }
    .main-text { font-size: 0.95rem; font-weight: 700; color: #111; }
    .sub-text { font-size: 0.75rem; color: #777; white-space: nowrap; }
    .work-desc { font-size: 0.7rem; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 1px; }
    
    /* 텍스트 액션 버튼 디자인 */
    .btn-group { display: flex; gap: 4px; }
    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 10px;
        height: 30px;
        border-radius: 4px;
        text-decoration: none !important;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .btn-tel { background-color: #fff; color: #007bff !important; border: 1px solid #007bff; }
    .btn-hp { background-color: #007bff; color: #fff !important; border: 1px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 직접 내장 및 정규화 (에러 원천 차단)
@st.cache_data
def load_data():
    # 구글 시트의 최신 데이터를 기반으로 구성
    data = [
        ["기타", "미셸푸드", "", "02-592-6111", "", ""],
        ["기타", "병원응급실", "", "02-2258-2020", "", "주간 2020, 야간(교) 2005"],
        ["기타", "성창기공", "최재식", "010-2232-6981", "010-2232-6981", ""],
        ["기타", "셔틀버스", "", "*1-6451", "", "셔틀버스 운영"],
        ["총무", "총무팀", "박현욱(팀장)", "02-3147-8190", "010-6245-0589", "부서업무 총괄"],
        ["총무", "총무팀", "김종래(차장)", "02-3147-8191", "010-9056-3701", "시설 및 자산관리"],
        ["총무", "총무팀", "주종호(과장)", "02-3147-8202", "010-3324-1187", "보안, 미화, 대관"],
        ["지원", "의학교육지원팀", "전성현", "8263", "010-8006-7374", "마리아홀 사용 장애"],
        ["지원", "정보운영팀", "", "9675", "", "홈페이지(성의정보 Unit)"],
        ["시설", "시설관리팀", "", "8200", "", "시설물 유지보수"],
    ]
    df = pd.DataFrame(data, columns=['구분', '부서명', '담당자', '전화', '휴대폰', '비고'])
    return df.fillna('')

df = load_data()

# 3. 검색 기능
search = st.text_input("", placeholder="성함, 부서, 업무 검색", label_visibility="collapsed")
if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 요청하신 탭 순서 (보안 -> 시설 -> 미화 -> 총무 -> 지원 -> 기타 -> 전체)
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_row(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    for _, row in target_df.iterrows():
        d = row.to_dict()
        name, dept, tel_raw, hp_raw, work = str(d.get('담당자','')), str(d.get('부서명','')), str(d.get('전화','')), str(d.get('휴대폰','')), str(d.get('비고',''))
        
        # 전화연결 번호 정리 (내선번호용 * 유지)
        tel_link = re.sub(r'[^0-9*]', '', tel_raw)
        hp_link = re.sub(r'[^0-9]', '', hp_raw)
        
        title, sub = (name, dept) if name else (dept, "")
        
        st.markdown(f'''
        <div class="list-row">
            <div class="info-section">
                <div class="title-line"><span class="main-text">{title}</span><span class="sub-text">{sub}</span></div>
                {"<div class='work-desc'>" + work + "</div>" if work.strip() else ""}
            </div>
            <div class="btn-group">
                {"<a href='tel:" + tel_link + "' class='action-btn btn-tel'>내선</a>" if tel_link else ""}
                {"<a href='tel:" + hp_link + "' class='action-btn btn-hp'>직통</a>" if hp_link else ""}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# 5. 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_titles[i]
        if cat == "전체":
            render_row(df)
        else:
            # 어느 열에서든 해당 단어가 포함되어 있으면 표시 (에러 방지용 전방위 검색)
            mask = df.apply(lambda x: x.astype(str).str.contains(cat, na=False)).any(axis=1)
            render_row(df[mask])
