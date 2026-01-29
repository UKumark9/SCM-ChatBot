"""Test Enhanced AI Chatbot with LLM"""
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

print("Testing Enhanced AI Chatbot")
print("="*70)

# Initialize in ENHANCED mode (with LLM)
print("\n1. Initializing Enhanced AI mode...")
app = SCMChatbotApp(use_enhanced=True, use_rag=False)

print("2. Loading data...")
if not app.setup(data_path="train"):
    print("[ERROR] Setup failed")
    sys.exit(1)

# Check if enhanced chatbot was initialized
if app.enhanced_chatbot:
    print("[OK] Enhanced AI chatbot initialized successfully!")

    # Check if LLM is enabled
    if app.enhanced_chatbot.use_llm:
        print("[OK] LLM integration is ENABLED")
    else:
        print("[WARNING] LLM integration is DISABLED")
else:
    print("[WARNING] Using legacy rule-based chatbot")

print("\n" + "="*70)
print("Testing Natural Language Query")
print("="*70)

# Test a conversational query
query = "What insights can you provide about our supply chain performance?"
print(f"\nQuery: {query}")
print("\n" + "-"*70)
print("Response:")
print("-"*70)

response = app.query(query)
print(response)

print("\n" + "="*70)
print("Test Complete!")
print("="*70)
