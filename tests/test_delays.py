"""
Quick test script to verify delay calculations are working
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, str(Path(__file__).parent))

# Suppress the emoji print from main.py by redirecting stdout temporarily
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()
from main import SCMChatbotApp
sys.stdout = old_stdout

print("="*70)
print("Testing Delay Calculation Fix")
print("="*70)

# Initialize app in legacy mode for faster testing
app = SCMChatbotApp(use_enhanced=False, use_rag=False)

# Load data
print("\n1. Loading data...")
if not app.setup(data_path="train"):
    print("❌ Setup failed!")
    sys.exit(1)

# Test delay analysis
print("\n2. Testing delay analysis...")
if app.analytics:
    try:
        result = app.analytics.analyze_delivery_delays()

        print("\n" + "="*70)
        print("OVERALL DELIVERY METRICS")
        print("="*70)
        print(f"Total Orders: {result['total_orders']:,}")
        print(f"Delayed Orders: {result['delayed_orders']:,}")
        print(f"Delay Rate: {result['delay_rate_percentage']:.2f}%")
        print(f"Average Delay: {result['average_delay_days']:.1f} days")
        print(f"Max Delay: {result['max_delay_days']:.0f} days")
        print(f"Median Delay: {result['median_delay_days']:.1f} days")

        print("\n" + "="*70)
        print("TOP 10 STATES BY DELAY RATE")
        print("="*70)

        delays_by_state = result.get('delays_by_state', {})
        if delays_by_state:
            # Sort by delay rate
            sorted_states = sorted(
                [(state, rate * 100) for state, rate in delays_by_state.items()],
                key=lambda x: x[1],
                reverse=True
            )

            print(f"{'State':<10} {'Delay Rate':<15}")
            print("-" * 25)
            for state, rate in sorted_states[:10]:
                print(f"{state:<10} {rate:>6.2f}%")

            # Check if all are zero
            if all(rate == 0 for _, rate in sorted_states):
                print("\n⚠️  WARNING: All states show 0% delay rate!")
                print("This suggests the delay calculation is not working.")
            else:
                print("\n✅ SUCCESS: Delay rates are being calculated correctly!")
        else:
            print("❌ No state-level delay data available")

        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Analytics not initialized")

print("\n3. Testing query...")
response = app.query("Which states have the most delays?")
print("\nBot Response:")
print(response)

print("\n" + "="*70)
print("Test Complete!")
print("="*70)
