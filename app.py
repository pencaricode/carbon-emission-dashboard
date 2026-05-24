import streamlit as st
import pandas as pd
import plotly.express as px

from data.emission_factors import *
from utils.calculations import *
from utils.recommendations import *
from database.db import *
from utils.pdf_export import *


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Dashboard Emisi Karbon",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
.hero-card {
    background: linear-gradient(135deg, #0f172a 0%, #064e3b 100%);
    padding: 32px;
    border-radius: 24px;
    color: white;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 17px;
    line-height: 1.6;
    color: #d1fae5;
    max-width: 900px;
}

.info-card {
    background-color: #ffffff;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    height: 100%;
}

.info-title {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 10px;
}

.info-text {
    font-size: 15px;
    line-height: 1.6;
    color: #374151;
}

.scope-card {
    background-color: #f9fafb;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    height: 100%;
}

.scope-title {
    font-size: 19px;
    font-weight: 700;
    color: #064e3b;
    margin-bottom: 8px;
}

.action-card {
    background-color: #ecfdf5;
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #059669;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
# =====================================================
# HERO SECTION
# =====================================================
st.markdown("""
<div class="hero-card">
    <div class="hero-title">Jejak Karbon Perusahaan Hari Ini</div>
    <div class="hero-subtitle">
        Pantau, pahami, dan kurangi emisi karbon dari aktivitas operasional
        perusahaan berdasarkan Scope 1, Scope 2, dan Scope 3. Dashboard ini
        dirancang sebagai ESG analytics dashboard, carbon footprint education
        dashboard, dan sustainability reporting tool.
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# LOAD DATABASE
# =====================================================
history = get_all_emissions()

history_df = pd.DataFrame(
    history,
    columns=[
        "ID",
        "Company",
        "Period",
        "Scope 1",
        "Scope 2",
        "Scope 3",
        "Total",
        "Created At"
    ]
)

# =====================================================
# FORMAT DATE COLUMN
# =====================================================
if not history_df.empty:

    history_df["Created At"] = pd.to_datetime(
        history_df["Created At"],
        errors="coerce"
    )

# =====================================================
# SIDEBAR INPUT
# =====================================================
st.sidebar.header("Input Data Emisi")

user_name = st.sidebar.text_input(
    "Nama Pengguna"
)

company = st.sidebar.text_input(
    "Perusahaan"
)

period = st.sidebar.text_input(
    "Periode",
    value="2025"
)


# =====================================================
# SCOPE 1A
# =====================================================
st.sidebar.subheader("Scope 1A - Emisi Statis")

static_fuel = st.sidebar.selectbox(
    "Bahan Bakar",
    list(FUEL_DATABASE.keys())
)

static_quantity = st.sidebar.number_input(
    "Jumlah Konsumsi",
    min_value=0.0,
    value=0.0
)


# =====================================================
# SCOPE 1B
# =====================================================
st.sidebar.subheader("Scope 1B - Emisi Kendaraan")

mobile_fuel = st.sidebar.selectbox(
    "Bahan Bakar Kendaraan",
    list(FUEL_DATABASE.keys())
)

mobile_distance = st.sidebar.number_input(
    "Jarak Tempuh (km)",
    min_value=0.0,
    value=0.0
)

mobile_efficiency = st.sidebar.number_input(
    "Efisiensi Kendaraan (km/l)",
    min_value=1.0,
    value=1.0
)


# =====================================================
# SCOPE 2
# =====================================================
st.sidebar.subheader("Scope 2 - Listrik")

scope2_kwh = st.sidebar.number_input(
    "Konsumsi Listrik (kWh)",
    min_value=0.0,
    value=0.0
)


# =====================================================
# SCOPE 3
# =====================================================
st.sidebar.subheader("Scope 3 - Emisi Tidak Langsung")

scope3_category = st.sidebar.selectbox(
    "Kategori Scope 3",
    list(SCOPE3_DATABASE.keys())
)

scope3_quantity = st.sidebar.number_input(
    "Jumlah Aktivitas",
    min_value=0.0,
    value=0.0
)


# =====================================================
# BUTTON
# =====================================================
calculate = st.sidebar.button(
    "Hitung Emisi"
)


# =====================================================
# SAVE NEW DATA
# =====================================================
if calculate:

    if company.strip() == "":
        st.error("Nama perusahaan wajib diisi.")

    else:
        # Scope 1A
        static_emission = calculate_scope1_static(
            static_fuel,
            static_quantity
        )

        # Scope 1B
        mobile_emission = calculate_scope1_mobile(
            mobile_fuel,
            mobile_distance,
            mobile_efficiency
        )

        scope1_total = (
            static_emission +
            mobile_emission
        )

        # Scope 2
        scope2_total = calculate_scope2(
            scope2_kwh
        )

        # Scope 3
        scope3_total = calculate_scope3(
            scope3_category,
            scope3_quantity
        )

        # Total kgCO2e
        total_kg = (
            scope1_total +
            scope2_total +
            scope3_total
        )

        # Convert to tCO2e
        scope1_ton = kg_to_ton(scope1_total)

        scope2_ton = kg_to_ton(scope2_total)

        scope3_ton = kg_to_ton(scope3_total)

        total_ton = kg_to_ton(total_kg)

        # Save to database
        insert_emission(
            company,
            period,
            scope1_ton,
            scope2_ton,
            scope3_ton,
            total_ton
        )

        st.success("Data emisi berhasil disimpan.")

        st.rerun()


# =====================================================
# FILTER SECTION
# =====================================================
st.sidebar.divider()

st.sidebar.subheader("Filter Analytics")

if not history_df.empty:

    company_options = ["All"] + sorted(
        history_df["Company"].astype(str).unique().tolist()
    )

    selected_company = st.sidebar.selectbox(
        "Filter Perusahaan",
        company_options
    )

    period_options = ["All"] + sorted(
        history_df["Period"].astype(str).unique().tolist()
    )

    selected_period = st.sidebar.selectbox(
        "Filter Periode",
        period_options
    )

    # =================================================
    # DATE RANGE FILTER
    # =================================================
    min_date = history_df["Created At"].min().date()

    max_date = history_df["Created At"].max().date()

    selected_date_range = st.sidebar.date_input(
        "Filter Rentang Tanggal",
        value=(
            min_date,
            max_date
        ),
        min_value=min_date,
        max_value=max_date
    )

else:

    selected_company = "All"
    selected_period = "All"
    selected_date_range = None

# =====================================================
# TARGET REDUCTION INPUT
# =====================================================
st.sidebar.divider()

st.sidebar.subheader("Target Reduction")

baseline_emission = st.sidebar.number_input(
    "Baseline Emission (tCO2e)",
    min_value=0.0,
    value=1000.0
)

target_reduction_percent = st.sidebar.number_input(
    "Target Reduction (%)",
    min_value=0.0,
    max_value=100.0,
    value=20.0
)


# =====================================================
# APPLY FILTER
# =====================================================
filtered_df = history_df.copy()

if not filtered_df.empty:

    if selected_company != "All":

        filtered_df = filtered_df[
            filtered_df["Company"].astype(str) ==
            selected_company
        ]

    if selected_period != "All":

        filtered_df = filtered_df[
            filtered_df["Period"].astype(str) ==
            selected_period
        ]

    if selected_date_range is not None and len(selected_date_range) == 2:

        start_date = selected_date_range[0]

        end_date = selected_date_range[1]

        filtered_df = filtered_df[
            (filtered_df["Created At"].dt.date >= start_date) &
            (filtered_df["Created At"].dt.date <= end_date)
        ]
# =====================================================
# CARBON STORYTELLING SECTION
# =====================================================
st.subheader("Kenapa Jejak Karbon Ini Penting?")

why_col1, why_col2 = st.columns([2, 1])

with why_col1:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">Dari angka menjadi keputusan</div>
        <div class="info-text">
            Setiap aktivitas operasional perusahaan menghasilkan jejak karbon.
            Dengan mengetahui sumber emisi terbesar, organisasi dapat mengambil
            keputusan yang lebih tepat untuk mengurangi dampak lingkungan,
            meningkatkan efisiensi energi, dan mendukung target keberlanjutan.
        </div>
    </div>
    """, unsafe_allow_html=True)

with why_col2:
    st.markdown("""
    <div class="info-card">
        <div class="info-title">Fokus dashboard</div>
        <div class="info-text">
            Dashboard ini membantu membaca emisi, memahami sumbernya,
            memantau target pengurangan, dan menghasilkan laporan
            sustainability secara lebih terstruktur.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

st.subheader("Memahami Scope Emisi")

scope_col1, scope_col2, scope_col3 = st.columns(3)

with scope_col1:
    st.markdown("""
    <div class="scope-card">
        <div class="scope-title">Scope 1</div>
        <div class="info-text">
            Emisi langsung dari aktivitas yang dikendalikan perusahaan,
            seperti bahan bakar kendaraan operasional, generator, proses
            pembakaran, dan konsumsi bahan bakar internal.
        </div>
    </div>
    """, unsafe_allow_html=True)

with scope_col2:
    st.markdown("""
    <div class="scope-card">
        <div class="scope-title">Scope 2</div>
        <div class="info-text">
            Emisi tidak langsung dari energi yang dibeli, terutama konsumsi
            listrik PLN. Scope ini sering menjadi sumber emisi besar pada
            kantor, kampus, pabrik, dan fasilitas operasional.
        </div>
    </div>
    """, unsafe_allow_html=True)

with scope_col3:
    st.markdown("""
    <div class="scope-card">
        <div class="scope-title">Scope 3</div>
        <div class="info-text">
            Emisi tidak langsung lain dari rantai nilai, seperti transportasi
            pihak ketiga, limbah operasional, komuter karyawan, dan pembelian
            barang atau jasa.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =====================================================
# DASHBOARD CONTENT
# =====================================================
if not filtered_df.empty:

    # =================================================
    # KPI CALCULATION
    # =================================================
    latest_total = filtered_df["Total"].sum()

    latest_scope1 = filtered_df["Scope 1"].sum()

    latest_scope2 = filtered_df["Scope 2"].sum()

    latest_scope3 = filtered_df["Scope 3"].sum()

    scopes = {
        "Scope 1": latest_scope1,
        "Scope 2": latest_scope2,
        "Scope 3": latest_scope3
    }

    dominant_scope = max(
        scopes,
        key=scopes.get
    )

    status = get_status(
        latest_total
    )

    recommendation = get_recommendation(
        latest_scope1,
        latest_scope2,
        latest_scope3
    )


    # =================================================
    # TARGET REDUCTION CALCULATION
    # =================================================
    target_emission = baseline_emission * (
        1 - target_reduction_percent / 100
    )

    reduction_needed = max(
        latest_total - target_emission,
        0
    )

    actual_reduction = max(
        baseline_emission - latest_total,
        0
    )

    required_reduction = baseline_emission - target_emission

    progress_percent = (
        actual_reduction / required_reduction * 100
        if required_reduction > 0
        else 0
    )

    progress_percent = min(
        progress_percent,
        100
    )

    # =================================================
    # DASHBOARD TABS
    # =================================================
    overview_tab, analytics_tab, comparison_tab, report_tab = st.tabs(
        [
            "Overview",
            "Analytics",
            "Comparison",
            "Report & Data"
        ]
    )
    with overview_tab:
        # =================================================
        # KPI CARDS
        # =================================================
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

        kpi1.metric(
            "🌍 Total Emisi",
            f"{latest_total:,.2f} tCO2e"
        )

        kpi2.metric(
            "🔥 Scope Dominan",
            dominant_scope
        )

        kpi3.metric(
            "⚠ Status",
            status
        )

        kpi4.metric(
            "📊 Total Data",
            len(filtered_df)
        )

        kpi5.metric(
            "🎯 Progress Target",
            f"{progress_percent:.1f}%"
        )

        st.divider()


        # =================================================
        # TARGET REDUCTION PANEL
        # =================================================
        st.subheader("🎯 Target Reduction Progress")

        target_col1, target_col2, target_col3 = st.columns(3)

        target_col1.metric(
            "Baseline Emission",
            f"{baseline_emission:,.2f} tCO2e"
        )

        target_col2.metric(
            "Target Emission",
            f"{target_emission:,.2f} tCO2e"
        )

        target_col3.metric(
            "Reduction Needed",
            f"{reduction_needed:,.2f} tCO2e"
        )

        st.progress(
            int(progress_percent)
        )

        if latest_total <= target_emission:

            st.success(
                "Target reduction sudah tercapai."
            )

        else:

            st.warning(
                f"Masih perlu menurunkan {reduction_needed:,.2f} tCO2e untuk mencapai target."
            )

        st.divider()


        # =================================================
        # MAIN VISUALIZATION
        # =================================================
        chart_col1, chart_col2 = st.columns(
            [2, 1]
        )

        with chart_col1:

            st.subheader("Distribusi Emisi Global")

            donut_df = pd.DataFrame({
                "Scope": [
                    "Scope 1",
                    "Scope 2",
                    "Scope 3"
                ],
                "Emission": [
                    latest_scope1,
                    latest_scope2,
                    latest_scope3
                ]
            })

            fig_donut = px.pie(
                donut_df,
                names="Scope",
                values="Emission",
                hole=0.65,
                title="Distribusi Emisi Berdasarkan Scope"
            )

            fig_donut.update_layout(
                height=500
            )

            st.plotly_chart(
                fig_donut,
                use_container_width=True
            )

        with chart_col2:

            st.subheader("Insight")

            st.info(
                f"Scope dominan saat ini adalah {dominant_scope}."
            )

            st.write(
                f"Total emisi berdasarkan filter saat ini adalah **{latest_total:,.2f} tCO2e**."
            )

            st.write(
                f"Target pengurangan yang digunakan adalah **{target_reduction_percent:.1f}%** dari baseline."
            )

            st.write(
                f"Progress menuju target saat ini adalah **{progress_percent:.1f}%**."
            )

            st.subheader("Rekomendasi")

            st.warning(
                recommendation
            )

            st.markdown("""
            <div class="action-card">
                <div class="info-title">Apa yang Bisa Dilakukan?</div>
                <div class="info-text">
                    Mulai dari efisiensi listrik, optimalisasi kendaraan operasional,
                    pengurangan limbah, penggunaan energi terbarukan, hingga evaluasi
                    rantai pasok. Fokus terbaik adalah mengurangi scope yang paling dominan
                    terlebih dahulu.
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.divider()

    with analytics_tab:
        # =================================================
        # TREND ANALYTICS
        # =================================================
        st.subheader("Trend Emisi Bulanan")

        trend_df = filtered_df.copy()

        trend_df["Created At"] = pd.to_datetime(
            trend_df["Created At"]
        )

        trend_df["Month"] = trend_df[
            "Created At"
        ].dt.to_period("M").astype(str)

        monthly_df = trend_df.groupby(
            "Month"
        )["Total"].sum().reset_index()

        fig_trend = px.line(
            monthly_df,
            x="Month",
            y="Total",
            markers=True,
            title="Trend Emisi Bulanan"
        )

        fig_trend.update_layout(
            height=500,
            xaxis_title="Bulan",
            yaxis_title="Total Emisi (tCO2e)"
        )

        st.plotly_chart(
            fig_trend,
            use_container_width=True
        )

        st.divider()

    with comparison_tab:
        # =================================================
        # COMPANY COMPARISON ANALYTICS
        # =================================================
        st.subheader("Company Comparison Analytics")

        company_comparison_df = filtered_df.groupby(
            "Company"
        )[
            ["Scope 1", "Scope 2", "Scope 3", "Total"]
        ].sum().reset_index()

        company_comparison_df = company_comparison_df.sort_values(
            by="Total",
            ascending=False
        )

        if not company_comparison_df.empty:

            highest_company = company_comparison_df.iloc[0]["Company"]

            highest_emission = company_comparison_df.iloc[0]["Total"]

            st.info(
                f"Perusahaan dengan emisi tertinggi adalah **{highest_company}** dengan total emisi **{highest_emission:,.2f} tCO2e**."
            )

            # =================================================
            # BAR CHART TOTAL EMISSION BY COMPANY
            # =================================================
            fig_company_total = px.bar(
                company_comparison_df,
                x="Company",
                y="Total",
                title="Total Emisi per Perusahaan",
                text_auto=".2f"
            )

            fig_company_total.update_layout(
                height=500,
                xaxis_title="Perusahaan",
                yaxis_title="Total Emisi (tCO2e)"
            )

            st.plotly_chart(
                fig_company_total,
                use_container_width=True
            )

            # =================================================
            # STACKED BAR SCOPE CONTRIBUTION
            # =================================================
            scope_melt_df = company_comparison_df.melt(
                id_vars="Company",
                value_vars=[
                    "Scope 1",
                    "Scope 2",
                    "Scope 3"
                ],
                var_name="Scope",
                value_name="Emission"
            )

            fig_scope_stack = px.bar(
                scope_melt_df,
                x="Company",
                y="Emission",
                color="Scope",
                title="Kontribusi Scope per Perusahaan",
                text_auto=".2f"
            )

            fig_scope_stack.update_layout(
                height=500,
                xaxis_title="Perusahaan",
                yaxis_title="Emisi (tCO2e)",
                barmode="stack"
            )

            st.plotly_chart(
                fig_scope_stack,
                use_container_width=True
            )

            # =================================================
            # RANKING TABLE
            # =================================================
            st.subheader("Ranking Emisi Perusahaan")

            company_comparison_df["Rank"] = range(
                1,
                len(company_comparison_df) + 1
            )

            company_comparison_df = company_comparison_df[
                [
                    "Rank",
                    "Company",
                    "Scope 1",
                    "Scope 2",
                    "Scope 3",
                    "Total"
                ]
            ]

            st.dataframe(
                company_comparison_df,
                use_container_width=True
            )

        else:

            st.warning(
                "Data perusahaan belum cukup untuk comparison analytics."
            )

        st.divider()
        
    with report_tab:

        # =================================================
        # REPORT PREVIEW
        # =================================================
        st.subheader("Sustainability Report Preview")

        report_col1, report_col2 = st.columns([2, 1])

        with report_col1:

            st.markdown("### Executive Summary")

            st.write(
                f"""
                Berdasarkan data yang difilter, total emisi karbon saat ini adalah 
                **{latest_total:,.2f} tCO2e**. Sumber emisi paling dominan berasal dari 
                **{dominant_scope}**. Status emisi saat ini berada pada kategori 
                **{status}**.
                """
            )

            st.write(
                f"""
                Target pengurangan emisi yang digunakan adalah 
                **{target_reduction_percent:.1f}%** dari baseline 
                **{baseline_emission:,.2f} tCO2e**. Target emisi setelah pengurangan adalah 
                **{target_emission:,.2f} tCO2e**.
                """
            )

            if latest_total <= target_emission:

                st.success(
                    "Status target: target pengurangan emisi sudah tercapai."
                )

            else:

                st.warning(
                    f"Status target: masih diperlukan pengurangan sebesar "
                    f"{reduction_needed:,.2f} tCO2e untuk mencapai target."
                )

        with report_col2:

            st.markdown("### Report Metrics")

            st.metric(
                "Total Emission",
                f"{latest_total:,.2f} tCO2e"
            )

            st.metric(
                "Dominant Scope",
                dominant_scope
            )

            st.metric(
                "Target Progress",
                f"{progress_percent:.1f}%"
            )

        st.divider()


        # =================================================
        # REPORT DETAIL TABLE
        # =================================================
        st.subheader("Scope Breakdown for Report")

        report_breakdown_df = pd.DataFrame({
            "Scope": [
                "Scope 1",
                "Scope 2",
                "Scope 3"
            ],
            "Emission (tCO2e)": [
                latest_scope1,
                latest_scope2,
                latest_scope3
            ]
        })

        st.dataframe(
            report_breakdown_df,
            use_container_width=True
        )

        st.divider()


        # =================================================
        # EXPORT SECTION
        # =================================================
        st.subheader("Export Sustainability Report")

        export_col1, export_col2 = st.columns(2)

        with export_col1:

            if st.button("Export PDF Report"):

                pdf_file = export_pdf(
                    selected_company,
                    selected_period,
                    latest_scope1,
                    latest_scope2,
                    latest_scope3,
                    latest_total,
                    recommendation,
                    baseline_emission,
                    target_reduction_percent,
                    target_emission,
                    reduction_needed,
                    progress_percent
                )

                with open(pdf_file, "rb") as file:

                    st.download_button(
                        label="Download PDF Report",
                        data=file,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

        with export_col2:

            csv_data = filtered_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download Filtered Data CSV",
                data=csv_data,
                file_name="filtered_emission_data.csv",
                mime="text/csv"
            )

        st.divider()


        # =================================================
        # RECOMMENDATION SUMMARY
        # =================================================
        st.subheader("Recommendation Summary")

        st.info(
            recommendation
        )

        st.markdown("""
        <div class="action-card">
            <div class="info-title">Catatan Pelaporan</div>
            <div class="info-text">
                Laporan ini dapat digunakan sebagai ringkasan awal untuk evaluasi
                keberlanjutan. Untuk kebutuhan pelaporan resmi ESG, data aktivitas,
                faktor emisi, metodologi perhitungan, dan batasan organisasi tetap
                perlu diverifikasi ulang.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # =================================================
        # DATA QUALITY CHECK
        # =================================================
        st.subheader("Data Quality Check")

        total_records = len(filtered_df)

        missing_values = filtered_df.isnull().sum().sum()

        duplicate_records = filtered_df.duplicated().sum()

        negative_values = (
            (filtered_df["Scope 1"] < 0).sum() +
            (filtered_df["Scope 2"] < 0).sum() +
            (filtered_df["Scope 3"] < 0).sum() +
            (filtered_df["Total"] < 0).sum()
        )

        dq_col1, dq_col2, dq_col3, dq_col4 = st.columns(4)

        dq_col1.metric(
            "Total Records",
            total_records
        )

        dq_col2.metric(
            "Missing Values",
            missing_values
        )

        dq_col3.metric(
            "Duplicate Records",
            duplicate_records
        )

        dq_col4.metric(
            "Negative Values",
            negative_values
        )

        if missing_values == 0 and duplicate_records == 0 and negative_values == 0:

            st.success(
                "Data quality terlihat baik untuk filter saat ini."
            )

        else:

            st.warning(
                "Terdapat potensi masalah kualitas data. Periksa missing value, duplikasi, atau nilai negatif."
            )

        st.divider()

        # =================================================
        # HISTORY TABLE
        # =================================================
        st.subheader("Riwayat Emisi")

        st.dataframe(
            filtered_df,
            use_container_width=True
        )

        st.divider()

        # =================================================
        # DATA MANAGEMENT PANEL
        # =================================================
        st.subheader("Data Management")

        st.warning(
            "Gunakan fitur ini dengan hati-hati. Data yang dihapus tidak bisa dikembalikan kecuali kamu punya backup."
        )

        # =================================================
        # BACKUP CSV
        # =================================================
        backup_csv = history_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Full Database Backup CSV",
            data=backup_csv,
            file_name="emission_database_backup.csv",
            mime="text/csv"
        )

        st.divider()

        # =================================================
        # DELETE BY ID
        # =================================================
        st.markdown("### Delete Single Record")

        delete_id = st.number_input(
            "Masukkan ID data yang ingin dihapus",
            min_value=1,
            step=1
        )

        confirm_delete = st.checkbox(
            "Saya yakin ingin menghapus data dengan ID tersebut"
        )

        if st.button("Delete Selected Record"):

            if confirm_delete:

                delete_emission_by_id(
                    delete_id
                )

                st.success(
                    f"Data dengan ID {delete_id} berhasil dihapus."
                )

                st.rerun()

            else:

                st.error(
                    "Centang konfirmasi terlebih dahulu sebelum menghapus data."
                )

        st.divider()

        # =================================================
        # RESET ALL DATA
        # =================================================
        st.markdown("### Reset All Data")

        reset_text = st.text_input(
            "Ketik RESET untuk menghapus semua data"
        )

        if st.button("Reset All Emission Data"):

            if reset_text == "RESET":

                reset_all_emissions()

                st.success(
                    "Semua data emisi berhasil dihapus."
                )

                st.rerun()

            else:

                st.error(
                    "Reset dibatalkan. Kamu harus mengetik RESET dengan huruf kapital."
                )
else:

    st.warning(
        "Belum ada data emisi untuk filter yang dipilih."
    )