import os
from dotenv import load_dotenv

# Load .env at project startup
load_dotenv()

def get_openai_api_key():
    """Fetch OPENAI_API_KEY from environment or .env"""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("❌ OPENAI_API_KEY not found. Please set it in your .env file or environment.")
   
    return key