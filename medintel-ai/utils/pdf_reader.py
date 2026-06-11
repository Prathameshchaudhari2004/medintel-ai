# utils/pdf_reader.py
# --------------------------------------------------
# This module handles reading medical PDFs and pulling
# out test values like Hemoglobin, Glucose, etc.
#
# It tries three approaches in order:
#   1. pdfplumber (works for most digital PDFs)
#   2. PyPDF2 (fallback)
#   3. EasyOCR (for scanned image-based PDFs)
#
# Real blood test PDFs have patterns like:
#   "Hemoglobin        9.5 g/dL"
# We use regex to find those patterns.
# --------------------------------------------------

import re
import os

# Try importing PDF libraries — they might not all be installed
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False


# --------------------------------------------------
# All the test parameters we know how to extract.
# Each entry has the parameter name and a list of
# possible labels that labs might use (different labs
# write things differently — "Hgb", "HGB", "Hemoglobin"
# all mean the same thing).
# --------------------------------------------------
PARAMETERS = {
    "Hemoglobin": ["hemoglobin", "hgb", "hb", "haemoglobin"],
    "RBC":        ["rbc", "red blood cell", "red blood cells", "erythrocytes"],
    "WBC":        ["wbc", "white blood cell", "white blood cells", "leukocytes", "total wbc"],
    "Platelets":  ["platelet", "platelets", "plt", "thrombocytes"],
    "Glucose":    ["glucose", "blood glucose", "fasting glucose", "random glucose", "blood sugar", "fbs", "rbs"],
    "Cholesterol":["cholesterol", "total cholesterol", "t. cholesterol", "serum cholesterol"],
    "HDL":        ["hdl", "hdl cholesterol", "hdl-c", "high density lipoprotein"],
    "LDL":        ["ldl", "ldl cholesterol", "ldl-c", "low density lipoprotein"],
    "Triglycerides":["triglycerides", "tg", "triglyceride", "serum triglycerides"],
    "Creatinine": ["creatinine", "serum creatinine", "s. creatinine", "s creatinine"],
    "Uric Acid":  ["uric acid", "serum uric acid", "s. uric acid"],
    "Bilirubin":  ["bilirubin", "total bilirubin", "t. bilirubin", "s. bilirubin"],
    "Vitamin D":  ["vitamin d", "25-oh vitamin d", "25(oh)d", "vit d", "vitamin d3"],
    "Vitamin B12":["vitamin b12", "vit b12", "cyanocobalamin", "cobalamin"],
    "SGPT":       ["sgpt", "alt", "alanine aminotransferase", "alanine transaminase"],
    "SGOT":       ["sgot", "ast", "aspartate aminotransferase", "aspartate transaminase"],
    "HbA1c":      ["hba1c", "glycated hemoglobin", "glycohemoglobin", "a1c"],
    "TSH":        ["tsh", "thyroid stimulating hormone", "thyrotropin"],
    "Sodium":     ["sodium", "na", "serum sodium"],
    "Potassium":  ["potassium", "k", "serum potassium"],
}


def extract_text_with_pdfplumber(pdf_path):
    """
    Best method — pdfplumber is the most reliable for digital PDFs.
    Returns all the text from every page as one big string.
    """
    if not HAS_PDFPLUMBER:
        return None

    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text if text.strip() else None
    except Exception as e:
        print(f"pdfplumber failed: {e}")
        return None


def extract_text_with_pypdf2(pdf_path):
    """
    Fallback method if pdfplumber fails.
    PyPDF2 is less accurate but works on most PDFs.
    """
    if not HAS_PYPDF2:
        return None

    try:
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text if text.strip() else None
    except Exception as e:
        print(f"PyPDF2 failed: {e}")
        return None


def extract_text_with_ocr(pdf_path):
    """
    Last resort — for scanned/image PDFs that have no digital text.
    Uses EasyOCR to read the image.
    This is slower but works even on scanned reports.
    """
    if not HAS_EASYOCR:
        return None

    try:
        # Convert PDF pages to images first
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        reader = easyocr.Reader(["en"])

        for page_num in range(len(doc)):
            page = doc[page_num]
            # Get the page as an image
            pix = page.get_pixmap(dpi=200)
            img_path = f"/tmp/page_{page_num}.png"
            pix.save(img_path)

            # Run OCR on the image
            results = reader.readtext(img_path, detail=0)
            text += " ".join(results) + "\n"

            # Clean up temp image
            os.remove(img_path)

        return text if text.strip() else None
    except Exception as e:
        print(f"OCR failed: {e}")
        return None


def find_value_in_text(text, parameter_name):
    """
    The core extraction function.
    
    Takes the full PDF text and looks for a specific parameter value.
    
    Lab reports typically look like:
        Hemoglobin    9.5    g/dL    (13.0 - 17.0)
    or:
        Hemoglobin: 9.5
    
    We use regex to match these patterns. The (?i) makes it case-insensitive.
    """
    text_lower = text.lower()
    aliases = PARAMETERS.get(parameter_name, [parameter_name.lower()])

    for alias in aliases:
        # Pattern explanation:
        # - alias: the test name (e.g., "hemoglobin")
        # - [:\s|]+: colon or spaces or pipe after the name
        # - (\d+\.?\d*): the number value (like 9.5 or 180)
        # We try a few different separator patterns since labs format differently

        patterns = [
            rf"(?i){re.escape(alias)}\s*[:\-|]*\s*(\d+\.?\d*)",
            rf"(?i){re.escape(alias)}\s+(\d+\.?\d*)\s",
            rf"(?i){re.escape(alias)}.*?(\d+\.\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                # Sanity check — reject obviously wrong values
                # (regex sometimes grabs test IDs or dates instead of values)
                if _is_reasonable_value(parameter_name, value):
                    return value

    return None


def _is_reasonable_value(parameter_name, value):
    """
    Quick sanity check — makes sure extracted values are in a plausible range.
    This prevents us from accidentally grabbing a date like "2024" as a glucose value.
    """
    reasonable_ranges = {
        "Hemoglobin":   (1,   25),
        "RBC":          (1,   10),
        "WBC":          (0.5, 100),
        "Platelets":    (10,  1500),
        "Glucose":      (20,  800),
        "Cholesterol":  (50,  500),
        "HDL":          (5,   200),
        "LDL":          (10,  400),
        "Triglycerides":(10,  1000),
        "Creatinine":   (0.1, 20),
        "Uric Acid":    (0.5, 20),
        "Bilirubin":    (0.1, 30),
        "Vitamin D":    (1,   200),
        "Vitamin B12":  (50,  2000),
        "SGPT":         (1,   5000),
        "SGOT":         (1,   5000),
        "HbA1c":        (3,   20),
        "TSH":          (0.01, 100),
        "Sodium":       (100, 180),
        "Potassium":    (1,   10),
    }
    lo, hi = reasonable_ranges.get(parameter_name, (0, 99999))
    return lo <= value <= hi


def extract_report_values(pdf_path):
    """
    Main function — the one app.py calls.
    
    1. Extracts all text from the PDF
    2. Searches for each known parameter
    3. Returns a dict of found values + the raw text
    
    Returns:
        tuple: (dict of {param: value}, raw text string)
    """
    print(f"\n📄 Trying to read: {pdf_path}")

    # Try each extraction method until one works
    raw_text = (
        extract_text_with_pdfplumber(pdf_path) or
        extract_text_with_pypdf2(pdf_path)      or
        extract_text_with_ocr(pdf_path)          or
        ""
    )

    if not raw_text:
        print("❌ Could not extract any text from this PDF.")
        return {}, ""

    print(f"✅ Extracted {len(raw_text)} characters of text")

    # Now search for each parameter in the extracted text
    found_values = {}
    for param_name in PARAMETERS:
        value = find_value_in_text(raw_text, param_name)
        if value is not None:
            found_values[param_name] = value
            print(f"   Found {param_name}: {value}")

    print(f"\n✅ Total parameters found: {len(found_values)}")
    return found_values, raw_text


def parse_manual_text(text):
    """
    Utility function for when users paste raw text instead of uploading a PDF.
    Works the same as the PDF extraction but on text directly.
    """
    found_values = {}
    for param_name in PARAMETERS:
        value = find_value_in_text(text, param_name)
        if value is not None:
            found_values[param_name] = value
    return found_values
