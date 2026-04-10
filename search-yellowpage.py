import streamlit as st
import pandas as pd
import re

# 1. 스타일 설정 (부서명 130px / 번호 가변 / 아이콘 60px)
st.set_page_config(page_title="성의교정 통합 지원포털", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    .block-container { padding: 1rem !important; max-width: 500px !important; margin: 0 auto; font-family: 'Pretendard', sans-serif; }
    
    .phone-item { 
        border-bottom: 1px solid #f1f5f9; 
        padding: 10px 0; 
        display: flex;
        flex-direction: column; 
    }
    
    .top-line { 
        display: flex; 
        align-items: center; 
        width: 100%;
        gap: 2px;
    }
    
    /* [확정] 1구역: 부서명 영역 130px 고정 */
    .name-area { 
        width: 130px !important; 
        min-width: 130px !important;
        flex-shrink: 0;
    }
    .name-text { 
        font-size: 15px; 
        font-weight: 800; 
        color: #0f172a; 
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis; 
    }
    
    /* 2구역: 전화번호 영역 (중앙 가변 공간) */
    .num-area { 
        flex: 1; 
        text-align: right; 
        padding-right: 6px;
        min-width: 0;
    }
    .num-text { font-size: 14px; font-weight: 700; color: #334155; white-space: nowrap; }
    .special-navy { color: #1e3a8a !important; font-style: italic !important; font-weight: 800 !important; }
    
    /* 3구역: 아이콘 영역 (60px 고정 및 우측 끝 정렬) */
    .icon-area { 
        width: 60px !important; 
        min-width: 60px !important;
        display: flex; 
        justify-content: flex-end; 
        gap: 4px;
        flex-shrink: 0;
    }

    /* 아이콘 디자인 (축소 사이즈 24px 유지) */
    .btn-icon { 
        text-decoration: none !important; background: #f8fafc; color: #475569 !important; 
        border: 1px solid #e2e8f0; width: 24px; height: 24px; 
        display: flex; align-items: center; justify-content: center; 
        border-radius: 4px; font-weight: 800; font-size: 10px; flex-shrink: 0;
    }
    .btn-m { background: #ecfdf5; color: #059669 !important; border-color: #d1fae5; }

    /* 비고 영역 */
    .bottom-line { margin-top: 3px; width: 100%; }
    .work-text { font-size: 12px; color: #10b981; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 처리 함수
def get_chosung(text):
    if not text: return ""
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    res = ""
    for char in str(text):
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            idx = (code - 0xAC00) // 588
            res += CHOSUNG_LIST[idx]
        else: res += char
    return res

def parse_sort_key(val):
    nums = re.findall(r'\d+', str(val))
    return [int(n) for n in nums] if nums else [999]

@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpOX8Ll6no4uXd5jnK0umTY3U_eKZXcDK2z_f2EsxSQDuOqk4YGzNkULJn_WgjTFBUseCbl6smBh0Z/pub?gid=1424582869&single=true&output=csv"
    try:
        df = pd.read_csv(url).fillna('').astype(str).apply(lambda x: x.str.strip())
        df.columns = ['cat', 'dept', 'name', 'tel', 'hp', 'work']
        df['sort_key'] = df['cat'].apply(parse_sort_key)
        df = df.sort_values(by='sort_key').drop(columns=['sort_key']).reset_index(drop=True)
        df['search_text'] = df['name'] + " " + df['dept'] + " " + df['work']
        df['cho'] = df['search_text'].apply(get_chosung)
        return df
    except: return pd.DataFrame()

# 3. 메인 로직
df = load_data()
q = st.text_input("🔍 검색 (성함, 부서, 업무, 초성)", placeholder="예: 보안, 시설, ㅂㅇ")

tabs = st.tabs(["전체", "보안", "시설", "미화", "총무", "지원", "기타"])
categories = ["전체", "보안", "시설", "미화", "총무", "지원", "기타"]

for i, cat in enumerate(categories):
    with tabs[i]:
        fdf = df if cat == "전체" else df[df['cat'].str.contains(cat) | df['dept'].str.contains(cat)]
        if q:
            is_cho = all('ㄱ' <= c <= 'ㅎ' or c == " " for c in q)
            fdf = fdf[fdf['cho'].str.contains(q.replace(" ", ""))] if is_cho else fdf[fdf['search_text'].str.contains(q)]

        for _, r in fdf.iterrows():
            d_name = r['name'] if r['name'] else r['dept']
            d_work = "" if r['work'] == r['dept'] or r['work'] == r['name'] else r['work']
            
            n_html = ""
            t_icon = ""
            if r['tel'] and r['tel'].lower() != 'nan':
                tel_val = r['tel']
                disp_num = tel_val.replace('02-3147-', '').replace('02-2258-', '')
                n_style = "num-text special-navy" if ("*1" in tel_val or "2258" in tel_val) else "num-text"
                clean_tel = re.sub(r'[^0-9*]', '', tel_val)
                t_url = f"tel:022258{clean_tel.replace('*1','')}" if "*1" in clean_tel else (f"tel:023147{clean_tel}" if len(clean_tel)==4 else f"tel:{clean_tel}")
                n_html = '<span class="' + n_style + '">' + disp_num + '</span>'
                t_icon = '<a href="' + t_url + '" class="btn-icon">T</a>'
            
            m_icon = ""
            if r['hp'] and r['hp'].lower() != 'nan':
                hp_num = re.sub(r'[^0-9]', '', r['hp'])
                m_icon = '<a href="tel:' + hp_num + '" class="btn-icon btn-m">M</a>'

            # 확정된 3구역 분할 적용 (130px / 가변 / 60px)
            item_html = (
                '<div class="phone-item">'
                '<div class="top-line">'
                '  <div class="name-area"><div class="name-text">' + d_name + '</div></div>'
                '  <div class="num-area">' + n_html + '</div>'
                '  <div class="icon-area">' + t_icon + m_icon + '</div>'
                '</div>'
                '<div class="bottom-line"><div class="work-text">' + d_work + '</div></div>'
                '</div>'
            )
            st.markdown(item_html, unsafe_allow_html=True)