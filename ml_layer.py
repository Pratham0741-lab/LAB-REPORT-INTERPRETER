# ml_layer.py
from typing import Dict, Any, List

from interpretation_config import LAB_METADATA


def _compute_risk(parsed_labs: Dict[str, float]) -> Dict[str, Any]:

    if not parsed_labs:
        return {
            "anomaly": {"is_anomalous": False, "score": 0.0},
            "risk": {"risk_label": "Unknown", "risk_score": 0.0},
        }

    abnormal = 0
    total = 0

    for key, value in parsed_labs.items():
        meta = LAB_METADATA.get(key)
        if not meta:
            continue
        total += 1
        low = meta.get("ref_low")
        high = meta.get("ref_high")
        if low is not None and value < low:
            abnormal += 1
        elif high is not None and value > high:
            abnormal += 1

    if total == 0:
        risk_score = 0.0
        risk_label = "Unknown"
    else:
        risk_score = min(1.0, abnormal / total)
        if risk_score < 0.25:
            risk_label = "Low"
        elif risk_score < 0.6:
            risk_label = "Moderate"
        else:
            risk_label = "High"

    anomaly_score = risk_score
    is_anomalous = abnormal > 0

    return {
        "anomaly": {
            "is_anomalous": is_anomalous,
            "score": float(round(anomaly_score, 3)),
        },
        "risk": {
            "risk_label": risk_label,
            "risk_score": float(round(risk_score, 3)),
        },
    }


def detect_conditions(parsed_labs: Dict[str, float]) -> List[str]:

    conditions: List[str] = []

    get = parsed_labs.get

    hb = get("hemoglobin")
    if hb is not None and hb < 12.0:
        conditions.append("anemia")

    fg = get("fasting_glucose")
    pp = get("pp_glucose")
    hba1c = get("hba1c")

    if (fg is not None and fg >= 126) or (pp is not None and pp >= 200) or (hba1c is not None and hba1c >= 6.5):
        conditions.append("diabetes_poor_control")
    elif (fg is not None and 100 <= fg < 126) or (hba1c is not None and 5.7 <= hba1c < 6.5):
        conditions.append("diabetes_borderline")

    creat = get("creatinine")
    urea = get("urea")
    if (creat is not None and creat > 1.5) or (urea is not None and urea > 40):
        conditions.append("kidney_issue")

    tb = get("total_bilirubin")
    db = get("direct_bilirubin")
    alt = get("sgpt") or get("sgpt")  # alias
    ast = get("sgot")
    alp = get("alp")
    if (
        (tb is not None and tb > 1.2)
        or (db is not None and db > 0.3)
        or (alt is not None and alt > 2 * LAB_METADATA["sgpt"]["ref_high"])
        or (ast is not None and ast > 2 * LAB_METADATA["sgot"]["ref_high"])
        or (alp is not None and alp > 1.5 * LAB_METADATA["alp"]["ref_high"])
    ):
        conditions.append("liver_issue")

    tc = get("total_cholesterol")
    tg = get("triglycerides")
    hdl = get("hdl")
    ldl = get("ldl")
    if (
        (tc is not None and tc > 200)
        or (tg is not None and tg > 150)
        or (ldl is not None and ldl > 130)
        or (hdl is not None and hdl < 40)
    ):
        conditions.append("lipid_issue")

    tsh = get("tsh")
    if tsh is not None:
        if tsh > 4.0:
            conditions.append("thyroid_hypo_pattern")
        elif tsh < 0.4:
            conditions.append("thyroid_hyper_pattern")

    crp = get("crp")
    esr = get("esr")
    if (crp is not None and crp > 5) or (esr is not None and esr > 20):
        conditions.append("inflammation_marker_raised")

    vit_d = get("vitamin_d")
    if vit_d is not None and vit_d < 20:
        conditions.append("vitamin_d_low")

    b12 = get("vitamin_b12")
    if b12 is not None and b12 < 200:
        conditions.append("vitamin_b12_low")

    seen = set()
    unique_conditions: List[str] = []
    for c in conditions:
        if c not in seen:
            seen.add(c)
            unique_conditions.append(c)

    return unique_conditions


def full_ml_analysis(parsed_labs: Dict[str, float]) -> Dict[str, Any]:

    risk_parts = _compute_risk(parsed_labs)
    conditions = detect_conditions(parsed_labs)

    return {
        "anomaly": risk_parts["anomaly"],
        "risk": risk_parts["risk"],
        "raw_features": {k: float(v) for k, v in parsed_labs.items()},
        "conditions": conditions,
    }
