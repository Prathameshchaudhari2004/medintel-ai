# utils/abnormality.py
# --------------------------------------------------
# This module compares blood test values against
# standard medical reference ranges and flags
# anything that's outside normal limits.
#
# Status levels:
#   Normal   — value is within healthy range
#   Low      — below normal (might need attention)
#   High     — above normal (might need attention)
#   Critical — dangerously out of range (see a doctor NOW)
# --------------------------------------------------


# --------------------------------------------------
# REFERENCE RANGES
# 
# Each parameter has:
#   - male_range:   (low_limit, high_limit) for men
#   - female_range: (low_limit, high_limit) for women
#   - critical_low:  value below this = Critical
#   - critical_high: value above this = Critical
#   - unit:          the measurement unit
#
# These ranges come from WHO and standard clinical guidelines.
# Some tests have the same range for both genders.
# --------------------------------------------------
REFERENCE_RANGES = {
    "Hemoglobin": {
        "male_range":    (13.0, 17.0),
        "female_range":  (12.0, 15.0),
        "critical_low":  7.0,
        "critical_high": 20.0,
        "unit":          "g/dL",
        "description":   "Protein in red blood cells that carries oxygen"
    },
    "RBC": {
        "male_range":    (4.5, 5.9),
        "female_range":  (4.0, 5.2),
        "critical_low":  2.0,
        "critical_high": 7.0,
        "unit":          "million/μL",
        "description":   "Red blood cells — carry oxygen throughout the body"
    },
    "WBC": {
        "male_range":    (4.0, 11.0),
        "female_range":  (4.0, 11.0),
        "critical_low":  2.0,
        "critical_high": 30.0,
        "unit":          "K/μL",
        "description":   "White blood cells — fight infections and disease"
    },
    "Platelets": {
        "male_range":    (150, 410),
        "female_range":  (150, 410),
        "critical_low":  50,
        "critical_high": 1000,
        "unit":          "K/μL",
        "description":   "Help your blood clot when you get a cut or injury"
    },
    "Glucose": {
        "male_range":    (70, 100),
        "female_range":  (70, 100),
        "critical_low":  40,
        "critical_high": 400,
        "unit":          "mg/dL",
        "description":   "Blood sugar — main energy source for your body"
    },
    "Cholesterol": {
        "male_range":    (0, 200),
        "female_range":  (0, 200),
        "critical_low":  None,
        "critical_high": 300,
        "unit":          "mg/dL",
        "description":   "Fat-like substance in blood — needed but dangerous in excess"
    },
    "HDL": {
        "male_range":    (40, 60),
        "female_range":  (50, 60),
        "critical_low":  20,
        "critical_high": None,
        "unit":          "mg/dL",
        "description":   "Good cholesterol — higher is better, protects the heart"
    },
    "LDL": {
        "male_range":    (0, 100),
        "female_range":  (0, 100),
        "critical_low":  None,
        "critical_high": 190,
        "unit":          "mg/dL",
        "description":   "Bad cholesterol — too much increases heart disease risk"
    },
    "Triglycerides": {
        "male_range":    (0, 150),
        "female_range":  (0, 150),
        "critical_low":  None,
        "critical_high": 500,
        "unit":          "mg/dL",
        "description":   "Type of fat in your blood — high levels raise heart disease risk"
    },
    "Creatinine": {
        "male_range":    (0.7, 1.3),
        "female_range":  (0.5, 1.1),
        "critical_low":  None,
        "critical_high": 10.0,
        "unit":          "mg/dL",
        "description":   "Waste product filtered by kidneys — high levels indicate kidney problems"
    },
    "Uric Acid": {
        "male_range":    (3.5, 7.2),
        "female_range":  (2.6, 6.0),
        "critical_low":  None,
        "critical_high": 12.0,
        "unit":          "mg/dL",
        "description":   "Waste product from breaking down purines — excess causes gout"
    },
    "Bilirubin": {
        "male_range":    (0.2, 1.2),
        "female_range":  (0.2, 1.2),
        "critical_low":  None,
        "critical_high": 15.0,
        "unit":          "mg/dL",
        "description":   "Yellowish pigment from RBC breakdown — liver processes it"
    },
    "Vitamin D": {
        "male_range":    (30, 100),
        "female_range":  (30, 100),
        "critical_low":  10,
        "critical_high": None,
        "unit":          "ng/mL",
        "description":   "Essential for bones, immune system, and overall health"
    },
    "Vitamin B12": {
        "male_range":    (200, 900),
        "female_range":  (200, 900),
        "critical_low":  150,
        "critical_high": None,
        "unit":          "pg/mL",
        "description":   "Essential for nerve function and red blood cell formation"
    },
    "SGPT": {
        "male_range":    (7, 56),
        "female_range":  (7, 45),
        "critical_low":  None,
        "critical_high": 1000,
        "unit":          "U/L",
        "description":   "Liver enzyme — elevated levels indicate liver damage or disease"
    },
    "SGOT": {
        "male_range":    (10, 40),
        "female_range":  (10, 35),
        "critical_low":  None,
        "critical_high": 1000,
        "unit":          "U/L",
        "description":   "Enzyme found in liver and heart — elevated in liver/heart damage"
    },
    "HbA1c": {
        "male_range":    (4.0, 5.6),
        "female_range":  (4.0, 5.6),
        "critical_low":  None,
        "critical_high": 9.0,
        "unit":          "%",
        "description":   "3-month average blood sugar — key test for diabetes monitoring"
    },
    "TSH": {
        "male_range":    (0.4, 4.0),
        "female_range":  (0.4, 4.0),
        "critical_low":  0.01,
        "critical_high": 10.0,
        "unit":          "mIU/L",
        "description":   "Thyroid-stimulating hormone — controls thyroid function"
    },
    "Sodium": {
        "male_range":    (135, 145),
        "female_range":  (135, 145),
        "critical_low":  120,
        "critical_high": 160,
        "unit":          "mEq/L",
        "description":   "Essential mineral for fluid balance and nerve function"
    },
    "Potassium": {
        "male_range":    (3.5, 5.0),
        "female_range":  (3.5, 5.0),
        "critical_low":  2.5,
        "critical_high": 6.5,
        "unit":          "mEq/L",
        "description":   "Mineral vital for heart rhythm and muscle function"
    },
}


def check_abnormalities(values_dict, gender="Male"):
    """
    The main function — takes extracted values and checks each one
    against the reference ranges.
    
    Args:
        values_dict: dict like {"Hemoglobin": 9.5, "Glucose": 180, ...}
        gender:      "Male" or "Female" (matters for some tests)
    
    Returns:
        dict with status info for each parameter:
        {
            "Hemoglobin": {
                "value":        9.5,
                "status":       "Low",
                "normal_range": "13.0 - 17.0 g/dL",
                "unit":         "g/dL",
                "severity":     2   (1=mild, 2=moderate, 3=severe)
            }
        }
    """
    results = {}

    for param, value in values_dict.items():
        if param not in REFERENCE_RANGES:
            # We don't have reference data for this parameter — skip it
            continue

        ref = REFERENCE_RANGES[param]

        # Pick the right range for the patient's gender
        if gender == "Female":
            low_limit, high_limit = ref["female_range"]
        else:
            low_limit, high_limit = ref["male_range"]

        critical_low  = ref.get("critical_low")
        critical_high = ref.get("critical_high")
        unit          = ref.get("unit", "")

        # Build the normal range string for display
        normal_range_str = f"{low_limit} - {high_limit} {unit}"

        # Determine status — check critical first, then normal
        status   = "Normal"
        severity = 0

        if critical_low is not None and value < critical_low:
            status   = "Critical"
            severity = 3
        elif critical_high is not None and value > critical_high:
            status   = "Critical"
            severity = 3
        elif low_limit is not None and value < low_limit:
            status   = "Low"
            # How far below normal? Use that to determine mild vs moderate
            pct_below = (low_limit - value) / low_limit * 100
            severity  = 2 if pct_below > 20 else 1
        elif high_limit is not None and value > high_limit:
            status   = "High"
            pct_above = (value - high_limit) / high_limit * 100
            severity  = 2 if pct_above > 20 else 1
        else:
            status   = "Normal"
            severity = 0

        results[param] = {
            "value":        value,
            "status":       status,
            "normal_range": normal_range_str,
            "unit":         unit,
            "severity":     severity,
            "description":  ref.get("description", "")
        }

    return results


def get_severity_label(severity):
    """Converts numeric severity to a readable label"""
    labels = {0: "Normal", 1: "Mild", 2: "Moderate", 3: "Severe"}
    return labels.get(severity, "Unknown")


def get_overall_health_score(abnormalities):
    """
    Calculates a simple overall health score (0-100)
    based on how many values are normal vs abnormal.
    
    This is a simplified scoring — in real clinical practice
    it's much more nuanced.
    """
    if not abnormalities:
        return 100

    total    = len(abnormalities)
    normal   = sum(1 for v in abnormalities.values() if v["status"] == "Normal")
    mild     = sum(1 for v in abnormalities.values() if v["severity"] == 1)
    moderate = sum(1 for v in abnormalities.values() if v["severity"] == 2)
    critical = sum(1 for v in abnormalities.values() if v["severity"] == 3)

    # Deduct points for each abnormality based on severity
    score = 100
    score -= mild     * 5
    score -= moderate * 15
    score -= critical * 30

    return max(0, min(100, score))


def get_critical_alerts(abnormalities):
    """Returns only critical-status parameters — useful for showing urgent warnings"""
    return {
        param: info for param, info in abnormalities.items()
        if info["status"] == "Critical"
    }
