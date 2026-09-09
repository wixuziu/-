"""
후성유전적 건강수명(Healthspan) & 위험도 조율 시뮬레이터
Epigenetic Healthspan & Risk Tuning Simulator

실행 방법:
    streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# 0. 페이지 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Epigenetic Healthspan & Risk Tuning Simulator",
    page_icon="🧬",
    layout="wide",
)

# ----------------------------------------------------------------------------
# 1. 생물학적 연산 함수 정의
# ----------------------------------------------------------------------------
def calc_biological_age(chrono_age: float, methylation: float, stress_index: float) -> float:
    """
    생물학적 나이 계산식.
    - 메틸화 수치가 기준점(50%)에서 벗어날수록 생물학적 나이가 실제 나이보다
      더 벌어진다고 가정 (후성유전적 표류, Epigenetic Drift 개념 반영).
    - 스트레스 지수(환경 요인)가 높을수록 이 표류 효과가 증폭됨.
    """
    return chrono_age + (methylation - 50) * 0.35 * (stress_index / 3)


def calc_cancer_risk(methylation: np.ndarray) -> np.ndarray:
    """
    암 발생 위험도(%).
    - p16INK4a 같은 종양억제유전자가 과메틸화(침묵)되지 않고 '충분히 낮은 메틸화'를
      유지해야 정상적으로 발현되어 종양을 억제함.
    - 메틸화가 30% 미만으로 떨어지면(=억제유전자 발현이 과도해지는 것이 아니라
      본 모델에서는 방어기전이 약화되는 문턱으로 정의) 위험이 비선형적으로 급증.
    - 문턱 함수: max(0, (30 - 메틸화)^1.4 * 1.5)
    """
    return np.maximum(0, (30 - methylation)) ** 1.4 * 1.5


def calc_senescence_risk(methylation: np.ndarray) -> np.ndarray:
    """
    세포 노화(Senescence) 위험도(%).
    - 메틸화가 70%를 초과하면 종양억제유전자를 포함한 다수의 유전자가 과도하게
      침묵(silencing)되어 세포 활성이 떨어지고 노화(senescence)가 가속됨.
    - 문턱 함수: max(0, (메틸화 - 70)^1.4 * 1.5)
    """
    return np.maximum(0, (methylation - 70)) ** 1.4 * 1.5


def calc_total_risk(methylation: np.ndarray) -> np.ndarray:
    """총 위험도 = 암 발생 위험도 + 세포 노화 위험도"""
    return calc_cancer_risk(methylation) + calc_senescence_risk(methylation)


# ----------------------------------------------------------------------------
# 2. 사이드바: 사용자 입력 파라미터
# ----------------------------------------------------------------------------
st.sidebar.header("🧪 시뮬레이션 파라미터")

chrono_age = st.sidebar.slider(
    "실제 나이 (Chronological Age)", min_value=20, max_value=80, value=50, step=1
)

methylation = st.sidebar.slider(
    "암 억제 유전자(p16INK4a) 메틸화 비율 (%)",
    min_value=0, max_value=100, value=40, step=1
)

stress_index = st.sidebar.slider(
    "후성유전적 스트레스 지수 (환경 요인)",
    min_value=1, max_value=5, value=3, step=1
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "※ 본 앱은 학술 발표/데모 목적의 개념 모델(conceptual model)이며, "
    "실제 임상 진단 도구가 아닙니다."
)

# ----------------------------------------------------------------------------
# 3. 헤더 & 학술적 서론
# ----------------------------------------------------------------------------
st.title("🧬 후성유전적 건강수명(Healthspan) & 위험도 조율 시뮬레이터")
st.markdown(
    """
    세포는 나이가 들면서 DNA 메틸화 패턴이 점진적으로 변화하는
    **후성유전적 표류(Epigenetic Drift)**를 겪습니다. 특히 p16INK4a와 같은
    종양억제유전자(tumor suppressor gene)의 프로모터 메틸화 수준은 두 가지
    상반된 리스크와 연결됩니다.

    - 메틸화가 **너무 낮으면** 방어 기전이 불안정해져 **암화(carcinogenesis) 위험**이 증가하고,
    - 메틸화가 **너무 높으면** 유전자가 과도하게 침묵되어 **세포 노화(senescence) 가속** 위험이 증가합니다.

    이 두 위험 사이에는 **트레이드오프(trade-off)** 관계가 존재하며, 본 시뮬레이터는
    이 균형점을 탐색하여 **최적의 Healthspan Zone(건강수명 구간, 약 30%~70%)**을
    진단하고 조율하는 것을 목표로 합니다.
    """
)

st.markdown("---")

# ----------------------------------------------------------------------------
# 4. 핵심 지표 계산
# ----------------------------------------------------------------------------
bio_age = calc_biological_age(chrono_age, methylation, stress_index)
age_gap = bio_age - chrono_age
cancer_risk = float(calc_cancer_risk(np.array([methylation]))[0])
senescence_risk = float(calc_senescence_risk(np.array([methylation]))[0])
total_risk = cancer_risk + senescence_risk

# ----------------------------------------------------------------------------
# 5. 상단 지표 (st.metric)
# ----------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="생물학적 나이 (Biological Age)",
        value=f"{bio_age:.1f} 세",
        delta=f"{age_gap:+.1f} 세 (실제 나이 대비)",
        delta_color="inverse",
    )

with col2:
    st.metric(
        label="암 발생 위험도 (Cancer Risk)",
        value=f"{cancer_risk:.1f} %",
    )

with col3:
    st.metric(
        label="세포 노화 위험도 (Senescence Risk)",
        value=f"{senescence_risk:.1f} %",
    )

st.markdown("---")

# ----------------------------------------------------------------------------
# 6. 인터랙티브 리스크 그래프 (Plotly)
# ----------------------------------------------------------------------------
st.subheader("📈 메틸화 수치에 따른 위험도 곡선")

x_meth = np.linspace(0, 100, 500)
y_cancer = calc_cancer_risk(x_meth)
y_senescence = calc_senescence_risk(x_meth)
y_total = y_cancer + y_senescence

fig = go.Figure()

# Healthspan Zone 배경 음영 (30% ~ 70%)
fig.add_vrect(
    x0=30, x1=70,
    fillcolor="green", opacity=0.12,
    layer="below", line_width=0,
    annotation_text="Healthspan Zone", annotation_position="top left",
)

# 암 발생 위험 곡선 (빨간색)
fig.add_trace(go.Scatter(
    x=x_meth, y=y_cancer, mode="lines", name="암 발생 위험도",
    line=dict(color="red", width=3)
))

# 세포 노화 위험 곡선 (주황색)
fig.add_trace(go.Scatter(
    x=x_meth, y=y_senescence, mode="lines", name="세포 노화 위험도",
    line=dict(color="orange", width=3)
))

# 총 위험도 곡선 (보라색 점선)
fig.add_trace(go.Scatter(
    x=x_meth, y=y_total, mode="lines", name="총 위험도",
    line=dict(color="purple", width=3, dash="dot")
))

# 현재 사용자 위치 마커
fig.add_trace(go.Scatter(
    x=[methylation], y=[total_risk], mode="markers",
    name="현재 위치",
    marker=dict(color="blue", size=16, symbol="star", line=dict(color="black", width=1))
))

fig.update_layout(
    xaxis_title="메틸화 비율 (%)",
    yaxis_title="위험도 (%)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=480,
    margin=dict(t=60, b=40, l=40, r=20),
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# 7. 진단 및 피드백 패널
# ----------------------------------------------------------------------------
st.subheader("🩺 진단 및 피드백")

if methylation < 30:
    st.error(
        f"⚠️ **암화 위험 경고**: 현재 메틸화 수치({methylation}%)가 30% 미만입니다. "
        "종양억제유전자 방어 기전이 약화되어 암 발생 위험이 비선형적으로 급증하는 구간입니다. "
        "메틸화 수치를 Healthspan Zone(30~70%) 쪽으로 끌어올리는 조율이 필요합니다."
    )
elif methylation <= 70:
    st.success(
        f"✅ **최적 균형 상태**: 현재 메틸화 수치({methylation}%)는 Healthspan Zone(30~70%) 내에 있습니다. "
        "암 예방 기전과 세포 활성 사이의 균형이 잘 유지되고 있는 안전 구간입니다."
    )
else:
    st.warning(
        f"⚠️ **세포 노화 가속 경고**: 현재 메틸화 수치({methylation}%)가 70%를 초과했습니다. "
        "과도한 후성유전적 억제(gene silencing)로 인해 세포 노화 위험이 비선형적으로 급증하는 구간입니다. "
        "메틸화 수치를 낮추는 방향의 조율이 필요합니다."
    )

st.markdown("---")

# ----------------------------------------------------------------------------
# 8. 표적 후성유전 조율(Fine-Tuning) 최적화 계산기
# ----------------------------------------------------------------------------
st.subheader("🎯 표적 후성유전 조율(Fine-Tuning) 최적화")

st.write(
    "아래 버튼을 누르면 총 위험도(Total Risk)가 최소가 되는 최적 메틸화 수치를 자동으로 "
    "탐색하고, 현재 상태 대비 개선 효과를 계산합니다."
)

if st.button("🚀 최적 조율 시뮬레이션 실행"):
    # 0~100% 사이를 촘촘히 탐색하여 총 위험도 최소값(최적 메틸화 수치) 탐색
    search_x = np.linspace(0, 100, 10001)
    search_y = calc_total_risk(search_x)
    optimal_idx = int(np.argmin(search_y))
    optimal_meth = float(search_x[optimal_idx])
    optimal_total_risk = float(search_y[optimal_idx])

    # 최적 상태로 조율했을 때의 생물학적 나이
    optimal_bio_age = calc_biological_age(chrono_age, optimal_meth, stress_index)

    # 개선 효과 계산
    bio_age_reduction = bio_age - optimal_bio_age
    if total_risk > 0:
        risk_reduction_pct = (total_risk - optimal_total_risk) / total_risk * 100
    else:
        risk_reduction_pct = 0.0

    st.info(
        f"**🔬 최적 메틸화 수치: 약 {optimal_meth:.1f}%** "
        f"(이론적 최소 총 위험도: {optimal_total_risk:.2f}%)"
    )

    colA, colB, colC = st.columns(3)
    with colA:
        st.metric(
            "조율 후 생물학적 나이",
            f"{optimal_bio_age:.1f} 세",
            delta=f"{-bio_age_reduction:+.1f} 세",
            delta_color="inverse",
        )
    with colB:
        st.metric(
            "총 위험도 감소",
            f"{optimal_total_risk:.1f} %",
            delta=f"{-(total_risk - optimal_total_risk):+.1f} %p",
            delta_color="inverse",
        )
    with colC:
        st.metric(
            "리스크 감축률",
            f"{risk_reduction_pct:.1f} %",
        )

    if bio_age_reduction > 0.01 or risk_reduction_pct > 0.01:
        st.success(
            f"현재 메틸화 수치({methylation}%)를 최적 수치(약 {optimal_meth:.1f}%)로 조율할 경우, "
            f"생물학적 나이를 약 **{bio_age_reduction:.1f}세** 낮추고, "
            f"총 위험도를 약 **{risk_reduction_pct:.1f}%** 감축할 수 있는 것으로 시뮬레이션됩니다."
        )
    else:
        st.success(
            "현재 메틸화 수치는 이미 최적 지점에 근접해 있어 추가적인 조율 효과가 크지 않습니다. "
            "현 상태를 유지하는 것이 바람직합니다."
        )

st.markdown("---")
st.caption(
    "본 시뮬레이터는 DNA 메틸화(p16INK4a)와 암/세포노화 위험 간의 트레이드오프를 "
    "설명하기 위한 개념적 수학 모델(conceptual mathematical model)이며, "
    "실제 생물학적 측정치나 임상 데이터에 기반한 진단 도구가 아닙니다."
)
