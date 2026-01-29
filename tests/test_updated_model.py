"""Test Enhanced Chatbot with Updated Groq Model"""
import sys
import os

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Suppress emoji print
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

from main import SCMChatbotApp

sys.stdout = old_stdout

print("Testing Enhanced AI with Updated Groq Model")
print("="*70)

# Check API key
api_key = os.getenv('GROQ_API_KEY')
if api_key:
    print(f"[OK] API Key loaded: {api_key[:15]}...{api_key[-10:]}")
else:
    print("[ERROR] No API key found")
    sys.exit(1)

# Initialize in ENHANCED mode
print("\n1. Initializing Enhanced AI mode...")
app = SCMChatbotApp(use_enhanced=True, use_rag=False)

print("2. Loading data...")
if not app.setup(data_path="train"):
    print("[ERROR] Setup failed")
    sys.exit(1)

if app.enhanced_chatbot and app.enhanced_chatbot.use_llm:
    print("[OK] Enhanced AI with LLM enabled")
    print(f"    Model: llama-3.3-70b-versatile")
else:
    print("[WARNING] LLM not enabled")

print("\n" + "="*70)
print("Testing Query with New Model")
print("="*70)

query = "What is the delivery delay rate?"
print(f"\nQuery: '{query}'")
print("\n" + "-"*70)
print("Response:")
print("-"*70)

try:
    response = app.query(query)
    print(response)
    print("\n" + "="*70)
    print("[SUCCESS] LLM response generated with updated model!")
    print("="*70)
except Exception as e:
    print(f"\n[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*70)
    print("Falling back to rule-based mode...")
    print("="*70)
