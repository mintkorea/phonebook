import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 스타일 (모바일 최적화)
st.set_page_config(page_title="성의교정 Workplace Hub", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .contact-card {
        background-color: white; padding: 15px; border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px;
    }
    .phone-text { color: #ff4b4b; font-weight: bold; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# 2. 통합 데이터 세팅 (이미지 및 PDF 내용 반영) [cite: 1, 2, 3, 6]
data = [
    {"분류": "누수", "상황": "소량 누수", "부서": "설비팀", "번호": "*1-5624", "비고": "FMS 등록 필수"},
    {"분류": "누수", "상황": "대량/소방 누수", "부서": "전기팀", "번호": "*1-5672", "비고": "통합관제 병행"},
    {"분류": "승강기", "상황": "EV 고장 (주간)", "부서": "반송통제실", "번호": "*1-5616", "비고": "탑승자 명단 기록"},
    {"분류": "승강기", "상황": "EV 고장 (야간)", "부서": "FMLG", "번호": "1899-7144", "비고": ""},
    {"분류": "시설", "상황": "자동문/장애인화장실/공조", "부서": "통합관제", "번호": "2258-5555", "비고": "중앙 공조기 포함"},
    {"분류": "시설", "상황": "카드문/CCTV/인터넷", "부서": "통신팀", "번호": "*1-5712", "비고": ""},
    {"분류": "냉난방", "상황": "개별 냉방기 고장", "부서": "설비팀", "번호": "*1-5624", "비고": ""},
    {"분류": "IT", "상황": "PC고장/컴퓨터AS", "부서": "정보지원팀", "번호": "*1-5820", "비고": "(교) 5824"},
    {"분류": "관리", "상황": "보안 소장", "부서": "보안", "성명": "이용춘", "번호": "010-6213-8502", "비고": "내선 8300"},
    {"분류": "미화", "상황": "미화 소장", "부서": "미화", "성명": "신성휴", "번호": "010-7161-2201", "비고": "내선 9102"},
    {"분류": "기타", "상황": "셔틀버스/주차", "부서": "관리", "번호": "*1-6451", "비고": "주차:*1-6000"},
]

df = pd.DataFrame(data)

# 3. 사이드바 및 상단 안내
st.title("📞 성의교정 비상연락망")
st.info("💡 미화팀/임직원 수리 요청 시 FMS 등록 후 조장에게 보고하세요. ")

# 4. 검색 및 필터링 기능
col_search, col_filter = st.columns([2, 1])
with col_search:
    search = st.text_input("🔍 상황, 부서, 성명 검색", placeholder="예: 누수, 이용춘, 전기")
with col_filter:
    category = st.selectbox("분류", ["전체"] + list(df["분류"].unique()))

# 데이터 필터링 로직
filtered_df = df.copy()
if search:
    filtered_df = filtered_df[filtered_df.apply(lambda row: search in str(row.values), axis=1)]
if category != "전체":
    filtered_df = filtered_df[filtered_df["분류"] == category]

# 5. 결과 출력 (모바일 카드 레이아웃)
if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="contact-card">
                    <small style="color:gray;">{row['분류']} | {row['부서']}</small><br>
                    <strong>{row['상황']}</strong> {f"({row['성명']})" if '성명' in row and pd.notna(row['성명']) else ""}<br>
                    <span class="phone-text">{row['번호']}</span><br>
                    <small>{row['비고']}</small>
                    <hr style="margin:10px 0;">
                    <a href="tel:{row['번호'].replace('*', '').replace('-', '')}" style="text-decoration: none;">
                        <button style="width:100%; background-color:#28a745; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">
                            즉시 전화걸기
                        </button>
                    </a>
                </div>
            """, unsafe_allow_html=True)
else:
    st.warning("검색 결과가 없습니다.")

# 6. 하단 고정 정보 (착신전환 등) 
st.divider()
st.subheader("📌 주요 단축키")
st.code("착신전환 : #1 + 번호 / 착신해제 : #2")
