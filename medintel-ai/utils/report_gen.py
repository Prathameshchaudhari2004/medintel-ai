# utils/report_gen.py
# --------------------------------------------------
# Generates a professional PDF health report that
# patients can download and share with their doctor.
#
# Uses ReportLab — the standard Python PDF library.
# The output looks like a real clinical report.
# --------------------------------------------------

from datetime import datetime
import io

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf_report(patient_info, extracted_values, abnormalities, include_sections):
    """
    Generates a complete PDF health report.
    
    Args:
        patient_info:      dict with name, age, gender
        extracted_values:  dict of {parameter: value}
        abnormalities:     dict of {parameter: {status, normal_range, ...}}
        include_sections:  list of section names to include
    
    Returns:
        bytes — the PDF file content, ready for download
    """
    if not REPORTLAB_AVAILABLE:
        # Return a simple text-based fallback if reportlab isn't installed
        return _generate_text_report(patient_info, extracted_values, abnormalities)
    
    # Create a buffer to hold the PDF in memory
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Set up text styles
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a3a5c"),
        spaceAfter=6
    )
    style_subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER
    )
    style_heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a3a5c"),
        spaceBefore=16,
        spaceAfter=8
    )
    style_normal = styles["Normal"]
    style_normal.fontSize = 10
    
    style_small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666")
    )
    
    style_disclaimer = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER,
        spaceBefore=20
    )
    
    # Build content elements
    content = []
    
    # ----- HEADER -----
    content.append(Paragraph("🏥 MedIntel AI", style_title))
    content.append(Paragraph("Intelligent Medical Report Analyzer", style_subtitle))
    content.append(Spacer(1, 0.3*cm))
    content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a5c")))
    content.append(Spacer(1, 0.4*cm))
    
    # Report metadata
    report_date = datetime.now().strftime("%d %B %Y at %I:%M %p")
    content.append(Paragraph(f"Report Generated: {report_date}", style_small))
    content.append(Spacer(1, 0.5*cm))
    
    # ----- PATIENT INFORMATION -----
    if "Patient Information" in include_sections:
        content.append(Paragraph("Patient Information", style_heading))
        
        name   = patient_info.get("name", "Not provided")
        age    = patient_info.get("age", "Not provided")
        gender = patient_info.get("gender", "Not provided")
        
        patient_data = [
            ["Patient Name", name],
            ["Age",          str(age)],
            ["Gender",       gender],
            ["Report Date",  datetime.now().strftime("%d/%m/%Y")],
        ]
        
        patient_table = Table(patient_data, colWidths=[5*cm, 12*cm])
        patient_table.setStyle(TableStyle([
            ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("BACKGROUND",  (0, 0), (0, -1), colors.HexColor("#f0f6ff")),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#ccddee")),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
            ("PADDING",     (0, 0), (-1, -1), 8),
        ]))
        content.append(patient_table)
    
    # ----- TEST RESULTS TABLE -----
    if "Test Results Table" in include_sections and extracted_values:
        content.append(Paragraph("Blood Test Results", style_heading))
        
        # Table header
        table_data = [["Parameter", "Your Value", "Normal Range", "Status"]]
        
        for param, value in extracted_values.items():
            if param in abnormalities:
                info   = abnormalities[param]
                status = info["status"]
                table_data.append([
                    param,
                    str(value),
                    info["normal_range"],
                    status
                ])
        
        result_table = Table(table_data, colWidths=[6*cm, 3.5*cm, 5*cm, 3*cm])
        
        # Color the status cells based on value
        style_cmds = [
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
            ("PADDING",     (0, 0), (-1, -1), 7),
            ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ]
        
        # Color individual status cells
        for i, row in enumerate(table_data[1:], start=1):
            status = row[3]
            cell_colors = {
                "Normal":   colors.HexColor("#e6ffed"),
                "Low":      colors.HexColor("#fff8e1"),
                "High":     colors.HexColor("#ffe6e6"),
                "Critical": colors.HexColor("#ffd0d0"),
            }
            if status in cell_colors:
                style_cmds.append(("BACKGROUND", (3, i), (3, i), cell_colors[status]))
        
        result_table.setStyle(TableStyle(style_cmds))
        content.append(result_table)
    
    # ----- ABNORMAL FINDINGS -----
    if "Abnormal Findings" in include_sections and abnormalities:
        abnormal = {k: v for k, v in abnormalities.items() if v["status"] != "Normal"}
        
        if abnormal:
            content.append(Paragraph("Abnormal Findings", style_heading))
            
            for param, info in abnormal.items():
                status = info["status"]
                icon   = "⚠" if status in ["High", "Low"] else "🚨"
                text   = (f"<b>{icon} {param}</b>: {info['value']} {info['unit']} — "
                          f"<font color='red'>{status}</font> "
                          f"(Normal: {info['normal_range']})")
                content.append(Paragraph(text, style_normal))
                content.append(Spacer(1, 0.15*cm))
    
    # ----- RECOMMENDATIONS -----
    if "Health Recommendations" in include_sections:
        content.append(Paragraph("Health Recommendations", style_heading))
        
        from utils.knowledge_base import get_diet_recommendations
        
        found_recs = False
        for param, info in abnormalities.items():
            if info["status"] != "Normal":
                recs = get_diet_recommendations(param, info["status"])
                if recs:
                    found_recs = True
                    content.append(Paragraph(f"For {param} ({info['status']}):", 
                                            ParagraphStyle("Bold", parent=style_normal, fontName="Helvetica-Bold")))
                    
                    if recs.get("include"):
                        content.append(Paragraph("Include: " + ", ".join(recs["include"][:4]), style_normal))
                    if recs.get("avoid"):
                        content.append(Paragraph("Avoid: " + ", ".join(recs["avoid"][:3]), style_normal))
                    content.append(Spacer(1, 0.2*cm))
        
        if not found_recs:
            content.append(Paragraph("All values are normal. Maintain your healthy lifestyle!", style_normal))
    
    # ----- DOCTOR ADVICE -----
    if "Doctor Consultation Advice" in include_sections:
        content.append(Paragraph("Doctor Consultation", style_heading))
        
        critical_params = [p for p, v in abnormalities.items() if v["status"] == "Critical"]
        abnormal_params = [p for p, v in abnormalities.items() if v["status"] in ["High", "Low"]]
        
        if critical_params:
            content.append(Paragraph(
                f"🚨 URGENT: The following values are at critical levels: {', '.join(critical_params)}. "
                "Please seek immediate medical attention.",
                ParagraphStyle("Alert", parent=style_normal, textColor=colors.red, fontName="Helvetica-Bold")
            ))
        elif abnormal_params:
            content.append(Paragraph(
                f"Please schedule an appointment with your doctor to discuss these abnormal values: "
                f"{', '.join(abnormal_params)}. Early intervention gives the best outcomes.",
                style_normal
            ))
        else:
            content.append(Paragraph(
                "Your blood values are within normal range. Continue with regular health check-ups "
                "as recommended by your doctor.",
                style_normal
            ))
    
    # ----- DISCLAIMER -----
    content.append(Spacer(1, 1*cm))
    content.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    content.append(Paragraph(
        "⚠️ DISCLAIMER: This report is generated by MedIntel AI for informational purposes only. "
        "It is NOT a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare professional before making any health decisions.",
        style_disclaimer
    ))
    content.append(Paragraph("Powered by MedIntel AI | www.medintelai.com", style_disclaimer))
    
    # Build the PDF
    doc.build(content)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _generate_text_report(patient_info, extracted_values, abnormalities):
    """
    Simple text-based report as fallback when reportlab isn't installed.
    Returns the text as bytes.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("        MEDINTEL AI - HEALTH REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}")
    lines.append("")
    lines.append(f"Patient: {patient_info.get('name', 'N/A')}")
    lines.append(f"Age:     {patient_info.get('age', 'N/A')}")
    lines.append(f"Gender:  {patient_info.get('gender', 'N/A')}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("TEST RESULTS")
    lines.append("-" * 60)
    
    for param, value in extracted_values.items():
        if param in abnormalities:
            status = abnormalities[param]["status"]
            rng    = abnormalities[param]["normal_range"]
            lines.append(f"{param:<20} {value:<10} Normal: {rng:<20} [{status}]")
    
    lines.append("")
    lines.append("-" * 60)
    lines.append("DISCLAIMER: For informational purposes only. Consult a doctor.")
    lines.append("=" * 60)
    
    return "\n".join(lines).encode("utf-8")
