# backend/main.py

import os
from typing import Dict

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ocr_layer import ocr_image_bytes
from parsing_layer import extract_labs_from_text
from ml_layer import full_ml_analysis
from llm_layer import generate_interpretation_full
from models_schema import OCRResult, MLResult, InterpretationResult
from fastapi import HTTPException, UploadFile, File


app = FastAPI(title="Lab Report Interpreter API")

# CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# SIMPLE FALLBACK PARSER (very basic regex-based)
# Used only if structured parser returns almost nothing.
# -------------------------------------------------------------------
import re


def simple_fallback_parser(text: str) -> Dict[str, float]:
    """
    Very naive regex parser for a few common tests.
    This is ONLY a backup if extract_labs_from_text() finds nothing.

    It looks for lines like:
        Hemoglobin 13.5 g/dL
        WBC 7800 /uL
        Creatinine 1.2 mg/dL
    and maps them to canonical keys that exist in LAB_METADATA.
    """
    patterns = {
        # canonical_key: regex pattern to capture numeric value
        "hemoglobin": r"hemoglobin[^0-9]*([\d.]+)",
        "wbc": r"(?:wbc count|total leucocyte count|wbc)[^0-9]*([\d.]+)",
        "platelets": r"(?:platelet count|platelets)[^0-9]*([\d.]+)",
        "fasting_glucose": r"(?:fasting glucose|fasting blood sugar|fbs)[^0-9]*([\d.]+)",
        "pp_glucose": r"(?:post[- ]prandial glucose|pp glucose)[^0-9]*([\d.]+)",
        "hba1c": r"(?:hba1c)[^0-9]*([\d.]+)",
        "creatinine": r"(?:serum creatinine|creatinine)[^0-9]*([\d.]+)",
        "urea": r"(?:blood urea|urea)[^0-9]*([\d.]+)",
        "total_cholesterol": r"(?:total cholesterol)[^0-9]*([\d.]+)",
        "triglycerides": r"(?:triglycerides)[^0-9]*([\d.]+)",
        "hdl": r"\bhdl\b[^0-9]*([\d.]+)",
        "ldl": r"\bldl\b[^0-9]*([\d.]+)",
        "total_bilirubin": r"(?:total bilirubin)[^0-9]*([\d.]+)",
        "direct_bilirubin": r"(?:direct bilirubin)[^0-9]*([\d.]+)",
        "sgpt": r"(?:alt\s*\(sgpt\)|sgpt|alt)[^0-9]*([\d.]+)",
        "sgot": r"(?:ast\s*\(sgot\)|sgot|ast)[^0-9]*([\d.]+)",
        "alp": r"(?:alkaline phosphatase|alp)[^0-9]*([\d.]+)",
        "tsh": r"\btsh\b[^0-9]*([\d.]+)",
        "vitamin_d": r"(?:vitamin\s*d)[^0-9]*([\d.]+)",
        "vitamin_b12": r"(?:vitamin\s*b12)[^0-9]*([\d.]+)",
        "crp": r"\bcrp\b[^0-9]*([\d.]+)",
        "esr": r"\besr\b[^0-9]*([\d.]+)",
    }

    text_low = text.lower()
    labs: Dict[str, float] = {}

    for key, pat in patterns.items():
        m = re.search(pat, text_low, re.IGNORECASE)
        if m:
            try:
                labs[key] = float(m.group(1))
            except ValueError:
                pass

    return labs


# -------------------------------------------------------------------
# API
# -------------------------------------------------------------------
@app.post("/analyze_report", response_model=InterpretationResult)
async def analyze_report(file: UploadFile = File(...)):
    # 1) Validate file type
    fname = (file.filename or "").lower()
    if fname.endswith(".pdf"):
        file_type = "pdf"
    elif any(fname.endswith(ext) for ext in (".png", ".jpg", ".jpeg")):
        file_type = "image"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, PNG or JPG.",
        )

    # 2) Read bytes
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file.")

    # 3) OCR layer
    ocr_raw = ocr_image_bytes(file_bytes, file_type=file_type)
    ocr_result = OCRResult(**ocr_raw)  # pages + full_text

    # 4) Structured parsing => canonical lab keys
    #    ✅ IMPORTANT: pass pages, not full_text
    parsed_labs = extract_labs_from_text(ocr_result.pages)

    # If almost nothing parsed, try simple regex fallback
    if not parsed_labs or len(parsed_labs) == 0:
        fallback = simple_fallback_parser(ocr_result.full_text)
        # merge / prefer structured parser values if any
        parsed_labs = {**fallback, **parsed_labs}

    # 5) ML analysis (risk + condition tags) on parsed labs
    ml_raw = full_ml_analysis(parsed_labs)
    ml_result = MLResult(**ml_raw)

    # 6) LLM-style explanation (uses parsed labs + ml_result)
    interpretation_text = generate_interpretation_full(parsed_labs, ml_raw)

    # 7) Return combined response
    return InterpretationResult(
        ocr=ocr_result,
        parsed_labs=parsed_labs,
        ml_result=ml_result,
        llm_summary=interpretation_text,
    )