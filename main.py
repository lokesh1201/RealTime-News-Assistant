import os
from dotenv import load_dotenv
import streamlit as st
import time
from knowledge_db import init_db, load_knowledge, save_knowledge
from utils import is_internet_connected, search_urls, extract_text
from ai_utils import answer_query
from helpers import generate_unique_key, sanitize_markdown
from ui import render_chat_message, render_empty_state

# Load environment variables
load_dotenv()

# Define API Keys (ensure they are in .env)
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SERPAPI_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing required API keys in .env file")

# Initialize database
KB_DB_FILE = "knowledge.db"
init_db(KB_DB_FILE)

# Load knowledge entries into session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "knowledge_entries" not in st.session_state:
    st.session_state.knowledge_entries = load_knowledge(limit=10)

def process_query(user_query, progress_bar=None):
    answer = ""

    # Check if query exists in knowledge base
    existing = [entry for entry in st.session_state.knowledge_entries if entry["Query"].lower() == user_query.lower()]
    if existing:
        answer = existing[0]["Answer"]
        return f"{answer}\n_(Retrieved from knowledge base)_"

    # Try web search + Gemini when connected
    if is_internet_connected():
        if progress_bar:
            progress_bar.progress(10, text="Searching for relevant articles...")

        try:
            urls = search_urls(user_query, serpapi_key=SERPAPI_API_KEY)
        except Exception as e:
            st.error(f"Search failed: {e}")
            urls = []

        if progress_bar:
            progress_bar.progress(30, text="Extracting content...")

        content = ""
        sources = []
        for i, url in enumerate(urls[:5]):
            extracted = extract_text(url)
            if extracted:
                content += extracted + "\n\n"
                domain = url.split("//")[-1].split("/")[0]
                sources.append(domain)

        if content.strip():
            if progress_bar:
                progress_bar.progress(80, text="Generating summary with AI...")
            answer = answer_query(user_query, content)
            source_text = "\n**Sources:** " + ", ".join(sources) if sources else ""
            answer += source_text
        else:
            if progress_bar:
                progress_bar.progress(80, text="No specific articles found, asking AI directly...")
            answer = answer_query(user_query, "")
    else:
        if progress_bar:
            progress_bar.progress(50, text="No internet connection, using AI knowledge...")
        answer = answer_query(user_query, "")
        answer += "\n_(Note: Generated without internet connection)_"

    # Save result to knowledge base
    save_knowledge(user_query, answer)

    if progress_bar:
        progress_bar.progress(100, text="Answer ready!")

    return answer

def main():
    st.set_page_config(
        page_title="News AI Bot",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for styling
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
        h1, h2, h3, h4, h5, h6, p {
            color: white !important;
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
        /* Sticky input container */
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
        /* Chat container padding */
        .chat-container {
            padding-bottom: 100px !important;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar setup
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2593/2593073.png", width=80)
        st.title("News AI Bot")
        connection_status = "🟢 Online" if is_internet_connected() else "🔴 Offline (Limited Functionality)"
        st.markdown(f"**Status:** {connection_status}")
        st.divider()

        # Knowledge Base Section
        st.subheader("📚 Knowledge Base")
        if st.session_state.knowledge_entries:
            for i, entry in enumerate(st.session_state.knowledge_entries):
                with st.expander(f"{entry['Query'][:40]}{'...' if len(entry['Query']) > 40 else ''}"):
                    st.markdown(f"**Query:** {entry['Query']}")
                    timestamp = entry.get('Timestamp', 'Unknown date')
                    st.markdown(f"**Date:** {timestamp}")
                    button_key = generate_unique_key(entry['Query'], f"btn_{i}")
                    if st.button("Use this query", key=button_key):
                        st.session_state.current_query = entry['Query']
                        st.rerun()
        else:
            st.info("Your knowledge base is empty. Ask questions to build it up!")
        
        st.divider()
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

    # Main content area
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 style='text-align:center;'>📰 News AI Bot</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Get real-time insights on current events</p>", unsafe_allow_html=True)
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        chat_container = st.container()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="input-container">
            <div id="input_placeholder"></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("📈 Trending Topics")
        trending_topics = ["Climate Change", "AI Advancements", "Global Economy", "Space Exploration", "Health Innovations"]
        for i, topic in enumerate(trending_topics):
            topic_key = f"trend_{i}_{topic.replace(' ', '_')}"
            if st.button(topic, key=topic_key):
                st.session_state.current_query = f"What's the latest news about {topic}?"
                st.rerun()
        st.divider()
        st.subheader("💡 Tips")
        st.markdown("""
        - Ask specific questions for better results
        - Include timeframes in your questions
        - Try comparing different topics
        - Ask for the latest updates on a subject
        """)

    # Display chat history
    with chat_container:
        if not st.session_state.chat_history:
            render_empty_state()
        else:
            for q, a in st.session_state.chat_history:
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                render_chat_message("user", q, timestamp)
                render_chat_message("bot", a)

    # User input area
    input_col1, input_col2 = st.columns([5, 1], gap="small")
    with input_col1:
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
        st.session_state.Enter = False
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        st.session_state.chat_history.append((user_query, "Thinking..."))
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
        answer = process_query(user_query, progress_bar)
        st.session_state.chat_history[-1] = (user_query, answer)
        st.session_state.knowledge_entries = load_knowledge(limit=10)
        response_placeholder.empty()
        st.rerun()

if __name__ == "__main__":
    main()