# config.py

import os
from dotenv import load_dotenv

load_dotenv()

# APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# AI backend
USE_OLLAMA = os.getenv("USE_OLLAMA", "True").lower() in ("true", "1", "yes")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")