# app.py
# MedIntel AI - Intelligent Medical Report Analyzer
# -------------------------------------------------------
# This is the main file. Run it with: streamlit run app.py
# 
# What this does: Creates a full healthcare dashboard where users can:
#   - Upload blood test PDFs and get them analyzed
#   - See disease risk predictions using ML models
#   - Chat with an AI health assistant
#   - Get personalized diet recommendations
#   - Download a professional health report
#
# Author: Built with Python + Streamlit + Scikit-Learn + Anthropic AI
# -------------------------------------------------------

import streamlit as st
import os
import sys
import pandas as pd
import plotly.graph_objects as go

# Make sure Python can find our custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Must be the very first Streamlit call — sets up the page
st.set_page_config(
    page_title="MedIntel AI - Medical Report Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# CSS STYLING
# -------------------------------------------------------
def load_styles():
    st.markdown("""
    <style>
        /* Main header banner */
        .main-banner {
            background: linear-gradient(135deg, #1a3a5c 0%, #2980b9 100%);
            padding: 25px 30px;
            border-radius: 14px;
            margin-bottom: 28px;
            color: white;
            text-align: center;
        }
        .main-banner h1 { font-size: 2.4rem; font-weight: 800; margin: 0; }
        .main-banner p  { font-size: 1rem; opacity: 0.9; margin: 6px 0 0; }

        /* Color-coded alert boxes for test results */
        .alert-box {
            padding: 14px 18px;
            border-radius: 8px;
            margin: 8px 0;
            font-size: 0.95rem;
        }
        .alert-high     { background:#fff0f0; border-left:4px solid #e53e3e; }
        .alert-low      { background:#fffbea; border-left:4px solid #e8a317; }
        .alert-normal   { background:#f0fff4; border-left:4px solid #38a169; }
        .alert-critical { background:#ffe4e4; border-left:4px solid #9b2c2c; }

        /* Chat bubble styling */
        .bubble-user { background:#dbeafe; padding:12px 16px; border-radius:18px 18px 4px 18px;
                       margin:6px 0; max-width:78%; margin-left:auto; }
        .bubble-ai   { background:#f0f9ff; padding:12px 16px; border-radius:18px 18px 18px 4px;
                       margin:6px 0; max-width:78%; border-left:3px solid #2980b9; }

        /* Feature cards on welcome screen */
        .feature-card { background:white; border-radius:10px; padding:20px;
                        box-shadow:0 2px 12px rgba(0,0,0,0.07); text-align:center; }

        /* Hide Streamlit's default footer */
        footer { visibility: hidden; }
        #MainMenu { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


def show_banner():
    st.markdown("""
    <div class="main-banner">
        <h1>🏥 MedIntel AI</h1>
        <p>Intelligent Medical Report Analyzer — Understand Your Health in Simple Language</p>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------
# PAGE: DASHBOARD
# -------------------------------------------------------
def show_dashboard():
    extracted  = st.session_state.get("extracted_values", {})
    abnormals  = st.session_state.get("abnormalities", {})

    if not extracted:
        # Welcome screen — shows when no report has been uploaded yet
        st.markdown("### Welcome to MedIntel AI 👋")
        st.write("Upload your blood test report and I'll explain everything in simple language.")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("📄 **PDF Analysis**\nUpload your blood test PDF for instant analysis")
        with c2:
            st.info("🔬 **ML Predictions**\nGet disease risk scores for Diabetes, Heart, Kidney")
        with c3:
            st.info("🤖 **AI Chatbot**\nAsk health questions in plain language")

        st.markdown("---")
        st.write("👈 Click **Analyze Report** in the sidebar to get started.")
        return

    # Summary metrics at the top
    normal_count   = sum(1 for v in abnormals.values() if v["status"] == "Normal")
    abnormal_count = len(abnormals) - normal_count
    critical_count = sum(1 for v in abnormals.values() if v["status"] == "Critical")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Parameters", len(extracted))
    c2.metric("Normal ✅",  normal_count)
    c3.metric("Abnormal ⚠️", abnormal_count)
    c4.metric("Critical 🔴", critical_count)

    st.markdown("---")

    # Bar chart of all test values
    if abnormals:
        params, values, colors = [], [], []
        color_map = {"Normal":"#38a169", "Low":"#e8a317", "High":"#e53e3e", "Critical":"#9b2c2c"}

        for param, info in abnormals.items():
            params.append(param)
            values.append(info["value"])
            colors.append(color_map.get(info["status"], "#718096"))

        fig = go.Figure(go.Bar(
            x=params, y=values,
            marker_color=colors,
            text=[f"{v} ({abnormals[p]['status']})" for p, v in zip(params, values)],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Value: %{y}<extra></extra>"
        ))
        fig.update_layout(
            title="Your Blood Test Parameters",
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=40, l=40, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Color-coded abnormal findings
    if abnormal_count > 0:
        st.subheader("🚨 Abnormal Findings")
        for param, info in abnormals.items():
            if info["status"] != "Normal":
                icon = "🔴" if info["status"] in ["High", "Critical"] else "🟡"
                css  = f"alert-{info['status'].lower()}"
                st.markdown(
                    f'<div class="alert-box {css}">'
                    f'{icon} <strong>{param}</strong>: {info["value"]} &nbsp;|&nbsp; '
                    f'Normal Range: {info["normal_range"]} &nbsp;|&nbsp; '
                    f'<em>{info["status"]}</em>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# -------------------------------------------------------
# PAGE: ANALYZE REPORT
# -------------------------------------------------------
def show_analyze_report(language):
    from utils.pdf_reader    import extract_report_values
    from utils.abnormality   import check_abnormalities
    from utils.knowledge_base import get_explanation
    from utils.translator    import translate_text
    from database.db_handler import save_report

    st.subheader("📄 Upload & Analyze Medical Report")
    st.write("Upload your blood test or lab report PDF — I'll read and explain it for you.")

    # Basic patient info
    c1, c2, c3 = st.columns(3)
    with c1:
        name   = st.text_input("Patient Name", placeholder="Your full name")
    with c2:
        age    = st.number_input("Age", min_value=1, max_value=120, value=30)
    with c3:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    # PDF upload
    uploaded = st.file_uploader(
        "Choose your medical report (PDF only)",
        type=["pdf"],
        help="Supports CBC, blood test, lipid profile, diabetes, liver, kidney reports"
    )

    if uploaded:
        with st.spinner("Reading your report... This takes a few seconds."):
            import tempfile
            tmp = os.path.join(tempfile.gettempdir(), uploaded.name)
            with open(tmp, "wb") as f:
                f.write(uploaded.read())
            extracted, raw_text = extract_report_values(tmp)

        if extracted:
            st.success(f"✅ Found {len(extracted)} parameters in your report!")

            # Save to session state so other pages can use the data
            abnormals = check_abnormalities(extracted, gender)
            st.session_state["extracted_values"] = extracted
            st.session_state["abnormalities"]    = abnormals
            st.session_state["patient_info"]     = {"name": name, "age": age, "gender": gender}

            # Table of results with color-coded status
            st.subheader("📋 Extracted Test Values")
            rows = []
            for param, val in extracted.items():
                if param in abnormals:
                    rows.append({
                        "Parameter":   param,
                        "Your Value":  val,
                        "Normal Range": abnormals[param]["normal_range"],
                        "Status":      abnormals[param]["status"]
                    })
            if rows:
                df = pd.DataFrame(rows)
                def color_status(val):
                    m = {"Normal":"#e6ffed", "High":"#ffe6e6", "Low":"#fff8e1", "Critical":"#ffe0e0"}
                    return f"background-color: {m.get(val, '')}"
                st.dataframe(df.style.map(color_status, subset=["Status"]), use_container_width=True)

            # Plain-language explanations for abnormal values
            st.subheader("💬 What This Means (In Simple Language)")
            abnormal_found = False
            for param, info in abnormals.items():
                if info["status"] != "Normal":
                    abnormal_found = True
                    explanation = get_explanation(param, info["value"], info["status"])
                    if language != "English":
                        explanation = translate_text(explanation, language)
                    icon = "🔴" if info["status"] in ["High","Critical"] else "🟡"
                    with st.expander(f"{icon} {param} — {info['status']} ({info['value']})"):
                        st.write(explanation)

            if not abnormal_found:
                st.success("🎉 Great news! All your values are within normal range.")

            # Save to database if patient name is provided
            if name:
                save_report(name, age, gender, extracted, abnormals)

        else:
            st.warning("Couldn't extract values from this PDF. It might be a scanned image or non-standard format.")
            with st.expander("See raw extracted text"):
                st.text(raw_text[:2000] if raw_text else "No text found")

    # Manual entry as an alternative
    st.markdown("---")
    st.subheader("✏️ Or Enter Values Manually")
    st.write("No PDF? Just type your values below.")

    params = [
        ("Hemoglobin","g/dL",13.5), ("Glucose","mg/dL",90),
        ("Cholesterol","mg/dL",180), ("HDL","mg/dL",50),
        ("LDL","mg/dL",100),        ("Triglycerides","mg/dL",150),
        ("WBC","K/μL",7.0),          ("RBC","M/μL",5.0),
        ("Platelets","K/μL",250),    ("Creatinine","mg/dL",0.9),
        ("Uric Acid","mg/dL",5.0),   ("Bilirubin","mg/dL",0.8),
    ]

    manual = {}
    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]
    for i, (p, unit, default) in enumerate(params):
        with cols[i % 3]:
            v = st.number_input(f"{p} ({unit})", min_value=0.0, value=float(default), step=0.1, key=f"manual_{p}")
            manual[p] = v

    if st.button("🔍 Analyze These Values", use_container_width=True):
        abnormals = check_abnormalities(manual, gender)
        st.session_state["extracted_values"] = manual
        st.session_state["abnormalities"]    = abnormals
        st.session_state["patient_info"]     = {"name": name or "Patient", "age": age, "gender": gender}
        st.success("Done! Go to Dashboard to see results.")
        st.rerun()


# -------------------------------------------------------
# PAGE: DISEASE PREDICTION
# -------------------------------------------------------
def show_disease_prediction():
    from models.predictor import predict_disease_risk

    st.subheader("🔬 Disease Risk Prediction (ML Models)")
    st.write("Using trained Machine Learning models to estimate your risk for common diseases.")

    extracted   = st.session_state.get("extracted_values", {})
    patient     = st.session_state.get("patient_info", {"age": 40, "gender": "Male"})

    tab1, tab2, tab3 = st.tabs(["🩸 Diabetes", "❤️ Heart Disease", "🫘 Kidney Disease"])

    # --- Diabetes ---
    with tab1:
        st.write("**Diabetes Risk — Random Forest Model (PIMA Dataset)**")
        c1, c2 = st.columns(2)
        with c1:
            glucose = st.number_input("Glucose (mg/dL)", value=float(extracted.get("Glucose", 90.0)), min_value=0.0, key="d_gluc")
            bmi     = st.number_input("BMI", value=25.0, min_value=10.0, max_value=70.0, key="d_bmi")
            age_d   = st.number_input("Age", value=int(patient.get("age", 35)), min_value=1, max_value=120, key="d_age")
            preg    = st.number_input("Pregnancies", value=0, min_value=0, max_value=20, key="d_preg")
        with c2:
            bp      = st.number_input("Blood Pressure (mmHg)", value=72.0, min_value=40.0, max_value=200.0, key="d_bp")
            insulin = st.number_input("Insulin (μU/mL)", value=80.0, min_value=0.0, max_value=900.0, key="d_ins")
            skin    = st.number_input("Skin Thickness (mm)", value=20.0, min_value=0.0, max_value=100.0, key="d_skin")
            dpf     = st.number_input("Diabetes Pedigree Function", value=0.5, min_value=0.0, max_value=3.0, key="d_dpf")

        if st.button("Predict Diabetes Risk 🔮", key="btn_diabetes", use_container_width=True):
            result = predict_disease_risk("diabetes", {
                "Pregnancies": preg, "Glucose": glucose, "BloodPressure": bp,
                "SkinThickness": skin, "Insulin": insulin, "BMI": bmi,
                "DiabetesPedigreeFunction": dpf, "Age": age_d
            })
            _show_risk_card(result, "Diabetes")

    # --- Heart Disease ---
    with tab2:
        st.write("**Heart Disease Risk — XGBoost Model (UCI Dataset)**")
        c1, c2 = st.columns(2)
        with c1:
            age_h   = st.number_input("Age", value=int(patient.get("age", 45)), min_value=1, max_value=120, key="h_age")
            chol    = st.number_input("Cholesterol (mg/dL)", value=float(extracted.get("Cholesterol", 200.0)), key="h_chol")
            thal_hr = st.number_input("Max Heart Rate Achieved", value=150, min_value=60, max_value=250, key="h_hr")
            sex     = 1 if st.selectbox("Gender", ["Male","Female"], key="h_sex") == "Male" else 0
        with c2:
            cp      = st.selectbox("Chest Pain Type", [0,1,2,3],
                                   format_func=lambda x: ["No pain","Atypical angina","Non-anginal","Typical angina"][x], key="h_cp")
            rbp     = st.number_input("Resting Blood Pressure", value=120.0, min_value=60.0, max_value=250.0, key="h_rbp")
            fbs     = 1 if st.checkbox("Fasting Blood Sugar > 120 mg/dL", key="h_fbs") else 0
            exang   = 1 if st.checkbox("Exercise-Induced Angina", key="h_exang") else 0

        if st.button("Predict Heart Disease Risk 🔮", key="btn_heart", use_container_width=True):
            result = predict_disease_risk("heart", {
                "age": age_h, "sex": sex, "cp": cp, "trestbps": rbp,
                "chol": chol, "fbs": fbs, "thalach": thal_hr, "exang": exang
            })
            _show_risk_card(result, "Heart Disease")

    # --- Kidney Disease ---
    with tab3:
        st.write("**Kidney Disease Risk — Random Forest Model (CKD Dataset)**")
        c1, c2 = st.columns(2)
        with c1:
            sc   = st.number_input("Serum Creatinine (mg/dL)", value=float(extracted.get("Creatinine", 0.9)), key="k_sc")
            hemo = st.number_input("Hemoglobin (g/dL)", value=float(extracted.get("Hemoglobin", 13.5)), key="k_hemo")
            bu   = st.number_input("Blood Urea (mg/dL)", value=40.0, min_value=0.0, key="k_bu")
        with c2:
            sod  = st.number_input("Sodium (mEq/L)", value=137.0, min_value=100.0, max_value=170.0, key="k_sod")
            pot  = st.number_input("Potassium (mEq/L)", value=4.5, min_value=2.0, max_value=8.0, key="k_pot")
            pcv  = st.number_input("Packed Cell Volume (%)", value=44.0, min_value=10.0, max_value=70.0, key="k_pcv")

        if st.button("Predict Kidney Disease Risk 🔮", key="btn_kidney", use_container_width=True):
            result = predict_disease_risk("kidney", {
                "sc": sc, "hemo": hemo, "bu": bu,
                "sod": sod, "pot": pot, "pcv": pcv
            })
            _show_risk_card(result, "Kidney Disease")


def _show_risk_card(result, disease_name):
    """Helper to display prediction result as gauge + recommendation"""
    if not result:
        st.error("Prediction failed. Please train the models first by running: python models/train_models.py")
        return

    score      = result["risk_score"]
    level      = result["risk_level"]
    prob       = result["probability"]
    level_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(level, "⚪")
    bar_color  = {"Low": "#38a169", "Medium": "#d69e2e", "High": "#e53e3e"}.get(level, "#718096")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric(f"{level_icon} {disease_name}", f"{level} Risk")
        st.metric("Risk Score", f"{score}/100")
        st.metric("Probability", f"{prob:.1%}")
    with c2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": f"{disease_name} Risk Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar":  {"color": bar_color},
                "steps": [
                    {"range": [0,  33], "color": "#f0fff4"},
                    {"range": [33, 66], "color": "#fffaeb"},
                    {"range": [66,100], "color": "#fff3f3"},
                ],
            }
        ))
        fig.update_layout(height=240, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    if level == "High":
        st.error(f"⚠️ High risk detected. Please consult a doctor as soon as possible.")
    elif level == "Medium":
        st.warning("⚠️ Moderate risk. Consider lifestyle changes and regular check-ups.")
    else:
        st.success("✅ Low risk. Keep up your healthy habits!")


# -------------------------------------------------------
# PAGE: AI CHATBOT
# -------------------------------------------------------
def show_chatbot():
    from chatbot.assistant import get_ai_response

    st.subheader("💬 MedIntel AI Assistant")
    st.write("Ask me anything about your health report or medical terms. I'll explain in simple language.")

    api_key = st.sidebar.text_input(
        "🔑 OpenRouter API Key (Free)",
        type="password",
        help="Get free key from openrouter.ai"
    )

    if not api_key:
        st.info("👆 Enter your Anthropic API key in the sidebar to activate the AI chatbot.")
        st.markdown("""
        **Example questions you can ask:**
        - "What is hemoglobin and why is mine low?"
        - "What does high cholesterol mean for me?"
        - "What foods can help reduce blood sugar?"
        - "Should I be worried about my creatinine level?"
        - "Explain what LDL and HDL mean in simple words"
        """)
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    extracted  = st.session_state.get("extracted_values", {})
    abnormals  = st.session_state.get("abnormalities", {})
    patient    = st.session_state.get("patient_info", {})

    # Show existing conversation
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="bubble-user">👤 <strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bubble-ai">🤖 <strong>MedIntel AI:</strong> {msg["content"]}</div>', unsafe_allow_html=True)

    # Quick question shortcuts
    st.write("**Quick Questions:**")
    quick = ["What does my report say?", "Which values are abnormal?", "What should I eat?", "Do I need to see a doctor?"]
    qcols = st.columns(4)
    for i, q in enumerate(quick):
        if qcols[i].button(q, key=f"q_{i}"):
            st.session_state["_pending"] = q

    # Main chat input
    user_input = st.chat_input("Type your health question here...")

    # Pick up any pending quick-question click
    if "_pending" in st.session_state:
        user_input = st.session_state.pop("_pending")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("MedIntel AI is thinking..."):
            reply = get_ai_response(user_input, api_key, st.session_state.chat_history, extracted, abnormals, patient)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.get("chat_history"):
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


# -------------------------------------------------------
# PAGE: DIET & LIFESTYLE
# -------------------------------------------------------
def show_diet():
    from utils.knowledge_base import get_diet_recommendations

    st.subheader("🥗 Personalized Diet & Lifestyle Recommendations")

    abnormals = st.session_state.get("abnormalities", {})
    if not abnormals:
        st.info("Upload a report first to get personalized recommendations.")
        return

    found_any = False
    for param, info in abnormals.items():
        if info["status"] != "Normal":
            recs = get_diet_recommendations(param, info["status"])
            if recs:
                found_any = True
                icon = "🔴" if info["status"] in ["High","Critical"] else "🟡"
                with st.expander(f"{icon} For {param} ({info['status']})"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**✅ Include these foods:**")
                        for item in recs.get("include", []):
                            st.write(f"• {item}")
                    with c2:
                        st.write("**❌ Avoid these:**")
                        for item in recs.get("avoid", []):
                            st.write(f"• {item}")
                    if recs.get("lifestyle"):
                        st.write("**💪 Lifestyle tips:**")
                        for tip in recs["lifestyle"]:
                            st.write(f"• {tip}")

    if not found_any:
        st.success("🎉 All values are normal! Here are some general health tips:")
        tips = [
            "Drink 8-10 glasses of water daily",
            "Exercise for at least 30 minutes a day",
            "Eat plenty of fruits and vegetables",
            "Get 7-8 hours of sleep every night",
            "Avoid smoking and limit alcohol",
            "Manage stress with meditation or yoga",
            "Get a full blood test every 6 months"
        ]
        for t in tips:
            st.write(f"• {t}")


# -------------------------------------------------------
# PAGE: GENERATE REPORT
# -------------------------------------------------------
def show_generate_report():
    from utils.report_gen import generate_pdf_report

    st.subheader("📥 Download Your Health Report")
    st.write("Generate a professional PDF summary of your analysis.")

    extracted = st.session_state.get("extracted_values", {})
    abnormals = st.session_state.get("abnormalities", {})
    patient   = st.session_state.get("patient_info", {"name": "Patient", "age": "N/A", "gender": "N/A"})

    if not extracted:
        st.info("Please analyze a report first before generating a PDF.")
        return

    include = st.multiselect(
        "What to include in the report:",
        ["Patient Information", "Test Results Table", "Abnormal Findings", "Health Recommendations", "Doctor Consultation Advice"],
        default=["Patient Information", "Test Results Table", "Abnormal Findings", "Doctor Consultation Advice"]
    )

    if st.button("📄 Generate PDF Report", use_container_width=True):
        with st.spinner("Creating your report..."):
            pdf_bytes = generate_pdf_report(patient, extracted, abnormals, include)
        if pdf_bytes:
            st.success("Report ready!")
            patient_name = patient.get("name", "patient").replace(" ", "_")
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"medintel_report_{patient_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )


# -------------------------------------------------------
# PAGE: AGENTS DEMO
# -------------------------------------------------------
def show_agents():
    from agents.medical_agents import run_full_analysis

    st.subheader("🤖 Multi-Agent AI System")
    st.write("Watch 5 specialized AI agents analyze your report together.")

    st.markdown("""
    | Agent | Role |
    |-------|------|
    | 🔍 Report Analysis Agent | Reads and parses your lab report |
    | 📊 Risk Prediction Agent | Runs ML models for disease risk |
    | 🥗 Nutrition Agent | Creates diet recommendations |
    | 🔬 Medical Research Agent | Provides clinical context |
    | 💬 Communication Agent | Translates findings to simple language |
    """)

    extracted = st.session_state.get("extracted_values", {})
    abnormals = st.session_state.get("abnormalities", {})

    if not extracted:
        st.info("Please analyze a report first before running the agent system.")
        return

    api_key = st.sidebar.text_input("API Key for Agents", type="password", key="agent_api_key")

    if st.button("🚀 Run Multi-Agent Analysis", use_container_width=True):
        if not api_key:
            st.warning("Please enter your Anthropic API key to run the AI agents.")
            return
        with st.spinner("Agents are working... This takes 15-30 seconds."):
            results = run_full_analysis(extracted, abnormals, api_key)
        if results:
            for agent_name, output in results.items():
                with st.expander(f"✅ {agent_name}", expanded=True):
                    st.write(output)


# -------------------------------------------------------
# MAIN APP — puts everything together
# -------------------------------------------------------
def main():
    load_styles()
    show_banner()

    # Init session state on first load
    for key in ["extracted_values", "abnormalities", "patient_info"]:
        if key not in st.session_state:
            st.session_state[key] = {} if key != "chat_history" else []

    # Sidebar
    with st.sidebar:
        st.markdown("## 🏥 MedIntel AI")
        st.markdown("---")

        language = st.selectbox("🌐 Report Language", ["English", "Hindi", "Marathi", "Gujarati"])

        st.markdown("---")

        page = st.radio("Navigation", [
            "🏠 Dashboard",
            "📄 Analyze Report",
            "🔬 Disease Prediction",
            "💬 AI Chatbot",
            "🤖 AI Agents",
            "🥗 Diet & Lifestyle",
            "📥 Generate Report",
        ])

        st.markdown("---")

        # Show quick status if report is loaded
        if st.session_state.get("extracted_values"):
            abnormals = st.session_state.get("abnormalities", {})
            ab_count  = sum(1 for v in abnormals.values() if v["status"] != "Normal")
            st.success("✅ Report loaded")
            if ab_count:
                st.warning(f"⚠️ {ab_count} abnormal values")

        st.markdown("---")
        st.caption("MedIntel AI v1.0")
        st.caption("⚠️ For educational use only. Always consult a qualified doctor.")

    # Route to the right page
    if   page == "🏠 Dashboard":       show_dashboard()
    elif page == "📄 Analyze Report":  show_analyze_report(language)
    elif page == "🔬 Disease Prediction": show_disease_prediction()
    elif page == "💬 AI Chatbot":      show_chatbot()
    elif page == "🤖 AI Agents":       show_agents()
    elif page == "🥗 Diet & Lifestyle": show_diet()
    elif page == "📥 Generate Report": show_generate_report()


if __name__ == "__main__":
    main()
