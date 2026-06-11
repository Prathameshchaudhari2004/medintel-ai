# agents/medical_agents.py
# --------------------------------------------------
# Multi-Agent AI System for MedIntel AI
#
# 5 specialized agents, each with one clear job:
#
#  Agent 1 - Report Analysis Agent
#            Reads raw values, spots abnormalities
#
#  Agent 2 - Risk Prediction Agent
#            Runs ML models, generates risk scores
#
#  Agent 3 - Nutrition Agent
#            Creates a personalized diet plan
#
#  Agent 4 - Medical Research Agent
#            Provides clinical context and guidelines
#
#  Agent 5 - Communication Agent
#            Takes all findings and writes a patient-
#            friendly summary anyone can understand
#
# Each agent gets a tightly-scoped system prompt so
# it focuses ONLY on its job — this is the key to
# making multi-agent systems actually work well.
# --------------------------------------------------

# agents/medical_agents.py
# 5 specialized AI agents using OpenRouter (free)

import urllib.request
import json


def _call_agent(api_key, system_prompt, user_message, max_tokens=600):
    """Single helper — calls OpenRouter API for any agent"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message}
    ]

    payload = {
        "model":      "meta-llama/llama-3.1-8b-instruct",
        "messages":   messages,
        "max_tokens": max_tokens
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
        with urllib.request.urlopen(req, timeout=40) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return f"❌ Agent error ({e.code}): {body[:150]}"
    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"


# ── Agent 1: Report Analysis ──────────────────────
def run_analysis_agent(api_key, extracted_values, abnormalities):
    system = """You are a medical report analysis expert.
Analyze blood test values and identify all abnormalities.
List each abnormal parameter with severity: Mild/Moderate/Severe.
Be factual and precise. Format as clean bullet points."""

    values_text = "Blood test results:\n"
    for param, value in extracted_values.items():
        if param in abnormalities:
            info = abnormalities[param]
            values_text += f"- {param}: {value} (Normal: {info['normal_range']}) → {info['status']}\n"

    prompt = f"{values_text}\nAnalyze these results. List abnormal values, severity, and urgent concerns."
    return _call_agent(api_key, system, prompt, 500)


# ── Agent 2: Risk Prediction ──────────────────────
def run_risk_agent(api_key, extracted_values, abnormalities):
    system = """You are a disease risk assessment specialist.
Based on blood test patterns, assess risk for common diseases.
Rate each as: Low / Medium / High Risk.
Explain which values contributed to each risk rating."""

    abnormal = {p: f"{v['value']} [{v['status']}]"
                for p, v in abnormalities.items() if v["status"] != "Normal"}

    if not abnormal:
        return "✅ All values normal. Overall disease risk appears LOW."

    prompt = f"""Abnormal values found:
{chr(10).join(f'- {p}: {v}' for p, v in abnormal.items())}

Assess risk for: Diabetes, Heart Disease, Kidney Disease, Liver Disease, Anemia.
Only mention diseases with actual signal from these values."""

    return _call_agent(api_key, system, prompt, 500)


# ── Agent 3: Nutrition ────────────────────────────
def run_nutrition_agent(api_key, extracted_values, abnormalities):
    system = """You are a clinical nutritionist.
Create personalized diet recommendations based on blood test results.
Give specific Indian food options.
For each abnormal value: 3-4 foods to eat, 2-3 to avoid, 1 lifestyle tip."""

    abnormal_items = [f"{p}: {v['value']} [{v['status']}]"
                      for p, v in abnormalities.items() if v["status"] != "Normal"]

    if not abnormal_items:
        prompt = "All values are normal. Create a general healthy Indian diet plan."
    else:
        prompt = f"""Abnormal values:
{chr(10).join(f'- {item}' for item in abnormal_items)}

Create a practical diet plan with Indian food options for each issue."""

    return _call_agent(api_key, system, prompt, 600)


# ── Agent 4: Medical Research ─────────────────────
def run_research_agent(api_key, extracted_values, abnormalities):
    system = """You are a medical research specialist.
Provide clinical context for blood test findings.
Explain what each abnormal value means medically.
Mention what follow-up tests a doctor might order.
Write in simple language a patient can understand."""

    abnormal_items = [f"{p}: {v['value']} (Normal: {v['normal_range']}) — {v['status']}"
                      for p, v in abnormalities.items() if v["status"] != "Normal"]

    if not abnormal_items:
        return "All values within normal range. Regular monitoring recommended."

    prompt = f"""Abnormal findings:
{chr(10).join(f'- {item}' for item in abnormal_items)}

For each finding: medical meaning, possible causes, and what follow-up tests to expect."""

    return _call_agent(api_key, system, prompt, 500)


# ── Agent 5: Communication ────────────────────────
def run_communication_agent(api_key, analysis, risk, nutrition):
    system = """You are a patient communication specialist.
Take complex medical findings and write a simple, friendly summary.
Use everyday language — no jargon.
Structure: What's Good → What Needs Attention → Action Steps.
Be warm, reassuring, and end with encouragement.
Keep it under 200 words."""

    prompt = f"""Based on these findings, write a patient-friendly summary:

ANALYSIS: {analysis[:400]}
RISK: {risk[:300]}
NUTRITION (key points): {nutrition[:300]}

Write a clear, kind summary with 2-3 action steps."""

    return _call_agent(api_key, system, prompt, 400)


# ── Orchestrator ──────────────────────────────────
def run_full_analysis(extracted_values, abnormalities, api_key):
    """Runs all 5 agents in sequence"""

    if not api_key:
        return None

    print("\n🤖 Starting multi-agent pipeline...")
    results = {}

    print("   Agent 1: Analyzing report...")
    results["🔍 Report Analysis Agent"] = run_analysis_agent(
        api_key, extracted_values, abnormalities)

    print("   Agent 2: Assessing risks...")
    results["📊 Risk Prediction Agent"] = run_risk_agent(
        api_key, extracted_values, abnormalities)

    print("   Agent 3: Creating nutrition plan...")
    results["🥗 Nutrition Agent"] = run_nutrition_agent(
        api_key, extracted_values, abnormalities)

    print("   Agent 4: Gathering clinical context...")
    results["🔬 Medical Research Agent"] = run_research_agent(
        api_key, extracted_values, abnormalities)

    print("   Agent 5: Writing patient summary...")
    results["💬 Patient Communication Agent"] = run_communication_agent(
        api_key,
        results["🔍 Report Analysis Agent"],
        results["📊 Risk Prediction Agent"],
        results["🥗 Nutrition Agent"]
    )

    print("✅ Done!")
    return results