from __future__ import annotations

import math
from io import BytesIO
from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="PHE GHG Carbon Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =====================================================
# THEME HANDLING
# =====================================================
def get_theme() -> str:
    theme = st.query_params.get("theme", "light")
    if isinstance(theme, list):
        theme = theme[0]
    return "dark" if theme == "dark" else "light"


def switch_theme() -> None:
    next_theme = "light" if get_theme() == "dark" else "dark"
    st.query_params["theme"] = next_theme
    st.rerun()


THEME = get_theme()
IS_DARK = THEME == "dark"

COLORS = {
    "dark": {
        "bg": "#07111f",
        "card": "#111c2e",
        "soft": "#18263a",
        "text": "#f8fafc",
        "muted": "#b6c2d1",
        "border": "#314158",
        "primary": "#10b981",
        "secondary": "#38bdf8",
        "danger": "#f97316",
        "plot_template": "plotly_dark",
    },
    "light": {
        "bg": "#f8fafc",
        "card": "#ffffff",
        "soft": "#eef6f3",
        "text": "#0f172a",
        "muted": "#475569",
        "border": "#d8e0ea",
        "primary": "#059669",
        "secondary": "#0284c7",
        "danger": "#ea580c",
        "plot_template": "plotly_white",
    },
}[THEME]


# =====================================================
# STYLE
# =====================================================
st.markdown(
    f"""
    <style>
    :root {{
        color-scheme: {THEME};
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: {COLORS["bg"]} !important;
        color: {COLORS["text"]} !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
    }}

    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[title="Collapse sidebar"],
    button[title="Expand sidebar"] {{
        display: none !important;
    }}

    .block-container {{
        padding-top: 2.3rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
    }}

    h1, h2, h3, h4, h5, h6, p, div, label, span {{
        color: {COLORS["text"]};
    }}

    .hero {{
        padding: 2rem 2.2rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #0f172a 0%, #064e3b 100%);
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.3rem;
    }}

    .hero h1 {{
        color: white !important;
        font-size: clamp(2rem, 4vw, 3.3rem);
        margin: 0 0 0.8rem 0;
        letter-spacing: -0.04em;
    }}

    .hero p {{
        color: #d1fae5 !important;
        font-size: 1rem;
        line-height: 1.65;
        max-width: 920px;
        margin: 0;
    }}

    .note-box {{
        padding: 1rem 1.15rem;
        border-radius: 14px;
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-left: 6px solid {COLORS["primary"]};
        color: {COLORS["text"]};
        margin: 0.8rem 0 1.2rem 0;
    }}

    .metric-card {{
        padding: 1.1rem 1.1rem;
        border-radius: 16px;
        border: 1px solid {COLORS["border"]};
        background: {COLORS["card"]};
        min-height: 118px;
    }}

    .metric-label {{
        font-size: 0.82rem;
        font-weight: 700;
        color: {COLORS["muted"]};
        margin-bottom: 0.55rem;
    }}

    .metric-value {{
        font-size: clamp(1.35rem, 2vw, 2.15rem);
        font-weight: 800;
        color: {COLORS["text"]};
        letter-spacing: -0.03em;
    }}

    .metric-caption {{
        font-size: 0.78rem;
        color: {COLORS["muted"]};
        margin-top: 0.35rem;
    }}

    .section-card {{
        padding: 1.2rem 1.25rem;
        border-radius: 16px;
        border: 1px solid {COLORS["border"]};
        background: {COLORS["card"]};
        margin: 0.75rem 0;
    }}

    .alert-red {{
        border-left: 6px solid #ef4444;
        background: {"#3b1111" if IS_DARK else "#fef2f2"};
        border-radius: 14px;
        padding: 1rem 1.15rem;
        margin: 0.8rem 0;
    }}

    .alert-green {{
        border-left: 6px solid #10b981;
        background: {"#083b2b" if IS_DARK else "#ecfdf5"};
        border-radius: 14px;
        padding: 1rem 1.15rem;
        margin: 0.8rem 0;
    }}

    .small-muted {{
        color: {COLORS["muted"]};
        font-size: 0.88rem;
        line-height: 1.55;
    }}

    .theme-wrap {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 0.5rem;
    }}

    div[data-testid="stButton"] > button {{
        border-radius: 999px !important;
        border: 1px solid {COLORS["border"]} !important;
        background-color: {COLORS["card"]} !important;
        color: {COLORS["text"]} !important;
        box-shadow: none !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        border-color: {COLORS["primary"]} !important;
        background-color: {COLORS["soft"]} !important;
        color: {COLORS["text"]} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {COLORS["muted"]};
        font-weight: 800;
    }}

    .stTabs [aria-selected="true"] {{
        color: {COLORS["primary"]} !important;
    }}

    .dataframe, .stDataFrame {{
        border-radius: 12px !important;
    }}

    @media (max-width: 900px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}

        .hero {{
            padding: 1.4rem;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# DATA HELPERS
# =====================================================
def id_num(value: str) -> float:
    """Convert Indonesian-formatted number string into float."""
    return float(value.replace(".", "").replace(",", "."))


def fmt_ton(value: float, decimals: int = 0) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_million(value_ton: float) -> str:
    return f"{value_ton / 1_000_000:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def make_metric(label: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def normalize_unit_label(unit: str) -> str:
    return unit.strip()


# =====================================================
# BASELINE DATA FROM PHE 2024 SUSTAINABILITY / GHG REPORT
# Units for dashboard baseline are TonCO2e unless stated.
# =====================================================
SCOPE_TREND = pd.DataFrame(
    [
        {"Year": 2022, "Scope 1": 12158.43 * 1000, "Scope 2": 1758.16 * 1000, "Scope 1+2": 13916.59 * 1000, "Intensity": 0.0389},
        {"Year": 2023, "Scope 1": 11994.21 * 1000, "Scope 2": 1971.92 * 1000, "Scope 1+2": 13966.13 * 1000, "Intensity": 0.0384},
        {"Year": 2024, "Scope 1": 12458.21 * 1000, "Scope 2": 2484.49 * 1000, "Scope 1+2": 14942.70 * 1000, "Intensity": 0.0471},
    ]
)

SCOPE1_SOURCE_TREND = pd.DataFrame(
    [
        {"Source": "Internal & External Combustion", "2024": 7232.75 * 1000, "2023": 7647.33 * 1000, "2022": 7693.96 * 1000},
        {"Source": "Flare", "2024": 2293.39 * 1000, "2023": 2848.12 * 1000, "2022": 2824.05 * 1000},
        {"Source": "Venting & Process", "2024": 2651.33 * 1000, "2023": 1205.20 * 1000, "2022": 1346.29 * 1000},
        {"Source": "Fugitive", "2024": 280.68 * 1000, "2023": 293.55 * 1000, "2022": 294.13 * 1000},
    ]
)

SCOPE1_BY_UNIT = pd.DataFrame(
    [
        {"Unit": "Regional 1 - Sumatera", "Internal & External Combustion": 1810.65 * 1000, "Flare": 635.96 * 1000, "Venting & Process": 16.38 * 1000, "Fugitive": 20.18 * 1000},
        {"Unit": "Regional 2 - Jawa", "Internal & External Combustion": 1201.11 * 1000, "Flare": 793.79 * 1000, "Venting & Process": 426.95 * 1000, "Fugitive": 56.47 * 1000},
        {"Unit": "Regional 3 - Kalimantan", "Internal & External Combustion": 1457.96 * 1000, "Flare": 274.90 * 1000, "Venting & Process": 4.76 * 1000, "Fugitive": 157.23 * 1000},
        {"Unit": "Regional 4 - Indonesia Timur", "Internal & External Combustion": 815.75 * 1000, "Flare": 504.81 * 1000, "Venting & Process": 1688.50 * 1000, "Fugitive": 39.02 * 1000},
        {"Unit": "Regional 5 - Internasional", "Internal & External Combustion": 162.59 * 1000, "Flare": 31.03 * 1000, "Venting & Process": 1.45 * 1000, "Fugitive": 5.29 * 1000},
        {"Unit": "PDSI", "Internal & External Combustion": 7.28 * 1000, "Flare": 0.0, "Venting & Process": 0.0, "Fugitive": 0.0},
        {"Unit": "Elnusa", "Internal & External Combustion": 85.39 * 1000, "Flare": 0.0, "Venting & Process": 0.0, "Fugitive": 0.0},
        {"Unit": "PT Badak NGL", "Internal & External Combustion": 1692.03 * 1000, "Flare": 52.90 * 1000, "Venting & Process": 513.28 * 1000, "Fugitive": 2.49 * 1000},
    ]
)
SCOPE1_BY_UNIT["Scope 1"] = SCOPE1_BY_UNIT[
    ["Internal & External Combustion", "Flare", "Venting & Process", "Fugitive"]
].sum(axis=1)

SCOPE2_BY_UNIT = pd.DataFrame(
    [
        {"Unit": "Regional 1 - Sumatera", "Scope 2": 2139.13 * 1000},
        {"Unit": "Regional 2 - Jawa", "Scope 2": 11.44 * 1000},
        {"Unit": "Regional 3 - Kalimantan", "Scope 2": 105.53 * 1000},
        {"Unit": "Regional 4 - Indonesia Timur", "Scope 2": 61.77 * 1000},
        {"Unit": "Regional 5 - Internasional", "Scope 2": 141.61 * 1000},
        {"Unit": "PDSI", "Scope 2": 0.0},
        {"Unit": "Elnusa", "Scope 2": 15.23 * 1000},
        {"Unit": "PT Badak NGL", "Scope 2": 9.77 * 1000},
    ]
)

REGIONAL_BASELINE = SCOPE1_BY_UNIT[["Unit", "Scope 1"]].merge(SCOPE2_BY_UNIT, on="Unit")
REGIONAL_BASELINE["Scope 1+2"] = REGIONAL_BASELINE["Scope 1"] + REGIONAL_BASELINE["Scope 2"]

SCOPE3_CATEGORIES = pd.DataFrame(
    [
        {"Category": "Category 3 - Fuel and energy-related activities", "2024": 0.199 * 1_000_000, "2023": 0.578 * 1_000_000},
        {"Category": "Category 5 - Waste generated in operations", "2024": 0.0283 * 1_000_000, "2023": 0.0385 * 1_000_000},
        {"Category": "Category 10 - Processing of sold products", "2024": 2.13 * 1_000_000, "2023": 2.49 * 1_000_000},
        {"Category": "Category 11 - Use of sold products", "2024": 0.924 * 1_000_000, "2023": 0.638 * 1_000_000},
    ]
)

TARGETS = {
    "bau_2030": 20_493_169.95,
    "target_2030": 13_935_355.56,
    "reduction_target_pct": 32.0,
    "nze_year": 2060,
    "actual_reduction_2024_vs_bau": 1_186_000.0,
    "intensity_2024": 0.0471,
    "intensity_yoy_increase_pct": 22.8,
}

SOURCE_NOTES = pd.DataFrame(
    [
        {"Item": "Reporting year", "Value": "2024"},
        {"Item": "Boundary", "Value": "Operational control approach"},
        {"Item": "Operational units", "Value": "Regional 1–5, PDSI, Elnusa, PT Badak NGL"},
        {"Item": "Scope 1 source categories", "Value": "Internal/external combustion, flare, venting & process, fugitive"},
        {"Item": "Scope 2 source", "Value": "Purchased electricity from third parties"},
        {"Item": "Scope 3 categories", "Value": "Category 3, 5, 10, 11"},
        {"Item": "Calculation standard", "Value": "Pertamina standard, Permen LH No. 12/2012, GHG Protocol/IPCC"},
    ]
)


# =====================================================
# SESSION STATE FOR 2025 INPUTS
# =====================================================
if "records_2025" not in st.session_state:
    st.session_state.records_2025 = []


# =====================================================
# CHART HELPERS
# =====================================================
def update_fig_layout(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        template=COLORS["plot_template"],
        height=height,
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        margin=dict(l=20, r=20, t=55, b=40),
        legend_title_text="",
    )
    return fig


def to_excel_bytes(sheets: Dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]
            df.to_excel(writer, index=False, sheet_name=safe_name)
    return output.getvalue()


def prepare_download_dataset() -> Dict[str, pd.DataFrame]:
    records_df = pd.DataFrame(st.session_state.records_2025)
    return {
        "Scope_Trend": SCOPE_TREND,
        "Scope1_Source_Trend": SCOPE1_SOURCE_TREND,
        "Regional_Baseline_2024": REGIONAL_BASELINE,
        "Scope1_By_Unit_2024": SCOPE1_BY_UNIT,
        "Scope2_By_Unit_2024": SCOPE2_BY_UNIT,
        "Scope3_Categories": SCOPE3_CATEGORIES,
        "Targets": pd.DataFrame([TARGETS]),
        "Source_Notes": SOURCE_NOTES,
        "Input_2025": records_df if not records_df.empty else pd.DataFrame(columns=["Year", "Unit", "Scope 1", "Scope 2", "Scope 3", "Scope 1+2", "Total"]),
    }


# =====================================================
# HEADER
# =====================================================
theme_col, _ = st.columns([1, 10])
with theme_col:
    icon = "☀️" if IS_DARK else "🌙"
    help_text = "Ubah ke mode terang" if IS_DARK else "Ubah ke mode gelap"
    if st.button(icon, help=help_text, key="theme_button"):
        switch_theme()

st.markdown(
    """
    <div class="hero">
        <h1>Dashboard GHG Emissions PHE 2024 + Kalkulator 2025</h1>
        <p>
            Dashboard ini disusun agar relevan dengan format GHG Report PT Pertamina Hulu Energi:
            baseline 2024 per regional/unit, emisi Scope 1 berdasarkan sumber, Scope 2 listrik pihak ketiga,
            Scope 3 kategori prioritas, target reduksi, dan kalkulator untuk input tahun berikutnya.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note-box">
        <b>Alur capstone:</b> dataset GHG report → indikator → visualisasi → red flag → insight → rekomendasi → kalkulator 2025.
        Data historis 2024 dipakai sebagai baseline, sedangkan kalkulator dipakai untuk simulasi atau pencatatan periode berikutnya.
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Ikhtisar GHG 2024",
        "Regional & Sumber Emisi",
        "Kalkulator 2025",
        "Perbandingan & Red Flag",
        "Metodologi & Kesiapan",
    ]
)


# =====================================================
# TAB 1 - GHG OVERVIEW
# =====================================================
with tab1:
    latest = SCOPE_TREND[SCOPE_TREND["Year"] == 2024].iloc[0]
    scope3_total_2024 = SCOPE3_CATEGORIES["2024"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        make_metric("Scope 1 2024", f"{fmt_million(latest['Scope 1'])} jt", "TonCO2eq")
    with col2:
        make_metric("Scope 2 2024", f"{fmt_million(latest['Scope 2'])} jt", "TonCO2eq")
    with col3:
        make_metric("Scope 1+2 2024", f"{fmt_million(latest['Scope 1+2'])} jt", "TonCO2eq")
    with col4:
        make_metric("Scope 3 2024", f"{fmt_million(scope3_total_2024)} jt", "TonCO2eq")
    with col5:
        make_metric("Intensitas 2024", "0,0471", "TonCO2eq/BOE")

    st.markdown(
        f"""
        <div class="section-card">
            <b>Interpretasi cepat:</b> Emisi Scope 1+2 2024 mencapai <b>{fmt_million(latest['Scope 1+2'])} juta TonCO2eq</b>.
            Intensitas emisi 2024 tercatat <b>0,0471 TonCO2eq/BOE</b>, naik <b>22,8%</b> dibanding tahun sebelumnya.
            Dashboard ini menempatkan angka tersebut sebagai baseline untuk membaca risiko dan perbandingan tahun 2025.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.25, 1])

    with c1:
        trend_long = SCOPE_TREND.melt(
            id_vars="Year",
            value_vars=["Scope 1", "Scope 2", "Scope 1+2"],
            var_name="Scope",
            value_name="TonCO2eq",
        )
        trend_long["Million TonCO2eq"] = trend_long["TonCO2eq"] / 1_000_000

        fig = px.line(
            trend_long,
            x="Year",
            y="Million TonCO2eq",
            color="Scope",
            markers=True,
            title="Tren Emisi Scope 1, Scope 2, dan Scope 1+2",
        )
        fig.update_yaxes(title="Juta TonCO2eq")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(update_fig_layout(fig), width="stretch")

    with c2:
        donut_df = pd.DataFrame(
            [
                {"Scope": "Scope 1", "TonCO2eq": latest["Scope 1"]},
                {"Scope": "Scope 2", "TonCO2eq": latest["Scope 2"]},
                {"Scope": "Scope 3", "TonCO2eq": scope3_total_2024},
            ]
        )
        fig = px.pie(
            donut_df,
            names="Scope",
            values="TonCO2eq",
            hole=0.58,
            title="Komposisi Scope 1, 2, dan 3 Tahun 2024",
        )
        st.plotly_chart(update_fig_layout(fig), width="stretch")

    c3, c4 = st.columns([1, 1])
    with c3:
        source_long = SCOPE1_SOURCE_TREND.melt(
            id_vars="Source",
            value_vars=["2022", "2023", "2024"],
            var_name="Year",
            value_name="TonCO2eq",
        )
        source_long["Million TonCO2eq"] = source_long["TonCO2eq"] / 1_000_000
        fig = px.bar(
            source_long,
            x="Year",
            y="Million TonCO2eq",
            color="Source",
            title="Scope 1 Berdasarkan Sumber Emisi",
            barmode="stack",
        )
        fig.update_yaxes(title="Juta TonCO2eq")
        st.plotly_chart(update_fig_layout(fig), width="stretch")

    with c4:
        scope3_long = SCOPE3_CATEGORIES.melt(
            id_vars="Category",
            value_vars=["2023", "2024"],
            var_name="Year",
            value_name="TonCO2eq",
        )
        scope3_long["Million TonCO2eq"] = scope3_long["TonCO2eq"] / 1_000_000
        fig = px.bar(
            scope3_long,
            x="Category",
            y="Million TonCO2eq",
            color="Year",
            barmode="group",
            title="Scope 3 Kategori Prioritas",
        )
        fig.update_layout(xaxis_tickangle=-25)
        fig.update_yaxes(title="Juta TonCO2eq")
        st.plotly_chart(update_fig_layout(fig, height=500), width="stretch")


# =====================================================
# TAB 2 - REGIONAL & SOURCE
# =====================================================
with tab2:
    st.subheader("Baseline 2024 per Regional/Unit")

    selected_unit = st.selectbox(
        "Pilih regional/unit untuk detail",
        REGIONAL_BASELINE["Unit"].tolist(),
        key="selected_unit_baseline",
    )

    region_long = REGIONAL_BASELINE.melt(
        id_vars="Unit",
        value_vars=["Scope 1", "Scope 2"],
        var_name="Scope",
        value_name="TonCO2eq",
    )
    region_long["Million TonCO2eq"] = region_long["TonCO2eq"] / 1_000_000

    fig = px.bar(
        region_long.sort_values("Million TonCO2eq", ascending=False),
        x="Unit",
        y="Million TonCO2eq",
        color="Scope",
        title="Perbandingan Scope 1 dan Scope 2 per Regional/Unit Tahun 2024",
        barmode="stack",
    )
    fig.update_layout(xaxis_tickangle=-25)
    fig.update_yaxes(title="Juta TonCO2eq")
    st.plotly_chart(update_fig_layout(fig, height=520), width="stretch")

    c1, c2 = st.columns([1.25, 1])

    with c1:
        source_unit_long = SCOPE1_BY_UNIT.melt(
            id_vars="Unit",
            value_vars=["Internal & External Combustion", "Flare", "Venting & Process", "Fugitive"],
            var_name="Scope 1 Source",
            value_name="TonCO2eq",
        )
        source_unit_long["Million TonCO2eq"] = source_unit_long["TonCO2eq"] / 1_000_000

        fig = px.bar(
            source_unit_long,
            x="Unit",
            y="Million TonCO2eq",
            color="Scope 1 Source",
            title="Detail Scope 1 Berdasarkan Sumber Emisi per Unit",
            barmode="stack",
        )
        fig.update_layout(xaxis_tickangle=-25)
        fig.update_yaxes(title="Juta TonCO2eq")
        st.plotly_chart(update_fig_layout(fig, height=520), width="stretch")

    with c2:
        selected_scope1 = SCOPE1_BY_UNIT[SCOPE1_BY_UNIT["Unit"] == selected_unit].copy()
        selected_long = selected_scope1.melt(
            id_vars="Unit",
            value_vars=["Internal & External Combustion", "Flare", "Venting & Process", "Fugitive"],
            var_name="Source",
            value_name="TonCO2eq",
        )
        fig = px.pie(
            selected_long,
            names="Source",
            values="TonCO2eq",
            hole=0.55,
            title=f"Komposisi Scope 1 - {selected_unit}",
        )
        st.plotly_chart(update_fig_layout(fig, height=520), width="stretch")

    baseline_display = REGIONAL_BASELINE.copy()
    for col in ["Scope 1", "Scope 2", "Scope 1+2"]:
        baseline_display[col] = baseline_display[col].apply(lambda x: fmt_ton(x, 0))
    st.dataframe(baseline_display, width="stretch", hide_index=True)


# =====================================================
# TAB 3 - CALCULATOR 2025
# =====================================================
with tab3:
    st.subheader("Kalkulator/Input Emisi 2025")

    st.markdown(
        """
        <div class="note-box">
            Kalkulator ini dibuat mengikuti struktur GHG report: Scope 1 dipisahkan berdasarkan sumber emisi,
            Scope 2 berasal dari konsumsi listrik, dan Scope 3 mengikuti kategori prioritas yang dipakai PHE.
            Untuk Scope 3 formal, faktor emisi perlu disesuaikan dengan metodologi resmi perusahaan.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("calculator_2025_form", clear_on_submit=False):
        id_col1, id_col2 = st.columns(2)
        with id_col1:
            calc_year = st.number_input("Tahun pelaporan", min_value=2025, max_value=2035, value=2025, step=1)
            calc_unit = st.selectbox("Regional/unit", REGIONAL_BASELINE["Unit"].tolist())
        with id_col2:
            reporter = st.text_input("Nama penyusun/pengguna", value="")
            note = st.text_input("Catatan singkat", value="Simulasi input periode berikutnya")

        st.markdown("### Scope 1 - Direct GHG Emissions")
        s1c1, s1c2, s1c3, s1c4 = st.columns(4)
        with s1c1:
            s1_combustion = st.number_input("Internal & external combustion (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)
        with s1c2:
            s1_flare = st.number_input("Flare / suar bakar (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)
        with s1c3:
            s1_venting = st.number_input("Venting & process (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)
        with s1c4:
            s1_fugitive = st.number_input("Fugitive (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)

        st.markdown("### Scope 2 - Purchased Electricity")
        s2c1, s2c2, s2c3 = st.columns(3)
        with s2c1:
            electricity_mwh = st.number_input("Konsumsi listrik pihak ketiga (MWh)", min_value=0.0, value=0.0, step=1000.0)
        with s2c2:
            grid_factor = st.number_input("Faktor emisi listrik (TonCO2eq/MWh)", min_value=0.0, value=0.790, step=0.001, format="%.3f")
        with s2c3:
            manual_scope2 = st.number_input("Override Scope 2 jika sudah tersedia (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)

        st.markdown("### Scope 3 - Categories Used in PHE Report")
        s3c1, s3c2 = st.columns(2)
        with s3c1:
            s3_cat3 = st.number_input("Category 3 - Fuel & energy-related activities (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)
            s3_cat5 = st.number_input("Category 5 - Waste generated in operations (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)
        with s3c2:
            s3_cat10 = st.number_input("Category 10 - Processing of sold products (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)
            s3_cat11 = st.number_input("Category 11 - Use of sold products (TonCO2eq)", min_value=0.0, value=0.0, step=1000.0)

        submitted = st.form_submit_button("Hitung dan Simpan Input 2025")

    if submitted:
        scope1_total = s1_combustion + s1_flare + s1_venting + s1_fugitive
        calculated_scope2 = electricity_mwh * grid_factor
        scope2_total = manual_scope2 if manual_scope2 > 0 else calculated_scope2
        scope3_total = s3_cat3 + s3_cat5 + s3_cat10 + s3_cat11
        scope12_total = scope1_total + scope2_total
        total_all = scope12_total + scope3_total

        if total_all <= 0:
            st.error("Input belum valid. Masukkan minimal satu nilai emisi atau data aktivitas.")
        else:
            record = {
                "Year": int(calc_year),
                "Unit": calc_unit,
                "Reporter": reporter.strip(),
                "Note": note.strip(),
                "Internal & External Combustion": s1_combustion,
                "Flare": s1_flare,
                "Venting & Process": s1_venting,
                "Fugitive": s1_fugitive,
                "Scope 1": scope1_total,
                "Electricity MWh": electricity_mwh,
                "Grid Factor": grid_factor,
                "Scope 2": scope2_total,
                "Scope 3 Category 3": s3_cat3,
                "Scope 3 Category 5": s3_cat5,
                "Scope 3 Category 10": s3_cat10,
                "Scope 3 Category 11": s3_cat11,
                "Scope 3": scope3_total,
                "Scope 1+2": scope12_total,
                "Total": total_all,
            }
            st.session_state.records_2025.append(record)
            st.success("Input berhasil dihitung dan disimpan di sesi aplikasi.")

    if st.session_state.records_2025:
        latest_record = pd.DataFrame(st.session_state.records_2025).iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            make_metric("Scope 1 input", f"{fmt_ton(latest_record['Scope 1'], 0)}", "TonCO2eq")
        with c2:
            make_metric("Scope 2 input", f"{fmt_ton(latest_record['Scope 2'], 0)}", "TonCO2eq")
        with c3:
            make_metric("Scope 3 input", f"{fmt_ton(latest_record['Scope 3'], 0)}", "TonCO2eq")
        with c4:
            make_metric("Total input", f"{fmt_ton(latest_record['Total'], 0)}", "TonCO2eq")

        records_df = pd.DataFrame(st.session_state.records_2025)
        st.dataframe(records_df, width="stretch", hide_index=True)

        csv_data = records_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download input 2025 CSV",
            data=csv_data,
            file_name="phe_input_2025.csv",
            mime="text/csv",
        )
    else:
        st.info("Belum ada input 2025. Gunakan form di atas untuk membuat simulasi atau pencatatan baru.")


# =====================================================
# TAB 4 - COMPARISON & RED FLAG
# =====================================================
with tab4:
    st.subheader("Perbandingan Baseline 2024 vs Input 2025")

    if not st.session_state.records_2025:
        st.info("Belum ada data input 2025. Isi tab Kalkulator 2025 terlebih dahulu agar perbandingan dapat ditampilkan.")
    else:
        records_df = pd.DataFrame(st.session_state.records_2025)
        grouped_2025 = records_df.groupby("Unit", as_index=False)[["Scope 1", "Scope 2", "Scope 3", "Scope 1+2", "Total"]].sum()

        comparison = REGIONAL_BASELINE.merge(
            grouped_2025,
            on="Unit",
            how="outer",
            suffixes=(" 2024", " 2025"),
        ).fillna(0)

        comparison["Change Scope 1+2"] = comparison["Scope 1+2 2025"] - comparison["Scope 1+2 2024"]
        comparison["Change %"] = comparison.apply(
            lambda row: (row["Change Scope 1+2"] / row["Scope 1+2 2024"] * 100) if row["Scope 1+2 2024"] > 0 else 0,
            axis=1,
        )

        red_flags: List[str] = []
        for _, row in comparison.iterrows():
            if row["Scope 1+2 2025"] > row["Scope 1+2 2024"] * 1.10 and row["Scope 1+2 2025"] > 0:
                red_flags.append(
                    f"{row['Unit']}: Scope 1+2 input 2025 naik lebih dari 10% dibanding baseline 2024."
                )
            if row["Scope 2 2025"] > row["Scope 2 2024"] * 1.15 and row["Scope 2 2025"] > 0:
                red_flags.append(
                    f"{row['Unit']}: Scope 2 input 2025 naik lebih dari 15% dibanding baseline 2024."
                )

        if red_flags:
            st.markdown('<div class="alert-red"><b>Red Flag Alert</b><br>' + "<br>".join(red_flags[:5]) + "</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-green"><b>Status:</b> Tidak ada red flag utama berdasarkan aturan sederhana 10% total Scope 1+2 dan 15% Scope 2.</div>', unsafe_allow_html=True)

        comp_display = comparison[
            ["Unit", "Scope 1+2 2024", "Scope 1+2 2025", "Change Scope 1+2", "Change %", "Scope 3 2025", "Total 2025"]
        ].copy()

        compare_long = comparison.melt(
            id_vars="Unit",
            value_vars=["Scope 1+2 2024", "Scope 1+2 2025"],
            var_name="Period",
            value_name="TonCO2eq",
        )
        compare_long["Million TonCO2eq"] = compare_long["TonCO2eq"] / 1_000_000

        fig = px.bar(
            compare_long,
            x="Unit",
            y="Million TonCO2eq",
            color="Period",
            barmode="group",
            title="Perbandingan Scope 1+2 Baseline 2024 dan Input 2025",
        )
        fig.update_layout(xaxis_tickangle=-25)
        fig.update_yaxes(title="Juta TonCO2eq")
        st.plotly_chart(update_fig_layout(fig, height=520), width="stretch")

        c1, c2 = st.columns([1, 1])
        with c1:
            total_2024 = comparison["Scope 1+2 2024"].sum()
            total_2025 = comparison["Scope 1+2 2025"].sum()
            gap_to_2030 = total_2025 - TARGETS["target_2030"] if total_2025 > 0 else total_2024 - TARGETS["target_2030"]
            make_metric("Total Scope 1+2 baseline 2024", f"{fmt_million(total_2024)} jt", "TonCO2eq")
            make_metric("Total Scope 1+2 input 2025", f"{fmt_million(total_2025)} jt", "TonCO2eq")
        with c2:
            make_metric("Target 2030", f"{fmt_million(TARGETS['target_2030'])} jt", "TonCO2eq")
            make_metric("Gap ke target 2030", f"{fmt_ton(gap_to_2030, 0)}", "TonCO2eq")

        comp_table = comp_display.copy()
        for col in ["Scope 1+2 2024", "Scope 1+2 2025", "Change Scope 1+2", "Scope 3 2025", "Total 2025"]:
            comp_table[col] = comp_table[col].apply(lambda x: fmt_ton(x, 0))
        comp_table["Change %"] = comp_table["Change %"].apply(lambda x: f"{x:.2f}%")
        st.dataframe(comp_table, width="stretch", hide_index=True)


# =====================================================
# TAB 5 - METHODOLOGY, INSIGHTS, DOWNLOAD
# =====================================================
with tab5:
    st.subheader("Insight, Rekomendasi, dan Metodologi")

    latest = SCOPE_TREND[SCOPE_TREND["Year"] == 2024].iloc[0]
    top_region = REGIONAL_BASELINE.sort_values("Scope 1+2", ascending=False).iloc[0]
    top_scope1_source = SCOPE1_SOURCE_TREND[["Source", "2024"]].sort_values("2024", ascending=False).iloc[0]
    top_scope3 = SCOPE3_CATEGORIES.sort_values("2024", ascending=False).iloc[0]

    st.markdown(
        f"""
        <div class="section-card">
            <h4>3 Key Insights</h4>
            <ol>
                <li><b>Scope 1 masih menjadi sumber dominan.</b> Scope 1 2024 mencapai {fmt_million(latest['Scope 1'])} juta TonCO2eq, lebih besar dari Scope 2.</li>
                <li><b>Regional/unit tertinggi adalah {top_region['Unit']}.</b> Kontribusi Scope 1+2 baseline 2024 mencapai {fmt_million(top_region['Scope 1+2'])} juta TonCO2eq.</li>
                <li><b>Sumber Scope 1 terbesar adalah {top_scope1_source['Source']}.</b> Nilainya mencapai {fmt_million(top_scope1_source['2024'])} juta TonCO2eq pada 2024.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="section-card">
            <h4>3 Actionable Recommendations</h4>
            <ol>
                <li><b>Prioritaskan sumber Scope 1 terbesar.</b> Fokus pada efisiensi combustion, flare reduction, dan kontrol venting/process sesuai sumber dominan per regional.</li>
                <li><b>Perkuat manajemen listrik untuk Scope 2.</b> Regional dengan Scope 2 tinggi perlu mengevaluasi konsumsi listrik pihak ketiga, efisiensi fasilitas, dan opsi energi rendah karbon.</li>
                <li><b>Gunakan red flag sebagai trigger aksi.</b> Jika input 2025 naik >10% terhadap baseline 2024, dashboard harus memicu review operasional dan rencana mitigasi.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="section-card">
            <h4>Target dan Dekarbonisasi</h4>
            <p>
                PHE menggunakan baseline BaU 2030 sebesar <b>{fmt_ton(TARGETS['bau_2030'], 0)} TonCO2eq</b>
                dan target penurunan <b>32%</b>, sehingga target emisi 2030 menjadi
                <b>{fmt_ton(TARGETS['target_2030'], 0)} TonCO2eq</b>. Komitmen jangka panjangnya adalah
                Net Zero GHG Emissions untuk Scope 1 dan 2 pada 2060.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("### Dataset Readiness Checklist")
        readiness = pd.DataFrame(
            [
                {"Checklist": "Data source clearly identified", "Status": "Ready"},
                {"Checklist": "Time period explicit", "Status": "2024 baseline + 2025 input"},
                {"Checklist": "Scope labels clear", "Status": "Scope 1, 2, 3"},
                {"Checklist": "Units consistent", "Status": "TonCO2eq"},
                {"Checklist": "Emission categories documented", "Status": "Ready"},
                {"Checklist": "Red flag rules included", "Status": "Ready"},
            ]
        )
        st.dataframe(readiness, width="stretch", hide_index=True)

    with c2:
        st.markdown("### Source Notes")
        st.dataframe(SOURCE_NOTES, width="stretch", hide_index=True)

    st.markdown("### Download Dataset Aplikasi")
    sheets = prepare_download_dataset()
    excel_bytes = to_excel_bytes(sheets)

    st.download_button(
        label="Download Excel Dataset Dashboard",
        data=excel_bytes,
        file_name="phe_ghg_dashboard_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown(
        """
        <div class="note-box">
            <b>Catatan batasan:</b> Dashboard ini adalah prototype capstone. Data baseline mengikuti angka yang diambil dari GHG/Sustainability Report PHE 2024.
            Input 2025 di aplikasi bersifat simulasi/pencatatan awal. Untuk pelaporan resmi, faktor emisi, boundary, dan assurance harus mengikuti metodologi perusahaan dan regulator.
        </div>
        """,
        unsafe_allow_html=True,
    )
