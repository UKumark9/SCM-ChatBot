"""Test Response Detail Levels"""
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

print("Testing Response Detail Levels")
print("="*70)

# Initialize Enhanced AI mode
app = SCMChatbotApp(use_enhanced=True, use_rag=False)

print("\n1. Loading data...")
if not app.setup(data_path="train"):
    print("[ERROR] Setup failed")
    sys.exit(1)

print("[OK] Setup complete\n")

# Test queries with different complexity levels
test_cases = [
    {
        'level': 'SIMPLE',
        'queries': [
            "What is the delivery delay rate?",
            "What is the total revenue?",
            "How many orders are delayed?"
        ],
        'expected': '1 sentence with just the answer'
    },
    {
        'level': 'MODERATE',
        'queries': [
            "Show delivery performance",
            "Analyze revenue trends",
            "List top delayed states"
        ],
        'expected': 'Brief answer with 3-5 key metrics'
    },
    {
        'level': 'COMPLEX',
        'queries': [
            "What insights can you provide about delivery delays?",
            "Why are some states experiencing more delays?",
            "How can we improve our supply chain performance?"
        ],
        'expected': 'Comprehensive analysis with insights and recommendations'
    }
]

for test_case in test_cases:
    print("="*70)
    print(f"{test_case['level']} QUESTIONS")
    print(f"Expected: {test_case['expected']}")
    print("="*70)

    for query in test_case['queries']:
        print(f"\nQuery: \"{query}\"")
        print("-"*70)

        response = app.query(query)

        # Show response
        print("Response:")
        print(response)

        # Analyze response length
        lines = response.strip().split('\n')
        words = len(response.split())
        print(f"\n[Stats: {len(lines)} lines, {words} words]")
        print("-"*70)

print("\n" + "="*70)
print("Test Complete!")
print("="*70)
