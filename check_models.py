import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load your API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: API Key not found in .env file")
else:
    # Configure the library
    genai.configure(api_key=api_key)

    print("--- 🔍 CHECKING AVAILABLE MODELS ---")
    try:
        # Ask Google what models are available for 'generateContent'
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Found: {m.name}")
    except Exception as e:
        print(f"❌ Error: {e}")