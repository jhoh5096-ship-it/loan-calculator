import streamlit as st
from datetime import date

# 1. 페이지 설정 및 모바일 최적화 CSS 추가
st.set_page_config(page_title="검단 중흥S-클래스 계산기", layout="wide")

# 모바일에서 제목 크기를 줄이고 가독성을 높이는 커스텀 스타일
st.markdown("""
    <style>
    /* 제목 폰트 크기 조절 (모바일 고려) */
    .main-title {
        font-size: 24px !important;
        font-weight: bold;
        color: #1E1E1E;
        padding-bottom: 10px;
        line-height: 1.4;
    }
    /* 서브 타이틀 스타일 */
    .sub-text {
        font-size: 14px !important;
        color: #666666;
        margin-bottom: 20px;
    }
    /* 모바일에서 카드 여백 조절 */
    div[data-testid="stExpander"] {
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 제목 변경 반영
st.markdown('<p class="main-title">🏢 검단 중흥S클래스 중도금대출 통합 이자 계산기</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">분양가와 회차별 일정에 따라 오늘 기준 발생 이자를 산출합니다.</p>', unsafe_allow_html=True)

# 3. 아파트 데이터 설정
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

# 4. 사이드바 설정
st.sidebar.header("📋 타입 선택")
selected_type = st.sidebar.selectbox("해당하는 타입을 선택하세요", list(TYPE_DATA.keys()))
total_price = TYPE_DATA[selected_type]
each_loan = int(total_price * 0.1) # 10% 계산

st.sidebar.divider()
st.sidebar.write(f"**선택 타입:** {selected_type}")
st.sidebar.write(f"**총 분양가:** {total_price:,} 원")
st.sidebar.write(f"**회차별 대출금(10%):** {each_loan:,} 원")

# 5. 계산 로직 함수
def calculate_interest(exec_date, amount, rate, rep_amt, rep_date):
    today = date.today()
    if exec_date > today: # 아직 대출 전인 미래 회차
        return 0, amount, 0
    
    if rep_amt == 0:
        days = (today - exec_date).days
        interest = (amount * (rate / 100) * days) / 365
        return int(interest), amount, days
    else:
        days_before = (rep_date - exec_date).days
        interest_before = (amount * (rate / 100) * days_before) / 365
        days_after = (today - rep_date).days
        remaining_principal = amount - rep_amt
        interest_after = (remaining_principal * (rate / 100) * days_after) / 365
        return int(interest_before + interest_after), remaining_principal, (days_before + days_after)

# 6. 메인 화면 구성
total_all_interest = 0
total_remaining_principal = 0

# 모바일 가독성을 위해 단일 컬럼으로 배치 권장
for i in range(6):
    with st.expander(f"📍 {i+1}회차 ({FIXED_DATES[i].strftime('%Y-%m-%d')})", expanded=(i<2)):
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
            st.success(f"경과: {elapsed}일 | 이자: **{interest:,}원**")
            total_all_interest += interest
            total_remaining_principal += remain

# 7. 최종 합계
st.divider()
st.subheader("📊 최종 정산 결과 (오늘 기준)")
res_col1, res_col2 = st.columns(2)
res_col1.metric("오늘까지 총 이자", f"{total_all_interest:,} 원")
res_col2.metric("총 잔여 원금", f"{total_remaining_principal:,} 원")
