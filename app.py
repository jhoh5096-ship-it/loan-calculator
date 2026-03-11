import streamlit as st
from datetime import date

# 1. 페이지 설정 및 디자인 CSS
st.set_page_config(page_title="검단 중흥S-클래스 계산기", layout="wide")

st.markdown("""
    <style>
    /* 제목 폰트: 두 줄 구성 및 모바일 최적화 */
    .main-title {
        font-size: 22px !important;
        font-weight: 800;
        color: #1E1E1E;
        line-height: 1.3;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 20px !important;
        font-weight: 700;
        color: #2E5A9E; /* 포인트 컬러 */
        margin-bottom: 15px;
    }
    /* 최종 정산 결과 폰트 크기 수정 */
    .result-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .result-label {
        font-size: 16px !important;
        font-weight: 600;
        color: #495057;
    }
    .result-value {
        font-size: 22px !important;
        font-weight: 800;
        color: #d9534f; /* 강조색 */
    }
    /* 안내 문구 */
    .info-text {
        font-size: 13px;
        color: #666;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 제목 (2줄 구성)
st.markdown('<p class="main-title">🏢 검단 중흥S-클래스</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">중도금대출 통합 이자 계산기</p>', unsafe_allow_html=True)
st.markdown('<p class="info-text">※ 타입 선택 시 분양가와 회차별 일정이 자동으로 세팅됩니다.</p>', unsafe_allow_html=True)

# 3. 아파트 데이터 설정
TYPE_DATA = {
    "72A": 435000000, "72B": 421000000,
    "84A": 498000000, "84B": 484000000,
    "101": 594000000, "147": 1110000000
}

FIXED_DATES = [
    date(2024, 6, 3), date(2025, 2, 3), date(2025, 10, 3),
    date(2026, 5, 3), date(2026, 10, 3), date(2027, 3, 3)
]

# 4. 사이드바 설정
st.sidebar.header("📋 타입 선택")
selected_type = st.sidebar.selectbox("타입을 선택하세요", list(TYPE_DATA.keys()))
total_price = TYPE_DATA[selected_type]
each_loan = int(total_price * 0.1)

st.sidebar.divider()
st.sidebar.write(f"**선택:** {selected_type} 타입")
st.sidebar.write(f"**분양가:** {total_price:,} 원")
st.sidebar.write(f"**회차별 원금:** {each_loan:,} 원")

# 5. 계산 함수
def calculate_interest(exec_date, amount, rate, rep_amt, rep_date):
    today = date.today()
    if exec_date > today: return 0, amount, 0
    
    if rep_amt == 0:
        days = (today - exec_date).days
        interest = (amount * (rate / 100) * days) / 365
        return int(interest), amount, days
    else:
        days_before = (rep_date - exec_date).days
        interest_before = (amount * (rate / 100) * days_before) / 365
        days_after = (today - rep_date).days
        rem_principal = amount - rep_amt
        interest_after = (rem_principal * (rate / 100) * days_after) / 365
        return int(interest_before + interest_after), rem_principal, (days_before + days_after)

# 6. 메인 회차별 입력창
total_all_interest = 0
total_remaining_principal = 0

for i in range(6):
    with st.expander(f"📍 {i+1}회차 ({FIXED_DATES[i].strftime('%Y-%m-%d')})", expanded=(i<2)):
        c1, c2 = st.columns(2)
        with c1:
            e_date = st.date_input(f"실행일_{i+1}", value=FIXED_DATES[i], key=f"d_{i}")
            amt = st.number_input(f"금액_{i+1}", value=each_loan, step=10000, key=f"a_{i}")
            curr_rate = st.number_input(f"금리(%)_{i+1}", value=4.5, step=0.1, key=f"r_{i}")
        with c2:
            r_amt = st.number_input(f"상환액_{i+1}", value=0, step=1000000, key=f"rp_{i}")
            r_date = st.date_input(f"상환일_{i+1}", value=date.today(), key=f"rd_{i}")
        
        interest, remain, elapsed = calculate_interest(e_date, amt, curr_rate, r_amt, r_date)
        
        if e_date > date.today():
            st.info("실행 예정 회차")
        else:
            st.success(f"경과: {elapsed}일 | 이자: {interest:,}원")
            total_all_interest += interest
            total_remaining_principal += remain

# 7. 최종 정산 결과 (폰트 크기 조정 적용)
st.divider()
st.markdown('<p style="font-size:18px; font-weight:bold;">📊 최종 정산 결과 (오늘 기준)</p>', unsafe_allow_html=True)

res_c1, res_c2 = st.columns(2)
with res_c1:
    st.markdown(f"""
        <div class="result-container">
            <p class="result-label">오늘까지 총 이자</p>
            <p class="result-value">{total_all_interest:,} 원</p>
        </div>
    """, unsafe_allow_html=True)
with res_c2:
    st.markdown(f"""
        <div class="result-container">
            <p class="result-label">총 잔여 원금</p>
            <p class="result-value">{total_remaining_principal:,} 원</p>
        </div>
    """, unsafe_allow_html=True)
