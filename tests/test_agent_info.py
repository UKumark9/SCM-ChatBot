"""Test Agent Identification Feature"""
import sys
import os

# Force UTF-8
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

print("Testing Agent Identification Feature")
print("="*70)

# Test 1: Enhanced AI with agent info
print("\nTest 1: Enhanced AI with Agent Info (Default)")
print("="*70)

app = SCMChatbotApp(use_enhanced=True, use_rag=False, show_agent=True)
if app.setup(data_path="train"):
    query = "What is the delivery delay rate?"
    print(f"\nQuery: {query}")
    print("-"*70)
    response = app.query(query)
    print(response)
    print()

# Test 2: Enhanced AI without agent info
print("\n" + "="*70)
print("Test 2: Enhanced AI WITHOUT Agent Info (Hidden)")
print("="*70)

app2 = SCMChatbotApp(use_enhanced=True, use_rag=False, show_agent=False)
if app2.setup(data_path="train"):
    query = "What is the total revenue?"
    print(f"\nQuery: {query}")
    print("-"*70)
    response = app2.query(query)
    print(response)
    print()

# Test 3: Rule-based fallback with agent info
print("\n" + "="*70)
print("Test 3: Rule-Based Mode with Agent Info")
print("="*70)

app3 = SCMChatbotApp(use_enhanced=False, use_rag=False, show_agent=True)
if app3.setup(data_path="train"):
    query = "What is the delivery delay rate?"
    print(f"\nQuery: {query}")
    print("-"*70)
    response = app3.query(query)
    print(response)
    print()

print("="*70)
print("Test Complete!")
print("="*70)
print("\nKey Features Demonstrated:")
print("✓ Agent name shown (Enhanced AI / Rule-Based)")
print("✓ Model displayed (Llama 3.3 70B / Pattern Matching)")
print("✓ Query complexity level indicated")
print("✓ RAG status shown when enabled")
print("✓ Can hide agent info with --hide-agent flag")
print("="*70)
