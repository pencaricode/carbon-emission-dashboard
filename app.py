from __future__ import annotations

import re
from io import BytesIO
from typing import Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="PHE Carbon Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =====================================================
# CONSTANTS & SECURITY LIMITS
# =====================================================
MAX_TEXT_LENGTH = 80
MAX_PERIOD_LENGTH = 20
MAX_ACTIVITY_VALUE = 1_000_000_000.0
MAX_ROWS_PER_SCOPE = 10

ELECTRICITY_FACTOR = 0.790  # kgCO2e/kWh

FUEL_DATABASE: Dict[str, Dict[str, float | str]] = {
    "Batubara": {"unit": "kg", "factor": 1.974},
    "Briket Batubara": {"unit": "kg", "factor": 2.018},
    "Arang": {"unit": "kg", "factor": 3.304},
    "Gas Alam": {"unit": "Nm3", "factor": 2.150},
    "LPG": {"unit": "kg", "factor": 3.015},
    "LGV": {"unit": "kg", "factor": 3.004},
    "LNG": {"unit": "kg", "factor": 2.699},
    "Bensin RON 98": {"unit": "liter", "factor": 2.310},
    "Bensin RON 92": {"unit": "liter", "factor": 2.305},
    "Bensin RON 90": {"unit": "liter", "factor": 2.309},
    "Bensin RON 88": {"unit": "liter", "factor": 2.315},
    "Avtur": {"unit": "liter", "factor": 2.549},
    "Minyak Tanah": {"unit": "liter", "factor": 2.553},
    "Minyak Solar CN 53": {"unit": "liter", "factor": 2.626},
    "Minyak Solar CN 51": {"unit": "liter", "factor": 2.650},
    "Minyak Solar CN 48": {"unit": "liter", "factor": 2.673},
    "Minyak Diesel": {"unit": "liter", "factor": 2.779},
    "Minyak Bakar": {"unit": "liter", "factor": 3.100},
}

SCOPE3_DATABASE: Dict[str, Dict[str, float | str]] = {
    "Transportasi pihak ketiga": {"unit": "km", "factor": 0.180},
    "Limbah operasional": {"unit": "kg", "factor": 0.420},
    "Komuter karyawan": {"unit": "km", "factor": 0.150},
    "Pembelian barang dan jasa": {"unit": "juta rupiah", "factor": 0.320},
}

# Baseline regional data derived from PHE Environmental Annual Report 2024.
# Scope 3 regional data is Category 3 only: fuel and energy-related activities.
BASELINE_2024_DATA = [
    {
        "Region_Entity": "Regional 1 - Sumatera",
        "Entity_Type": "Region",
        "Year": 2024,
        "Scope 1": 2_483_179.59,
        "Scope 2": 2_139_129.12,
        "Scope 3 Category 3": 170_831.60,
        "Total": 4_793_140.31,
        "Dominant Scope": "Scope 1",
    },
    {
        "Region_Entity": "Regional 2 - Jawa",
        "Entity_Type": "Region",
        "Year": 2024,
        "Scope 1": 2_478_322.30,
        "Scope 2": 11_443.97,
        "Scope 3 Category 3": 827.38,
        "Total": 2_490_593.65,
        "Dominant Scope": "Scope 1",
    },
    {
        "Region_Entity": "Regional 3 - Kalimantan",
        "Entity_Type": "Region",
        "Year": 2024,
        "Scope 1": 1_894_840.93,
        "Scope 2": 105_525.46,
        "Scope 3 Category 3": 11_161.87,
        "Total": 2_011_528.26,
        "Dominant Scope": "Scope 1",
    },
    {
        "Region_Entity": "Regional 4 - Indonesia Timur",
        "Entity_Type": "Region",
        "Year": 2024,
        "Scope 1": 3_048_149.20,
        "Scope 2": 61_773.89,
        "Scope 3 Category 3": 4_897.89,
        "Total": 3_114_820.98,
        "Dominant Scope": "Scope 1",
    },
    {
        "Region_Entity": "Regional 5 - Internasional",
        "Entity_Type": "Region",
        "Year": 2024,
        "Scope 1": 200_358.62,
        "Scope 2": 141_609.90,
        "Scope 3 Category 3": 9_797.45,
        "Total": 351_765.97,
        "Dominant Scope": "Scope 1",
    },
    {
        "Region_Entity": "PDSI",
        "Entity_Type": "AP Service",
        "Year": 2024,
        "Scope 1": 7_279.91,
        "Scope 2": 0.00,
        "Scope 3 Category 3": 26.51,
        "Total": 7_306.42,
        "Dominant Scope": "Scope 1",
    },
    {
        "Region_Entity": "Elnusa",
        "Entity_Type": "AP Service",
        "Year": 2024,
        "Scope 1": 85_386.76,
        "Scope 2": 15_231.63,
        "Scope 3 Category 3": 1_304.42,
        "Total": 101_922.81,
        "Dominant Scope": "Scope 1",
    },
    {
        "Region_Entity": "PT Badak NGL",
        "Entity_Type": "Subsidiary",
        "Year": 2024,
        "Scope 1": 2_260_693.97,
        "Scope 2": 9_773.02,
        "Scope 3 Category 3": 494.84,
        "Total": 2_270_961.83,
        "Dominant Scope": "Scope 1",
    },
]

ANNUAL_EMISSIONS = [
    {"Year": 2023, "Scope": "Scope 1", "Emission": 11_994_210.00},
    {"Year": 2024, "Scope": "Scope 1", "Emission": 12_458_211.29},
    {"Year": 2023, "Scope": "Scope 2", "Emission": 1_971_920.00},
    {"Year": 2024, "Scope": "Scope 2", "Emission": 2_484_487.00},
    {"Year": 2023, "Scope": "Scope 3", "Emission": 3_752_555.71},
    {"Year": 2024, "Scope": "Scope 3", "Emission": 3_280_914.22},
]

TARGETS = {
    "scope12_bau_2030": 20_493_169.96,
    "scope12_target_2030": 13_935_355.56,
    "scope12_reduction_percent": 32.0,
    "nze_year": 2060,
    "reduction_realization_2024": 1_186_870.00,
    "reduction_target_2024": 789_181.00,
    "reduction_achievement_percent": 150.39,
}


# =====================================================
# THEME
# =====================================================
def get_theme_mode() -> str:
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"

    query_theme = st.query_params.get("theme")
    if isinstance(query_theme, list):
        query_theme = query_theme[0]
    if query_theme in {"light", "dark"}:
        st.session_state.theme_mode = query_theme

    return st.session_state.theme_mode


theme_mode = get_theme_mode()
is_dark = theme_mode == "dark"

if is_dark:
    page_bg = "#0b1120"
    card_bg = "#111827"
    soft_card_bg = "#1f2937"
    text_color = "#f9fafb"
    muted_text = "#d1d5db"
    border_color = "#374151"
    hero_bg = "linear-gradient(135deg, #020617 0%, #064e3b 100%)"
    chart_bg = "#0b1120"
    chart_grid = "#374151"
    table_alt_bg = "#0f172a"
    plotly_template = "plotly_dark"
else:
    page_bg = "#f8fafc"
    card_bg = "#ffffff"
    soft_card_bg = "#f9fafb"
    text_color = "#111827"
    muted_text = "#374151"
    border_color = "#e5e7eb"
    hero_bg = "linear-gradient(135deg, #0f172a 0%, #047857 100%)"
    chart_bg = "#ffffff"
    chart_grid = "#e5e7eb"
    table_alt_bg = "#f3f4f6"
    plotly_template = "plotly_white"

accent_color = "#059669"
accent_dark = "#047857"
warning_bg = "#451a03" if is_dark else "#fff7ed"
warning_border = "#f97316"

st.markdown(
    f"""
    <style>
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
        visibility: hidden !important;
    }}

    .stApp {{
        background-color: {page_bg};
        color: {text_color};
    }}

    .block-container {{
        max-width: 1320px;
        padding-top: 1.4rem !important;
        padding-bottom: 2rem !important;
    }}

    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {text_color};
    }}

    .hero-card {{
        background: {hero_bg};
        padding: 30px 34px;
        border-radius: 20px;
        color: white;
        margin: 14px 0 22px 0;
    }}

    .hero-title {{
        font-size: clamp(28px, 4vw, 46px);
        font-weight: 850;
        letter-spacing: -0.03em;
        margin-bottom: 10px;
        color: white;
    }}

    .hero-subtitle {{
        font-size: 16px;
        line-height: 1.65;
        color: #d1fae5;
        max-width: 1050px;
    }}

    .workflow-note {{
        background-color: {card_bg};
        color: {muted_text};
        border: 1px solid {border_color};
        border-left: 6px solid {accent_color};
        border-radius: 14px;
        padding: 14px 18px;
        margin: 8px 0 22px 0;
        line-height: 1.6;
        font-size: 14px;
    }}

    .info-card, .method-card, .warning-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
    }}

    .method-card {{
        border-left: 6px solid {accent_color};
    }}

    .warning-card {{
        background-color: {warning_bg};
        border-left: 6px solid {warning_border};
    }}

    .card-title {{
        color: {text_color};
        font-weight: 800;
        font-size: 18px;
        margin-bottom: 8px;
    }}

    .card-text {{
        color: {muted_text};
        line-height: 1.6;
        font-size: 14px;
    }}

    [data-testid="stMetric"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 16px;
        height: 100%;
    }}

    [data-testid="stMetric"] label {{
        color: {muted_text};
    }}

    [data-testid="stMetricValue"] {{
        color: {text_color};
        font-size: clamp(1.25rem, 2vw, 2rem);
        overflow-wrap: anywhere;
        white-space: normal;
    }}

    .stButton > button {{
        background-color: {accent_color};
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.05rem;
        font-weight: 750;
    }}

    .stButton > button:hover {{
        background-color: {accent_dark};
        color: white !important;
    }}

    .stDownloadButton > button {{
        background-color: #2563eb;
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.05rem;
        font-weight: 750;
    }}

    input, textarea {{
        background-color: {soft_card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {soft_card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}

    div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}

    button[kind="secondary"],
    [data-testid="stNumberInput"] button {{
        background-color: {soft_card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}

    button[data-baseweb="tab"] {{
        color: {muted_text} !important;
        font-weight: 750 !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {accent_color} !important;
        border-bottom-color: {accent_color} !important;
    }}

    .theme-row {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-top: -4px;
        margin-bottom: 6px;
    }}

    .theme-pill {{
        width: 92px;
        height: 42px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        padding: 5px;
        text-decoration: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.20);
        transition: all 0.2s ease;
    }}

    .theme-pill.dark {{
        justify-content: flex-start;
        background-color: #2f3336;
        border: 1px solid #444b52;
    }}

    .theme-pill.light {{
        justify-content: flex-end;
        background-color: #ffffff;
        border: 1px solid #d1d5db;
    }}

    .theme-knob {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }}

    .theme-pill.dark .theme-knob {{
        background-color: #ffffff;
        color: #111827;
    }}

    .theme-pill.light .theme-knob {{
        background-color: #000000;
        color: #ffffff;
    }}

    .table-wrapper {{
        width: 100%;
        overflow-x: auto;
        border: 1px solid {border_color};
        border-radius: 14px;
        background-color: {card_bg};
        margin-top: 8px;
        margin-bottom: 16px;
    }}

    .pretty-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        color: {text_color};
        background-color: {card_bg};
    }}

    .pretty-table thead tr {{
        background-color: {soft_card_bg};
    }}

    .pretty-table th {{
        text-align: left;
        padding: 12px 14px;
        color: {muted_text};
        font-weight: 800;
        border-bottom: 1px solid {border_color};
        white-space: nowrap;
    }}

    .pretty-table td {{
        padding: 12px 14px;
        border-bottom: 1px solid {border_color};
        color: {text_color};
        white-space: nowrap;
    }}

    .pretty-table tbody tr:nth-child(even) {{
        background-color: {table_alt_bg};
    }}

    .pretty-table tbody tr:hover {{
        background-color: rgba(5, 150, 105, 0.12);
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .hero-card {{
            padding: 24px 22px;
            border-radius: 16px;
        }}
        .pretty-table {{
            font-size: 12px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# HELPERS
# =====================================================
def sanitize_text(value: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    value = str(value or "").strip()
    value = re.sub(r"[\x00-\x1f\x7f]", "", value)
    return value[:max_length]


def sanitize_period(value: str) -> str:
    value = sanitize_text(value, MAX_PERIOD_LENGTH)
    return re.sub(r"[^0-9A-Za-z_./ -]", "", value)


def kg_to_ton(value_kg: float) -> float:
    return float(value_kg) / 1000.0


def format_number_id(value: float, decimals: int = 2) -> str:
    formatted = f"{float(value):,.{decimals}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def format_ton(value: float) -> str:
    return f"{format_number_id(value)} tCO2e"


def get_status(total_tco2e: float) -> str:
    if total_tco2e < 100:
        return "RENDAH"
    if total_tco2e < 10_000:
        return "SEDANG"
    return "TINGGI"


def calculate_scope1_static(fuel: str, quantity: float) -> float:
    return quantity * float(FUEL_DATABASE[fuel]["factor"])


def calculate_scope1_mobile(fuel: str, distance: float, efficiency: float) -> float:
    if efficiency <= 0:
        return 0.0
    fuel_used = distance / efficiency
    return fuel_used * float(FUEL_DATABASE[fuel]["factor"])


def calculate_scope2(kwh: float) -> float:
    return kwh * ELECTRICITY_FACTOR


def calculate_scope3(category: str, quantity: float) -> float:
    return quantity * float(SCOPE3_DATABASE[category]["factor"])


def dominant_scope(scope1: float, scope2: float, scope3: float) -> str:
    scopes = {
        "Scope 1": scope1,
        "Scope 2": scope2,
        "Scope 3": scope3,
    }
    return max(scopes, key=scopes.get)


def get_recommendation(scope1: float, scope2: float, scope3: float) -> str:
    dominant = dominant_scope(scope1, scope2, scope3)
    if dominant == "Scope 1":
        return (
            "Prioritas aksi: efisiensi bahan bakar langsung, optimasi kendaraan/alat operasi, "
            "pengurangan flaring, dan transisi ke bahan bakar rendah karbon."
        )
    if dominant == "Scope 2":
        return (
            "Prioritas aksi: efisiensi konsumsi listrik, audit energi, substitusi peralatan hemat energi, "
            "dan peningkatan kontribusi listrik/energi terbarukan."
        )
    return (
        "Prioritas aksi: evaluasi rantai pasok, logistik pihak ketiga, limbah operasional, "
        "komuter, dan pembelian barang/jasa."
    )


def apply_chart_theme(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=chart_bg,
        plot_bgcolor=chart_bg,
        font=dict(color=text_color),
        legend=dict(font=dict(color=text_color)),
        margin=dict(l=20, r=20, t=70, b=30),
    )
    fig.update_xaxes(
        gridcolor=chart_grid,
        linecolor=chart_grid,
        tickfont=dict(color=text_color),
        title_font=dict(color=text_color),
    )
    fig.update_yaxes(
        gridcolor=chart_grid,
        linecolor=chart_grid,
        tickfont=dict(color=text_color),
        title_font=dict(color=text_color),
    )
    return fig


def render_pretty_table(df: pd.DataFrame) -> None:
    html = df.to_html(index=False, escape=True, classes="pretty-table", border=0)
    st.markdown(f'<div class="table-wrapper">{html}</div>', unsafe_allow_html=True)


def to_excel_bytes(sheets: Dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in sheets.items():
            safe_name = name[:31]
            df.to_excel(writer, index=False, sheet_name=safe_name)
    return output.getvalue()


def init_state() -> None:
    if "records_2025" not in st.session_state:
        st.session_state.records_2025: List[Dict[str, object]] = []
    if "scope1a_count" not in st.session_state:
        st.session_state.scope1a_count = 1
    if "scope1b_count" not in st.session_state:
        st.session_state.scope1b_count = 1
    if "scope3_count" not in st.session_state:
        st.session_state.scope3_count = 1


def add_row(key: str) -> None:
    if st.session_state[key] >= MAX_ROWS_PER_SCOPE:
        st.warning(f"Maksimal {MAX_ROWS_PER_SCOPE} baris untuk bagian ini.")
        return
    st.session_state[key] += 1
    st.rerun()


def remove_row(key: str, label: str) -> None:
    if st.session_state[key] <= 1:
        st.warning(f"Minimal 1 baris {label} harus tersedia.")
        return
    st.session_state[key] -= 1
    st.rerun()


def render_scope_controls(title: str, state_key: str, label: str, add_key: str, remove_key: str) -> None:
    """Render add/remove buttons close to each scope section."""
    title_col, button_col = st.columns([8, 2])

    with title_col:
        st.markdown(f"### {title}")

    with button_col:
        add_col, remove_col = st.columns(2)
        with add_col:
            if st.button(
                "(+)",
                key=add_key,
                help=f"Tambah baris {label}",
                use_container_width=True,
            ):
                add_row(state_key)
        with remove_col:
            if st.button(
                "(-)",
                key=remove_key,
                help=f"Hapus baris {label}",
                use_container_width=True,
            ):
                remove_row(state_key, label)


init_state()

baseline_df = pd.DataFrame(BASELINE_2024_DATA)
annual_df = pd.DataFrame(ANNUAL_EMISSIONS)
records_2025_df = pd.DataFrame(st.session_state.records_2025)
region_options = baseline_df["Region_Entity"].tolist()


# =====================================================
# HEADER
# =====================================================
target_theme = "light" if is_dark else "dark"
theme_class = "dark" if is_dark else "light"
theme_icon = "☀️" if is_dark else "🌙"
theme_title = "Mode terang" if is_dark else "Mode gelap"

st.markdown(
    f"""
    <div class="theme-row">
        <a class="theme-pill {theme_class}" href="?theme={target_theme}" target="_self" title="{theme_title}">
            <span class="theme-knob">{theme_icon}</span>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Dashboard Emisi Karbon PHE</div>
        <div class="hero-subtitle">
            Baseline 2024 sudah tertanam per regional/unit dari Environmental Annual Report PHE 2024.
            Untuk penggunaan berikutnya, user dapat memakai kalkulator 2025 untuk menghitung emisi baru,
            lalu membandingkannya dengan baseline 2024.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workflow-note">
        <strong>Alur kerja:</strong> baseline dataset 2024 → kalkulator input 2025 → perbandingan regional → insight → rekomendasi aksi.
        Data 2024 bersifat historis, sedangkan data 2025 berasal dari input kalkulator pada sesi aplikasi ini.
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# TOP SUMMARY
# =====================================================
baseline_scope1 = baseline_df["Scope 1"].sum()
baseline_scope2 = baseline_df["Scope 2"].sum()
baseline_scope3cat3 = baseline_df["Scope 3 Category 3"].sum()
baseline_total = baseline_df["Total"].sum()

if not records_2025_df.empty:
    calc_scope1 = records_2025_df["Scope 1"].sum()
    calc_scope2 = records_2025_df["Scope 2"].sum()
    calc_scope3 = records_2025_df["Scope 3"].sum()
    calc_total = records_2025_df["Total"].sum()
else:
    calc_scope1 = calc_scope2 = calc_scope3 = calc_total = 0.0

summary_cols = st.columns(5)
summary_cols[0].metric("Baseline 2024", format_ton(baseline_total))
summary_cols[1].metric("Regional/unit", len(baseline_df))
summary_cols[2].metric("Input 2025", format_ton(calc_total))
summary_cols[3].metric("Record 2025", len(records_2025_df))
summary_cols[4].metric("Status 2025", get_status(calc_total) if calc_total > 0 else "BELUM ADA")


# =====================================================
# TABS
# =====================================================
baseline_tab, calculator_tab, comparison_tab, insight_tab, dataset_tab = st.tabs(
    [
        "Baseline 2024",
        "Kalkulator 2025",
        "Perbandingan",
        "Insight & Rekomendasi",
        "Dataset & Metodologi",
    ]
)


# =====================================================
# BASELINE TAB
# =====================================================
with baseline_tab:
    st.subheader("Baseline Emisi 2024 per Regional/Unit")

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Scope 1 2024", format_ton(baseline_scope1))
    col_b.metric("Scope 2 2024", format_ton(baseline_scope2))
    col_c.metric("Scope 3 Cat. 3 2024", format_ton(baseline_scope3cat3))
    col_d.metric("Total baseline", format_ton(baseline_total))

    st.caption(
        "Catatan: untuk perbandingan regional, Scope 3 yang tersedia pada laporan adalah Scope 3 Category 3 "
        "(fuel and energy-related activities). Total Scope 3 perusahaan juga mencakup kategori lain, tetapi tidak semuanya tersedia per regional."
    )

    chart_col1, chart_col2 = st.columns([1.1, 1.4])
    with chart_col1:
        donut_df = pd.DataFrame(
            {
                "Scope": ["Scope 1", "Scope 2", "Scope 3 Cat. 3"],
                "Emission": [baseline_scope1, baseline_scope2, baseline_scope3cat3],
            }
        )
        fig = px.pie(
            donut_df,
            names="Scope",
            values="Emission",
            hole=0.58,
            title="Distribusi Baseline 2024",
            labels={"Emission": "Emisi (tCO2e)"},
        )
        fig.update_layout(height=460)
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

    with chart_col2:
        stacked_df = baseline_df.melt(
            id_vars="Region_Entity",
            value_vars=["Scope 1", "Scope 2", "Scope 3 Category 3"],
            var_name="Scope",
            value_name="Emission",
        )
        fig = px.bar(
            stacked_df,
            x="Region_Entity",
            y="Emission",
            color="Scope",
            title="Kontribusi Scope per Regional/Unit 2024",
            labels={"Region_Entity": "Regional/Unit", "Emission": "Emisi (tCO2e)"},
        )
        fig.update_layout(height=460, barmode="stack")
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

    rank_df = baseline_df.sort_values("Total", ascending=False).copy()
    rank_df["Peringkat"] = range(1, len(rank_df) + 1)
    rank_df["Total Emisi"] = rank_df["Total"].apply(format_ton)
    rank_df["Scope 1"] = rank_df["Scope 1"].apply(format_ton)
    rank_df["Scope 2"] = rank_df["Scope 2"].apply(format_ton)
    rank_df["Scope 3 Cat. 3"] = rank_df["Scope 3 Category 3"].apply(format_ton)
    rank_df = rank_df[
        [
            "Peringkat",
            "Region_Entity",
            "Entity_Type",
            "Scope 1",
            "Scope 2",
            "Scope 3 Cat. 3",
            "Total Emisi",
            "Dominant Scope",
        ]
    ].rename(
        columns={
            "Region_Entity": "Regional/Unit",
            "Entity_Type": "Tipe",
            "Dominant Scope": "Scope Dominan",
        }
    )
    render_pretty_table(rank_df)


# =====================================================
# CALCULATOR TAB
# =====================================================
with calculator_tab:
    st.subheader("Kalkulator Input Emisi 2025")
    st.write(
        "Gunakan bagian ini untuk mencatat estimasi atau data aktivitas baru tahun 2025. "
        "Hasilnya akan dibandingkan dengan baseline 2024 berdasarkan regional/unit yang dipilih."
    )

    st.markdown("### 1. Identitas Input")
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        company = sanitize_text(
            st.text_input("Perusahaan", value="PHE Subholding Upstream", key="input_company")
        )
    with meta_col2:
        region = st.selectbox("Regional/Unit", region_options, key="input_region")
    with meta_col3:
        period = sanitize_period(
            st.text_input("Periode pelaporan", value="2025", key="input_period")
        ) or "2025"

    render_scope_controls(
        "2. Scope 1A - Emisi Statis",
        "scope1a_count",
        "Scope 1A",
        "add_1a_near_section",
        "remove_1a_near_section",
    )
    scope1a_items = []
    for idx in range(st.session_state.scope1a_count):
        row_cols = st.columns([1.4, 1.0])
        with row_cols[0]:
            fuel = st.selectbox(
                f"Bahan bakar 1A #{idx + 1}",
                list(FUEL_DATABASE.keys()),
                key=f"main_scope1a_fuel_{idx}",
            )
        with row_cols[1]:
            unit = FUEL_DATABASE[fuel]["unit"]
            quantity = st.number_input(
                f"Jumlah ({unit}) #{idx + 1}",
                min_value=0.0,
                max_value=MAX_ACTIVITY_VALUE,
                value=0.0,
                step=1.0,
                key=f"main_scope1a_qty_{idx}",
            )
        scope1a_items.append({"fuel": fuel, "quantity": quantity})

    render_scope_controls(
        "3. Scope 1B - Emisi Kendaraan",
        "scope1b_count",
        "Scope 1B",
        "add_1b_near_section",
        "remove_1b_near_section",
    )
    vehicle_fuels = [fuel for fuel, data in FUEL_DATABASE.items() if data["unit"] == "liter"]
    scope1b_items = []
    for idx in range(st.session_state.scope1b_count):
        row_cols = st.columns([1.2, 1.0, 1.0])
        with row_cols[0]:
            fuel = st.selectbox(
                f"Bahan bakar kendaraan #{idx + 1}",
                vehicle_fuels,
                key=f"main_scope1b_fuel_{idx}",
            )
        with row_cols[1]:
            distance = st.number_input(
                f"Jarak (km) #{idx + 1}",
                min_value=0.0,
                max_value=MAX_ACTIVITY_VALUE,
                value=0.0,
                step=1.0,
                key=f"main_scope1b_dist_{idx}",
            )
        with row_cols[2]:
            efficiency = st.number_input(
                f"Efisiensi (km/l) #{idx + 1}",
                min_value=0.1,
                max_value=1000.0,
                value=10.0,
                step=0.1,
                key=f"main_scope1b_eff_{idx}",
            )
        scope1b_items.append(
            {"fuel": fuel, "distance": distance, "efficiency": efficiency}
        )

    st.markdown("### 4. Scope 2 - Listrik")
    scope2_kwh = st.number_input(
        "Konsumsi listrik PLN (kWh)",
        min_value=0.0,
        max_value=MAX_ACTIVITY_VALUE,
        value=0.0,
        step=100.0,
        key="main_scope2_kwh",
    )

    render_scope_controls(
        "5. Scope 3 - Emisi Tidak Langsung",
        "scope3_count",
        "Scope 3",
        "add_s3_near_section",
        "remove_s3_near_section",
    )
    scope3_items = []
    for idx in range(st.session_state.scope3_count):
        row_cols = st.columns([1.4, 1.0])
        with row_cols[0]:
            category = st.selectbox(
                f"Kategori Scope 3 #{idx + 1}",
                list(SCOPE3_DATABASE.keys()),
                key=f"main_scope3_category_{idx}",
            )
        with row_cols[1]:
            unit = SCOPE3_DATABASE[category]["unit"]
            quantity = st.number_input(
                f"Jumlah ({unit}) #{idx + 1}",
                min_value=0.0,
                max_value=MAX_ACTIVITY_VALUE,
                value=0.0,
                step=1.0,
                key=f"main_scope3_qty_{idx}",
            )
        scope3_items.append({"category": category, "quantity": quantity})

    submitted = st.button("Hitung dan Tambahkan Record 2025", type="primary")

    if submitted:
        if not company:
            st.error("Nama perusahaan wajib diisi.")
        else:
            scope1a_kg = sum(
                calculate_scope1_static(item["fuel"], item["quantity"])
                for item in scope1a_items
                if item["quantity"] > 0
            )
            scope1b_kg = sum(
                calculate_scope1_mobile(
                    item["fuel"], item["distance"], item["efficiency"]
                )
                for item in scope1b_items
                if item["distance"] > 0 and item["efficiency"] > 0
            )
            scope1_ton = kg_to_ton(scope1a_kg + scope1b_kg)
            scope2_ton = kg_to_ton(calculate_scope2(scope2_kwh))
            scope3_ton = kg_to_ton(
                sum(
                    calculate_scope3(item["category"], item["quantity"])
                    for item in scope3_items
                    if item["quantity"] > 0
                )
            )
            total_ton = scope1_ton + scope2_ton + scope3_ton

            if total_ton <= 0:
                st.error("Masukkan minimal satu aktivitas dengan nilai lebih dari 0.")
            else:
                record = {
                    "Company": company,
                    "Year": int(period) if period.isdigit() else period,
                    "Period": period,
                    "Region_Entity": region,
                    "Scope 1": round(scope1_ton, 4),
                    "Scope 2": round(scope2_ton, 4),
                    "Scope 3": round(scope3_ton, 4),
                    "Total": round(total_ton, 4),
                    "Dominant Scope": dominant_scope(scope1_ton, scope2_ton, scope3_ton),
                    "Method": "Calculator input: activity data × emission factor",
                }
                st.session_state.records_2025.append(record)
                st.success("Record 2025 berhasil ditambahkan ke sesi dashboard.")
                st.rerun()

    if st.session_state.records_2025:
        st.markdown("### Data Input 2025 pada Sesi Ini")
        display_2025 = pd.DataFrame(st.session_state.records_2025).copy()
        display_2025["Scope 1"] = display_2025["Scope 1"].apply(format_ton)
        display_2025["Scope 2"] = display_2025["Scope 2"].apply(format_ton)
        display_2025["Scope 3"] = display_2025["Scope 3"].apply(format_ton)
        display_2025["Total"] = display_2025["Total"].apply(format_ton)
        render_pretty_table(display_2025)

        dl_cols = st.columns([1, 1, 2])
        with dl_cols[0]:
            csv = pd.DataFrame(st.session_state.records_2025).to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV 2025",
                data=csv,
                file_name="phe_calculator_records_2025.csv",
                mime="text/csv",
            )
        with dl_cols[1]:
            if st.button("Reset Input 2025"):
                st.session_state.records_2025 = []
                st.rerun()
    else:
        st.info("Belum ada input 2025. Isi kalkulator di atas untuk mulai membandingkan dengan baseline 2024.")


# =====================================================
# COMPARISON TAB
# =====================================================
with comparison_tab:
    st.subheader("Perbandingan Baseline 2024 vs Input 2025")

    if records_2025_df.empty:
        st.info("Belum ada record 2025. Masukkan data pada tab Kalkulator 2025 untuk menampilkan perbandingan.")
    else:
        calc_agg = (
            records_2025_df.groupby("Region_Entity")[["Scope 1", "Scope 2", "Scope 3", "Total"]]
            .sum()
            .reset_index()
        )
        baseline_compare = baseline_df[
            ["Region_Entity", "Scope 1", "Scope 2", "Scope 3 Category 3", "Total"]
        ].rename(
            columns={
                "Scope 3 Category 3": "Scope 3",
                "Total": "Baseline 2024",
            }
        )
        calc_compare = calc_agg.rename(columns={"Total": "Input 2025"})
        comparison = baseline_compare.merge(calc_compare, on="Region_Entity", how="left", suffixes=(" 2024", " 2025"))
        comparison["Input 2025"] = comparison["Input 2025"].fillna(0)
        comparison["Change vs 2024"] = comparison["Input 2025"] - comparison["Baseline 2024"]
        comparison["Change %"] = comparison.apply(
            lambda row: (row["Change vs 2024"] / row["Baseline 2024"] * 100)
            if row["Baseline 2024"] else 0,
            axis=1,
        )

        comp_long = comparison.melt(
            id_vars="Region_Entity",
            value_vars=["Baseline 2024", "Input 2025"],
            var_name="Periode",
            value_name="Total Emisi",
        )
        fig = px.bar(
            comp_long,
            x="Region_Entity",
            y="Total Emisi",
            color="Periode",
            barmode="group",
            title="Total Emisi: Baseline 2024 vs Input 2025",
            labels={"Region_Entity": "Regional/Unit", "Total Emisi": "tCO2e"},
        )
        fig.update_layout(height=520)
        st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

        comp_display = comparison[
            ["Region_Entity", "Baseline 2024", "Input 2025", "Change vs 2024", "Change %"]
        ].copy()
        comp_display["Baseline 2024"] = comp_display["Baseline 2024"].apply(format_ton)
        comp_display["Input 2025"] = comp_display["Input 2025"].apply(format_ton)
        comp_display["Change vs 2024"] = comp_display["Change vs 2024"].apply(format_ton)
        comp_display["Change %"] = comp_display["Change %"].map(lambda value: f"{value:.2f}%")
        comp_display = comp_display.rename(columns={"Region_Entity": "Regional/Unit"})
        render_pretty_table(comp_display)

        selected_regions = calc_agg["Region_Entity"].tolist()
        for region_name in selected_regions:
            row = comparison[comparison["Region_Entity"] == region_name].iloc[0]
            if row["Input 2025"] > row["Baseline 2024"]:
                st.warning(
                    f"Red flag: input 2025 untuk {region_name} lebih tinggi daripada baseline 2024. "
                    f"Kenaikan sebesar {format_ton(row['Input 2025'] - row['Baseline 2024'])}."
                )


# =====================================================
# INSIGHT TAB
# =====================================================
with insight_tab:
    st.subheader("Insight dan Rekomendasi Aksi")

    highest_region = baseline_df.sort_values("Total", ascending=False).iloc[0]
    scope12_2024 = baseline_scope1 + baseline_scope2
    gap_to_2030_target = max(scope12_2024 - TARGETS["scope12_target_2030"], 0)

    insight_cols = st.columns(3)
    with insight_cols[0]:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="card-title">Insight 1 — Regional tertinggi</div>
                <div class="card-text">
                    Baseline 2024 tertinggi berasal dari <strong>{highest_region['Region_Entity']}</strong>
                    dengan total {format_ton(highest_region['Total'])}.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with insight_cols[1]:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="card-title">Insight 2 — Scope dominan</div>
                <div class="card-text">
                    Scope 1 menjadi kontributor terbesar pada baseline regional 2024. Ini menandakan prioritas awal berada pada
                    bahan bakar langsung, pembakaran, flaring, venting/process, dan fugitive emission.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with insight_cols[2]:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="card-title">Insight 3 — Gap target 2030</div>
                <div class="card-text">
                    Scope 1+2 tahun 2024 sebesar {format_ton(scope12_2024)}. Target 2030 adalah
                    {format_ton(TARGETS['scope12_target_2030'])}, sehingga gap saat ini sekitar {format_ton(gap_to_2030_target)}.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Red Flag Alert")
    if scope12_2024 > TARGETS["scope12_target_2030"]:
        st.markdown(
            f"""
            <div class="warning-card">
                <div class="card-title">Scope 1+2 masih di atas target 2030</div>
                <div class="card-text">
                    Baseline Scope 1+2 tahun 2024 masih perlu diturunkan sekitar
                    <strong>{format_ton(gap_to_2030_target)}</strong> untuk mencapai target 2030.
                    Fokus pengurangan paling logis adalah Scope 1 karena kontribusinya paling besar.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("Scope 1+2 baseline 2024 sudah berada di bawah target 2030.")

    st.markdown("### 3 Actionable Recommendations")
    rec_cols = st.columns(3)
    with rec_cols[0]:
        st.markdown(
            """
            <div class="method-card">
                <div class="card-title">1. Prioritaskan Scope 1</div>
                <div class="card-text">
                    Optimalkan konsumsi bahan bakar, pengurangan routine flaring, pemanfaatan flare gas,
                    kontrol venting/process, dan program LDAR untuk fugitive emissions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with rec_cols[1]:
        st.markdown(
            """
            <div class="method-card">
                <div class="card-title">2. Tekan Scope 2</div>
                <div class="card-text">
                    Lakukan audit energi, efisiensi listrik, substitusi peralatan hemat energi, dan perluas
                    penggunaan PLTS atau listrik dari sumber terbarukan.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with rec_cols[2]:
        st.markdown(
            """
            <div class="method-card">
                <div class="card-title">3. Perkuat pencatatan 2025</div>
                <div class="card-text">
                    Gunakan kalkulator untuk mencatat aktivitas per regional secara konsisten agar dapat dibandingkan
                    dengan baseline 2024 dan menjadi bahan monitoring tahun berjalan.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Tren Emisi 2023–2024")
    fig = px.line(
        annual_df,
        x="Year",
        y="Emission",
        color="Scope",
        markers=True,
        title="Tren Emisi PHE per Scope",
        labels={"Emission": "Emisi (tCO2e)", "Year": "Tahun"},
    )
    fig.update_layout(height=480)
    st.plotly_chart(apply_chart_theme(fig), use_container_width=True)


# =====================================================
# DATASET TAB
# =====================================================
with dataset_tab:
    st.subheader("Dataset & Metodologi")

    meta_cols = st.columns(2)
    with meta_cols[0]:
        st.markdown(
            """
            <div class="method-card">
                <div class="card-title">Sumber Data 2024</div>
                <div class="card-text">
                    Dataset baseline berasal dari Environmental Annual Report PHE 2024.
                    Data yang ditanam di aplikasi mencakup regional/unit, Scope 1, Scope 2,
                    dan Scope 3 Category 3. Ini digunakan sebagai baseline historis.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with meta_cols[1]:
        st.markdown(
            """
            <div class="method-card">
                <div class="card-title">Metodologi Kalkulator 2025</div>
                <div class="card-text">
                    Rumus utama: <strong>Emisi = Data Aktivitas × Faktor Emisi</strong>.
                    Output awal kgCO2e dikonversi menjadi tCO2e dengan membagi 1.000.
                    Scope 3 pada kalkulator bersifat prototype/simulasi dan perlu diganti faktor resmi jika dipakai untuk pelaporan formal.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Checklist Minimum Capstone")
    checklist_df = pd.DataFrame(
        [
            ["Clean dataset", "Baseline 2024 sudah disusun per regional/unit dan scope", "Ready"],
            ["Working dashboard/calculator", "Tab baseline, kalkulator 2025, perbandingan, insight", "Ready"],
            ["Minimum 5 indicators", "Baseline total, regional count, input 2025, record count, status", "Ready"],
            ["Minimum 3 visualizations", "Donut scope, stacked regional, annual trend, comparison chart", "Ready"],
            ["1 red flag alert", "Gap Scope 1+2 terhadap target 2030 dan kenaikan 2025 vs 2024", "Ready"],
            ["3 key insights", "Regional tertinggi, scope dominan, gap target", "Ready"],
            ["3 recommendations", "Scope 1, Scope 2, pencatatan 2025", "Ready"],
        ],
        columns=["Requirement", "Dashboard Response", "Status"],
    )
    render_pretty_table(checklist_df)

    st.markdown("### Download Dataset Dashboard")
    sheets = {
        "Baseline_2024": baseline_df,
        "Annual_Emissions": annual_df,
        "Records_2025": records_2025_df if not records_2025_df.empty else pd.DataFrame(columns=["Company", "Year", "Period", "Region_Entity", "Scope 1", "Scope 2", "Scope 3", "Total"]),
        "Targets": pd.DataFrame([TARGETS]),
        "Checklist": checklist_df,
    }
    excel_bytes = to_excel_bytes(sheets)
    st.download_button(
        "Download Excel Dataset Dashboard",
        data=excel_bytes,
        file_name="phe_dashboard_dataset_baseline_2024_calculator_2025.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown("### Baseline Raw Data")
    render_pretty_table(baseline_df)
