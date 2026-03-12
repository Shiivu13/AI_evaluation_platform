# 🧪 AI Experiment Evaluation Platform

## 📖 Project Description
The **AI Experiment Evaluation Platform** is a robust framework built to systematically evaluate, compare, and track how well different Generative AI (GenAI) models and Prompt Templates perform on specific tasks. 

If you are building an AI app, you shouldn't guess if a new prompt is "better" than an old one. This system allows you to build a structured "exam" (Test Cases) for your AI, run different configurations (Variants) through that exam, and automatically grade them across multiple dimensions.

### 🌟 Key Features
- **Experiment Tracking**: Organize test cases and prompt variants logically.
- **Automated Grading Engine**:
  - **Rule-Based**: Checks for data leakage (Risk metrics like PII, emails).
  - **LLM-as-a-Judge**: Uses a highly-instructed LLM to calculate floating-point scores and provide verbatim *Rationales* for metrics like **Clarity**, **Overconfidence**, **Consistency**, **RAG Answer Relevance**, and **RAG Context Adherence**.
- **Interactive Dashboard**: A beautiful Streamlit UI with metric scorecards and full result exploration.
- **Free API Tier**: Powered entirely by the `google-genai` API (Gemini 2.5) holding costs to zero.

---

## 🗺️ Project Roadmap & Core Architecture

Our development roadmap followed exactly 8 structured phases:
1. **Planning & Architecture:** Defined the SQLite database schema for Experiments, Variants, Test Cases, and Results tracking.
2. **Core Evaluation Engine:** Built the Pydantic domain models and the LLM wrappers to communicate with APIs.
3. **Experiment Tracking & Storage:** Implemented full CRUD SQL operations to isolate states.
4. **User Interface (Frontend):** Bootstrapped the Streamlit Dashboard for creating prompt templates and viewing results.
5. **System Integration & Verification:** Connected the frontend to the backend evaluation engine via test scripts.
6. **RAG Metrics & UI Tweaks:** Enhanced the LLM Judges to evaluate Context Hallucinations and Answer Relevancy; styled the dashboard with metric cards.
7. **Free API Integration:** Deprecated OpenAI in favor of Google's Gemini Models for a 100% free workflow.
8. **Deployment Setup:** Generated `requirements.txt` and `.gitignore` and refactored keys to rely on `st.secrets` natively.

---

## 🚀 Step-by-Step Deployment Guide (Streamlit Community Cloud)

To make this project live on the internet so anyone can see your portfolio or use the platform:

### Step 1: Push Your Code to GitHub (Already Done!)
Your code currently lives in the `Shiivu13/AI_evaluation_platform` repository. Streamlit will read directly from this repository to build your website!

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and create a free account (connect your GitHub account).
2. Click the **Create app** button in the top right corner.
3. Click **Yep, I have an app**, and then select **Deploy a public app from GitHub**.
4. Fill in the form:
   - **Repository:** `Shiivu13/AI_evaluation_platform`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **Deploy!** (Your app will now start booting up. You might see an error on the screen initially—that's normal! We need to give it the API Key).

### Step 3: Add Your Free Gemini API Key
To grade the tests, the app needs permission to use Google's Gemini models.
1. Get your free API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Go back to your deployed Streamlit App. Look at the bottom right corner of the screen for a **three-dots menu icon `⋮`**. Click it and select **Settings**.
3. Go to the **Secrets** tab on the left menu.
4. Paste your key in TOML format exactly like this:
   ```toml
   GEMINI_API_KEY = "PASTE_YOUR_KEY_HERE"
   ```
5. Click **Save**.

🎉 **Congratulations!** Your app will quickly restart and will now be live on the internet! 

---

## 💻 Local Setup (If you want to run it on your own computer)

1. Clone the repository: `git clone https://github.com/Shiivu13/AI_evaluation_platform.git`
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
    - Windows: `.\venv\Scripts\Activate.ps1`
    - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Export your API Key:
    - Windows: `$env:GEMINI_API_KEY="your-key-here"`
    - Mac/Linux: `export GEMINI_API_KEY="your-key-here"`
6. Run the App: `streamlit run app.py`
