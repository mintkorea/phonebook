import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
import io

# 1. 페이지 설정 및 디자인 (PC 버전 고정)
st.set_page_config(page_title="성의교정 대관 현황(PC)", page_icon="🏫", layout="wide")
KST = pytz.timezone('Asia/Seoul')
now_today = datetime.now(KST).date()

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .main .block-container {
        max-width: 1200px; 
        margin: 0 auto;
        padding: 0.5rem 1rem !important;
    }
    .main-title { font-size: 26px; font-weight: bold; color: #1E3A5F; text-align: center; margin-bottom: 15px; }
    .date-bar { background-color: #343a40; color: white; padding: 12px; border-radius: 6px; text-align: center; font-weight: bold; margin-top: 35px; margin-bottom: 15px; font-size: 17px; }
    .bu-header { font-size: 18px; font-weight: bold; color: #1E3A5F; margin: 15px 0 8px 0; border-left: 6px solid #1E3A5F; padding-left: 12px; background: #f1f4f9; padding: 7px 12px; }
    .mobile-card { background: white; border: 1px solid #eef0f2; border-radius: 6px; padding: 10px 15px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .row-1 { display: flex; align-items: center; width: 100%; }
    .loc-text { font-size: 15px; font-weight: 800; color: #1E3A5F; flex: 1; }
    .time-text { font-size: 14px; font-weight: 700; color: #e74c3c; margin-left: auto; margin-right: 10px; }
    .status-badge { padding: 3px 8px; border-radius: 4px; font-size: 11px; color: white; font-weight: bold; background-color: #2ecc71; }
    .row-2 { font-size: 13px; color: #333; border-top: 1px solid #f8f9fa; padding-top: 7px; margin-top: 7px; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# 2. 엑셀 생성 함수 (날짜 변경 시 여백 강화)
def create_excel(df, selected_bu, start_date, end_date):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('성의교정대관현황')
        
        # 서식 설정
        title_fmt = workbook.add_format({'bold': True, 'size': 18, 'align': 'center', 'valign': 'vcenter'})
        date_sep_fmt = workbook.add_format({'bold': True, 'bg_color': '#343a40', 'font_color': 'white', 'align': 'center', 'border': 1})
        bu_sep_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'font_color': '#1E3A5F', 'align': 'left', 'border': 1})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2', 'align': 'center', 'border': 1})
        content_fmt = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True, 'size': 10})

        # 컬럼 너비 설정
        widths = [25, 15, 45, 25, 10, 10]
        for i, w in enumerate(widths): worksheet.set_column(i, i, w)
        
        # 타이틀
        worksheet.merge_range('A1:F1', "성의교정 대관 현황", title_fmt)
        worksheet.set_row(0, 35)
        
        row_idx = 2
        curr = start_date
        while curr <= end_date:
            d_str = curr.strftime('%Y-%m-%d')
            day_df = df[df['full_date'] == d_str]
            
            # [수정] 날짜 구분선 전에 빈 행 추가 (첫 날짜 제외)
            if curr > start_date:
                row_idx += 2 # 날짜가 바뀔 때 빈 행 2줄 삽입 (여백 확보)

            # 날짜 구분선
            worksheet.merge_range(row_idx, 0, row_idx, 5, f"📅 {d_str}", date_sep_fmt)
            worksheet.set_row(row_idx, 22)
            row_idx += 1
            
            for bu in BUILDING_ORDER:
                if bu in selected_bu:
                    b_df = day_df[day_df['건물명'].str.replace(" ","") == bu.replace(" ","")]
                    
                    # 건물명 구분선
                    worksheet.merge_range(row_idx, 0, row_idx, 5, f"🏢 {bu} ({len(b_df)}건)", bu_sep_fmt)
                    worksheet.set_row(row_idx, 20)
                    row_idx += 1
                    
                    # 헤더
                    headers = ['장소', '시간', '행사명', '부서', '인원', '상태']
                    for col, h in enumerate(headers): worksheet.write(row_idx, col, h, header_fmt)
                    row_idx += 1
                    
                    # 데이터 내용
                    if not b_df.empty:
                        for _, r in b_df.sort_values('시간').iterrows():
                            worksheet.set_row(row_idx, 30)
                            worksheet.write_row(row_idx, 0, [r['장소'], r['시간'], r['행사명'], r['부서'], r['인원'], r['상태']], content_fmt)
                            row_idx += 1
                    
                    row_idx += 1 # 건물 간 여백 1줄
            curr += timedelta(days=1)
            
    return output.getvalue()

BUILDING_ORDER = ["성의회관", "의생명산업연구원", "옴니버스 파크", "옴니버스파크 의과대학", "옴니버스파크 간호대학", "대학본관", "서울성모별관"]
WEEKDAYS = ["", "월", "화", "수", "목", "금", "토", "일"]

def get_shift(target_date):
    base_date = date(2026, 3, 13)
    diff = (target_date - base_date).days
    return f"{['A', 'B', 'C'][diff % 3]}조"

@st.cache_data(ttl=60)
def get_data(start_date, end_date):
    url = "https://songeui.catholic.ac.kr/ko/service/application-for-rental_calendar.do"
    params = {"mode": "getReservedData", "start": start_date.isoformat(), "end": end_date.isoformat()}
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        raw, rows = res.json().get('res', []), []
        for item in raw:
            if not item.get('startDt'): continue
            s_dt = datetime.strptime(item['startDt'], '%Y-%m-%d').date()
            e_dt = datetime.strptime(item['endDt'], '%Y-%m-%d').date()
            allowed = [d.strip() for d in str(item.get('allowDay', '')).split(",") if d.strip().isdigit()]
            curr = s_dt
            while curr <= e_dt:
                if start_date <= curr <= end_date:
                    if not allowed or str(curr.isoweekday()) in allowed:
                        rows.append({
                            'full_date': curr.strftime('%Y-%m-%d'), 
                            '건물명': str(item.get('buNm', '')).strip(), 
                            '장소': item.get('placeNm', '') or '-', 
                            '시간': f"{item.get('startTime', '')}~{item.get('endTime', '')}", 
                            '행사명': item.get('eventNm', '') or '-', 
                            '부서': item.get('mgDeptNm', '') or '-', 
                            '인원': str(item.get('peopleCount', '0')), 
                            '상태': '확정' if item.get('status') == 'Y' else '대기'
                        })
                curr += timedelta(days=1)
        return pd.DataFrame(rows)
    except: return pd.DataFrame()

# 3. 메인 화면
st.markdown('<div class="main-title">🏫 성의교정 대관 현황 (PC버전)</div>', unsafe_allow_html=True)

with st.expander("🔍 조회 기간 설정 및 엑셀 다운로드", expanded=True):
    c1, c2, c3 = st.columns([1.5, 2, 1])
    with c1:
        s_date = st.date_input("시작일", value=now_today)
        e_date = st.date_input("종료일", value=s_date + timedelta(days=1))
    with c2:
        sel_bu = st.multiselect("건물 선택", options=BUILDING_ORDER, default=["성의회관", "의생명산업연구원"])
    with c3:
        view_mode = st.radio("화면 출력", ["카드 형태", "표 형태"], horizontal=True)
        df = get_data(s_date, e_date)
        if not df.empty:
            st.download_button(
                label="📥 인쇄용 엑셀 다운로드", 
                data=create_excel(df, sel_bu, s_date, e_date), 
                file_name=f"대관현황_{s_date}_{e_date}.xlsx", 
                use_container_width=True
            )

# 4. 리스트 출력
if not df.empty:
    curr = s_date
    while curr <= e_date:
        d_str = curr.strftime('%Y-%m-%d')
        day_df = df[df['full_date'] == d_str]
        st.markdown(f'<div class="date-bar">📅 {d_str} ({WEEKDAYS[curr.isoweekday()]}요일) | 근무: {get_shift(curr)}</div>', unsafe_allow_html=True)
        for bu in BUILDING_ORDER:
            if bu in sel_bu:
                b_df = day_df[day_df['건물명'].str.replace(" ","") == bu.replace(" ","")]
                st.markdown(f'<div class="bu-header">🏢 {bu} ({len(b_df)}건)</div>', unsafe_allow_html=True)
                if not b_df.empty:
                    if view_mode == "표 형태":
                        st.dataframe(b_df[['장소', '시간', '행사명', '부서', '인원', '상태']].sort_values('시간'), hide_index=True, use_container_width=True)
                    else:
                        for _, r in b_df.sort_values('시간').iterrows():
                            st.markdown(f'<div class="mobile-card"><div class="row-1"><span class="loc-text">📍 {r["장소"]}</span><span class="time-text">🕒 {r["시간"]}</span><span class="status-badge">{"확정" if r["상태"]=="확정" else "대기"}</span></div><div class="row-2"><b>{r["행사명"]}</b> | {r["부서"]} ({r["인원"]}명)</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#999; font-size:13px; text-align:center; padding:10px; border:1px dashed #eee;">내역 없음</div>', unsafe_allow_html=True)
        curr += timedelta(days=1)
else:
    st.info("조회 기간에 대관 데이터가 없습니다.")