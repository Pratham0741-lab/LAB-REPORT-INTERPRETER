# interpret_config.py
from typing import Dict, Any

# --- ADVANCED ALIAS SYSTEM (works for ANY type of report) ---
TEST_ALIASES = {
    "hemoglobin": ["hemoglobin", "hb", "hgb", "haemoglobin"],
    "wbc": ["wbc", "white blood cell", "white blood cells", "total leucocyte count", "tlc"],
    "rbc": ["rbc", "red blood cell", "erythrocyte"],
    "platelets": ["platelet", "plt", "platelets", "platelet count"],
    "hematocrit": ["hematocrit", "hct", "pcv"],
    "mcv": ["mcv", "mean corpuscular volume"],
    "mch": ["mch", "mean corpuscular hemoglobin"],
    "mchc": ["mchc", "mean corpuscular hemoglobin concentration"],

    # Metabolic
    "glucose_fasting": ["glucose fasting", "fbs", "fasting", "fasting blood sugar"],
    "glucose_random": ["random glucose", "rbs"],
    "hba1c": ["hba1c", "glycated hemoglobin"],

    # Lipids
    "tchol": ["total cholesterol", "cholesterol total", "chol", "tchol"],
    "ldl": ["ldl", "low density lipoprotein"],
    "hdl": ["hdl", "high density lipoprotein"],
    "triglycerides": ["triglyceride", "tg", "trigs"],

    # Kidney
    "creatinine": ["creatinine", "cr"],
    "bun": ["bun", "urea", "blood urea"],

    # Liver
    "alt": ["alt", "sgpt"],
    "ast": ["ast", "sgot"],
    "bilirubin_total": ["bilirubin total", "total bilirubin"],

    # Thyroid
    "tsh": ["tsh", "thyroid stimulating hormone"],
    "t3": ["t3"],
    "t4": ["t4"],

    # Infection markers
    "crp": ["crp", "c-reactive protein"],
    "esr": ["esr", "erythrocyte sedimentation rate"],
}

# --- FULL TEST RANGES + MESSAGES (no external file needed) ---
TEST_CONFIG: Dict[str, Dict[str, Any]] = {
    "hemoglobin": {
        "label": "Hemoglobin",
        "group": "CBC",
        "normal_range": (12.0, 16.0),
        "unit": "g/dL",
        "low_msg": "Low hemoglobin may indicate anemia.",
        "high_msg": "High hemoglobin may occur in dehydration or other conditions.",
    },
    "wbc": {
        "label": "White Blood Cells (WBC)",
        "group": "CBC",
        "normal_range": (4.0, 11.0),
        "unit": "×10⁹/L",
        "low_msg": "Low WBC reduces immunity.",
        "high_msg": "High WBC can indicate infection or inflammation.",
    },
    "rbc": {
        "label": "Red Blood Cells (RBC)",
        "group": "CBC",
        "normal_range": (4.5, 5.9),
        "unit": "×10⁶/µL",
        "low_msg": "Low RBC may suggest anemia.",
        "high_msg": "High RBC may be due to dehydration or chronic hypoxia.",
    },
    "platelets": {
        "label": "Platelets",
        "group": "CBC",
        "normal_range": (150, 450),
        "unit": "×10⁹/L",
        "low_msg": "Low platelets increase bleeding risk.",
        "high_msg": "High platelets may occur due to inflammation or other conditions.",
    },

    # Lipids
    "tchol": {
        "label": "Total Cholesterol",
        "group": "Lipids",
        "normal_range": (0, 200),
        "unit": "mg/dL",
        "low_msg": "",
        "high_msg": "High cholesterol increases heart disease risk.",
    },
    "ldl": {
        "label": "LDL Cholesterol",
        "group": "Lipids",
        "normal_range": (0, 130),
        "unit": "mg/dL",
        "low_msg": "",
        "high_msg": "High LDL increases cardiovascular risk.",
    },
    "hdl": {
        "label": "HDL Cholesterol",
        "group": "Lipids",
        "normal_range": (40, 999),
        "unit": "mg/dL",
        "low_msg": "Low HDL is a heart risk factor.",
        "high_msg": "",
    },
    "triglycerides": {
        "label": "Triglycerides",
        "group": "Lipids",
        "normal_range": (0, 150),
        "unit": "mg/dL",
        "low_msg": "",
        "high_msg": "High triglycerides can indicate metabolic issues.",
    },

    # Kidney
    "creatinine": {
        "label": "Creatinine",
        "group": "Kidney",
        "normal_range": (0.6, 1.3),
        "unit": "mg/dL",
        "low_msg": "",
        "high_msg": "High creatinine suggests reduced kidney function.",
    },
    "bun": {
        "label": "Blood Urea Nitrogen (BUN)",
        "group": "Kidney",
        "normal_range": (7, 20),
        "unit": "mg/dL",
        "low_msg": "",
        "high_msg": "High BUN may indicate kidney issues or dehydration.",
    },

    # Liver
    "alt": {
        "label": "ALT",
        "group": "Liver",
        "normal_range": (0, 40),
        "unit": "U/L",
        "low_msg": "",
        "high_msg": "High ALT suggests liver cell injury.",
    },
    "ast": {
        "label": "AST",
        "group": "Liver",
        "normal_range": (0, 40),
        "unit": "U/L",
        "low_msg": "",
        "high_msg": "High AST may indicate liver or muscle stress.",
    },
    "bilirubin_total": {
        "label": "Total Bilirubin",
        "group": "Liver",
        "normal_range": (0.1, 1.2),
        "unit": "mg/dL",
        "low_msg": "",
        "high_msg": "High bilirubin may indicate jaundice or liver dysfunction.",
    },

    # Thyroid
    "tsh": {
        "label": "TSH",
        "group": "Thyroid",
        "normal_range": (0.4, 4.0),
        "unit": "µIU/mL",
        "low_msg": "Low TSH suggests hyperthyroidism.",
        "high_msg": "High TSH suggests hypothyroidism.",
    },
    "t3": {
        "label": "T3",
        "group": "Thyroid",
        "normal_range": (80, 200),
        "unit": "ng/dL",
        "low_msg": "Low T3 may indicate hypothyroidism.",
        "high_msg": "High T3 may indicate hyperthyroidism.",
    },
    "t4": {
        "label": "T4",
        "group": "Thyroid",
        "normal_range": (4.5, 12.5),
        "unit": "µg/dL",
        "low_msg": "Low T4 suggests hypothyroidism.",
        "high_msg": "High T4 suggests hyperthyroidism.",
    },

    # Infection markers
    "crp": {
        "label": "CRP",
        "group": "Inflammation",
        "normal_range": (0, 6),
        "unit": "mg/L",
        "low_msg": "",
        "high_msg": "Elevated CRP indicates inflammation or infection.",
    },
    "esr": {
        "label": "ESR",
        "group": "Inflammation",
        "normal_range": (0, 20),
        "unit": "mm/hr",
        "low_msg": "",
        "high_msg": "High ESR suggests inflammation or infection.",
    },
}
# Optional backward compatibility (old code expects this)
# Build LAB_METADATA in the format expected by ml_layer.py and llm_layer.py
LAB_METADATA: Dict[str, Dict[str, Any]] = {}

for key, cfg in TEST_CONFIG.items():
    low, high = cfg["normal_range"]
    LAB_METADATA[key] = {
        "name": cfg["label"],
        "group": cfg["group"],
        "unit": cfg["unit"],
        "ref_low": low,
        "ref_high": high,
        "low_note": cfg.get("low_msg", ""),
        "high_note": cfg.get("high_msg", ""),
    }

# Extra keys so it matches the names used by the parser / frontend
ALIAS_KEYS = {
    "total_cholesterol": "tchol",
    "total_bilirubin": "bilirubin_total",
    "sgpt": "alt",
    "sgot": "ast",
}
for new_key, base_key in ALIAS_KEYS.items():
    if base_key in LAB_METADATA:
        LAB_METADATA[new_key] = LAB_METADATA[base_key]

# Optional helpers if you still need them anywhere
SUPPORTED_TESTS = list(TEST_CONFIG.keys())
ALIAS_MAP = TEST_ALIASES
UNITS = {k: v["unit"] for k, v in TEST_CONFIG.items()}

