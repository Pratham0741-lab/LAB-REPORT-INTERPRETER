# backend/llm_layer.py
from typing import Dict, Any, List

from interpretation_config import LAB_METADATA


def _format_overall_section(ml_outputs: Dict[str, Any]) -> List[str]:
    risk = ml_outputs.get("risk", {})
    anomaly = ml_outputs.get("anomaly", {})

    risk_label = risk.get("risk_label", "Unknown")
    risk_score = risk.get("risk_score", 0.0)
    anomaly_flag = anomaly.get("is_anomalous", False)

    lines: List[str] = []

    lines.append("## 🩺 Overall Assessment\n")

    if risk_label == "Low":
        lines.append(
            f"**Model-estimated overall risk: Low** (score: `{risk_score:.2f}`). "
            "Most values are near commonly used reference ranges, but they still "
            "need to be interpreted by a doctor in the context of your symptoms and history.\n"
        )
    elif risk_label == "Moderate":
        lines.append(
            f"**Model-estimated overall risk: Moderate** (score: `{risk_score:.2f}`). "
            "Several results are outside typical ranges. This does not prove any disease, "
            "but it means a doctor should review the report and decide on follow-up.\n"
        )
    elif risk_label == "High":
        lines.append(
            f"**Model-estimated overall risk: High** (score: `{risk_score:.2f}`). "
            "Many values appear outside common reference ranges. A timely review by a doctor "
            "is recommended to understand what this means for you.\n"
        )
    else:
        lines.append(
            "The system could not compute a clear overall risk. This may be due to limited or "
            "incomplete numeric data in the report.\n"
        )

    if anomaly_flag:
        lines.append(
            "⚠️ The combination of values looks mathematically unusual compared with typical patterns. "
            "This is **only** a statistical flag and **not** a diagnosis.\n"
        )

    return lines


def _format_per_test_section(parsed_labs: Dict[str, float]) -> List[str]:
    lines: List[str] = []
    lines.append("## 🔍 Test-by-Test Explanation\n")

    if not parsed_labs:
        lines.append(
            "No lab numbers could be confidently extracted from the uploaded report. "
            "Please check that the file is clear and show the original report to your doctor.\n"
        )
        return lines

    for key, value in parsed_labs.items():
        meta = LAB_METADATA.get(key)
        if not meta:
            lines.append(f"### **{key}: {value}**\n")
            lines.append(
                "- This test is not configured in this demo, so no automated interpretation is provided.\n"
            )
            continue

        name = meta["name"]
        unit = meta.get("unit", "")
        ref_low = meta.get("ref_low")
        ref_high = meta.get("ref_high")
        low_note = meta.get("low_note", "")
        high_note = meta.get("high_note", "")

        status = "within commonly used reference range"
        explanation = ""
        if ref_low is not None and value < ref_low:
            status = "below commonly used reference range"
            explanation = low_note
        elif ref_high is not None and value > ref_high:
            status = "above commonly used reference range"
            explanation = high_note

        if ref_low is not None and ref_high is not None:
            ref_text = f"(Ref: {ref_low}–{ref_high} {unit})"
        else:
            ref_text = ""

        lines.append(
            f"### **{name}: {value} {unit}** {ref_text}\n"
            f"Status: **{status.upper()}**.\n"
        )

        if explanation.strip():
            lines.append(f"- {explanation.strip()}\n")

        lines.append("")  

    return lines


def _list_present_tests(parsed_labs: Dict[str, float], keys: List[str]) -> str:
    present = []
    for k in keys:
        if k in parsed_labs:
            meta = LAB_METADATA.get(k, {})
            present.append(meta.get("name", k))
    if not present:
        return ""
    if len(present) == 1:
        return present[0]
    if len(present) == 2:
        return f"{present[0]} and {present[1]}"
    return ", ".join(present[:-1]) + f" and {present[-1]}"


def _home_care_guidance(parsed_labs: Dict[str, float],
                        conditions: List[str]) -> List[str]:

    lines: List[str] = []
    lines.append("## 🏠 Home and Lifestyle Guidance (Based on This Pattern)\n")

    if not conditions:
        lines.append(
            "- The model did not detect a clear pattern (like anemia, diabetes or kidney strain) "
            "from the available values. Follow the general advice of your doctor and routine healthy "
            "habits such as balanced diet, regular sleep and physical activity as allowed.\n"
        )
        return lines

    if "anemia" in conditions:
        tests_used = _list_present_tests(parsed_labs, ["hemoglobin", "mcv", "mch", "rdw"])
        if tests_used:
            lines.append(f"### Pattern related to lower red cell indices ({tests_used})\n")
        else:
            lines.append("### Pattern related to lower red cell indices\n")
        lines.append(
            "- Prefer iron-rich foods in your regular diet (for example: green leafy vegetables, pulses, "
            "jaggery, dates, eggs or as suitable for your culture and medical conditions).\n"
            "- Pair meals with Vitamin C sources (like lemon, amla or oranges) rather than strong tea/coffee, "
            "which can reduce iron absorption.\n"
            "- If you feel increasing breathlessness, chest pain, black/tarry stools or very heavy bleeding, "
            "seek urgent medical care rather than only relying on diet changes.\n"
        )

    if "diabetes_poor_control" in conditions or "diabetes_borderline" in conditions:
        tests_used = _list_present_tests(parsed_labs, ["fasting_glucose", "pp_glucose", "hba1c"])
        if tests_used:
            lines.append(f"### Blood sugar pattern suggested by {tests_used}\n")
        else:
            lines.append("### Blood sugar pattern\n")
        lines.append(
            "- Try to keep meal timings regular and avoid long fasting gaps followed by very large meals.\n"
            "- Reduce sugary drinks, sweets and refined flour snacks; prefer whole grains, pulses, vegetables and nuts.\n"
            "- If your doctor has allowed it, aim for daily light to moderate activity (like 20–30 minutes of walking).\n"
            "- Do **not** change diabetes medicines or insulin doses on your own; any change should be guided by your doctor.\n"
        )

    if "lipid_issue" in conditions:
        tests_used = _list_present_tests(parsed_labs,
                                        ["total_cholesterol", "triglycerides", "hdl", "ldl"])
        if tests_used:
            lines.append(f"### Cholesterol / triglyceride pattern suggested by {tests_used}\n")
        else:
            lines.append("### Cholesterol / triglyceride pattern\n")
        lines.append(
            "- Limit deep-fried foods, fast food and repeated-use cooking oils.\n"
            "- Prefer home-cooked meals with vegetables, fruits, whole grains and appropriate healthy fats "
            "(like nuts and seeds in moderation).\n"
            "- Discuss with your doctor whether long-term lifestyle changes or medicines are needed for your level of risk.\n"
        )

    if "liver_issue" in conditions:
        tests_used = _list_present_tests(parsed_labs,
                                        ["total_bilirubin", "direct_bilirubin", "sgpt", "sgot", "alp", "gamma_gt"])
        if tests_used:
            lines.append(f"### Liver-related pattern suggested by {tests_used}\n")
        else:
            lines.append("### Liver-related pattern\n")
        lines.append(
            "- Avoid alcohol completely unless your doctor has explicitly advised otherwise.\n"
            "- Avoid unnecessary over-the-counter painkillers and herbal products; some can stress the liver.\n"
            "- Prefer simpler, less oily meals and avoid very heavy, greasy foods.\n"
            "- If you notice yellowing of eyes/skin, very dark urine, very pale stools or increasing abdominal swelling, "
            "seek medical attention quickly.\n"
        )

    if "kidney_issue" in conditions:
        tests_used = _list_present_tests(parsed_labs, ["creatinine", "urea", "uric_acid"])
        if tests_used:
            lines.append(f"### Kidney-related pattern suggested by {tests_used}\n")
        else:
            lines.append("### Kidney-related pattern\n")
        lines.append(
            "- Do not start or continue painkillers (especially NSAIDs) on your own; they can affect kidney function.\n"
            "- Avoid very salty processed foods (packaged snacks, instant soups, pickles) unless your doctor says otherwise.\n"
            "- Fluid quantity (how much water you drink) should follow your doctor’s advice, especially if you also have "
            "heart or kidney disease.\n"
            "- If you notice swelling of feet/face, very reduced urine output or breathlessness, seek prompt medical help.\n"
        )

    if "thyroid_hypo_pattern" in conditions or "thyroid_hyper_pattern" in conditions:
        tests_used = _list_present_tests(parsed_labs, ["tsh", "t3", "t4"])
        if tests_used:
            lines.append(f"### Thyroid pattern suggested by {tests_used}\n")
        else:
            lines.append("### Thyroid pattern\n")
        lines.append(
            "- If you are already on thyroid medicine, take it exactly as prescribed (usually on an empty stomach) "
            "unless your doctor changes the plan.\n"
            "- Keep a simple log of symptoms like change in weight, heat/cold intolerance, palpitations or unusual tiredness "
            "to discuss with your doctor.\n"
        )

    if "inflammation_marker_raised" in conditions:
        tests_used = _list_present_tests(parsed_labs, ["crp", "esr"])
        if tests_used:
            lines.append(f"### Inflammation marker pattern suggested by {tests_used}\n")
        else:
            lines.append("### Inflammation marker pattern\n")
        lines.append(
            "- Raised CRP/ESR are non-specific and can be seen in many infections or inflammatory conditions.\n"
            "- Focus on rest, adequate hydration and following your doctor’s advice on further tests or antibiotics if needed.\n"
        )

    vitamin_conditions = [c for c in conditions if c in ("vitamin_d_low", "vitamin_b12_low")]
    if vitamin_conditions:
        tests_used = _list_present_tests(parsed_labs, ["vitamin_d", "vitamin_b12"])
        if tests_used:
            lines.append(f"### Vitamin level pattern suggested by {tests_used}\n")
        else:
            lines.append("### Vitamin level pattern\n")
        lines.append(
            "- Discuss with your doctor whether supplements are needed and in what dose; large-dose supplements "
            "should not be started without guidance.\n"
            "- When feasible, a varied diet and safe outdoor activity may support vitamin levels, but exact requirements "
            "are individual.\n"
        )

    lines.append(
        "\nThe above points are **supportive lifestyle suggestions based on the patterns detected in this report**. "
        "They are **not a treatment plan**. Never start, stop or change medicines based only on this summary.\n"
    )

    return lines


def _when_to_seek_help_section() -> List[str]:
    lines: List[str] = []

    lines.append("## 🧑‍⚕️ When to See a Doctor or Visit a Hospital\n")
    lines.append(
        "- Share this report with a qualified doctor, especially if any values are flagged as high or low, "
        "or if you feel unwell.\n"
    )
    lines.append(
        "- Plan a follow-up visit to discuss how these results fit with your symptoms, examination and other tests.\n"
    )
    lines.append("### 🚨 Seek urgent or emergency care if you experience:\n")
    lines.append(
        "- Severe or sudden chest pain\n"
        "- Severe breathlessness or difficulty breathing\n"
        "- Sudden weakness of face/arm/leg, slurred speech or confusion\n"
        "- Very low urine output or no urine for many hours\n"
        "- Very heavy or uncontrolled bleeding\n"
        "- Seizures, loss of consciousness or any feeling that something is seriously wrong\n"
    )
    return lines


def generate_interpretation_full(parsed_labs: Dict[str, float],
                                ml_outputs: Dict[str, Any]) -> str:

    lines: List[str] = []

    lines.append("## 🧾 Detailed Summary of Your Lab Report\n")
    lines.append(
        "This explanation is generated automatically to help you understand the numbers on your lab report. "
        "It is **not a diagnosis** and cannot replace a consultation with a qualified doctor.\n"
    )

    lines.extend(_format_overall_section(ml_outputs))

    lines.extend(_format_per_test_section(parsed_labs))

    conditions: List[str] = ml_outputs.get("conditions", []) or []
    lines.extend(_home_care_guidance(parsed_labs, conditions))

    lines.extend(_when_to_seek_help_section())

    lines.append("---\n")
    lines.append(
        "⚠️ **Important:** This tool does not know your full medical history, current medicines or physical examination findings. "
        "Never make changes to treatment based only on this report or this summary. Always follow the advice of your doctor.\n"
    )

    return "\n".join(lines)
