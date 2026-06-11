# chatbot/assistant.py
# OpenRouter API — Free, works in India, no credit card
# Uses Llama 3.1 model (completely free)

import urllib.request
import json


def build_report_context(extracted_values, abnormalities, patient_info):
    context = ""
    if patient_info:
        context += f"Patient: {patient_info.get('name','Unknown')}, "
        context += f"Age: {patient_info.get('age','?')}, "
        context += f"Gender: {patient_info.get('gender','?')}\n\n"

    if extracted_values:
        context += "Blood Test Results:\n"
        for param, value in extracted_values.items():
            if param in abnormalities:
                status = abnormalities[param]['status']
                rng    = abnormalities[param]['normal_range']
                flag   = f" WARNING:{status}" if status != "Normal" else " OK"
                context += f"  - {param}: {value} (Normal: {rng}){flag}\n"
    return context


def get_ai_response(user_message, api_key, chat_history,
                    extracted_values, abnormalities, patient_info):

    if not api_key or not api_key.strip():
        return "Please enter your OpenRouter API key in the sidebar."

    report_context = build_report_context(
        extracted_values, abnormalities, patient_info
    )

    system_msg = f"""You are MedIntel AI Assistant — a friendly health assistant.
Explain medical terms in simple, clear language.
Always recommend consulting a doctor for final diagnosis.
Be warm, supportive, and concise (3-5 sentences).

{report_context}"""

    messages = [{"role": "system", "content": system_msg}]
    for msg in chat_history[-6:]:
        if msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    payload = {
        "model":    "meta-llama/llama-3.1-8b-instruct",
        "messages": messages,
        "max_tokens": 600
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer":  "http://localhost:8501",
                "X-Title":       "MedIntel AI"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        return result["choices"][0]["message"]["content"]

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        if "401" in str(e.code):
            return "❌ Invalid API key. Make sure you copied the full sk-or-v1-... key."
        elif "429" in str(e.code):
            return "⏳ Rate limit. Wait 30 seconds and try again."
        return f"Error {e.code}: {body[:150]}"

    except Exception as e:
        return f"Error: {str(e)[:150]}"