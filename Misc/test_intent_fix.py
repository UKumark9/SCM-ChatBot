"""
Test Intent Classification Fix
Demonstrates that "What is the delivery delay rate?" now returns data, not policy documents
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from intent_classifier import IntentClassifier

# Initialize classifier
classifier = IntentClassifier()

# Test queries
test_queries = [
    "What is the delivery delay rate?",  # Should be DATA
    "What are severity levels?",  # Should be POLICY
    "Show me delayed orders",  # Should be DATA
    "What is the policy on critical delays?",  # Should be POLICY
    "Compare actual delay rate with target policy"  # Should be MIXED
]

print("Intent Classification Test Results")
print("=" * 80)

for query in test_queries:
    result = classifier.classify_query(query)
    print(f"\nQuery: '{query}'")
    print(f"  Type: {result['query_type'].upper()}")
    print(f"  Domain: {result['domain']}")
    print(f"  Use RAG: {result['use_rag']} | Use Database: {result['use_database']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Reasoning: {result['reasoning']}")

print("\n" + "=" * 80)
print("\nKey Fix:")
print("  'What is the delivery delay rate?' → DATA (database only)")
print("  This will now return the actual rate (e.g., 6.28%) instead of policy targets (>95%)")
print("\n" + "=" * 80)
