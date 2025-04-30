# ai_utils.py

from config import GEMINI_API_KEY, USE_OLLAMA, OLLAMA_MODEL
import google.generativeai as genai
import requests

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def ask_gemini(prompt):
    """Ask Google Gemini AI with a prompt"""
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API error: {str(e)}"

def ask_ollama(prompt, model=OLLAMA_MODEL):
    """Ask local Ollama server using configured model"""
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }, timeout=60)

        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"🔴 Failed to get response from Ollama ({response.status_code})"
    
    except Exception as e:
        return f"⚠️ Ollama connection failed: {str(e)}"

def answer_query(query, content="", use_ollama=None, progress_bar=None):
    """
    Unified interface to answer the query
    
    Args:
        query (str): User's question
        content (str): Optional web-extracted context
        use_ollama (bool): Whether to use local LLM or Gemini
        progress_bar (Streamlit progress bar): Optional for UI feedback

    Returns:
        str: AI-generated answer
    """

    # Use global config if no override provided
    if use_ollama is None:
        use_ollama = USE_OLLAMA

    # If we have extracted content, build a detailed prompt
    if content.strip():
        prompt = f"""
        You are a news summarizer AI.
        
        Based on the following query and articles:
        Query: {query}

        Articles:
        {content[:3000]}
        """
    else:
        prompt = query

    # Decide which backend to use
    if use_ollama:
        return ask_ollama(prompt, OLLAMA_MODEL)
    else:
        return ask_gemini(prompt)