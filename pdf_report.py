# pdf_report.py
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(interp, home_guidance, patient_name=""):


    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Lab Report – AI Interpretation", styles["Title"]))

    if patient_name:
        story.append(Paragraph(f"Patient: <b>{patient_name}</b>", styles["Normal"]))

    story.append(
        Paragraph(
            f"Overall Severity: <b>{interp.get('overall_severity','Unknown')}</b>",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 14))

    if interp.get("group_severity"):
        table_data = [["Panel", "Severity"]]
        for panel, sev in interp["group_severity"].items():
            table_data.append([panel, sev])

        tbl = Table(table_data)
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )

        story.append(Paragraph("Panel Severity Overview", styles["Heading2"]))
        story.append(tbl)
        story.append(Spacer(1, 10))

    story.append(Paragraph("Test-wise Interpretation", styles["Heading2"]))

    test_data = [
        ["Test", "Group", "Value", "Ref Range", "Status", "Severity", "Comment"]
    ]

    for t in interp["tests"]:
        ref = f"{t['normal_range'][0]} – {t['normal_range'][1]} {t['unit']}"
        val = f"{t['value']} {t['unit']}"

        test_data.append([
            t["test_name"], t["group"], val, ref,
            t["status"], t["severity"], t["comment"]
        ])

    t2 = Table(test_data, colWidths=[85, 55, 60, 85, 60, 60, 140])
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    story.append(t2)
    story.append(Spacer(1, 14))


    story.append(Paragraph("What You Can Do at Home", styles["Heading2"]))

    bullets = [ListItem(Paragraph(t, styles["Normal"])) for t in home_guidance]
    story.append(ListFlowable(bullets, bulletType="bullet"))
    story.append(Spacer(1, 14))


    story.append(
        Paragraph(
            "Disclaimer: This AI interpretation is for educational purposes only and "
            "should not replace medical consultation.",
            styles["Italic"],
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
