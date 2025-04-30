
# 📰 RealTime-News-Assistant

A smart AI-powered app that helps you stay updated with real-time news, provides quick summaries using Gemini AI, and saves your previous questions for future reference.

![License](https://img.shields.io/badge/license-MIT-blue.svg)  
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)

---

## ✅ What It Does

- 🔍 **Live News Search** – Gets fresh news from the internet using SerpAPI  
- 🧠 **AI Summaries** – Uses Google Gemini AI to simplify complex news  
- 💾 **Knowledge Storage** – Remembers your old questions and answers  
- 🌐 **Works Online & Offline** – No internet? No problem. Still works with saved info  
- 🔥 **Trending Topics** – One-click access to hot topics like AI, climate change, economy, and more

---

## 🖥️ How to Install

### 1. **Requirements**
- Python 3.8 or newer  
- API Keys:
  - [SerpAPI Key](https://serpapi.com/)
  - [Gemini API Key](https://ai.google.dev/)

### 2. **Setup Steps**
```bash
# Clone the project
git clone https://github.com/lokesh1201/RealTime-News-Assistant.git
cd RealTime-News-Assistant

# Add your API keys in a .env file
touch .env
```
Then open `.env` and add:
```
SERPAPI_API_KEY=your_serpapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

```bash
# Install required packages
pip install -r requirements.txt

# Start the app
streamlit run main.py
```

---

## 💡 How to Use

1. **Type Your Question** – Example: _"What's happening in the tech world?"_  
2. **Get Instant News Summary** – The app shows a clear summary + source links  
3. **View Saved Questions** – Past queries show up in the sidebar  
4. **See What’s Trending** – Click on a trending topic to get quick updates

---

## 📁 Project Structure

```
RealTime-News-Assistant/
├── .env                ← Your API keys
├── main.py             ← Main Streamlit app
├── knowledge_db.py     ← Handles database for saved questions
├── utils.py            ← Useful functions
├── helpers.py          ← Extra helper code
├── requirements.txt    ← List of packages
└── README.md           ← This file
```

---

## 🙌 Want to Contribute?

We’d love your help!

```bash
# 1. Fork this repo
# 2. Create a branch: git checkout -b feature/your-feature
# 3. Commit changes: git commit -m "Add feature"
# 4. Push it: git push origin feature/your-feature
# 5. Create a Pull Request
```

