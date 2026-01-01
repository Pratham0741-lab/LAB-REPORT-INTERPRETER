# app.py
import streamlit as st
import json
import html
import io
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
except Exception:
    reportlab_available = False
else:
    reportlab_available = True

st.set_page_config(page_title="Lab Report Interpreter", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#f8fbff 0%, #ffffff 100%); }
    .title { font-size:30px; font-weight:700; margin-bottom:6px; }
    .subtitle { color:#4b5563; margin-top:0; margin-bottom:18px; }
    .card { background: #ffffff; padding:14px; border-radius:10px; box-shadow: 0 6px 18px rgba(14,30,37,0.06); margin-bottom:12px; }
    .lab-value { font-size:18px; font-weight:700; }
    .lab-meta { color:#6b7280; font-size:13px; }
    .label-pill { display:inline-block; padding:6px 8px; border-radius:999px; font-weight:600; margin-right:6px; }
    .ocr-box { background:#fff; border-radius:8px; padding:10px; box-shadow: 0 6px 18px rgba(14,30,37,0.04); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">🩺 Lab Report Interpreter </div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a scanned lab report (PDF). The app OCRs, extracts labs, highlights matched lines and lets you download a formatted interpreted PDF.</div>', unsafe_allow_html=True)

uploaded = st.file_uploader("Upload PDF", type=["pdf"])
if not uploaded:
    st.info("Upload a PDF to get started.")
    st.stop()

KEYWORDS = {
    "hemoglobin": ["hemoglobin", "hb"],
    "wbc": ["wbc", "white blood"],
    "platelets": ["platelet", "plt"],
    "glucose": ["glucose", "fbs", "fasting"],
    "cholesterol": ["cholesterol", "tchol"],
    "age": ["age", "yrs", "years"]
}
RANGES = {
    "hemoglobin": (12.0, 17.0),
    "wbc": (4.0, 11.0),
    "platelets": (150.0, 450.0),
    "glucose": (70.0, 99.0),
    "cholesterol": (0.0, 200.0)
}
COLORS = {
    "hemoglobin": "#ffd6d6",
    "wbc": "#fff0d1",
    "platelets": "#fff9d9",
    "glucose": "#eaffea",
    "cholesterol": "#e6f0ff",
    "age": "#f3e6ff"
}

def first_number_in_line(line: str):
    for token in line.replace(",", " ").split():
        token = token.strip(":;")
        cleaned = "".join(ch for ch in token if (ch.isdigit() or ch == "." or ch == "-"))
        if cleaned and any(ch.isdigit() for ch in cleaned):
            try:
                return float(cleaned)
            except:
                pass
    return None

def ocr_pdf_bytes(file_bytes: bytes, dpi=300):
    pages = convert_from_bytes(file_bytes, dpi=dpi)
    texts = []
    for page in pages:
        gray = page.convert("L")
        txt = pytesseract.image_to_string(gray)
        texts.append(txt)
    return "\n\n".join(texts)

def parse_and_match_lines(text: str):
    parsed = {k: None for k in KEYWORDS}
    matches = {k: [] for k in KEYWORDS}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        low = line.lower()
        for lab, kws in KEYWORDS.items():
            found_kw_in_line = any(kw in low for kw in kws)
            if found_kw_in_line:
                val = first_number_in_line(line)
                if parsed[lab] is None and val is not None:
                    parsed[lab] = int(val) if lab == "age" else float(val)
                matches[lab].append((i, line, val))
    return parsed, matches, lines

def interpret(parsed):
    flags = {}
    for lab, rng in RANGES.items():
        v = parsed.get(lab)
        if v is None:
            flags[lab] = "not found"
        else:
            lo, hi = rng
            flags[lab] = "low" if v < lo else ("high" if v > hi else "normal")

    conditions = {}
    hb = parsed.get("hemoglobin")
    wbc = parsed.get("wbc")
    glucose = parsed.get("glucose")
    chol = parsed.get("cholesterol")

    conditions["anemia"] = ("possible" if hb is not None and hb < 12.0 else
                            ("unknown" if hb is None else "unlikely"))
    if wbc is None:
        conditions["infection"] = "unknown"
    else:
        conditions["infection"] = "possible" if (wbc > 11.0 or wbc < 3.0) else "unlikely"
    if glucose is None:
        conditions["diabetes"] = "unknown"
    else:
        conditions["diabetes"] = ("likely" if glucose >= 126.0 else
                                ("borderline" if glucose >= 100.0 else "unlikely"))
    conditions["high_cholesterol"] = ("possible" if chol is not None and chol > 200.0 else
                                    ("unknown" if chol is None else "unlikely"))
    return flags, conditions

def build_interpreted_pdf_bytes(parsed, flags, conditions, matches, lines, ocr_text):
    """
    Build a nicely formatted PDF (in-memory) summarizing the interpretation.
    Returns bytes.
    """
    if not reportlab_available:
        raise RuntimeError("reportlab is required to create PDF. Install with: pip install reportlab")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("ABC Diagnostic Laboratory — Interpreted Report", styles["Title"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Auto-generated interpretation (simple rules). For clinical decisions, consult a clinician.", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Extracted Values", styles["Heading2"]))
    data = [["Test", "Value", "Status"]]
    for lab in ["hemoglobin", "wbc", "platelets", "glucose", "cholesterol", "age"]:
        val = parsed.get(lab)
        status = flags.get(lab, "not found")
        data.append([lab.capitalize(), str(val) if val is not None else "—", status])
    t = Table(data, colWidths=[120, 120, 120])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f6ff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e6edf7")),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8)
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Plain-language summary & suggested next steps", styles["Heading2"]))
    for k, v in conditions.items():
        story.append(Paragraph(f"<b>{k.replace('_',' ').title()}:</b> {v}", ParagraphStyle("normal", parent=styles["Normal"], spaceAfter=6)))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Matched OCR lines (where values were found)", styles["Heading2"]))
    matched_items = []
    for lab, occ in matches.items():
        for idx, line, val in occ:
            matched_items.append((lab, idx, line.strip()))
    matched_items.sort(key=lambda x: x[1])
    if not matched_items:
        story.append(Paragraph("(No matched lines detected in OCR output.)", styles["Normal"]))
    else:
        for lab, idx, line in matched_items[:200]:
            display = f"{lab.upper()} (line {idx+1}): {line}"
            story.append(Paragraph(display, ParagraphStyle("mono", parent=styles["Code"], fontName="Courier", fontSize=9, spaceAfter=4)))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Raw OCR text (truncated)", styles["Heading2"]))
    raw_preview = "\n".join(lines[:50])  # first 50 lines
    story.append(Paragraph(raw_preview.replace("<","&lt;").replace(">","&gt;"), ParagraphStyle("mono2", parent=styles["Code"], fontName="Courier", fontSize=8)))

    doc.build(story)
    buf.seek(0)
    return buf.read()

if st.button("Analyze"):
    with st.spinner("Running OCR and extracting values..."):
        try:
            ocr_text = ocr_pdf_bytes(uploaded.getvalue(), dpi=300)
        except Exception as e:
            st.error("OCR failed. Make sure Tesseract and Poppler are installed and paths are set.")
            st.error(str(e))
            st.stop()

        parsed, matches, lines = parse_and_match_lines(ocr_text)
        flags, conditions = interpret(parsed)

    left, right = st.columns([1, 1.6], gap="large")

    with left:
        st.markdown("### Extracted values")
        kv_cols = st.columns(2)
        keys = ["hemoglobin", "wbc", "platelets", "glucose", "cholesterol", "age"]
        for i, lab in enumerate(keys):
            col = kv_cols[i % 2]
            val = parsed.get(lab)
            col.markdown(f"**{lab.capitalize()}**")
            col.markdown(f"{val if val is not None else '—'}")

        st.markdown("### Flags")
        for lab, flag in flags.items():
            emoji = "🟢" if flag == "normal" else ("🔴" if flag in ("low", "high") else "⚪")
            st.write(f"{emoji} **{lab}**: {flag}")

        st.markdown("### Plain-language hints")
        for k, v in conditions.items():
            st.write(f"**{k}** — {v}")

    with right:
        st.markdown("### Highlights (OCR text)")
        legend_html = "<div style='display:flex;gap:8px;margin-bottom:8px;'>"
        for lab, color in COLORS.items():
            legend_html += f"<div style='padding:6px 10px;border-radius:8px;background:{color};font-weight:600'>{lab}</div>"
        legend_html += "</div>"
        st.markdown(legend_html, unsafe_allow_html=True)

        line_lab_map = {}
        for lab, occ in matches.items():
            for idx, ln, val in occ:
                line_lab_map.setdefault(idx, []).append((lab, val))

        html_lines = []
        for i, raw_line in enumerate(lines):
            safe = html.escape(raw_line) if raw_line.strip() != "" else "&nbsp;"
            if i in line_lab_map:
                labs_on_line = line_lab_map[i]
                color = COLORS.get(labs_on_line[0][0], "#fff9e6")
                labels = " | ".join(f"{lab}{('='+str(int(val)) if val and val==int(val) else ('='+str(val) if val else ''))}" for lab, val in labs_on_line)
                html_lines.append(
                    f"<div style='background:{color}; padding:10px; border-radius:8px; margin-bottom:6px;'>"
                    f"<div style='font-weight:700; margin-bottom:6px; color:#111'>{labels}</div>"
                    f"<div style='white-space:pre-wrap; font-family:monospace; color:#111'>{safe}</div>"
                    f"</div>"
                )
            else:
                html_lines.append(f"<div style='color:#555; white-space:pre-wrap; font-family:monospace; margin-bottom:6px'>{safe}</div>")

        highlighted_html = "<div style='max-height:520px; overflow:auto;'>" + "".join(html_lines) + "</div>"
        st.markdown(highlighted_html, unsafe_allow_html=True)

    out = {
        "parsed_values": parsed,
        "flags": flags,
        "conditions": conditions,
        "matched_lines": {lab: [{"index": idx, "line": ln, "value": val} for idx, ln, val in occ] for lab, occ in matches.items()}
    }
    st.download_button("📥 Download JSON summary", data=json.dumps(out, indent=2).encode("utf-8"),
                    file_name="lab_summary.json", mime="application/json")

    if reportlab_available:
        try:
            pdf_bytes = build_interpreted_pdf_bytes(parsed, flags, conditions, matches, lines, ocr_text)
            st.download_button("📄 Download interpreted PDF", data=pdf_bytes, file_name="interpreted_report.pdf", mime="application/pdf")
        except Exception as e:
            st.error("Failed to build PDF: " + str(e))
    else:
        st.warning("Install reportlab to enable PDF export: pip install reportlab")

    with st.expander("Show raw OCR text"):
        st.text_area("OCR text", value=ocr_text, height=300)
