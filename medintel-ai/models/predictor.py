# models/predictor.py
# --------------------------------------------------
# This module loads trained ML models and makes
# disease risk predictions.
#
# If a trained model file is not found (meaning
# train_models.py hasn't been run yet), it falls back
# to a smart rule-based system so the app still works.
#
# The rule-based system is based on medical guidelines
# (not random guesses) so it's actually reasonable.
# --------------------------------------------------

import os
import numpy as np
import joblib

# Path where trained models are saved
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models")

# Cache loaded models so we don't reload from disk every time
_model_cache = {}


def _load_model(model_name):
    """
    Loads a trained model from disk. Uses caching to avoid
    reloading from disk on every prediction call.
    """
    if model_name in _model_cache:
        return _model_cache[model_name]

    model_path = os.path.join(MODELS_DIR, f"{model_name}_model.pkl")

    if not os.path.exists(model_path):
        print(f"⚠️  Model not found: {model_path}")
        print("   Run: python models/train_models.py to train models first.")
        return None

    try:
        model = joblib.load(model_path)
        _model_cache[model_name] = model
        print(f"✅ Loaded {model_name} model from disk")
        return model
    except Exception as e:
        print(f"❌ Failed to load {model_name} model: {e}")
        return None


def _load_feature_names(model_name):
    """Loads the list of feature names the model was trained on"""
    path = os.path.join(MODELS_DIR, f"{model_name}_features.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None


def _make_risk_result(probability):
    """
    Converts a probability (0-1) into a risk score (0-100)
    and a risk level label.
    
    Thresholds:
      0-33%:  Low Risk
      34-60%: Medium Risk
      61%+:   High Risk
    """
    risk_score = int(probability * 100)

    if probability < 0.33:
        risk_level = "Low"
    elif probability < 0.60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "risk_score":  risk_score,
        "risk_level":  risk_level,
        "probability": probability,
        "model_used":  "ML"
    }


# -------------------------------------------------------
# RULE-BASED FALLBACKS
# These activate when trained models aren't available.
# Based on standard clinical guidelines.
# -------------------------------------------------------

def _diabetes_rule_based(features):
    """
    Estimates diabetes risk using clinical guidelines.
    Based on ADA risk factors.
    """
    risk = 0.0
    glucose = features.get("Glucose", 90)
    bmi     = features.get("BMI", 25)
    age     = features.get("Age", 30)
    hba1c   = features.get("HbA1c", 5.0)

    # Glucose is the strongest predictor
    if glucose >= 200:
        risk += 0.75
    elif glucose >= 126:
        risk += 0.60
    elif glucose >= 100:
        risk += 0.25

    # BMI
    if bmi >= 35:   risk += 0.20
    elif bmi >= 30: risk += 0.12
    elif bmi >= 25: risk += 0.05

    # Age
    if age >= 60:   risk += 0.15
    elif age >= 45: risk += 0.08

    # HbA1c if provided
    if hba1c >= 6.5:  risk += 0.40
    elif hba1c >= 5.7: risk += 0.15

    # Pregnancies (diabetes pedigree)
    preg = features.get("Pregnancies", 0)
    if preg >= 6: risk += 0.08

    prob = min(risk, 0.98)
    return {"probability": prob, "model_used": "Rule-Based"}


def _heart_rule_based(features):
    """
    Estimates heart disease risk using Framingham-inspired rules.
    """
    risk = 0.0
    age  = features.get("age", 45)
    chol = features.get("chol", 200)
    bp   = features.get("trestbps", 120)
    sex  = features.get("sex", 1)   # 1 = male, 0 = female

    # Cholesterol
    if chol >= 240:   risk += 0.20
    elif chol >= 200: risk += 0.10

    # Blood pressure
    if bp >= 160:   risk += 0.25
    elif bp >= 140: risk += 0.15
    elif bp >= 130: risk += 0.07

    # Age (risk rises significantly after 45 for men, 55 for women)
    age_threshold = 45 if sex == 1 else 55
    if age >= age_threshold + 15: risk += 0.25
    elif age >= age_threshold + 5: risk += 0.15
    elif age >= age_threshold:     risk += 0.08

    # Chest pain
    cp = features.get("cp", 0)
    if cp == 3:   risk += 0.30   # typical angina
    elif cp == 1: risk += 0.15   # atypical angina

    # Exercise-induced angina
    if features.get("exang", 0) == 1:
        risk += 0.20

    # Max heart rate (lower is worse for heart patients)
    thalach = features.get("thalach", 150)
    if thalach < 120: risk += 0.15
    elif thalach < 140: risk += 0.07

    prob = min(risk, 0.97)
    return {"probability": prob, "model_used": "Rule-Based"}


def _kidney_rule_based(features):
    """
    Estimates CKD risk based on clinical CKD staging criteria (eGFR/creatinine).
    """
    risk = 0.0
    sc  = features.get("sc", 1.0)    # serum creatinine
    hb  = features.get("hemo", 13.5) # hemoglobin
    bu  = features.get("bu", 30)     # blood urea
    sod = features.get("sod", 137)   # sodium

    # Creatinine is the most important kidney marker
    if sc >= 8.0:    risk += 0.80
    elif sc >= 4.0:  risk += 0.60
    elif sc >= 2.0:  risk += 0.40
    elif sc >= 1.5:  risk += 0.20
    elif sc >= 1.3:  risk += 0.10

    # Anemia is very common in CKD
    if hb < 8.0:    risk += 0.25
    elif hb < 11.0: risk += 0.15
    elif hb < 12.0: risk += 0.05

    # Blood urea
    if bu >= 200:   risk += 0.30
    elif bu >= 100: risk += 0.20
    elif bu >= 60:  risk += 0.10

    # Sodium imbalance
    if sod < 130 or sod > 150: risk += 0.10

    prob = min(risk, 0.99)
    return {"probability": prob, "model_used": "Rule-Based"}


# -------------------------------------------------------
# MAIN PREDICTION FUNCTION
# This is what app.py calls.
# -------------------------------------------------------

def predict_disease_risk(disease_type, features):
    """
    Main prediction function.
    
    Args:
        disease_type: "diabetes", "heart", or "kidney"
        features:     dict of feature name → value
    
    Returns:
        dict with keys: risk_score, risk_level, probability, model_used
        Returns None if something goes wrong.
    """
    disease_type = disease_type.lower()

    # Try to use trained ML model first
    model = _load_model(disease_type)

    if model is not None:
        try:
            feature_names = _load_feature_names(disease_type)
            if feature_names:
                # Build a feature array in the right order
                # Use 0 for any missing features
                feature_array = np.array([[features.get(f, 0) for f in feature_names]])
            else:
                # No feature list saved — just use values in whatever order they come in
                feature_array = np.array([list(features.values())])

            probability = model.predict_proba(feature_array)[0][1]
            result = _make_risk_result(probability)
            result["model_used"] = "ML Model"
            return result

        except Exception as e:
            print(f"⚠️  ML prediction failed: {e}. Falling back to rules.")
            # Fall through to rule-based

    # Fallback: use rule-based system
    print(f"ℹ️  Using rule-based prediction for {disease_type}")

    fallback_functions = {
        "diabetes": _diabetes_rule_based,
        "heart":    _heart_rule_based,
        "kidney":   _kidney_rule_based,
    }

    fallback_fn = fallback_functions.get(disease_type)
    if not fallback_fn:
        return None

    fallback_result = fallback_fn(features)
    probability     = fallback_result["probability"]
    result          = _make_risk_result(probability)
    result["model_used"] = "Rule-Based (train models for ML predictions)"

    return result


def get_models_status():
    """
    Returns a status dict showing which models are trained and ready.
    Used in the UI to show what's available.
    """
    status = {}
    for name in ["diabetes", "heart", "kidney"]:
        path = os.path.join(MODELS_DIR, f"{name}_model.pkl")
        status[name] = {
            "trained": os.path.exists(path),
            "path": path
        }
    return status
