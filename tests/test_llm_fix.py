"""Test LLM integration with Period object fix"""
import sys
import os

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Check API key
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("[ERROR] GROQ_API_KEY not found in .env")
    sys.exit(1)

print(f"[OK] API Key loaded: {api_key[:10]}...{api_key[-10:]}")

# Suppress emoji print
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

from main import SCMChatbotApp

sys.stdout = old_stdout

print("\nTesting LLM with Period Object Fix")
print("="*70)

# Initialize in ENHANCED mode
print("\n1. Initializing Enhanced AI mode...")
app = SCMChatbotApp(use_enhanced=True, use_rag=False)

print("2. Loading data...")
if not app.setup(data_path="train"):
    print("[ERROR] Setup failed")
    sys.exit(1)

if app.enhanced_chatbot and app.enhanced_chatbot.use_llm:
    print("[OK] Enhanced AI with LLM enabled\n")
else:
    print("[WARNING] LLM not enabled\n")
    sys.exit(1)

print("="*70)
print("Testing Query That Previously Failed")
print("="*70)

# This query triggers analytics gathering which has Period objects
query = "What is the delivery delay rate?"
print(f"\nQuery: {query}")
print("\n" + "-"*70)
print("Response:")
print("-"*70)

try:
    response = app.query(query)
    print(response)
    print("\n" + "="*70)
    print("[OK] SUCCESS! LLM response generated without errors")
    print("="*70)
except Exception as e:
    print(f"\n[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()
    print("="*70)
