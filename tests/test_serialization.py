"""Test that Period objects are now serializable"""
import sys
import json
import pandas as pd
import numpy as np

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("Testing JSON Serialization Fix for Period Objects")
print("="*70)

# Import the conversion function
from enhanced_chatbot import convert_to_serializable

# Create test data with Period objects (like in analytics results)
test_data = {
    "total_orders": 89316,
    "delay_rate": 6.28,
    "delays_by_month": {
        pd.Period('2017-01', 'M'): 0.05,
        pd.Period('2017-02', 'M'): 0.06,
        pd.Period('2017-03', 'M'): 0.07
    },
    "some_timestamp": pd.Timestamp('2017-01-01'),
    "numpy_int": np.int64(123),
    "numpy_float": np.float64(45.67),
    "nested": {
        "period": pd.Period('2018-01', 'M'),
        "value": 100
    }
}

print("\n1. Original data (with Period objects):")
print("-"*70)
for key, value in test_data.items():
    print(f"   {key}: {type(value).__name__} = {value}")

print("\n2. Testing JSON serialization WITHOUT conversion:")
print("-"*70)
try:
    result = json.dumps(test_data, indent=2)
    print("[UNEXPECTED] Serialization succeeded (shouldn't happen!)")
except (TypeError, ValueError) as e:
    print(f"[EXPECTED] Error: {e}")

print("\n3. Converting data to serializable format:")
print("-"*70)
converted = convert_to_serializable(test_data)
print("[OK] Conversion completed")

print("\n4. Converted data types:")
print("-"*70)
for key, value in converted.items():
    if isinstance(value, dict):
        print(f"   {key}: dict with {len(value)} items")
        for k, v in list(value.items())[:2]:
            print(f"      {k}: {type(k).__name__} -> {type(v).__name__}")
    else:
        print(f"   {key}: {type(value).__name__} = {value}")

print("\n5. Testing JSON serialization WITH conversion:")
print("-"*70)
try:
    result = json.dumps(converted, indent=2)
    print("[OK] Serialization succeeded!")
    print("\nSample JSON output:")
    print("-"*70)
    print(result[:500] + "..." if len(result) > 500 else result)
except (TypeError, ValueError) as e:
    print(f"[ERROR] Still failing: {e}")

print("\n" + "="*70)
print("Test Complete!")
print("="*70)

if 'result' in locals():
    print("\n[SUCCESS] Period serialization fix is working!")
else:
    print("\n[FAILED] Serialization still has issues")
