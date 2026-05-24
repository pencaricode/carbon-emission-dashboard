from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import os


# =====================================================
# EXPORT PDF REPORT
# =====================================================
def export_pdf(
    company,
    period,
    scope1,
    scope2,
    scope3,
    total,
    recommendation,
    baseline_emission,
    target_reduction_percent,
    target_emission,
    reduction_needed,
    progress_percent
):
    # =================================================
    # CREATE EXPORT FOLDER
    # =================================================
    export_dir = "exports"

    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    safe_company = str(company).replace(" ", "_").replace("/", "_")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = (
        f"{export_dir}/carbon_emission_report_"
        f"{safe_company}_{period}_{timestamp}.pdf"
    )

    # =================================================
    # DOCUMENT SETUP
    # =================================================
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#111827"),
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=18
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111827"),
        spaceBefore=14,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#374151")
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6b7280")
    )

    story = []

    # =================================================
    # TITLE
    # =================================================
    story.append(
        Paragraph(
            "Carbon Emission Report",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Generated from ESG Carbon Intelligence Dashboard",
            subtitle_style
        )
    )

    # =================================================
    # COMPANY INFORMATION
    # =================================================
    story.append(
        Paragraph(
            "Company Information",
            section_style
        )
    )

    company_table_data = [
        ["Company", str(company)],
        ["Period", str(period)],
        ["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]

    company_table = Table(
        company_table_data,
        colWidths=[5 * cm, 10 * cm]
    )

    company_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(company_table)

    # =================================================
    # EXECUTIVE SUMMARY
    # =================================================
    story.append(
        Paragraph(
            "Executive Summary",
            section_style
        )
    )

    summary_table_data = [
        ["Metric", "Value"],
        ["Total Emission", f"{total:,.2f} tCO2e"],
        ["Scope 1", f"{scope1:,.2f} tCO2e"],
        ["Scope 2", f"{scope2:,.2f} tCO2e"],
        ["Scope 3", f"{scope3:,.2f} tCO2e"],
    ]

    summary_table = Table(
        summary_table_data,
        colWidths=[7 * cm, 8 * cm]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(summary_table)

    # =================================================
    # TARGET REDUCTION
    # =================================================
    story.append(
        Paragraph(
            "Target Reduction Progress",
            section_style
        )
    )

    target_table_data = [
        ["Metric", "Value"],
        ["Baseline Emission", f"{baseline_emission:,.2f} tCO2e"],
        ["Target Reduction", f"{target_reduction_percent:.1f}%"],
        ["Target Emission", f"{target_emission:,.2f} tCO2e"],
        ["Reduction Needed", f"{reduction_needed:,.2f} tCO2e"],
        ["Progress", f"{progress_percent:.1f}%"],
    ]

    target_table = Table(
        target_table_data,
        colWidths=[7 * cm, 8 * cm]
    )

    target_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(target_table)

    # =================================================
    # RECOMMENDATION
    # =================================================
    story.append(
        Paragraph(
            "Recommendation",
            section_style
        )
    )

    clean_recommendation = str(recommendation).replace("\n", "<br/>")

    story.append(
        Paragraph(
            clean_recommendation,
            normal_style
        )
    )

    story.append(
        Spacer(1, 18)
    )

    # =================================================
    # FOOTER NOTE
    # =================================================
    story.append(
        Paragraph(
            "This report is generated automatically and should be reviewed before formal ESG or sustainability submission.",
            small_style
        )
    )

    # =================================================
    # BUILD PDF
    # =================================================
    doc.build(story)

    return filename