# utils/translator.py
# --------------------------------------------------
# Handles translating health report explanations into
# Hindi, Marathi, and Gujarati.
#
# Uses deep_translator (googletrans wrapper) which is
# free and doesn't need an API key.
#
# If translation fails for any reason, it just falls back
# to English — so the app never crashes because of this.
# --------------------------------------------------

# Language codes for Google Translate
LANGUAGE_CODES = {
    "Hindi":   "hi",
    "Marathi": "mr",
    "Gujarati": "gu",
    "English": "en"
}

# Track whether the translation library is available
translation_available = False

try:
    from deep_translator import GoogleTranslator
    translation_available = True
except ImportError:
    print("deep_translator not installed. Translation will be disabled.")
    print("Install it with: pip install deep-translator")


def translate_text(text, target_language):
    """
    Translates a piece of text to the target language.
    
    Args:
        text:             The text to translate (in English)
        target_language:  "Hindi", "Marathi", "Gujarati", or "English"
    
    Returns:
        Translated text, or original English text if translation fails
    """
    # No need to translate if already English
    if target_language == "English" or target_language == "en":
        return text
    
    lang_code = LANGUAGE_CODES.get(target_language)
    if not lang_code:
        return text
    
    if not translation_available:
        return text + f"\n\n(Translation to {target_language} not available. Install deep-translator.)"
    
    try:
        # Google Translate has a character limit, so we split long text
        # into chunks if needed
        if len(text) > 4500:
            chunks = _split_text(text, 4000)
            translated_chunks = []
            for chunk in chunks:
                translated = GoogleTranslator(source="en", target=lang_code).translate(chunk)
                translated_chunks.append(translated)
            return "\n".join(translated_chunks)
        else:
            translated = GoogleTranslator(source="en", target=lang_code).translate(text)
            return translated
    
    except Exception as e:
        print(f"Translation failed: {e}")
        # Return original English text with a note
        return text


def translate_report_summary(abnormalities_dict, target_language):
    """
    Translates the key finding labels (like "High", "Low", "Normal") 
    and parameter names for the report display.
    
    This is for when we want the entire dashboard in another language.
    """
    if target_language == "English":
        return abnormalities_dict
    
    # Pre-translated common medical terms
    # This is faster and more accurate than machine-translating these
    term_translations = {
        "Hindi": {
            "Normal": "सामान्य",
            "High": "अधिक",
            "Low": "कम",
            "Critical": "गंभीर",
            "Hemoglobin": "हीमोग्लोबिन",
            "Glucose": "ग्लूकोज़",
            "Cholesterol": "कोलेस्ट्रॉल",
            "Creatinine": "क्रिएटिनिन",
            "Platelets": "प्लेटलेट्स",
            "Your value is": "आपका मूल्य है",
            "Normal range": "सामान्य सीमा",
            "Please consult your doctor": "कृपया अपने डॉक्टर से मिलें"
        },
        "Marathi": {
            "Normal": "सामान्य",
            "High": "जास्त",
            "Low": "कमी",
            "Critical": "गंभीर",
            "Hemoglobin": "हिमोग्लोबिन",
            "Glucose": "ग्लुकोज",
            "Cholesterol": "कोलेस्टेरॉल",
            "Creatinine": "क्रिएटिनिन",
            "Platelets": "प्लेटलेट्स",
            "Please consult your doctor": "कृपया आपल्या डॉक्टरांचा सल्ला घ्या"
        },
        "Gujarati": {
            "Normal": "સામાન્ય",
            "High": "વધુ",
            "Low": "ઓછું",
            "Critical": "ગંભીર",
            "Hemoglobin": "હિમોગ્લોબિન",
            "Glucose": "ગ્લુકોઝ",
            "Cholesterol": "કોલેસ્ટ્રોલ",
            "Creatinine": "ક્રિએટિનિન",
            "Platelets": "પ્લેટલેટ્સ",
            "Please consult your doctor": "કૃપા કરીને તમારા ડૉક્ટરની સલાહ લો"
        }
    }
    
    return term_translations.get(target_language, {})


def get_language_greeting(language):
    """Returns a language-appropriate greeting for the chatbot"""
    greetings = {
        "Hindi":    "नमस्ते! मैं MedIntel AI हूं। आपकी कैसे मदद कर सकता हूं?",
        "Marathi":  "नमस्कार! मी MedIntel AI आहे. मी तुम्हाला कसे मदत करू शकतो?",
        "Gujarati": "નમસ્તે! હું MedIntel AI છું. હું તમારી કેવી રીતે મદદ કરી શકું?",
        "English":  "Hello! I'm MedIntel AI. How can I help you today?"
    }
    return greetings.get(language, greetings["English"])


def _split_text(text, chunk_size):
    """
    Splits long text into smaller chunks at sentence boundaries.
    This is needed because Google Translate has a character limit.
    """
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
