"""
Dataset loading and preprocessing for the SCM Chatbot.

Single Responsibility: turn the raw Olist CSVs into clean, analytics-ready
DataFrames (date parsing, delay calculation, customer-state merge). This
module knows nothing about agents, LLMs, RAG, or the UI - callers just get
back a populated SCMDataset or a load() failure.

SCMDataset also serves as the "data wrapper" that SCMAnalytics and
AgentOrchestrator expect (orders/customers/products/order_items/payments +
get_summary_statistics()) - previously that wrapper was a small class
redefined identically in two places in main.py; now there is one definition.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class SCMDataset:
    """Holds the loaded/preprocessed order, customer, product, item, and payment data."""

    def __init__(self):
        self.orders = None
        self.customers = None
        self.products = None
        self.order_items = None
        self.payments = None

    def load(self, data_path: str = "train") -> bool:
        """Load CSVs and preprocess: parse dates, compute delays, merge customer state."""
        logger.info(f"Loading {data_path} data...")

        try:
            base_path = Path(f"data/{data_path}")

            logger.info("Loading CSV files...")
            self.customers = pd.read_csv(base_path / "df_Customers.csv")
            self.orders = pd.read_csv(base_path / "df_Orders.csv")
            self.order_items = pd.read_csv(base_path / "df_OrderItems.csv")
            self.payments = pd.read_csv(base_path / "df_Payments.csv")
            self.products = pd.read_csv(base_path / "df_Products.csv")

            logger.info(f"✅ Loaded {len(self.customers):,} customers")
            logger.info(f"✅ Loaded {len(self.orders):,} orders")
            logger.info(f"✅ Loaded {len(self.order_items):,} order items")
            logger.info(f"✅ Loaded {len(self.payments):,} payments")
            logger.info(f"✅ Loaded {len(self.products):,} products")

            self._process_orders()
            self._merge_customer_state()

            logger.info("✅ Data processing complete")
            return True

        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _process_orders(self):
        """Parse date columns and compute delivery delay fields on self.orders."""
        logger.info(f"Order columns: {self.orders.columns.tolist()}")
        logger.info("Processing orders data...")

        possible_date_cols = {
            "purchase": [
                "order_purchase_timestamp",
                "purchase_timestamp",
                "order_date",
            ],
            "approved": ["order_approved_at", "approved_at", "approval_date"],
            "delivered_carrier": [
                "order_delivered_carrier_date",
                "delivered_carrier_date",
                "carrier_date",
            ],
            "delivered_customer": [
                "order_delivered_timestamp",
                "order_delivered_customer_date",
                "delivered_customer_date",
                "delivery_date",
                "delivered_date",
            ],
            "estimated": [
                "order_estimated_delivery_date",
                "estimated_delivery_date",
                "estimated_date",
            ],
        }

        date_col_map = {}
        for key, possible_names in possible_date_cols.items():
            for name in possible_names:
                if name in self.orders.columns:
                    date_col_map[key] = name
                    break

        logger.info(f"Found date columns: {date_col_map}")

        for key, col in date_col_map.items():
            self.orders[col] = pd.to_datetime(self.orders[col], errors="coerce")
            logger.info(f"  Converted {col} to datetime")

        if "delivered_customer" in date_col_map and "estimated" in date_col_map:
            self._calculate_delays(date_col_map)
        else:
            logger.warning(
                "⚠️  Could not find delivery date columns - delay analysis will be limited"
            )
            self.orders["delay_days"] = 0
            self.orders["is_delayed"] = False
            self.orders["is_on_time"] = True

        if "purchase" in date_col_map:
            purchase_col = date_col_map["purchase"]
            self.orders["order_month"] = self.orders[purchase_col].dt.to_period("M")
            self.orders["order_year"] = self.orders[purchase_col].dt.year

            if purchase_col != "order_purchase_timestamp":
                self.orders["order_purchase_timestamp"] = self.orders[purchase_col]

    def _calculate_delays(self, date_col_map: dict):
        """Compute delay_days / is_delayed / is_on_time from the delivered & estimated columns."""
        logger.info("Calculating delivery metrics...")

        delivered_col = date_col_map["delivered_customer"]
        estimated_col = date_col_map["estimated"]

        delivered_mask = (
            self.orders[delivered_col].notna() & self.orders[estimated_col].notna()
        )
        delivered_orders = self.orders[delivered_mask].copy()

        delivered_orders["delay_days"] = (
            delivered_orders[delivered_col] - delivered_orders[estimated_col]
        ).dt.days
        delivered_orders["is_delayed"] = delivered_orders["delay_days"] > 0
        delivered_orders["is_on_time"] = delivered_orders["delay_days"] <= 0

        self.orders["delay_days"] = 0
        self.orders["is_delayed"] = False
        self.orders["is_on_time"] = False

        self.orders.loc[delivered_mask, "delay_days"] = delivered_orders[
            "delay_days"
        ].values
        self.orders.loc[delivered_mask, "is_delayed"] = delivered_orders[
            "is_delayed"
        ].values
        self.orders.loc[delivered_mask, "is_on_time"] = delivered_orders[
            "is_on_time"
        ].values

        total_delivered = delivered_orders.shape[0]
        total_delayed = delivered_orders["is_delayed"].sum()
        delay_rate = (
            (total_delayed / total_delivered * 100) if total_delivered > 0 else 0
        )

        logger.info(f"✅ Processed {total_delivered:,} delivered orders")
        logger.info(
            f"✅ Found {total_delayed:,} delayed orders ({delay_rate:.2f}% delay rate)"
        )

    def _merge_customer_state(self):
        """Merge customer state info into self.orders as 'customer_state'."""
        logger.info("Merging customer data...")

        if (
            "customer_id" not in self.orders.columns
            or "customer_id" not in self.customers.columns
        ):
            return

        state_col = None
        for possible in ["customer_state", "state", "customer_uf"]:
            if possible in self.customers.columns:
                state_col = possible
                break

        if not state_col:
            logger.warning("⚠️  Could not find customer state column")
            self.orders["customer_state"] = "Unknown"
            return

        customer_info = self.customers[["customer_id", state_col]].drop_duplicates(
            "customer_id"
        )
        customer_info = customer_info.rename(columns={state_col: "customer_state"})
        self.orders = self.orders.merge(
            customer_info, on="customer_id", how="left", suffixes=("", "_merged")
        )
        logger.info("✅ Merged customer state information")

    def get_summary_statistics(self) -> dict:
        """
        Summary-stats view consumed by SCMAnalytics / AgentOrchestrator.
        This is what the old inline `DataWrapper` classes existed only to provide.
        """
        return {
            "total_orders": len(self.orders),
            "total_customers": len(self.customers),
            "total_products": len(self.products),
            "total_order_items": len(self.order_items),
            "total_payments": len(self.payments),
            "date_range": {
                "start": str(self.orders["order_purchase_timestamp"].min()),
                "end": str(self.orders["order_purchase_timestamp"].max()),
            },
        }
