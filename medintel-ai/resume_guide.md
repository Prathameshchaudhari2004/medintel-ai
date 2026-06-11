# 📄 MedIntel AI — Resume & Interview Guide

---

## ✅ CV / Resume Bullet Points

Copy these directly into your resume. Pick the ones that fit your role target.

### For Data Science / ML Roles:
- Built **MedIntel AI**, an end-to-end healthcare ML platform that analyzes blood test PDFs, detects abnormalities, and predicts disease risk using trained ML models (Random Forest, XGBoost)
- Trained 3 disease prediction models (Diabetes, Heart Disease, Kidney Disease) achieving **77–97% accuracy** using scikit-learn pipelines with imputation, scaling, cross-validation, and hyperparameter tuning
- Implemented a complete ML pipeline — data cleaning, feature engineering, train/test split, 5-fold CV, metrics evaluation (Accuracy, Precision, Recall, F1, AUC-ROC)
- Deployed an interactive Streamlit dashboard with Plotly visualizations, risk gauge charts, and downloadable PDF reports using ReportLab

### For AI / LLM Roles:
- Integrated **Anthropic Claude API** to build a context-aware medical chatbot that answers health questions using the patient's actual report values
- Designed a **multi-agent AI system** with 5 specialized agents (Report Analysis, Risk Prediction, Nutrition, Medical Research, Communication) using Claude API with distinct system prompts
- Built a **RAG-style architecture** where the chatbot's system prompt is dynamically populated with the patient's extracted blood values for personalized responses

### For Software Engineering Roles:
- Developed a production-style Python application with modular architecture: separate modules for PDF parsing, ML inference, AI chatbot, multi-agent orchestration, and database operations
- Built a PDF extraction pipeline using **pdfplumber** + regex with OCR fallback (EasyOCR) for scanned documents
- Designed an SQLite database schema for storing patient reports, test values, and risk predictions with full CRUD operations
- Added **multi-language support** (English, Hindi, Marathi, Gujarati) using deep-translator for health report explanations

---

## 🎤 Interview Questions & Answers

---

**Q: Explain your project in 60 seconds.**

> "MedIntel AI is a healthcare platform where patients upload their blood test PDFs, and the system automatically reads the values, detects abnormalities, predicts disease risks using ML, and explains everything in plain language. It uses Random Forest for diabetes and kidney disease prediction, XGBoost for heart disease, an Anthropic Claude-powered chatbot for Q&A, and a 5-agent AI system that analyzes the report from multiple angles simultaneously."

---

**Q: How does your PDF extraction work?**

> "I used pdfplumber as the primary extractor since it handles most digital PDFs well. It extracts all the text from each page. Then I use regex patterns to search for specific parameter names and their values — for example, matching 'Hemoglobin' followed by a number in a reasonable range. I also have a sanity check function that rejects values outside plausible ranges, so if regex accidentally grabs a date like 2024 instead of a glucose value, it gets filtered out. For scanned image PDFs, I fall back to EasyOCR."

---

**Q: Why did you use Random Forest for diabetes prediction?**

> "Random Forest works well for tabular medical data for a few reasons: it handles missing values after imputation, it's robust to outliers (important in medical data), it gives feature importance so you can explain which values matter most, and it doesn't overfit easily. The PIMA dataset has only 768 samples, and Random Forest handles small datasets better than deep learning approaches. XGBoost I used for heart disease because the UCI dataset has more complex feature interactions that gradient boosting captures better."

---

**Q: How did you handle class imbalance in the datasets?**

> "The PIMA diabetes dataset is about 65-35 in favor of non-diabetic, which isn't severe. I used the class_weight='balanced' parameter in RandomForestClassifier which automatically adjusts weights inversely proportional to class frequencies. I also used stratified train/test split and stratified cross-validation to ensure both classes are proportionally represented in every fold. The evaluation metrics I focused on were F1-score and AUC-ROC rather than just accuracy, since accuracy can be misleading with imbalanced classes."

---

**Q: Explain your multi-agent system design.**

> "Each of the 5 agents has a tightly-scoped system prompt that restricts it to one job. Agent 1 only analyzes values. Agent 2 only assesses disease risk. Agent 3 only creates diet plans. Agent 4 only provides clinical context. Agent 5 takes all the previous outputs and writes a simple patient-friendly summary. This specialization is key — if one agent does everything, it gets confused and the outputs are mediocre. When agents are specialized, each output is high quality in its domain. The orchestrator function calls them in sequence and passes outputs where needed."

---

**Q: What ML metrics did you use and why?**

> "I tracked Accuracy, Precision, Recall, F1, and AUC-ROC.
> - Accuracy alone is misleading with medical data due to class imbalance
> - Recall (sensitivity) is critical in healthcare — missing a true positive (false negative) can be dangerous
> - Precision matters to avoid unnecessary anxiety from false positives
> - F1 balances precision and recall
> - AUC-ROC shows model performance across all thresholds, not just the default 0.5"

---

**Q: How would you scale this to production?**

> "Several changes: swap SQLite for PostgreSQL for concurrent access. Add user authentication with JWT tokens. Move ML models to a FastAPI backend so the Streamlit frontend just calls APIs. Use async processing for the multi-agent calls since they're slow. Add model versioning — retrain models monthly as new data comes in. Use Redis for caching frequent predictions. Add monitoring with logging to track prediction accuracy drift over time."

---

**Q: What was the hardest problem you solved?**

> "The PDF extraction was the trickiest part. Real blood test reports from different labs have completely different formats — some use tables, some plain text, some have the value before the parameter name, some after. I had to build multiple regex patterns per parameter, add sanity checks on extracted values, and implement a fallback chain: pdfplumber → PyPDF2 → OCR. The other challenge was the multi-agent system latency — each agent is a separate API call, so 5 agents in sequence means 5 round trips. I partially addressed this by giving each agent a token budget and caching the client connection."

---

## 📌 Project Links to Add on Resume

- GitHub: `github.com/YourUsername/medintel-ai`
- Demo: `your-app.streamlit.app`
- Add screenshots to your GitHub README

---

## 🔖 Tech Keywords for Your Resume/LinkedIn

Add these to your skills section:
`Python` · `Machine Learning` · `Scikit-Learn` · `XGBoost` · `Random Forest` · `Streamlit` · `OpenRouter API Key (Free)` · `LLM Integration` · `Multi-Agent Systems` · `PDF Processing` · `NLP` · `Healthcare AI` · `SQLite` · `Plotly` · `ReportLab` · `Feature Engineering` · `Cross-Validation` · `Hyperparameter Tuning`
