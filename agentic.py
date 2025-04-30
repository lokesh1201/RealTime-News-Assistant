import os
import pandas as pd
import time
import hashlib
from dotenv import load_dotenv
from newspaper import Article
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai
from serpapi import GoogleSearch
import socket
import streamlit as st
import re

# Load environment variables
load_dotenv()

# Constants
KB_FILE = "knowledge_base.xlsx"
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SERPAPI_API_KEY or not GENAI_API_KEY:
    raise ValueError("API keys are missing! Please add SERPAPI_API_KEY and GEMINI_API_KEY to .env")

# -------------------- Knowledge Base --------------------
def load_knowledge_base():
    if os.path.exists(KB_FILE):
        return pd.read_excel(KB_FILE, engine="openpyxl")
    else:
        return pd.DataFrame(columns=["Query", "Answer", "Timestamp"])

def save_to_knowledge_base(query, answer):
    df = load_knowledge_base()
    if not ((df["Query"].str.lower() == query.lower())).any():
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        df = pd.concat([df, pd.DataFrame([[query, answer, timestamp]], 
                                        columns=["Query", "Answer", "Timestamp"])], 
                       ignore_index=True)
        df.to_excel(KB_FILE, index=False, engine="openpyxl")

# -------------------- Internet Check --------------------
def is_internet_connected():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except:
        return False

# -------------------- Web Search --------------------
def search_urls(query, max_results=10):
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": max_results,
            "sort_by": "date"
        })
        results = search.get_dict()
        urls = [result['link'] for result in results.get('organic_results', [])]
        return urls
    except Exception as e:
        st.error(f"Error fetching URLs: {e}")
        return []

# -------------------- Content Extraction --------------------
def extract_text(url):
    for method in [extract_with_newspaper, extract_with_bs4]:
        text = method(url)
        if len(text) > 200:
            return text
    return ""

def extract_with_newspaper(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except:
        return ""

def extract_with_bs4(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return "\n".join(p.get_text() for p in paragraphs)
    except:
        return ""

# -------------------- AI Query Response --------------------
def ask_gemini(query):
    try:
        genai.configure(api_key=GENAI_API_KEY)
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(query)
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini API: {e}"

# -------------------- Final Query Handler --------------------
def answer_query(query, progress_bar=None):
    answer = ""
    knowledge_base = load_knowledge_base()
    
    # Check if query already in knowledge base
    existing_query = knowledge_base[knowledge_base["Query"].str.lower() == query.lower()]
    if not existing_query.empty:
        answer = existing_query.iloc[0]["Answer"]
        return f"{answer}\n\n_(Retrieved from knowledge base)_"
    
    if is_internet_connected():
        if progress_bar:
            progress_bar.progress(10, text="Searching for relevant articles...")
        
        urls = search_urls(query)
        
        if progress_bar:
            progress_bar.progress(30, text="Extracting content from sources...")
        
        content = ""
        sources = []
        for i, url in enumerate(urls[:5]):  # Limit to 5 sources
            if progress_bar:
                progress_bar.progress(30 + i*10, text=f"Analyzing source {i+1} of 5...")
            
            extracted = extract_text(url)
            if len(extracted) > 100:
                content += extracted + "\n\n"
                domain = url.split("//")[-1].split("/")[0]
                sources.append(domain)
        
        if content.strip():
            if progress_bar:
                progress_bar.progress(80, text="Generating summary with AI...")
            
            answer = ask_gemini(f"Summarize the following articles to answer the query: '{query}':\n\n{content}")
            source_text = "\n\n**Sources:** " + ", ".join(sources) if sources else ""
            answer += source_text
        else:
            if progress_bar:
                progress_bar.progress(80, text="No specific articles found, asking AI directly...")
            
            answer = ask_gemini(query)
    else:
        if progress_bar:
            progress_bar.progress(50, text="No internet connection, using AI knowledge...")
        
        answer = ask_gemini(query)
        answer += "\n\n_(Note: Generated without internet connection)_"
    
    save_to_knowledge_base(query, answer)
    
    if progress_bar:
        progress_bar.progress(100, text="Answer ready!")
    
    return answer

# -------------------- Helper Functions --------------------
def generate_unique_key(text, suffix=""):
    """Generate a unique key based on text content"""
    # Create a hash of the full text to ensure uniqueness
    hash_obj = hashlib.md5(text.encode())
    hash_str = hash_obj.hexdigest()[:8]  # Take first 8 chars of hash
    return f"{suffix}_{hash_str}"

# Function to sanitize HTML output
def sanitize_markdown(text):
    # Remove any HTML tags that might cause rendering issues
    text = re.sub(r'<(?!\/?(strong|em|p|h[1-6]|ul|ol|li|blockquote|code|pre|a|br|hr)(\s[^>]*)?\/?>)[^>]*>', '', text)
    return text

# -------------------- Custom Components --------------------
def render_chat_message(role, content, timestamp=None):
    # Sanitize the content to prevent HTML rendering issues
    content = sanitize_markdown(content)
    
    if role == "user":
        st.markdown(f"""
        <div style="display: flex; margin-bottom: 10px;">
            <div style="background-color: #6a5acd; border-radius: 15px; padding: 10px 15px; margin-left: auto; max-width: 80%;">
                <p style="margin: 0; color: #ffffff;"><strong>You:</strong> {content}</p>
                {f'<p style="margin: 0; font-size: 0.7em; color: #e6e6e6; text-align: right;">{timestamp}</p>' if timestamp else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; margin-bottom: 10px;">
            <div style="background-color: #4a4a6d; border-radius: 15px; padding: 10px 15px; margin-right: auto; max-width: 80%;">
                <p style="margin: 0; color: #ffffff;"><strong>News AI:</strong> {content}</p>
                {f'<p style="margin: 0; font-size: 0.7em; color: #e6e6e6;">{timestamp}</p>' if timestamp else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_empty_state():
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 50px; padding: 30px; background-color: #34344A; border-radius: 10px; color: white;">
        <img src="https://cdn-icons-png.flaticon.com/512/2593/2593073.png" width="100" height="100">
        <h3>Welcome to News AI Bot!</h3>
        <p>Ask me anything about recent news and events. I'll search the web for the latest information and provide you with a concise summary.</p>
        <p style="font-size: 0.9em; color: #b8b8d4;">Example questions:</p>
        <ul style="list-style-type: none; padding: 0;">
            <li>• "What are the latest advancements in AI technology?"</li>
            <li>• "What happened in the stock market today?"</li>
            <li>• "What are the current trends in renewable energy?"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -------------------- Streamlit UI --------------------
def main():
    st.set_page_config(
        page_title="News AI Bot",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #1e1e2f;
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            background-color: #6a5acd;
            color: white;
            font-weight: bold;
        }
        
        .stTextInput>div>div>input {
            border-radius: 20px;
            padding: 15px;
            background-color: #2d2d42;
            color: white;
            border: 1px solid #6a5acd;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .st-emotion-cache-fg4pbf {
            background-color: #1e1e2f;
            color: white;
        }
        
        .st-emotion-cache-16txtl3 {
            background-color: #1e1e2f;
            color: white;
        }
        
        div[data-testid="stSidebar"] {
            background-color: #2d2d42;
            color: white;
        }
        
        h1, h2, h3, h4, h5, h6, p {
            color: white !important;
        }
        
        .knowledge-card {
            background-color: #34344A;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            color: white;
        }
        
        .trending-topics span {
            display: inline-block;
            margin: 5px;
            padding: 5px 10px;
            background-color: #34344A;
            border-radius: 15px;
            cursor: pointer;
            color: white;
        }
        
        .stExpander {
            background-color: #34344A !important;
            border: 1px solid #6a5acd !important;
            border-radius: 10px !important;
        }
        
        .stProgress > div > div {
            background-color: #6a5acd !important;
        }
        
        .stProgress {
            height: 10px !important;
        }
        
        .stDivider {
            border-color: #4a4a6d !important;
        }
        
        /* Make sure all text is visible on dark background */
        div.stMarkdown {
            color: white !important;
        }
        
        .css-10trblm {
            color: white !important;
        }
        
        .css-z5fcl4 {
            padding: 2rem 1rem 1.5rem !important;
        }
        
        /* This adds a gradient background to the main content */
        .main {
            background-image: linear-gradient(to bottom right, #1e1e2f, #2d2d42) !important;
        }
        
        /* Create a sticky input container at the bottom */
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #1e1e2f;
            padding: 15px;
            box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            margin-left: 21%; /* Adjust based on sidebar width */
            margin-right: 1%;
            border-top: 1px solid #4a4a6d;
        }
        
        /* Add padding to the bottom of chat container so content isn't hidden behind sticky input */
        .chat-container {
            padding-bottom: 100px !important;
            margin-bottom: 20px;
        }
        
        /* Make input elements in the sticky container look better */
        .input-container .stTextInput>div>div>input {
            border-radius: 20px;
            padding: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "knowledge_entries" not in st.session_state:
        knowledge_base = load_knowledge_base()
        st.session_state.knowledge_entries = knowledge_base.sort_values(by='Timestamp', ascending=False).head(10).to_dict('records') if 'Timestamp' in knowledge_base.columns else []

    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2593/2593073.png", width=80)
        st.title("News AI Bot")
        
        # Connection status
        connection_status = "🟢 Online" if is_internet_connected() else "🔴 Offline (Limited Functionality)"
        st.markdown(f"**Status:** {connection_status}")
        
        st.divider()
        
        # Knowledge Base
        st.subheader("📚 Knowledge Base")
        if st.session_state.knowledge_entries:
            for i, entry in enumerate(st.session_state.knowledge_entries):
                # For expanders, use default behavior without custom keys
                with st.expander(f"{entry['Query'][:40]}{'...' if len(entry['Query']) > 40 else ''}"):
                    st.markdown(f"**Query:** {entry['Query']}")
                    timestamp = entry.get('Timestamp', 'Unknown date')
                    st.markdown(f"**Date:** {timestamp}")
                    # Create unique button key using index and hash
                    button_key = generate_unique_key(entry['Query'], f"btn_{i}")
                    if st.button("Use this query", key=button_key):
                        st.session_state.current_query = entry['Query']
                        st.rerun()
        else:
            st.info("Your knowledge base is empty. Ask questions to build it up!")
        
        st.divider()
        
        # App info
        st.subheader("ℹ️ About")
        st.markdown("""
        News AI Bot uses Gemini AI with real-time web search to provide up-to-date information on current events and topics.
        
        **Features:**
        - Real-time news search
        - AI-powered summaries
        - Knowledge base storage
        """)
        
        if st.button("Clear Chat History", key="clear_history_btn"):
            st.session_state.chat_history = []
            st.rerun()

    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Header
        st.markdown("<h1 style='text-align:center;'>📰 News AI Bot</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Get real-time insights on current events</p>", unsafe_allow_html=True)
        
        # Chat container with added class for padding
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        chat_container = st.container()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Custom HTML for sticky input bar
        st.markdown("""
        <div class="input-container">
            <div id="input_placeholder"></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📈 Trending Topics")
        trending_topics = ["Climate Change", "AI Advancements", "Global Economy", "Space Exploration", "Health Innovations"]
        
        st.markdown('<div class="trending-topics">', unsafe_allow_html=True)
        for i, topic in enumerate(trending_topics):
            # Create unique key for each trending topic button
            topic_key = f"trend_{i}_{topic.replace(' ', '_')}"
            if st.button(topic, key=topic_key):
                st.session_state.current_query = f"What's the latest news about {topic}?"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("💡 Tips")
        st.markdown("""
        - Ask specific questions for better results
        - Include timeframes in your questions
        - Try comparing different topics
        - Ask for the latest updates on a subject
        """)

    # Display chat in the chat container
    with chat_container:
        if not st.session_state.chat_history:
            render_empty_state()
        else:
            for i, (query, answer) in enumerate(st.session_state.chat_history):
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                render_chat_message("user", query, timestamp)
                render_chat_message("bot", answer)
    
    # User input area (will be moved to sticky position by CSS)
    input_col1, input_col2 = st.columns([5, 1], gap="small")
    
    with input_col1:
        # Add the key_press handler to detect Enter key
        # First, initialize the Enter key state if it doesn't exist
        if "Enter" not in st.session_state:
            st.session_state.Enter = False
        
        if "current_query" in st.session_state:
            user_query = st.text_input(
                "🔍 Ask your question:", 
                value=st.session_state.current_query, 
                key="user_input",
                on_change=lambda: setattr(st.session_state, "Enter", True),
                label_visibility="collapsed"
            )
            # Clear the current_query after using it
            del st.session_state.current_query
        else:
            user_query = st.text_input(
                "🔍 Ask your question:", 
                key="user_input", 
                placeholder="e.g., What's happening with climate change?",
                on_change=lambda: setattr(st.session_state, "Enter", True),
                label_visibility="collapsed"
            )
    
    with input_col2:
        submit_button = st.button("Ask 🚀", key="submit_btn")
    
    # Process user input
    if (user_query and submit_button) or (user_query and user_query != "" and st.session_state.Enter):
        # Reset the Enter state
        st.session_state.Enter = False
        
        # Add user message to chat history immediately
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        st.session_state.chat_history.append((user_query, "Thinking..."))
        
        # Create a placeholder for the AI response with a progress bar
        with chat_container:
            render_chat_message("user", user_query, timestamp)
            response_placeholder = st.empty()
            response_placeholder.markdown("""
            <div style="display: flex; margin-bottom: 10px;">
                <div style="background-color: #4a4a6d; border-radius: 15px; padding: 10px 15px; margin-right: auto; max-width: 80%;">
                    <p style="margin: 0; color: #ffffff;"><strong>News AI:</strong> <i>Thinking...</i></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0, text="Preparing to answer...")
        
        # Generate answer
        answer = answer_query(user_query, progress_bar)
        
        # Update chat history with the answer
        st.session_state.chat_history[-1] = (user_query, answer)
        
        # Refresh knowledge base entries
        knowledge_base = load_knowledge_base()
        st.session_state.knowledge_entries = knowledge_base.sort_values(by='Timestamp', ascending=False).head(10).to_dict('records') if 'Timestamp' in knowledge_base.columns else []
        
        # Remove progress bar and show full response
        response_placeholder.empty()
        
        st.rerun()

if __name__ == "__main__":
    main()