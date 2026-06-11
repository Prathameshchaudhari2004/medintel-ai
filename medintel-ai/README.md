# 🏥 MedIntel AI — Intelligent Medical Report Analyzer

> Upload your blood test report → Get instant analysis, disease risk prediction, and AI-powered health insights in simple language.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-orange)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 What This Does

Patients receive blood test reports but often can't understand what the values mean. MedIntel AI solves this by:

- **Reading PDF reports** and extracting all blood test values automatically
- **Detecting abnormalities** with color-coded alerts (Normal / Low / High / Critical)
- **Explaining results** in plain language — no medical jargon
- **Predicting disease risk** for Diabetes, Heart Disease, and Kidney Disease using trained ML models
- **AI Health Chatbot** — ask questions about your report in any language
- **Multi-language support** — English, Hindi, Marathi, Gujarati
- **Multi-Agent AI system** — 5 specialized AI agents analyzing your report together
- **Personalized diet recommendations** based on your specific values
- **Downloadable PDF report** with professional summary

---

## 🛠 Tech Stack

| Layer         | Technology                                      |
|---------------|-------------------------------------------------|
| Frontend      | Streamlit, Plotly, Custom CSS                   |
| ML Models     | Random Forest, XGBoost, Scikit-Learn            |
| AI/LLM        | Anthropic Claude (claude-sonnet-4-20250514)     |
| PDF Reading   | pdfplumber, PyPDF2, EasyOCR                     |
| PDF Generation| ReportLab                                       |
| Translation   | deep-translator (Google Translate API)          |
| Database      | SQLite (dev) / PostgreSQL (production-ready)    |
| Deployment    | Streamlit Community Cloud / Docker              |

---

## 📁 Project Structure

```
medintel-ai/
│
├── app.py                    # Main Streamlit app (entry point)
├── requirements.txt          # All dependencies
├── README.md
│
├── .streamlit/
│   └── config.toml           # UI theme configuration
│
├── utils/
│   ├── pdf_reader.py         # PDF text extraction + regex parsing
│   ├── abnormality.py        # Normal ranges + status detection
│   ├── knowledge_base.py     # Medical explanations + diet recs
│   ├── translator.py         # Hindi/Marathi/Gujarati translation
│   └── report_gen.py         # Professional PDF report generation
│
├── models/
│   ├── train_models.py       # Training pipeline for all 3 models
│   └── predictor.py          # Load models + make predictions
│
├── chatbot/
│   └── assistant.py          # AI chatbot using Anthropic API
│
├── agents/
│   └── medical_agents.py     # Multi-agent AI system (5 agents)
│
├── database/
│   └── db_handler.py         # SQLite operations
│
├── saved_models/             # Trained model .pkl files (auto-created)
└── notebooks/                # Jupyter notebooks for exploration
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YourUsername/medintel-ai.git
cd medintel-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Train the ML models
```bash
python models/train_models.py
```
This downloads real datasets and trains 3 models. Takes ~2-3 minutes.

### 4. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### 5. For AI features
Get a free API key from [console.anthropic.com](https://console.anthropic.com) and enter it in the sidebar.

---

## 🤖 ML Models

| Model               | Dataset              | Algorithm       | Accuracy |
|---------------------|----------------------|-----------------|----------|
| Diabetes Prediction | PIMA Indians (768)   | Random Forest   | ~77%     |
| Heart Disease       | UCI Cleveland (303)  | XGBoost         | ~84%     |
| Kidney Disease      | UCI CKD (400)        | Random Forest   | ~97%     |

### Training Pipeline
```
Raw Data → Clean Zeros/NaN → Feature Engineering
→ Train/Test Split (80/20) → Pipeline (Imputer + Scaler + Model)
→ Hyperparameter Tuning → 5-Fold Cross Validation
→ Evaluate (Accuracy, F1, AUC-ROC) → Save with joblib
```

---

## 🌐 Deployment on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file: `app.py`
5. Deploy!

**Note:** Train models locally first and push `saved_models/*.pkl` files to GitHub so they're available on deployment.

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t medintel-ai .

# Run
docker run -p 8501:8501 medintel-ai
```

---

## 💬 Sample Questions for the Chatbot

- "What does my hemoglobin value mean?"
- "Why is my glucose high and what should I eat?"
- "Is my cholesterol dangerous?"
- "What tests should I get if my creatinine is high?"
- "Explain what LDL and HDL are in simple words"

---

## ⚠️ Disclaimer

This application is for **educational and informational purposes only**. It is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical decisions.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with Python, Streamlit, Scikit-Learn, and Anthropic AI*
