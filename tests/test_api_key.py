"""Test if GROQ_API_KEY is loaded from .env file"""
import os
import sys

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("Testing API Key Loading")
print("="*70)

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] python-dotenv is installed")
except ImportError:
    print("[ERROR] python-dotenv not installed!")
    sys.exit(1)

# Check API key
api_key = os.getenv('GROQ_API_KEY')

if api_key:
    print(f"[OK] GROQ_API_KEY loaded successfully")
    print(f"     Key starts with: {api_key[:10]}...")
    print(f"     Key ends with: ...{api_key[-10:]}")
    print(f"     Key length: {len(api_key)} characters")
else:
    print("[ERROR] GROQ_API_KEY not found in environment")
    print("     Check that .env file exists with GROQ_API_KEY=your_key")

print("="*70)

# Now test the chatbot initialization
print("\nTesting Chatbot with API Key...")
print("="*70)

import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

try:
    from main import SCMChatbotApp
    sys.stdout = old_stdout

    print("[OK] Chatbot imported successfully")
    print("     API key should be detected in main.py")

except Exception as e:
    sys.stdout = old_stdout
    print(f"[ERROR] Failed to import chatbot: {e}")

print("="*70)
