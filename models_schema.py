# backend/models_schema.py
from typing import List, Dict

from pydantic import BaseModel


class OCRPage(BaseModel):
    page_number: int
    text: str


class OCRResult(BaseModel):
    pages: List[OCRPage]
    full_text: str


class MLAnomalyResult(BaseModel):
    is_anomalous: bool
    score: float


class MLRiskResult(BaseModel):
    risk_label: str
    risk_score: float


class MLResult(BaseModel):
    anomaly: MLAnomalyResult
    risk: MLRiskResult
    raw_features: Dict[str, float]
    conditions: List[str] = []  


class InterpretationResult(BaseModel):
    ocr: OCRResult
    parsed_labs: Dict[str, float]
    ml_result: MLResult
    llm_summary: str
