"""
Test Feature Store - Verify extracted features
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.feature_store import FeatureStore, MLFeatures

def test_feature_store():
    """Test feature store access"""

    print("Testing Feature Store...")
    print("=" * 60)

    # Initialize feature store
    fs = FeatureStore(use_redis=False)
    ml = MLFeatures(fs)

    # Get stats
    stats = fs.get_stats()
    print(f"\nFeature Store Statistics:")
    print(f"  Backend: {stats['backend']}")
    print(f"  Total Features: {stats['total_features']:,}")
    print(f"  Storage Size: {stats.get('storage_size_mb', 0):.2f} MB")

    # Test customer feature retrieval
    print(f"\n" + "=" * 60)
    print("Sample Customer Features:")
    print("=" * 60)

    customer_feature = fs.get('customer', 'hCT0x9JiGXBQ')
    if customer_feature:
        print(f"\nCustomer ID: {customer_feature['customer_id']}")
        print(f"  Total Orders: {customer_feature['total_orders']}")
        print(f"  Total Spend: ${customer_feature['total_spend']:.2f}")
        print(f"  Avg Order Value: ${customer_feature['avg_order_value']:.2f}")
        print(f"  Location: {customer_feature['customer_city']}, {customer_feature['customer_state']}")
        print(f"  Favorite Category: {customer_feature['favorite_category']}")
        print(f"  Segment: {customer_feature['segment']}")
        print(f"  Days Since Last Order: {customer_feature['days_since_last_order']}")
    else:
        print("  No customer feature found")

    # Test product feature retrieval
    print(f"\n" + "=" * 60)
    print("Sample Product Features:")
    print("=" * 60)

    product_feature = fs.get('product', '90K0C1fIyQUf')
    if product_feature:
        print(f"\nProduct ID: {product_feature['product_id']}")
        print(f"  Category: {product_feature['category']}")
        print(f"  Weight: {product_feature['weight_g']}g")
        print(f"  Volume: {product_feature['volume_cm3']:.1f} cm³")
        print(f"  Avg Price: ${product_feature['avg_price']:.2f}")
        print(f"  Total Revenue: ${product_feature['total_revenue']:.2f}")
        print(f"  Units Sold: {product_feature['units_sold']}")
        print(f"  Category Rank: {product_feature['category_rank']}")
    else:
        print("  No product feature found")

    # Test order feature retrieval
    print(f"\n" + "=" * 60)
    print("Sample Order Features:")
    print("=" * 60)

    order_feature = fs.get('order', 'Axfy13Hk4PIk')
    if order_feature:
        print(f"\nOrder ID: {order_feature['order_id']}")
        print(f"  Customer ID: {order_feature['customer_id']}")
        print(f"  Status: {order_feature['order_status']}")
        print(f"  Total: ${order_feature['order_total']:.2f}")
        print(f"  Item Count: {order_feature['item_count']}")
        print(f"  Payment Type: {order_feature['payment_type']}")
        print(f"  Installments: {order_feature['installments']}")
        print(f"  Delivery Time: {order_feature['delivery_time_days']} days")
        print(f"  Delivery Delay: {order_feature['delivery_delay_days']} days")
        print(f"  On-Time: {order_feature['on_time_delivery']}")
    else:
        print("  No order feature found")

    # Test aggregate features
    print(f"\n" + "=" * 60)
    print("Aggregate Analytics:")
    print("=" * 60)

    # Top selling products
    top_products = fs.get('analytics', 'top_selling_products')
    if top_products:
        print(f"\nTop 5 Selling Products:")
        for product_id, count in list(top_products.items())[:5]:
            print(f"  {product_id}: {count} orders")

    # Category performance
    category_perf = fs.get('analytics', 'category_performance')
    if category_perf:
        print(f"\nTop 5 Categories by Revenue:")
        sorted_categories = sorted(category_perf, key=lambda x: x['total_revenue'], reverse=True)[:5]
        for cat in sorted_categories:
            print(f"  {cat['category']}: ${cat['total_revenue']:.2f} ({cat['order_count']} orders)")

    # Delivery performance
    delivery = fs.get('analytics', 'delivery_performance')
    if delivery:
        print(f"\nDelivery Performance:")
        print(f"  On-Time Rate: {delivery['on_time_rate_percent']:.1f}%")
        print(f"  Avg Delay (when late): {delivery['avg_delay_days']:.1f} days")
        print(f"  Total Delivered Orders: {delivery['total_delivered_orders']:,}")

    # Payment distribution
    payment_dist = fs.get('analytics', 'payment_distribution')
    if payment_dist:
        print(f"\nPayment Method Distribution:")
        for payment_type, count in sorted(payment_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"  {payment_type}: {count:,} orders")

    print(f"\n" + "=" * 60)
    print("Feature Store Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_feature_store()
