"""Test chatbot queries"""
import sys
import os

# Force UTF-8 and suppress emoji print
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Suppress initial print
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

from main import SCMChatbotApp

sys.stdout = old_stdout

print("Testing SCM Chatbot Queries")
print("="*70)

# Initialize in legacy mode (faster, no LLM needed)
app = SCMChatbotApp(use_enhanced=False, use_rag=False)

print("\n1. Setting up chatbot...")
if app.setup(data_path="train"):
    print("[OK] Setup complete\n")
else:
    print("[ERROR] Setup failed")
    sys.exit(1)

# Test queries
queries = [
    "Which states have the most delays?",
    "What is the delivery delay rate?",
    "Show on-time delivery performance"
]

for i, query in enumerate(queries, 1):
    print(f"\n{'='*70}")
    print(f"Query {i}: {query}")
    print('='*70)

    response = app.query(query)
    print(response)

print(f"\n{'='*70}")
print("Test Complete!")
print('='*70)
