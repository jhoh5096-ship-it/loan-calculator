import streamlit as st
from datetime import date

# 1. 페이지 설정
st.set_page_config(page_title="검단 중흥S-클래스 계산기", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 22px !important; font-weight: 800; color: #1E1E1E; line-height: 1.3; margin-bottom: 5px; }
    .sub-title { font-size: 20px !important; font-weight: 700; color: #2E5A9E; margin-bottom: 15px; }
    .result-container { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; }
    .result-label { font-size: 16px !important; font-weight: 600; color: #495057; }
    .result-value { font-size: 22px !important; font-weight: 800; color: #d9534f; }
    /* 모바일 사이드바 안내 문구 */
    .sidebar-guide { font-size: 14px; color: #d9534f; font-weight: bold; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 제목 (2줄)
st.markdown('<p class="main-title">🏢 검단 중흥S-클래스</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">중도금대출 통합 이자 계산기</p>', unsafe_allow_html=True)

# 모바일 사용자용 사이드바 안내 추가
st.markdown('<p class="sidebar-guide">👈 왼쪽 상단 화살표(> )를 눌러 "타입 선택"을 먼저 해주세요!</p>', unsafe_allow_html=True)

# 3. 데이터 설정
TYPE_DATA = {
    "72A": 435000000, "72B": 421000000,
    "84A": 498000000, "84B": 484000000,
    "101": 594000000, "147": 1110000000
}

FIXED_DATES = [
    date(2024, 6, 3), date(2025, 2, 3), date(2025, 10, 3),
    date(2026, 5, 3), date(2026, 10, 3), date(2027, 3, 3)
]

# 4. 사이드바 (문구 강조)
st.sidebar.markdown("### 🏠 타입 선택하기")
selected_type = st.sidebar.selectbox("아래에서 타입을 고르세요", list(TYPE_DATA.keys()))
total_price = TYPE_DATA[selected_type]
each_loan = int(total_price * 0.1)

st.sidebar.divider()
st.sidebar.info(f"**현재 선택:** {selected_type} 타입\n\n**분양가:** {total_price:,} 원\n\n**회차별 대출금:** {each_loan:,} 원")

# 5. 이자 계산 함수
def calculate_flexible_interest(start_date, amount, base_rate, changes, rep_amt, rep_date):
    today = date.today()
    if start_date > today: return 0, amount
    
    timeline = [{'date': start_date, 'rate': base_rate}]
    for c_date, c_rate in changes:
        if start_date < c_date < today:
            timeline.append({'date': c_date, 'rate': c_rate})
    
    timeline.sort(key=lambda x: x['date'])
    timeline.append({'date': today})
    
    total_int = 0
    curr_principal = amount
    
    for i in range(len(timeline)-1):
        d1 = timeline[i]['date']
        d2 = timeline[i+1]['date']
        r = timeline[i].get('rate', base_rate)
        
        if rep_amt > 0 and d1 <= rep_date < d2:
            days_pre = (rep_date - d1).days
            total_int += (curr_principal * (r/100) * days_pre) / 365
            curr_principal -= rep_amt
            days_post = (d2 - rep_date).days
            total_int += (curr_principal * (r/100) * days_post) / 365
        else:
            days = (d2 - d1).days
            total_int += (curr_principal * (r/100) * days) / 365
            
    return int(total_int), curr_principal

# 6. 메인 화면 구성
total_all_interest = 0
total_remaining_principal = 0

for i in range(6):
    with st.expander(f"📍 {i+1}회차 ({FIXED_DATES[i].strftime('%Y-%m-%d')})", expanded=(i<2)):
        c1, c2 = st.columns(2)
        with c1:
            e_date = st.date_input(f"실행일_{i+1}", value=FIXED_DATES[i], key=f"d_{i}")
            amt = st.number_input(f"금액_{i+1}", value=each_loan, step=10000, key=f"a_{i}")
            b_rate = st.number_input(f"최초금리(%)_{i+1}", value=4.5, step=0.1, key=f"r_{i}")
        with c2:
            r_amt = st.number_input(f"중도상환액_{i+1}", value=0, key=f"rp_{i}")
            r_date = st.date_input(f"상환일_{i+1}", value=date.today(), key=f"rd_{i}")

        st.caption("📉 금리 변경 기록 (있는 경우만)")
        ch1, ch2 = st.columns(2)
        c_date = ch1.date_input(f"변경일_{i+1}", value=FIXED_DATES[i], key=f"cd_{i}")
        c_rate = ch2.number_input(f"변경금리(%)_{i+1}", value=b_rate, key=f"cr_{i}")
        
        changes = [(c_date, c_rate)] if c_rate != b_rate else []
        interest, remain = calculate_flexible_interest(e_date, amt, b_rate, changes, r_amt, r_date)
        
        if e_date > date.today():
            st.info("실행 예정 회차")
        else:
            st.success(f"이자 합계: **{interest:,}원**")
            total_all_interest += interest
            total_remaining_principal += remain

# 7. 최종 결과
st.divider()
st.markdown('<p style="font-size:18px; font-weight:bold;">📊 최종 정산 결과 (오늘 기준)</p>', unsafe_allow_html=True)
res_c1, res_c2 = st.columns(2)
with res_c1:
    st.markdown(f'<div class="result-container"><p class="result-label">오늘까지 총 이자</p><p class="result-value">{total_all_interest:,} 원</p></div>', unsafe_allow_html=True)
with res_c2:
    st.markdown(f'<div class="result-container"><p class="result-label">총 잔여 원금</p><p class="result-value">{total_remaining_principal:,} 원</p></div>', unsafe_allow_html=True)
