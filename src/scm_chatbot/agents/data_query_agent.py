"""
Data Query Agent - Specialized agent for querying raw data
Part of the SCM Chatbot Agentic Architecture
"""

import logging
import re
import io
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ui_formatter import UIFormatter

logger = logging.getLogger(__name__)

try:
    from langchain_groq import ChatGroq
    from langchain_core.tools import Tool
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available for Data Query Agent")


class DataQueryAgent:
    """Specialized agent for querying and retrieving specific data records"""

    # Chart theme constants (dark theme matching ForecastingEngine)
    CHART_BG = '#1e293b'
    CHART_TEXT = '#f1f5f9'
    CHART_GRID = '#334155'
    CHART_PRIMARY = '#6366f1'

    # User-friendly column name mapping
    COLUMN_NAMES = {
        'order_id': 'Order ID',
        'customer_id': 'Customer ID',
        'order_purchase_timestamp': 'Purchase Date',
        'order_delivered_timestamp': 'Delivered Date',
        'order_delivered_customer_date': 'Delivered Date',
        'order_estimated_delivery_date': 'Estimated Delivery',
        'customer_state': 'State',
        'customer_city': 'City',
        'product_id': 'Product ID',
        'product_category_name': 'Category',
        'price': 'Price',
        'payment_value': 'Payment Amount',
        'delay_days': 'Delay (Days)',
        'is_delayed': 'Delayed',
        'is_on_time': 'On-Time',
        'total_sold': 'Units Sold',
        'total_revenue': 'Total Revenue',
        'order_month': 'Month',
        'order_status': 'Status'
    }

    def __init__(self, data_wrapper, llm_client=None, use_langchain: bool = True, rag_module=None):
        """
        Initialize Data Query Agent

        Args:
            data_wrapper: Object with orders, customers, products dataframes
            llm_client: LLM client
            use_langchain: Whether to use LangChain framework
            rag_module: RAG module for semantic search (optional)
        """
        self.data = data_wrapper
        self.llm_client = llm_client
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.rag_module = rag_module
        self.agent_executor = None
        self._pending_chart: Optional[str] = None
        self._pending_charts: Optional[list] = None

        if self.use_langchain and llm_client:
            self._initialize_langchain_agent()

        logger.info(f"Data Query Agent initialized (LangChain: {self.use_langchain}, RAG: {rag_module is not None})")

    # ── Helper methods ──────────────────────────────────────────────────────

    @staticmethod
    def _friendly_column_name(col: str) -> str:
        """Convert technical column name to user-friendly display name."""
        return DataQueryAgent.COLUMN_NAMES.get(col, col.replace('_', ' ').title())

    # ── Chart generation helpers ────────────────────────────────────────────

    def _generate_bar_chart(
        self, labels: list, values: list, title: str,
        xlabel: str, ylabel: str, color: str = None,
        horizontal: bool = False
    ) -> str:
        """Generate bar chart (vertical or horizontal) — returns base64 PNG."""
        if color is None:
            color = self.CHART_PRIMARY

        fig, ax = plt.subplots(
            figsize=(10, max(4, len(labels) * 0.5)) if horizontal else (10, 5),
            facecolor=self.CHART_BG
        )
        ax.set_facecolor(self.CHART_BG)

        if horizontal:
            bars = ax.barh(labels, values, color=color, height=0.6, edgecolor='none')
            ax.set_xlabel(xlabel, color=self.CHART_TEXT, fontsize=11)
            v_max = max(values) if values else 1
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_width() + v_max * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    f'{val:,.0f}', va='center',
                    color=self.CHART_TEXT, fontweight='bold', fontsize=10
                )
            ax.set_xlim(0, v_max * 1.18)
            ax.grid(True, alpha=0.15, color=self.CHART_GRID, axis='x')
        else:
            bars = ax.bar(labels, values, color=color, width=0.6, edgecolor='none')
            ax.set_ylabel(ylabel, color=self.CHART_TEXT, fontsize=11)
            v_max = max(values) if values else 1
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + v_max * 0.02,
                    f'{val:,.0f}', ha='center', va='bottom',
                    color=self.CHART_TEXT, fontweight='bold', fontsize=9
                )
            ax.set_ylim(0, v_max * 1.18)
            ax.grid(True, alpha=0.15, color=self.CHART_GRID, axis='y')
            if len(labels) > 10:
                fig.autofmt_xdate(rotation=45)

        ax.set_title(title, color=self.CHART_TEXT, fontsize=13,
                     fontweight='bold', pad=16)
        ax.tick_params(colors=self.CHART_TEXT, labelsize=9)

        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']:
            ax.spines[spine].set_color(self.CHART_GRID)

        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor=self.CHART_BG, edgecolor='none')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_b64

    def _generate_pie_chart(
        self, labels: list, values: list, title: str, colors: list = None
    ) -> str:
        """Generate pie chart with dark theme — returns base64 PNG."""
        fig, ax = plt.subplots(figsize=(7, 7), facecolor=self.CHART_BG)
        ax.set_facecolor(self.CHART_BG)

        if colors is None:
            colors = [
                '#10b981', '#ef4444', '#f59e0b', '#6366f1', '#06b6d4',
                '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#84cc16'
            ]

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors[:len(values)],
            autopct='%1.1f%%', startangle=90, pctdistance=0.78,
            textprops={'color': self.CHART_TEXT, 'fontsize': 10},
            wedgeprops={'edgecolor': self.CHART_BG, 'linewidth': 1.5}
        )

        for autotext in autotexts:
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)

        ax.set_title(title, color=self.CHART_TEXT, fontsize=13,
                     fontweight='bold', pad=18)

        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor=self.CHART_BG, edgecolor='none')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_b64

    # ── Parameter parsing helpers ───────────────────────────────────────────

    def _extract_order_id(self, text: str) -> Optional[str]:
        """Extract order ID from text using regex patterns."""
        # Match 12-char alphanumeric IDs (Olist format like Axfy13Hk4PIk)
        match = re.search(r'\b[a-zA-Z0-9]{12}\b', text)
        if not match:
            # Fallback: try 32-char hex IDs (UUID format)
            match = re.search(r'\b[a-f0-9]{32}\b', text.lower())
        return match.group() if match else None

    def _extract_limit(
        self, text: str, default: int = 10, max_limit: int = 50
    ) -> int:
        """Extract limit/top-N from text like 'top 10' or 'best 5'."""
        match = re.search(
            r'top\s+(\d+)|(\d+)\s+(?:products|categories|items)|limit\s+(\d+)',
            text.lower()
        )
        if match:
            limit = int(match.group(1) or match.group(2) or match.group(3))
            return min(limit, max_limit)
        return default

    def _extract_state(self, text: str) -> Optional[str]:
        """Extract Brazilian state code from text."""
        # Brazilian state name to code mapping
        # Organize by length to match longer names first (e.g., "rio de janeiro" before "rio")
        state_map = {
            'rio de janeiro': 'RJ',
            'rio grande do sul': 'RS',
            'rio grande do norte': 'RN',
            'mato grosso do sul': 'MS',
            'espírito santo': 'ES', 'espirito santo': 'ES',
            'santa catarina': 'SC',
            'mato grosso': 'MT',
            'minas gerais': 'MG',
            'são paulo': 'SP', 'sao paulo': 'SP',
            'pernambuco': 'PE',
            'tocantins': 'TO',
            'sergipe': 'SE',
            'roraima': 'RR',
            'rondônia': 'RO', 'rondonia': 'RO',
            'piauí': 'PI', 'piaui': 'PI',
            'paraíba': 'PB', 'paraiba': 'PB',
            'maranhão': 'MA', 'maranhao': 'MA',
            'amazonas': 'AM',
            'goiás': 'GO', 'goias': 'GO',
            'ceará': 'CE', 'ceara': 'CE',
            'brasília': 'DF', 'brasilia': 'DF',
            'bahia': 'BA',
            'paraná': 'PR', 'parana': 'PR',
            'pará': 'PA', 'para': 'PA',
            'alagoas': 'AL',
            'amapá': 'AP', 'amapa': 'AP',
            'minas': 'MG',
            'acre': 'AC',
            'rio': 'RJ',
        }

        text_lower = text.lower()

        # First try multi-word state names (they can use substring matching)
        for key, code in state_map.items():
            if ' ' in key:  # Multi-word names like "rio de janeiro"
                if key in text_lower:
                    return code

        # Then try single-word state names with word boundary matching
        for key, code in state_map.items():
            if ' ' not in key:  # Single-word names like "rio", "minas"
                # Use word boundary matching to avoid matching "states" → "es"
                if re.search(rf'\b{re.escape(key)}\b', text_lower):
                    return code

        # Finally, try 2-letter uppercase codes with strict word boundaries
        match = re.search(r'\b([A-Z]{2})\b', text)
        return match.group(1) if match else None

    def _parse_date_range(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse date range from natural language."""
        text_lower = text.lower()

        # Handle specific months like "January 2024"
        month_match = re.search(
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
            text_lower
        )
        if month_match:
            month_name = month_match.group(1)
            year = month_match.group(2)
            month_num = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }[month_name]
            start = pd.Timestamp(year=int(year), month=month_num, day=1)
            end = start + pd.offsets.MonthEnd(0)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

        # Handle quarters like "Q1 2024"
        quarter_match = re.search(r'q([1-4])\s+(\d{4})', text_lower)
        if quarter_match:
            quarter = int(quarter_match.group(1))
            year = int(quarter_match.group(2))
            start_month = (quarter - 1) * 3 + 1
            start = pd.Timestamp(year=year, month=start_month, day=1)
            end = start + pd.offsets.QuarterEnd(0)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

        # Handle year like "2024" or "in 2024"
        year_match = re.search(r'\b(20\d{2})\b', text_lower)
        if year_match and 'from' not in text_lower and 'to' not in text_lower:
            year = int(year_match.group(1))
            return f'{year}-01-01', f'{year}-12-31'

        # Handle explicit ranges like "2024-01-01 to 2024-03-31"
        range_match = re.search(
            r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})',
            text_lower
        )
        if range_match:
            return range_match.group(1), range_match.group(2)

        # Handle "from X to Y"
        from_to_match = re.search(
            r'from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})',
            text_lower
        )
        if from_to_match:
            return from_to_match.group(1), from_to_match.group(2)

        # Handle "between X and Y" with ISO dates
        between_match = re.search(
            r'between\s+(\d{4}-\d{2}-\d{2})\s+and\s+(\d{4}-\d{2}-\d{2})',
            text_lower
        )
        if between_match:
            return between_match.group(1), between_match.group(2)

        # Handle "between Month Day Year and Month Day Year" (e.g., "between January 1 2024 and March 31 2024")
        between_named_match = re.search(
            r'between\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})\s+(\d{4})\s+and\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})\s+(\d{4})',
            text_lower
        )
        if between_named_match:
            month_map = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            start_month = month_map[between_named_match.group(1)]
            start_day = int(between_named_match.group(2))
            start_year = int(between_named_match.group(3))
            end_month = month_map[between_named_match.group(4)]
            end_day = int(between_named_match.group(5))
            end_year = int(between_named_match.group(6))

            start_date = f'{start_year:04d}-{start_month:02d}-{start_day:02d}'
            end_date = f'{end_year:04d}-{end_month:02d}-{end_day:02d}'
            return start_date, end_date

        return None, None

    # ── Tool implementation methods ─────────────────────────────────────────

    def _find_order_by_id(self, query: str = "") -> str:
        """Find and display full details for a specific order ID."""
        order_id = self._extract_order_id(query)

        if not order_id:
            return "**Error**: Could not extract order ID from query. Please provide a valid order ID (e.g., 'Axfy13Hk4PIk')."

        try:
            # Find the order
            order = self.data.orders[self.data.orders['order_id'] == order_id]

            if order.empty:
                return f"**No order found** with ID: `{order_id}`"

            order_row = order.iloc[0]

            # Get order items
            items = self.data.order_items[self.data.order_items['order_id'] == order_id]

            # Get payment info
            payment = self.data.payments[self.data.payments['order_id'] == order_id]
            total_payment = payment['payment_value'].sum() if not payment.empty else 0

            # Build response
            response = f"## Order Details: `{order_id}`\n\n"
            response += "### Order Information\n"
            response += f"- **{self._friendly_column_name('customer_id')}**: {order_row.get('customer_id', 'N/A')}\n"
            response += f"- **{self._friendly_column_name('order_purchase_timestamp')}**: {order_row.get('order_purchase_timestamp', 'N/A')}\n"
            response += f"- **{self._friendly_column_name('customer_state')}**: {order_row.get('customer_state', 'N/A')}\n\n"

            response += "### Delivery Status\n"
            delivered_date = order_row.get('order_delivered_timestamp', order_row.get('order_delivered_customer_date', 'Not delivered'))
            estimated_date = order_row.get('order_estimated_delivery_date', 'N/A')
            response += f"- **{self._friendly_column_name('order_delivered_customer_date')}**: {delivered_date}\n"
            response += f"- **{self._friendly_column_name('order_estimated_delivery_date')}**: {estimated_date}\n"

            if 'delay_days' in order_row and pd.notna(order_row['delay_days']):
                delay_days = int(order_row['delay_days'])
                if delay_days > 0:
                    response += f"- **Status**: **Delayed** by {delay_days} days\n"
                else:
                    response += f"- **Status**: **On-time** (delivered {abs(delay_days)} days early)\n"
            else:
                response += f"- **Status**: Pending or unknown\n"

            response += f"\n### Payment\n"
            response += f"- **Total Payment**: R$ {total_payment:,.2f}\n"

            if not items.empty:
                response += f"\n### Order Items ({len(items)} items)\n\n"
                response += f"| {self._friendly_column_name('product_id')} | {self._friendly_column_name('price')} |\n|---|---|\n"
                for _, item in items.head(10).iterrows():
                    response += f"| {item.get('product_id', 'N/A')} | R$ {item.get('price', 0):.2f} |\n"
                if len(items) > 10:
                    response += f"\n*... and {len(items) - 10} more items*\n"

            return response

        except Exception as e:
            logger.error(f"Error finding order: {e}")
            return f"**Error** retrieving order details: {e}"

    def _get_top_products(self, query: str = "") -> str:
        """Get top N products by sales volume with bar chart."""
        limit = self._extract_limit(query, default=10, max_limit=50)

        try:
            # Merge order_items with products
            items_products = self.data.order_items.merge(
                self.data.products[['product_id', 'product_category_name']],
                on='product_id',
                how='left'
            )

            # Group by product and count sales
            product_sales = items_products.groupby('product_id').agg({
                'product_id': 'count',
                'price': 'sum',
                'product_category_name': 'first'
            }).rename(columns={'product_id': 'total_sold', 'price': 'total_revenue'})

            # Sort and get top N
            top_products = product_sales.nlargest(limit, 'total_sold')

            # Generate bar chart
            labels = [f"{pid[:8]}..." for pid in top_products.index]
            values = top_products['total_sold'].tolist()

            chart_b64 = self._generate_bar_chart(
                labels=list(reversed(labels)),
                values=list(reversed(values)),
                title=f'Top {limit} Products by Sales Volume',
                xlabel='Units Sold',
                ylabel='',
                horizontal=True
            )

            self._pending_chart = chart_b64
            self._pending_charts = [chart_b64]

            # Build text response
            response = f"## Top {limit} Products by Sales Volume\n\n"
            response += f"| Rank | {self._friendly_column_name('product_id')} | {self._friendly_column_name('product_category_name')} | {self._friendly_column_name('total_sold')} | {self._friendly_column_name('total_revenue')} |\n"
            response += "|---|---|---|---|---|\n"

            for i, (pid, row) in enumerate(top_products.iterrows(), 1):
                category = row['product_category_name'] if pd.notna(row['product_category_name']) else 'Unknown'
                response += f"| {i} | {pid[:16]}... | {category[:20]} | {int(row['total_sold']):,} | R$ {row['total_revenue']:,.2f} |\n"

            return response

        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return f"**Error** retrieving top products: {e}"

    def _get_top_categories(self, query: str = "") -> str:
        """Get top N categories by sales with pie chart."""
        limit = self._extract_limit(query, default=10, max_limit=20)

        try:
            # Merge order_items with products
            items_products = self.data.order_items.merge(
                self.data.products[['product_id', 'product_category_name']],
                on='product_id',
                how='left'
            )

            # Group by category
            category_sales = items_products.groupby('product_category_name').agg({
                'product_id': 'count',
                'price': 'sum'
            }).rename(columns={'product_id': 'total_sold', 'price': 'total_revenue'})

            # Remove nulls and sort
            category_sales = category_sales[category_sales.index.notna()]
            top_categories = category_sales.nlargest(limit, 'total_sold')

            # Generate pie chart
            labels = [cat[:20] if isinstance(cat, str) else str(cat)[:20] for cat in top_categories.index]
            values = top_categories['total_sold'].tolist()

            pie_b64 = self._generate_pie_chart(
                labels=labels,
                values=values,
                title=f'Top {limit} Categories by Sales Distribution'
            )

            self._pending_chart = pie_b64
            self._pending_charts = [pie_b64]

            # Build text response
            response = f"## Top {limit} Product Categories\n\n"
            response += f"| Rank | {self._friendly_column_name('product_category_name')} | {self._friendly_column_name('total_sold')} | {self._friendly_column_name('total_revenue')} |\n"
            response += "|---|---|---|\n"

            for i, (cat, row) in enumerate(top_categories.iterrows(), 1):
                cat_display = cat if isinstance(cat, str) else str(cat)
                response += f"| {i} | {cat_display[:30]} | {int(row['total_sold']):,} | R$ {row['total_revenue']:,.2f} |\n"

            return response

        except Exception as e:
            logger.error(f"Error getting top categories: {e}")
            return f"**Error** retrieving top categories: {e}"

    def _list_unique_categories(self, query: str = "") -> str:
        """List all unique product categories in user-readable format."""
        try:
            # Get all unique categories from products
            categories = self.data.products['product_category_name'].dropna().unique()
            categories = sorted(categories)  # Sort alphabetically

            total_categories = len(categories)

            # Format categories to be user-readable
            def format_category(cat_name):
                """Convert technical category name to user-readable format."""
                if pd.isna(cat_name):
                    return "Unknown"
                # Replace underscores with spaces and title case each word
                formatted = cat_name.replace('_', ' ').title()
                return formatted

            # Build response
            response = f"## Product Categories\n\n"
            response += f"**Total Categories**: {total_categories}\n\n"

            # Create formatted list
            formatted_categories = [format_category(cat) for cat in categories]

            # Display in numbered list for better readability
            response += "### All Categories\n\n"

            # Split into 2 columns for cleaner display
            mid_point = (len(formatted_categories) + 1) // 2

            response += "| # | Category | # | Category |\n"
            response += "|---|---|---|---|\n"

            for i in range(mid_point):
                left_num = i + 1
                left_cat = formatted_categories[i]

                # Right column (if exists)
                right_idx = i + mid_point
                if right_idx < len(formatted_categories):
                    right_num = right_idx + 1
                    right_cat = formatted_categories[right_idx]
                    response += f"| {left_num} | {left_cat} | {right_num} | {right_cat} |\n"
                else:
                    response += f"| {left_num} | {left_cat} | | |\n"

            return response

        except Exception as e:
            logger.error(f"Error listing unique categories: {e}")
            return f"**Error** listing unique categories: {e}"

    def _filter_orders_by_date_range(self, query: str = "") -> str:
        """Filter orders by date range with monthly breakdown chart."""
        start_date, end_date = self._parse_date_range(query)

        try:
            orders = self.data.orders.copy()

            # Ensure timestamp column exists
            date_col = 'order_purchase_timestamp'
            if date_col not in orders.columns:
                date_col = 'purchase_timestamp' if 'purchase_timestamp' in orders.columns else None

            if date_col is None:
                return "**Error**: No purchase timestamp column found in orders data."

            # Convert to datetime
            orders[date_col] = pd.to_datetime(orders[date_col])

            # Filter by date range if provided
            if start_date and end_date:
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                filtered_orders = orders[(orders[date_col] >= start_dt) & (orders[date_col] <= end_dt)]
                title_suffix = f"{start_date} to {end_date}"
            elif start_date:
                start_dt = pd.to_datetime(start_date)
                filtered_orders = orders[orders[date_col] >= start_dt]
                title_suffix = f"from {start_date}"
            else:
                filtered_orders = orders
                title_suffix = "All Time"

            if filtered_orders.empty:
                return f"**No orders found** in the specified date range."

            # Group by month
            filtered_orders['month'] = filtered_orders[date_col].dt.to_period('M')
            monthly_counts = filtered_orders.groupby('month').size()

            # Generate bar chart
            labels = [str(m) for m in monthly_counts.index]
            values = monthly_counts.tolist()

            chart_b64 = self._generate_bar_chart(
                labels=labels,
                values=values,
                title=f'Monthly Order Volume — {title_suffix}',
                xlabel='Month',
                ylabel='Orders',
                horizontal=False
            )

            self._pending_chart = chart_b64
            self._pending_charts = [chart_b64]

            # Calculate stats
            total_orders = len(filtered_orders)

            # Get payment total if available
            if hasattr(self.data, 'payments'):
                order_ids = filtered_orders['order_id'].unique()
                payments = self.data.payments[self.data.payments['order_id'].isin(order_ids)]
                total_revenue = payments['payment_value'].sum()
                avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            else:
                total_revenue = 0
                avg_order_value = 0

            # Build response
            response = f"## Orders: {title_suffix}\n\n"
            response += f"- **Total Orders**: {total_orders:,}\n"
            if total_revenue > 0:
                response += f"- **Total Revenue**: R$ {total_revenue:,.2f}\n"
                response += f"- **Avg Order Value**: R$ {avg_order_value:.2f}\n"
            response += f"- **Date Range**: {filtered_orders[date_col].min().date()} to {filtered_orders[date_col].max().date()}\n\n"

            response += "### Monthly Breakdown\n\n"
            response += f"| {self._friendly_column_name('order_month')} | Orders |\n|---|---|\n"
            for month, count in monthly_counts.items():
                response += f"| {month} | {count:,} |\n"

            return response

        except Exception as e:
            logger.error(f"Error filtering orders by date: {e}")
            return f"**Error** filtering orders: {e}"

    def _get_customers_by_state(self, query: str = "") -> str:
        """Get customers filtered by state with distribution chart."""
        state_filter = self._extract_state(query)

        try:
            customers = self.data.customers.copy()

            # Find state column
            state_col = None
            for col in ['customer_state', 'state', 'customer_uf']:
                if col in customers.columns:
                    state_col = col
                    break

            if state_col is None:
                return "**Error**: No state column found in customers data."

            # Filter by state if specified
            if state_filter:
                filtered_customers = customers[customers[state_col] == state_filter]
                if filtered_customers.empty:
                    return f"**No customers found** in state: {state_filter}"
                total_customers = len(filtered_customers)
                response = f"## Customers in {state_filter}\n\n"
                response += f"- **Total Customers**: {total_customers:,}\n"
            else:
                filtered_customers = customers
                total_customers = len(filtered_customers)

                # Get state distribution
                state_counts = filtered_customers[state_col].value_counts().head(10)

                # Generate bar chart
                labels = list(reversed(state_counts.index.tolist()))
                values = list(reversed(state_counts.tolist()))

                chart_b64 = self._generate_bar_chart(
                    labels=labels,
                    values=values,
                    title='Top 10 States by Customer Count',
                    xlabel='Customers',
                    ylabel='',
                    horizontal=True
                )

                self._pending_chart = chart_b64
                self._pending_charts = [chart_b64]

                response = f"## Customer Distribution by State\n\n"
                response += f"- **Total Customers**: {total_customers:,}\n\n"
                response += "### Top 10 States\n\n"
                response += f"| Rank | {self._friendly_column_name('customer_state')} | Customers |\n|---|---|---|\n"
                for i, (state, count) in enumerate(state_counts.items(), 1):
                    response += f"| {i} | {state} | {count:,} |\n"

            return response

        except Exception as e:
            logger.error(f"Error getting customers by state: {e}")
            return f"**Error** retrieving customers: {e}"

    def _get_order_status_breakdown(self, query: str = "") -> str:
        """Get order delivery status breakdown with pie chart."""
        try:
            orders = self.data.orders.copy()

            # Count by status
            if 'is_on_time' in orders.columns and 'is_delayed' in orders.columns:
                on_time_count = int((orders['is_on_time'] == True).sum())
                delayed_count = int((orders['is_delayed'] == True).sum())
                pending_count = len(orders) - on_time_count - delayed_count
            else:
                # Fallback: check if delivered
                delivered = orders[orders.get('order_delivered_timestamp', orders.get('order_delivered_customer_date')).notna()]
                on_time_count = len(delivered)
                delayed_count = 0
                pending_count = len(orders) - on_time_count

            total = len(orders)

            # Generate pie chart
            labels = []
            values = []
            colors = []

            if on_time_count > 0:
                labels.append(f'On-Time ({on_time_count:,})')
                values.append(on_time_count)
                colors.append('#10b981')

            if delayed_count > 0:
                labels.append(f'Delayed ({delayed_count:,})')
                values.append(delayed_count)
                colors.append('#ef4444')

            if pending_count > 0:
                labels.append(f'Pending ({pending_count:,})')
                values.append(pending_count)
                colors.append('#f59e0b')

            pie_b64 = self._generate_pie_chart(
                labels=labels,
                values=values,
                title='Order Delivery Status Breakdown',
                colors=colors
            )

            self._pending_chart = pie_b64
            self._pending_charts = [pie_b64]

            # Build response
            response = f"## Order Status Breakdown\n\n"
            response += f"- **Total Orders**: {total:,}\n\n"
            response += "| Status | Count | Percentage |\n|---|---|---|\n"

            if on_time_count > 0:
                pct = (on_time_count / total) * 100
                response += f"| On-Time | {on_time_count:,} | {pct:.1f}% |\n"

            if delayed_count > 0:
                pct = (delayed_count / total) * 100
                response += f"| Delayed | {delayed_count:,} | {pct:.1f}% |\n"

            if pending_count > 0:
                pct = (pending_count / total) * 100
                response += f"| ⏳ Pending | {pending_count:,} | {pct:.1f}% |\n"

            return response

        except Exception as e:
            logger.error(f"Error getting order status breakdown: {e}")
            return f"**Error** retrieving status breakdown: {e}"

    def _get_monthly_order_trends(self, query: str = "") -> str:
        """Get monthly order trends with bar chart."""
        try:
            orders = self.data.orders.copy()

            # Use order_month if available (precomputed in main.py)
            if 'order_month' in orders.columns:
                monthly_counts = orders.groupby('order_month').size().sort_index()
            else:
                # Fallback: compute from timestamp
                date_col = 'order_purchase_timestamp' if 'order_purchase_timestamp' in orders.columns else 'purchase_timestamp'
                if date_col not in orders.columns:
                    return "**Error**: No purchase timestamp column found."

                orders[date_col] = pd.to_datetime(orders[date_col])
                orders['month'] = orders[date_col].dt.to_period('M')
                monthly_counts = orders.groupby('month').size()

            # Generate bar chart
            labels = [str(m) for m in monthly_counts.index]
            values = monthly_counts.tolist()

            chart_b64 = self._generate_bar_chart(
                labels=labels,
                values=values,
                title='Monthly Order Trends',
                xlabel='Month',
                ylabel='Orders',
                horizontal=False
            )

            self._pending_chart = chart_b64
            self._pending_charts = [chart_b64]

            # Calculate growth rates
            growth_rates = monthly_counts.pct_change() * 100

            # Find peak month
            peak_month = monthly_counts.idxmax()
            peak_count = monthly_counts.max()

            # Build response
            response = f"## Monthly Order Trends\n\n"
            response += f"- **Peak Month**: {peak_month} ({peak_count:,} orders)\n"
            response += f"- **Average Orders/Month**: {monthly_counts.mean():.0f}\n"
            response += f"- **Total Months**: {len(monthly_counts)}\n\n"

            response += "### Monthly Data (Last 12 months)\n\n"
            response += f"| {self._friendly_column_name('order_month')} | Orders | MoM Growth |\n|---|---|---|\n"

            for month, count in monthly_counts.tail(12).items():
                growth = growth_rates.get(month, 0)
                growth_str = f"{growth:+.1f}%" if pd.notna(growth) else "N/A"
                response += f"| {month} | {count:,} | {growth_str} |\n"

            return response

        except Exception as e:
            logger.error(f"Error getting monthly trends: {e}")
            return f"**Error** retrieving monthly trends: {e}"

    def _get_customer_order_history(self, query: str = "") -> str:
        """Get all orders for a specific customer."""
        # Extract customer ID - support both 12-char alphanumeric and 32-char hex formats
        # First try 32-char hex (order IDs)
        match = re.search(r'\b[a-f0-9]{32}\b', query.lower())
        if not match:
            # Try 12-char alphanumeric (customer IDs like hCT0x9JiGXBQ)
            match = re.search(r'\b[a-zA-Z0-9]{12}\b', query)

        customer_id = match.group() if match else None

        if not customer_id:
            return "**Error**: Could not extract customer ID from query. Please provide a valid customer ID (e.g., 'hCT0x9JiGXBQ')."

        try:
            # Find orders for this customer
            customer_orders = self.data.orders[self.data.orders['customer_id'] == customer_id]

            if customer_orders.empty:
                return f"**No orders found** for customer ID: `{customer_id}`"

            # Sort by date
            date_col = 'order_purchase_timestamp' if 'order_purchase_timestamp' in customer_orders.columns else 'purchase_timestamp'
            if date_col in customer_orders.columns:
                customer_orders = customer_orders.sort_values(date_col)

            # Get payment totals if available
            if hasattr(self.data, 'payments'):
                order_ids = customer_orders['order_id'].unique()
                payments = self.data.payments[self.data.payments['order_id'].isin(order_ids)]
                payment_by_order = payments.groupby('order_id')['payment_value'].sum()
            else:
                payment_by_order = {}

            # Build response
            response = f"## Customer Order History: `{customer_id}`\n\n"
            response += f"- **Total Orders**: {len(customer_orders)}\n"

            if hasattr(self.data, 'payments') and len(payment_by_order) > 0:
                total_spent = payment_by_order.sum()
                avg_order_value = total_spent / len(customer_orders)
                response += f"- **Total Spent**: R$ {total_spent:,.2f}\n"
                response += f"- **Avg Order Value**: R$ {avg_order_value:.2f}\n"

            response += f"\n### Orders\n\n"
            response += f"| {self._friendly_column_name('order_id')} | {self._friendly_column_name('order_purchase_timestamp')} | Status | {self._friendly_column_name('payment_value')} |\n|---|---|---|---|\n"

            for _, order in customer_orders.head(20).iterrows():
                order_id = order['order_id']
                date = order.get(date_col, 'N/A')
                if pd.notna(date):
                    date = str(date)[:10]

                if 'is_delayed' in order and order['is_delayed']:
                    status = "Delayed"
                elif 'is_on_time' in order and order['is_on_time']:
                    status = "On-time"
                else:
                    status = "Pending"

                payment = payment_by_order.get(order_id, 0)
                payment_str = f"R$ {payment:,.2f}" if payment > 0 else "N/A"

                response += f"| {order_id[:16]}... | {date} | {status} | {payment_str} |\n"

            if len(customer_orders) > 20:
                response += f"\n*... and {len(customer_orders) - 20} more orders*\n"

            return response

        except Exception as e:
            logger.error(f"Error getting customer order history: {e}")
            return f"**Error** retrieving order history: {e}"

    # ── LangChain Agent Initialization ──────────────────────────────────────

    def _initialize_langchain_agent(self):
        """Initialize LangChain agent"""
        try:
            tools = [
                # Original tools
                Tool(
                    name="QueryOrders",
                    func=self._query_orders,
                    description="Query order records - basic sample and count"
                ),
                Tool(
                    name="QueryCustomers",
                    func=self._query_customers,
                    description="Query customer records - basic sample and count"
                ),
                Tool(
                    name="QueryProducts",
                    func=self._query_products,
                    description="Query product records - basic sample and count"
                ),
                Tool(
                    name="GetDataSummary",
                    func=self._get_data_summary,
                    description="Get summary of available data and record counts"
                ),
                # NEW ENHANCED TOOLS
                Tool(
                    name="FindOrderByID",
                    func=self._find_order_by_id,
                    description=(
                        "Find a specific order by order ID. Returns full order details including "
                        "order info, items, payment, and delivery status. Input format: provide order ID "
                        "as text (e.g., 'find order abc123' or just 'abc123')."
                    )
                ),
                Tool(
                    name="GetTopProducts",
                    func=self._get_top_products,
                    description=(
                        "Get top N products by sales volume with horizontal bar chart. Returns products "
                        "ranked by total items sold with revenue. Input format: 'top 10 products' or "
                        "'best selling products' (default: 10, max: 50)."
                    )
                ),
                Tool(
                    name="GetTopCategories",
                    func=self._get_top_categories,
                    description=(
                        "Get top N product categories by sales with pie chart showing distribution. "
                        "Input format: 'top 5 categories' (default: 10, max: 20)."
                    )
                ),
                Tool(
                    name="ListUniqueCategories",
                    func=self._list_unique_categories,
                    description=(
                        "List all unique product categories. Returns a complete alphabetically sorted "
                        "list of all product categories in the database. Input format: 'list categories', "
                        "'unique categories', 'all categories'."
                    )
                ),
                Tool(
                    name="FilterOrdersByDateRange",
                    func=self._filter_orders_by_date_range,
                    description=(
                        "Filter orders by date range or specific month with monthly breakdown bar chart. "
                        "Input formats: 'orders in January 2024', 'orders from 2024-01-01 to 2024-03-31', "
                        "'orders in Q1 2024', 'orders in 2023'."
                    )
                ),
                Tool(
                    name="GetCustomersByState",
                    func=self._get_customers_by_state,
                    description=(
                        "Get customers filtered by state with distribution bar chart. "
                        "Input format: 'customers in SP', 'customers in São Paulo'. "
                        "If no state specified, shows top 10 states distribution."
                    )
                ),
                Tool(
                    name="GetOrderStatusBreakdown",
                    func=self._get_order_status_breakdown,
                    description=(
                        "Get breakdown of orders by delivery status (on-time, delayed, pending) "
                        "with pie chart showing distribution."
                    )
                ),
                Tool(
                    name="GetMonthlyOrderTrends",
                    func=self._get_monthly_order_trends,
                    description=(
                        "Get monthly order trends and patterns with bar chart. Shows order volume "
                        "by month, growth rates, and peak months."
                    )
                ),
                Tool(
                    name="GetCustomerOrderHistory",
                    func=self._get_customer_order_history,
                    description=(
                        "Get all orders for a specific customer. Returns chronological list of orders "
                        "with dates, totals, and delivery status. Input format: provide customer ID."
                    )
                ),
            ]

            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized Data Query Agent for supply chain management.

Your expertise includes:
- Finding specific orders by ID
- Analyzing top products and categories with visual charts
- Filtering data by date ranges and geographic locations
- Tracking order status and delivery performance
- Analyzing customer purchase history and trends

IMPORTANT - POLICY VS DATA QUESTIONS:
If the user's query is asking about CONCEPTUAL/THEORETICAL topics (e.g., "approaches to warehousing", "modes of transport", "supply chain strategies"), and relevant context is provided at the beginning of the query, USE THAT CONTEXT to answer.
DO NOT try to answer conceptual questions using database tools. Database tools only contain transactional data (orders, customers, products), NOT policy documents or theoretical information.

TOOL SELECTION GUIDELINES:

**Direct Lookups**:
- "Find order X", "Order details" → FindOrderByID
- "Customer history for X", "Purchase history", "Orders for customer X" → GetCustomerOrderHistory

**Top Rankings** (with charts):
- "Top N products", "Best selling", "Most sold" → GetTopProducts (horizontal bar chart)
- "Top N categories", "Category breakdown" → GetTopCategories (pie chart)
- "List categories", "Unique categories", "All categories" → ListUniqueCategories (complete list)

**Date Filtering**:
- "Orders in [month/year]" (e.g., "Orders in January 2024") → FilterOrdersByDateRange
- "Orders from X to Y" (e.g., "Orders from 2024-01-01 to 2024-03-31") → FilterOrdersByDateRange
- "Orders between X and Y" (e.g., "Orders between January 1 2024 and March 31 2024") → FilterOrdersByDateRange
- "Orders in Q1/Q2/Q3/Q4 [year]" → FilterOrdersByDateRange

**Geographic Filtering**:
- "Customers in [state]" (e.g., "Customers in SP", "Customers in São Paulo") → GetCustomersByState
- "Customer distribution by state", "State breakdown" → GetCustomersByState

**Status & Trends**:
- "Order status", "Delivery status", "How many delayed" → GetOrderStatusBreakdown (pie chart)
- "Monthly trends", "Orders by month", "Monthly patterns" → GetMonthlyOrderTrends (bar chart)

**Basic Info**:
- "Show me orders", "List customers", "Show products" → QueryOrders, QueryCustomers, QueryProducts
- "Data summary" → GetDataSummary

PARAMETER PARSING:
- Extract order/customer IDs (12-char alphanumeric or 32-char hex) from natural language
- Parse dates flexibly: "January 2024", "Q1 2024", "2024-01-01 to 2024-03-31", "between X and Y"
- Recognize state codes (SP, RJ) and full names (São Paulo, Rio de Janeiro, Minas Gerais)
- Extract limits from "top 10", "best 5", etc.

Always choose the most specific tool for the user's query."""),
                ("human", "{input}"),
            ])

            agent = create_tool_calling_agent(self.llm_client, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True
            )

            logger.info("Data Query Agent LangChain executor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Data Query agent: {e}")
            self.use_langchain = False

    def _query_orders(self, query: str = "") -> str:
        """Query orders data"""
        try:
            total = len(self.data.orders)
            sample = self.data.orders.head(3)

            response = f"## Orders Data\n\n"
            response += f"- **Total Orders**: {total:,}\n\n"
            response += "### Sample Orders\n\n"

            if 'order_id' in sample.columns:
                # Create markdown table with friendly column names
                response += f"| {self._friendly_column_name('order_id')} | {self._friendly_column_name('customer_id')} | {self._friendly_column_name('order_purchase_timestamp')} |\n"
                response += "|---|---|---|\n"

                for _, row in sample.iterrows():
                    order_id = str(row.get('order_id', 'N/A'))[:16] + '...'
                    customer_id = str(row.get('customer_id', 'N/A'))[:16] + '...'
                    purchase_date = str(row.get('order_purchase_timestamp', 'N/A'))
                    response += f"| {order_id} | {customer_id} | {purchase_date} |\n"
            else:
                response += "*Columns not found*\n"

            return response
        except Exception as e:
            return f"Error querying orders: {e}"

    def _query_customers(self, query: str = "") -> str:
        """Query customers data"""
        try:
            total = len(self.data.customers)
            states = self.data.customers['customer_state'].value_counts().head(5) if 'customer_state' in self.data.customers.columns else None

            response = f"## Customer Data\n\n"
            response += f"- **Total Customers**: {total:,}\n\n"

            if states is not None:
                response += "### Top 5 States\n\n"
                response += f"| {self._friendly_column_name('customer_state')} | Customers | Percentage |\n"
                response += "|---|---|---|\n"
                for state, count in states.items():
                    pct = (count / total) * 100
                    response += f"| {state} | {count:,} | {pct:.1f}% |\n"

            return response
        except Exception as e:
            return f"Error querying customers: {e}"

    def _query_products(self, query: str = "") -> str:
        """Query products data"""
        try:
            total = len(self.data.products)
            sample = self.data.products.head(5)

            response = f"## Product Data\n\n"
            response += f"- **Total Products**: {total:,}\n\n"
            response += "### Sample Products\n\n"

            if 'product_id' in sample.columns and 'product_category_name' in sample.columns:
                response += f"| {self._friendly_column_name('product_id')} | {self._friendly_column_name('product_category_name')} |\n"
                response += "|---|---|\n"
                for _, row in sample.iterrows():
                    product_id = str(row.get('product_id', 'N/A'))[:24] + '...'
                    category = row.get('product_category_name', 'Unknown')
                    if pd.notna(category):
                        category = str(category)[:30]
                    else:
                        category = 'Unknown'
                    response += f"| {product_id} | {category} |\n"
            else:
                response += "*Product columns not found*\n"

            return response
        except Exception as e:
            return f"Error querying products: {e}"

    def _get_data_summary(self, query: str = "") -> str:
        """Get data summary"""
        try:
            summary = self.data.get_summary_statistics()

            response = f"## Data Summary\n\n"
            response += "| Metric | Value |\n"
            response += "|---|---|\n"
            response += f"| **Total Orders** | {summary['total_orders']:,} |\n"
            response += f"| **Total Customers** | {summary['total_customers']:,} |\n"
            response += f"| **Total Products** | {summary['total_products']:,} |\n"
            response += f"| **Date Range** | {summary['date_range']['start']} to {summary['date_range']['end']} |\n"

            return response
        except Exception as e:
            return f"Error getting data summary: {e}"

    def query(self, user_query: str, classification: Dict = None) -> Dict[str, Any]:
        """Process data query"""
        try:
            # Determine if should use RAG based on classification
            should_use_rag = classification.get('use_rag', True) if classification else True
            should_use_database = classification.get('use_database', True) if classification else True

            logger.info(f"Data Query Agent - Use RAG: {should_use_rag} | Use Database: {should_use_database}")

            # Try RAG context retrieval if classification allows it
            rag_context = None
            used_rag = False
            if self.rag_module and should_use_rag:
                try:
                    rag_context = self.rag_module.retrieve_context(user_query)
                    if rag_context and len(rag_context.strip()) > 0:
                        used_rag = True
                        logger.info("✅ RAG context retrieved for data query")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")

            # If using LangChain agent
            if self.use_langchain and self.agent_executor:
                # Augment query with RAG context if available
                if used_rag:
                    augmented_query = f"Context from documents:\n{rag_context}\n\nUser query: {user_query}"
                else:
                    augmented_query = user_query

                # Reset chart storage
                self._pending_chart = None
                self._pending_charts = None

                response = self.agent_executor.invoke({"input": augmented_query})

                # Capture generated charts
                chart_b64 = self._pending_chart
                charts_b64 = self._pending_charts

                return {
                    'response': response['output'],
                    'chart_base64': chart_b64,
                    'charts_base64': charts_b64,
                    'agent': 'Data Query Agent (LangChain)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag
                }

            # Fallback to rule-based
            else:
                query_lower = user_query.lower()

                # Reset chart storage
                self._pending_chart = None
                self._pending_charts = None

                # Data query agent typically doesn't handle policy questions
                # But respect classification if provided
                if classification and classification.get('query_type') == 'policy':
                    if used_rag and rag_context and len(rag_context.strip()) > 20:
                        response = UIFormatter.synthesize_rag_response(user_query, rag_context, self.llm_client)

                        return {
                            'response': response,
                            'chart_base64': None,
                            'charts_base64': None,
                            'agent': 'Data Query Agent (Rule-Based) + RAG',
                            'success': True,
                            'used_rag': True,
                            'classification': classification
                        }
                    else:
                        # RAG failed or no sufficient context - don't fall through to database queries
                        return {
                            'response': "This appears to be a conceptual/policy question, but I couldn't find relevant information in the uploaded documents. Please ensure you've uploaded the necessary policy documents, or try rephrasing your question.",
                            'chart_base64': None,
                            'charts_base64': None,
                            'agent': 'Data Query Agent (Rule-Based)',
                            'success': False,
                            'used_rag': False,
                            'classification': classification
                        }

                # Route to appropriate tool based on keywords
                if any(kw in query_lower for kw in ['find order', 'order id', 'lookup order', 'order details']):
                    response = self._find_order_by_id(user_query)
                elif any(kw in query_lower for kw in ['top products', 'best selling', 'most sold', 'top items']):
                    response = self._get_top_products(user_query)
                elif any(kw in query_lower for kw in ['top categories', 'category breakdown', 'best categories']):
                    response = self._get_top_categories(user_query)
                elif any(kw in query_lower for kw in ['list categories', 'unique categories', 'all categories', 'list unique', 'show all categories', 'list product categories']):
                    response = self._list_unique_categories(user_query)
                elif any(kw in query_lower for kw in ['orders in', 'orders from', 'orders between', 'between', 'date range', 'q1', 'q2', 'q3', 'q4', 'quarter']):
                    response = self._filter_orders_by_date_range(user_query)
                elif any(kw in query_lower for kw in ['customers in', 'customer state', 'state distribution', 'by state', 'state breakdown']):
                    response = self._get_customers_by_state(user_query)
                elif any(kw in query_lower for kw in ['order status', 'status breakdown', 'delivery status', 'status distribution', 'how many delayed', 'delayed orders']):
                    response = self._get_order_status_breakdown(user_query)
                elif any(kw in query_lower for kw in ['monthly trend', 'orders by month', 'monthly order', 'order trend', 'monthly pattern', 'monthly analysis', 'trends over time']):
                    response = self._get_monthly_order_trends(user_query)
                elif any(kw in query_lower for kw in ['customer history', 'orders for customer', 'customer orders', 'purchase history', 'customer purchase']):
                    response = self._get_customer_order_history(user_query)
                # Fall back to original simple queries
                elif 'order' in query_lower:
                    response = self._query_orders()
                elif 'customer' in query_lower:
                    response = self._query_customers()
                elif 'product' in query_lower:
                    response = self._query_products()
                else:
                    response = self._get_data_summary()

                # Capture generated charts
                chart_b64 = self._pending_chart
                charts_b64 = self._pending_charts

                # Append RAG context only if classification allows it (mixed queries)
                if used_rag and should_use_rag and rag_context and len(rag_context.strip()) > 20 and "no relevant" not in rag_context.lower():
                    # Only append if this is a mixed query (both RAG and database)
                    if classification and classification.get('query_type') == 'mixed':
                        # Use UIFormatter for better RAG context formatting
                        formatted_rag = UIFormatter.format_rag_context(rag_context)
                        response += f"\n\n{formatted_rag}"

                return {
                    'response': response,
                    'chart_base64': chart_b64,
                    'charts_base64': charts_b64,
                    'agent': 'Data Query Agent (Rule-Based)' + (' + RAG' if used_rag else ''),
                    'success': True,
                    'used_rag': used_rag,
                    'classification': classification
                }

        except Exception as e:
            logger.error(f"Data Query Agent error: {e}")
            return {
                'response': f"Error processing data query: {e}",
                'agent': 'Data Query Agent',
                'success': False,
                'used_rag': False
            }
