
# 📰 RealTime-News-Assistant

A smart AI-powered app that helps you stay updated with real-time news, provides quick summaries using Gemini AI, and saves your previous questions for future reference.

![License](https://img.shields.io/badge/license-MIT-blue.svg)  
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)

---

## 📘 Project Description

**RealTime-News-Assistant** is a smart, AI-powered news application that delivers real-time insights and summaries from current events across the globe. Built with **Streamlit**, it integrates **SerpAPI** for live web search and **Google Gemini AI** to generate human-like summaries, making news easier and faster to understand. The app also stores previous queries locally, allowing users to access important information even without an internet connection.

Whether you’re a casual news reader, a student doing research, or a professional looking for fast updates, RealTime-News-Assistant is your intelligent companion for staying informed.

---

## 🚀 Getting Started

Want to know what’s happening in the world without digging through dozens of articles?

With **RealTime-News-Assistant**, just ask a question like “What’s the latest in AI?” and get a summarized, AI-curated response instantly — complete with source links and stored history. No fluff, just the news you need.

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

---
