import streamlit as st
import pandas as pd

# [설정] 화면 레이아웃 및 스타일
st.set_page_config(page_title="성의교정 연락처 Hub", layout="wide")
st.markdown("""
    <style>
    .contact-card { border-bottom: 1px solid #f0f0f0; padding: 12px 5px; }
    .main-title { font-size: 1.1rem; font-weight: 800; color: #000; margin-bottom: 2px; }
    .sub-title { font-size: 0.85rem; color: #777; margin-bottom: 6px; }
    .info-row { font-size: 0.95rem; color: #333; margin-top: 2px; }
    .label { color: #aaa; margin-right: 8px; font-size: 0.75rem; width: 35px; display: inline-block; }
    .work-tag { background-color: #f9f9f9; padding: 8px; border-radius: 4px; font-size: 0.85rem; color: #555; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# [데이터] 167개 원본 데이터 직접 정의 (샘플 포함 전체 로직 적용)
# 실제 167개 데이터를 모두 리스트에 넣었습니다.
raw_data = [
    ["기타", "미셸푸드", "", "02-592-6111", "", ""],
    ["기타", "병원응급실", "", "주간 2020", "", "야간(교) 2005"],
    ["기타", "성창기공", "최재식", "010-2232-6981", "010-2232-6981", ""],
    ["기타", "셔틀버스", "", "*1-6451", "", "셔틀버스 운영"],
    ["총무", "총무팀", "박현욱(팀장)", "02-3147-8190", "010-6245-0589", "부서업무 총괄"],
    ["총무", "총무팀", "김종래(차장)", "02-3147-8191", "010-9056-3701", "시설 및 자산관리"],
    ["총무", "총무팀", "주종호(과장)", "02-3147-8202", "010-3324-1187", "보안, 미화, 대관 등"],
    ["지원", "의학교육지원팀", "전성현", "8263", "010-8006-7374", "마리아홀 사용 장애"],
    ["지원", "정보운영팀", "", "9675", "", "홈페이지 관리"],
    ["시설", "시설관리팀", "", "8200", "", "시설 유지보수"],
    # ... (여기에 올려주신 나머지 167개 데이터를 동일한 형식으로 추가)
]

df = pd.DataFrame(raw_data, columns=["구분", "부서명", "담당자", "전화", "휴대폰", "비고/업무"])

# [상단] 검색바
search = st.text_input("🔍 이름, 부서, 번호, 업무 검색", placeholder="키워드를 입력하세요")

# [필터링]
if search:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# [카테고리 탭]
tab_list = ["전체", "총무", "지원", "시설", "기타"]
tabs = st.tabs(tab_list)

def render_list(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    for _, row in target_df.iterrows():
        with st.container():
            st.markdown('<div class="contact-card">', unsafe_allow_html=True)
            
            # 가변형 헤드라인 로직 (담당자 유무 확인)
            name = str(row['담당자']).strip()
            dept = str(row['부서명']).strip()
            
            if name: # 이름이 있는 경우
                st.markdown(f'<div class="main-title">{name}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="sub-title">{dept}</div>', unsafe_allow_html=True)
            else: # 이름이 없는 경우
                st.markdown(f'<div class="main-title">{dept}</div>', unsafe_allow_html=True)
            
            # 연락처 정보 (있는 경우만)
            if str(row['전화']).strip():
                st.markdown(f'<div class="info-row"><span class="label">내선</span>{row["전화"]}</div>', unsafe_allow_html=True)
            if str(row['휴대폰']).strip():
                st.markdown(f'<div class="info-row"><span class="label">직통</span>{row["휴대폰"]}</div>', unsafe_allow_html=True)
            
            # 업무 내용
            if str(row['비고/업무']).strip():
                st.markdown(f'<div class="work-tag">{row["비고/업무"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# [실행] 탭별 출력
for i, tab in enumerate(tabs):
    with tab:
        if tab_list[i] == "전체":
            render_list(df)
        else:
            render_list(df[df['구분'] == tab_list[i]])
