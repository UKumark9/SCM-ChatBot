"""Simple verification that the column fix works"""
import pandas as pd
import sys

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("Checking Orders CSV columns...")
print("="*50)

# Read the CSV
df = pd.read_csv('data/train/df_Orders.csv')

print(f"Total rows: {len(df)}")
print(f"\nColumns found: {df.columns.tolist()}")

# Check for delivery timestamp column
if 'order_delivered_timestamp' in df.columns:
    print("\n[OK] Found 'order_delivered_timestamp' column")

    # Convert to datetime
    df['order_delivered_timestamp'] = pd.to_datetime(df['order_delivered_timestamp'], errors='coerce')
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'], errors='coerce')

    # Calculate delays
    delivered_mask = (
        df['order_delivered_timestamp'].notna() &
        df['order_estimated_delivery_date'].notna()
    )

    delivered = df[delivered_mask].copy()
    delivered['delay_days'] = (
        delivered['order_delivered_timestamp'] -
        delivered['order_estimated_delivery_date']
    ).dt.days

    delivered['is_delayed'] = delivered['delay_days'] > 0

    # Stats
    total_delivered = len(delivered)
    total_delayed = delivered['is_delayed'].sum()
    delay_rate = (total_delayed / total_delivered * 100) if total_delivered > 0 else 0

    print(f"\nDelivery Statistics:")
    print(f"  Delivered orders: {total_delivered:,}")
    print(f"  Delayed orders: {total_delayed:,}")
    print(f"  Delay rate: {delay_rate:.2f}%")
    print(f"  Avg delay (delayed only): {delivered[delivered['is_delayed']]['delay_days'].mean():.1f} days")

    if delay_rate > 0:
        print("\n[OK] SUCCESS: Delays are being calculated!")
    else:
        print("\n[ERROR] WARNING: No delays found")

else:
    print("\n[ERROR] Column 'order_delivered_timestamp' NOT found")
    print("Available columns:", df.columns.tolist())

print("="*50)
