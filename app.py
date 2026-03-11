import streamlit as st
from datetime import date

st.set_page_config(page_title="검단 중도금 이자 계산기", layout="wide")

# 1. 아파트 데이터 설정
TYPE_DATA = {
    "72A": 435000000,
    "72B": 421000000,
    "84A": 498000000,
    "84B": 484000000,
    "101": 594000000,
    "147": 1110000000
}

FIXED_DATES = [
    date(2024, 6, 3),   # 1회차
    date(2025, 2, 3),   # 2회차
    date(2025, 10, 3),  # 3회차
    date(2026, 5, 3),   # 4회차
    date(2026, 10, 3),  # 5회차
    date(2027, 3, 3)    # 6회차
]

st.title("🏢 아파트 중도금 통합 이자 계산기")
st.markdown("입력하신 분양가와 회차별 일정에 따라 **오늘 기준** 발생 이자를 산출합니다.")

# 2. 사이드바 설정
st.sidebar.header("📋 타입 선택")
selected_type = st.sidebar.selectbox("해당하는 타입을 선택하세요", list(TYPE_DATA.keys()))
total_price = TYPE_DATA[selected_type]
each_loan = int(total_price * 0.1) # 10% 계산

st.sidebar.divider()
st.sidebar.write(f"**선택 타입:** {selected_type}")
st.sidebar.write(f"**총 분양가:** {total_price:,} 원")
st.sidebar.write(f"**회차별 대출금(10%):** {each_loan:,} 원")

# 3. 계산 로직 함수
def calculate_interest(exec_date, amount, rate, rep_amt, rep_date):
    today = date.today()
    if exec_date > today: # 아직 대출 전인 미래 회차
        return 0, amount, 0
    
    # 중도 상환이 없는 경우
    if rep_amt == 0:
        days = (today - exec_date).days
        interest = (amount * (rate / 100) * days) / 365
        return int(interest), amount, days
    
    # 중도 상환이 있는 경우
    else:
        # 상환 전 이자
        days_before = (rep_date - exec_date).days
        interest_before = (amount * (rate / 100) * days_before) / 365
        # 상환 후 이자
        days_after = (today - rep_date).days
        remaining_principal = amount - rep_amt
        interest_after = (remaining_principal * (rate / 100) * days_after) / 365
        
        return int(interest_before + interest_after), remaining_principal, (days_before + days_after)

# 4. 메인 화면 구성
total_all_interest = 0
total_remaining_principal = 0

cols = st.columns(2)

for i in range(6):
    with cols[i % 2].expander(f"📍 중도금 {i+1}회차 ({FIXED_DATES[i].strftime('%Y-%m-%d')})", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            e_date = st.date_input(f"실행일_{i+1}", value=FIXED_DATES[i], key=f"date_{i}")
            amt = st.number_input(f"대출금액_{i+1}", value=each_loan, step=10000, key=f"amt_{i}")
            current_rate = st.number_input(f"현재금리(%)_{i+1}", value=4.5, step=0.1, key=f"rate_{i}")
        with c2:
            r_amt = st.number_input(f"중도상환액_{i+1}", value=0, step=1000000, key=f"repay_{i}")
            r_date = st.date_input(f"상환일_{i+1}", value=date.today(), key=f"r_date_{i}")
        
        interest, remain, elapsed = calculate_interest(e_date, amt, current_rate, r_amt, r_date)
        
        if e_date > date.today():
            st.info("실행 예정인 회차입니다.")
        else:
            st.success(f"경과일수: {elapsed}일 | 이자: **{interest:,}원**")
            total_all_interest += interest
            total_remaining_principal += remain

# 5. 최종 합계
st.divider()
st.subheader("📊 최종 정산 결과 (오늘 기준)")
res_col1, res_col2 = st.columns(2)
res_col1.metric("오늘까지 총 합산 이자", f"{total_all_interest:,} 원")
res_col2.metric("총 잔여 대출 원금", f"{total_remaining_principal:,} 원")
