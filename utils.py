# web_utils.py

import socket
from bs4 import BeautifulSoup
import requests
from newspaper import Article
from serpapi.google_search import GoogleSearch

def is_internet_connected():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False

def search_urls(query, max_results=10, serpapi_key=None):
    if not serpapi_key:
        raise ValueError("SerpAPI key is required to perform web searches")

    try:
        search = GoogleSearch({
            "q": query,
            "api_key": serpapi_key,  # ← Now using passed-in key
            "num": max_results,
            "sort_by": "date"
        })
        results = search.get_dict()
        urls = [result['link'] for result in results.get('organic_results', [])]
        return urls
    except Exception as e:
        st.error(f"Error fetching URLs: {e}")
        return []

def extract_text(url):
    methods = [extract_with_newspaper, extract_with_bs4]
    for method in methods:
        text = method(url)
        if len(text.strip()) > 300:  # Require meaningful content
            return text
    return ""
    
# utils.py

def extract_with_newspaper(url):
    try:
        article = Article(url)
        article.download()
        if "pdf" in url or not article.html():
            return ""
        article.parse()
        return article.text.strip()
    except:
        return ""

def extract_with_bs4(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p', limit=6)
        text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        return text[:3000] if text else ""
    except Exception as e:
        print(f"BS4 failed for {url}: {e}")
        return ""