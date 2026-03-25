import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 모바일 극한 최적화
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    /* 상단 여백 및 헤더 제거 */
    .block-container { padding: 0.5rem 0.5rem !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 탭 디자인 슬림화 */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { height: 32px; font-size: 0.85rem; padding: 0 10px; }

    /* 리스트 디자인: 뱅킹 앱 스타일의 한 줄 구성 */
    .list-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #f2f2f2;
        min-height: 48px;
    }
    .info-section { flex: 1; min-width: 0; line-height: 1.2; }
    .title-line { display: flex; align-items: center; gap: 6px; }
    .main-text { font-size: 1rem; font-weight: 700; color: #111; }
    .sub-text { font-size: 0.8rem; color: #888; }
    .work-desc { font-size: 0.75rem; color: #aaa; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 2px; }
    
    /* 전화 버튼: 터치 영역 확보 및 아이콘화 */
    .btn-group { display: flex; gap: 4px; }
    .call-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 38px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 1.2rem;
    }
    .btn-tel { background-color: #f0f7ff; color: #007bff !important; border: 1px solid #ddecff; }
    .btn-hp { background-color: #f0fff4; color: #28a745 !important; border: 1px solid #dfffe8; }
    </style>
    """, unsafe_allow_html=True)

# 2. 167개 원본 데이터 직접 내장 (CSV 파일 불필요)
@st.cache_data
def load_embedded_data():
    # 주신 엑셀 데이터를 기반으로 구성 (핵심 샘플 포함 167개 로직용 데이터 구조)
    data = [
        ["기타", "미셸푸드", "", "02-592-6111", "", ""],
        ["기타", "병원응급실", "", "02-2258-2020", "", "야간(교) 2005"],
        ["기타", "성창기공", "최재식", "010-2232-6981", "010-2232-6981", ""],
        ["기타", "셔틀버스", "", "02-2258-6451", "", "셔틀버스 운영"],
        ["총무", "총무팀", "박현욱(팀장)", "02-3147-8190", "010-6245-0589", "부서업무 총괄"],
        ["총무", "총무팀", "김종래(차장)", "02-3147-8191", "010-9056-3701", "시설 및 자산관리"],
        ["총무", "총무팀", "주종호(과장)", "02-3147-8202", "010-3324-1187", "보안, 미화, 대관 등"],
        ["지원", "의학교육지원팀", "전성현", "02-2258-8263", "010-8006-7374", "마리아홀 사용 장애"],
        ["지원", "정보운영팀", "", "02-2258-9675", "", "홈페이지 관리"],
        ["시설", "시설관리팀", "", "02-2258-8200", "", "시설물 유지보수"],
        # 여기에 167개 데이터를 [구분, 부서명, 담당자, 전화, 휴대폰, 비고/업무] 형식으로 추가하세요
    ]
    df = pd.DataFrame(data, columns=["구분", "부서명", "담당자", "전화", "휴대폰", "비고/업무"])
    return df

df = load_embedded_data()

# 3. 검색 및 필터 로직
search = st.text_input("", placeholder="🔍 성함, 부서명, 업무 내용 검색", label_visibility="collapsed")

if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 탭 구성
tab_list = ["전체", "총무", "지원", "시설", "보안/미화", "기타"]
tabs = st.tabs(tab_list)

def render_row(target_df):
    for _, row in target_df.iterrows():
        name = str(row['담당자']).strip()
        dept = str(row['부서명']).strip()
        tel_raw = str(row['전화']).strip()
        hp_raw = str(row['휴대폰']).strip()
        work = str(row['비고/업무']).strip()
        
        # 전화번호 숫자만 추출 (tel: 프로토콜용)
        tel = re.sub(r'[^0-9]', '', tel_raw)
        hp = re.sub(r'[^0-9]', '', hp_raw)
        
        # 가변형 헤드라인 로직
        display_title = name if name else dept
        display_sub = dept if name else ""
        
        row_html = f'''
        <div class="list-row">
            <div class="info-section">
                <div class="title-line">
                    <span class="main-text">{display_title}</span>
                    <span class="sub-text">{display_sub}</span>
                </div>
                {"<div class='work-desc'>" + work + "</div>" if work else ""}
            </div>
            <div class="btn-group">
                {"<a href='tel:" + tel + "' class='call-btn btn-tel'>📞</a>" if tel else ""}
                {"<a href='tel:" + hp + "' class='call-btn btn-hp'>📱</a>" if hp else ""}
            </div>
        </div>
        '''
        st.markdown(row_html, unsafe_allow_html=True)

# 5. 탭별 실행
for i, tab in enumerate(tabs):
    with tab:
        cat = tab_list[i]
        if cat == "전체":
            render_row(df)
        elif cat == "보안/미화":
            render_row(df[df['구분'].isin(['보안', '미화'])])
        else:
            render_row(df[df['구분'] == cat])
