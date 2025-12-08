# app.py  (Streamlit frontend)
import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000/analyze_report"


def call_backend(file):
    files = {"file": (file.name, file.getvalue(), file.type)}
    resp = requests.post(BACKEND_URL, files=files, timeout=120)
    resp.raise_for_status()
    return resp.json()


def main():
    st.set_page_config(
        page_title="Lab Report Interpreter",
        layout="wide",
    )

    st.title("🧬 Lab Report Interpreter")
    st.caption("Prototype – OCR + rules-based risk scoring + AI-style explanation")

    with st.sidebar:
        st.header("Settings")
        view_mode = st.radio("View mode", ["Patient view", "Doctor view"])
        st.markdown(
            "⚠️ This is a **demo** tool. Do not use for real medical decisions."
        )

    uploaded = st.file_uploader(
        "Upload a lab report (PDF, JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"]
    )

    if not uploaded:
        st.info("Upload a report to start.")
        return

    if st.button("Analyze report"):
        with st.spinner("Sending to backend and analyzing..."):
            try:
                data = call_backend(uploaded)
            except Exception as e:
                st.error(f"Error calling backend: {e}")
                return

        ocr = data.get("ocr", {})
        parsed = data.get("parsed_labs", {})
        ml = data.get("ml_result", {})
        summary = data.get("llm_summary", "")

        st.success("Analysis complete.")

        if view_mode == "Patient view":
            show_patient_view(parsed, ml, summary)
        else:
            show_doctor_view(ocr, parsed, ml, summary)


def show_patient_view(parsed, ml, summary):
    risk = ml.get("risk", {})
    risk_label = risk.get("risk_label", "Unknown")
    risk_score = risk.get("risk_score", 0.0)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Overall risk")
        color = {
            "Low": "🟢",
            "Moderate": "🟡",
            "High": "🔴",
        }.get(risk_label, "⚪")
        st.markdown(f"{color} **{risk_label}** (score: `{risk_score:.2f}`)")

        st.subheader("Key values")
        if not parsed:
            st.write("No lab values extracted.")
        else:
            st.table(
                {
                    "Test": list(parsed.keys()),
                    "Value": [parsed[k] for k in parsed],
                }
            )

    with col2:
        st.subheader("Explanation (AI-style)")
        st.markdown(summary)


def show_doctor_view(ocr, parsed, ml, summary):
    st.subheader("OCR text (first page)")
    pages = ocr.get("pages", [])
    if pages:
        st.code(pages[0].get("text", ""), language="text")
    else:
        st.write("No OCR text")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Parsed labs (JSON)")
        st.json(parsed)

    with col2:
        st.subheader("ML outputs")
        st.json(ml)

    st.subheader("Raw explanation text")
    st.code(summary, language="markdown")


if __name__ == "__main__":
    main()
