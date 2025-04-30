from helpers import sanitize_markdown
import streamlit as st

def render_user_message(content, timestamp=None):
    content = sanitize_markdown(content)
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
        <div style="background-color: #6a5acd; border-radius: 15px; padding: 10px 15px; max-width: 80%;">
            <p style="margin: 0; color: #ffffff;"><strong>You:</strong> {content}</p>
            {f'<p style="margin: 0; font-size: 0.7em; color: #e6e6e6; text-align: right;">{timestamp}</p>' if timestamp else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_bot_message(content, timestamp=None):
    content = sanitize_markdown(content)
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
        <div style="background-color: #4a4a6d; border-radius: 15px; padding: 10px 15px; max-width: 80%;">
            <p style="margin: 0; color: #ffffff;"><strong>News AI:</strong> {content}</p>
            {f'<p style="margin: 0; font-size: 0.7em; color: #e6e6e6;">{timestamp}</p>' if timestamp else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_message(role, content, timestamp=None):
    if role == "user":
        render_user_message(content, timestamp)
    elif role == "bot":
        render_bot_message(content, timestamp)
    else:
        raise ValueError("Invalid role. Must be 'user' or 'bot'.")

def render_empty_state():
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 50px; padding: 30px; background-color: #34344A; border-radius: 10px; color: white;">
        <img src="https://cdn-icons-png.flaticon.com/512/2593/2593073.png" alt="News AI Bot Logo" width="100" height="100">
        <h3>Welcome to News AI Bot!</h3>
        <p>Ask me anything about recent news and events.</p>
    </div>
    """, unsafe_allow_html=True)