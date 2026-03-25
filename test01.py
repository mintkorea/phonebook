import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 모바일 극한 최적화
st.set_page_config(page_title="성의 연락처", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0.4rem 0.6rem !important; }
    header, footer { visibility: hidden; }
    
    /* 탭 디자인: 글자 크기 축소 및 간격 최적화 */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { height: 32px; font-size: 0.8rem; padding: 0 6px; font-weight: 600; }

    /* 리스트: 한 화면 노출 극대화 (최소 높이 40px 수준) */
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
    
    /* 텍스트 액션 버튼 (아이콘 제거) */
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

# 2. 데이터 로드: 구조를 몰라도 읽어오는 방어적 로직
@st.cache_data
def load_data():
    try:
        # 파일 읽기
        df = pd.read_csv('성의교정 연락처.xlsx - Sheet1.csv')
        df = df.fillna('')
        
        # [해결책] 기존 컬럼명이 무엇이든 상관없이 우리가 쓸 이름으로 강제 교체
        # 만약 열 개수가 부족하면 부족한 대로, 남으면 남는 대로 처리
        cols = ['구분', '부서명', '담당자', '전화', '휴대폰', '비고']
        new_columns = {df.columns[i]: cols[i] for i in range(min(len(df.columns), len(cols)))}
        df.rename(columns=new_columns, inplace=True)
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 3. 검색 (데이터가 있을 때만 실행)
search = st.text_input("", placeholder="성함, 부서, 업무 검색", label_visibility="collapsed")
if search and not df.empty:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

# 4. 요청하신 탭 순서 적용
tab_titles = ["보안", "시설", "미화", "총무", "지원", "기타", "전체"]
tabs = st.tabs(tab_titles)

def render_row(target_df):
    if target_df.empty:
        st.caption("결과가 없습니다.")
        return
    
    for _, row in target_df.iterrows():
        # 데이터 추출 (KeyError 방지를 위해 위치 기반 및 dict get 혼용)
        d = row.to_dict()
        # 컬럼명이 바뀌었을 수 있으므로 안전하게 추출
        name = str(d.get('담당자', '')).strip()
        dept = str(d.get('부서명', '')).strip()
        tel_raw = str(d.get('전화', '')).strip()
        hp_raw = str(d.get('휴대폰', '')).strip()
        work = str(d.get('비고', '')).strip()
        
        # 전화연결 번호 정리 (숫자와 내선용 *만 남김)
        tel_link = re.sub(r'[^0-9*]', '', tel_raw)
        hp_link = re.sub(r'[^0-9]', '', hp_raw)
        
        # 헤드라인 결정
        title = name if name else dept
        sub = dept if name else ""
        
        st.markdown(f'''
        <div class="list-row">
            <div class="info-section">
                <div class="title-line">
                    <span class="main-text">{title}</span>
                    <span class="sub-text">{sub}</span>
                </div>
                {"<div class='work-desc'>" + work + "</div>" if work else ""}
            </div>
            <div class="btn-group">
                {"<a href='tel:" + tel_link + "' class='action-btn btn-tel'>내선</a>" if tel_link else ""}
                {"<a href='tel:" + hp_link + "' class='action-btn btn-hp'>직통</a>" if hp_link else ""}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# 5. 탭별 필터링 실행
for i, tab in enumerate(tabs):
    with tab:
        cat_name = tab_titles[i]
        if df.empty:
            st.error("데이터를 불러오지 못했습니다. 파일명을 확인해주세요.")
        elif cat_name == "전체":
            render_row(df)
        else:
            # [가장 강력한 필터링] 어느 열에서든 해당 단어가 포함되어 있으면 표시
            # 특정 열('구분')이 깨져서 못 찾는 상황을 원천 방지함
            mask = df.apply(lambda x: x.astype(str).str.contains(cat_name, na=False)).any(axis=1)
            render_row(df[mask])
