import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env file.")
    exit(1)

print(f"Using API Key: {api_key[:5]}...{api_key[-5:] if len(api_key)>10 else ''}")

try:
    genai.configure(api_key=api_key)
    
    print("\nfetching available models...")
    models = genai.list_models()
    
    print("\n--- Available Gemini Models ---")
    found = False
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            # handle field names safely
            d_name = getattr(m, 'display_name', None) or getattr(m, 'displayName', 'Unknown')
            print(f"- {m.name} (Display Name: {d_name})")
            found = True
            
    if not found:
        print("No models found that support 'generateContent'.")
        
except Exception as e:
    print(f"\nFailed to list models. Error: {e}")
