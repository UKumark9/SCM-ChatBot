"""
Matplotlib chart generation for the SCM Chatbot Gradio UI.

Single Responsibility: build the dark-themed analysis charts (delay,
revenue, forecast) shown in the chat. Extracted from ui.py so chart
rendering can change independently of event-wiring/layout code.
"""

import logging
import os
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

logger = logging.getLogger(__name__)


def _style_dark_axes(ax, title, xlabel=None, ylabel=None):
    """Apply the dark-theme axis styling shared by every chart in this module"""
    ax.set_facecolor("#1e293b")
    if xlabel:
        ax.set_xlabel(xlabel, color="#94a3b8", fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color="#94a3b8", fontsize=10)
    ax.set_title(title, color="#f1f5f9", fontweight="bold", fontsize=13, pad=12)
    ax.tick_params(colors="#94a3b8")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#334155")
    ax.spines["bottom"].set_color("#334155")


def _save_chart(fig, filename):
    """Save a chart to the temp dir with the shared dark background, then close it"""
    path = os.path.join(tempfile.gettempdir(), filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="#1e293b")
    plt.close(fig)
    return path


def generate_delay_charts(app):
    """Generate matplotlib bar charts for delay analysis, styled for dark theme."""
    charts = []
    try:
        result = app.analytics.analyze_delivery_delays()

        # ── Chart 1: On-Time vs Delayed ──
        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor("#1e293b")

        on_time_pct = 100 - result["delay_rate_percentage"]
        delay_pct = result["delay_rate_percentage"]
        categories = ["On-Time", "Delayed"]
        values = [on_time_pct, delay_pct]
        colors = ["#10b981", "#ef4444"]

        bars = ax.bar(categories, values, color=colors, width=0.5, edgecolor="none")
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{val:.1f}%",
                ha="center",
                va="bottom",
                color="#f1f5f9",
                fontweight="bold",
                fontsize=13,
            )

        _style_dark_axes(ax, "Delivery Performance Overview", ylabel="Percentage")
        ax.set_ylim(0, max(values) * 1.25)
        charts.append(_save_chart(fig, "delay_overview.png"))

        # ── Chart 2: Top 10 States by Delay Rate ──
        delays_by_state = result.get("delays_by_state", {})
        if delays_by_state:
            sorted_states = sorted(
                [(state, rate * 100) for state, rate in delays_by_state.items()],
                key=lambda x: x[1],
                reverse=True,
            )[:10]

            fig, ax = plt.subplots(figsize=(7, 4.5))
            fig.patch.set_facecolor("#1e293b")

            states = [s[0] for s in reversed(sorted_states)]
            rates = [s[1] for s in reversed(sorted_states)]
            bar_colors = [
                "#ef4444" if r > 10 else "#f59e0b" if r > 5 else "#10b981"
                for r in rates
            ]

            bars = ax.barh(
                states, rates, color=bar_colors, height=0.6, edgecolor="none"
            )
            for bar, val in zip(bars, rates):
                ax.text(
                    bar.get_width() + 0.3,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%",
                    va="center",
                    color="#f1f5f9",
                    fontsize=10,
                )

            _style_dark_axes(ax, "Top 10 States by Delay Rate", xlabel="Delay Rate (%)")
            ax.set_xlim(0, max(rates) * 1.2)
            charts.append(_save_chart(fig, "delay_states.png"))

        # ── Chart 3: Delay Severity Distribution ──
        orders = app.orders
        delayed = orders[orders["is_delayed"]]
        on_time_count = int(orders["is_on_time"].sum())
        minor = int(((delayed["delay_days"] > 0) & (delayed["delay_days"] <= 2)).sum())
        major = int(((delayed["delay_days"] > 2) & (delayed["delay_days"] <= 5)).sum())
        critical = int((delayed["delay_days"] > 5).sum())

        fig, ax = plt.subplots(figsize=(6, 3.5))
        fig.patch.set_facecolor("#1e293b")

        cats = [
            "On-Time",
            "Minor\n(1-2 days)",
            "Major\n(3-5 days)",
            "Critical\n(>5 days)",
        ]
        vals = [on_time_count, minor, major, critical]
        cols = ["#10b981", "#f59e0b", "#f97316", "#ef4444"]

        bars = ax.bar(cats, vals, color=cols, width=0.6, edgecolor="none")
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(vals) * 0.02,
                f"{val:,}",
                ha="center",
                va="bottom",
                color="#f1f5f9",
                fontweight="bold",
                fontsize=11,
            )

        _style_dark_axes(ax, "Delay Severity Distribution", ylabel="Number of Orders")
        charts.append(_save_chart(fig, "delay_severity.png"))

    except Exception as e:
        logger.error(f"Chart generation error: {e}")
    return charts


def generate_revenue_charts(app):
    """Generate matplotlib charts for revenue analysis, styled for dark theme."""
    charts = []
    try:
        result = app.analytics.analyze_revenue_trends()

        # ── Chart 1: Monthly Revenue Trend ──
        monthly = result.get("monthly_revenue", {})
        if monthly:
            months = list(monthly.keys())
            values = list(monthly.values())

            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor("#1e293b")
            ax.plot(
                range(len(months)),
                values,
                color="#6366f1",
                marker="o",
                markersize=4,
                linewidth=2,
            )
            ax.fill_between(range(len(months)), values, color="#6366f1", alpha=0.1)

            _style_dark_axes(ax, "Monthly Revenue Trend", ylabel="Revenue ($)")
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, rotation=45, ha="right", fontsize=8)
            charts.append(_save_chart(fig, "revenue_trend.png"))

        # ── Chart 2: Top 10 States by Revenue ──
        by_state = result.get("revenue_by_state", {})
        if by_state:
            sorted_states = sorted(by_state.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]
            states = [s[0] for s in reversed(sorted_states)]
            values = [s[1] for s in reversed(sorted_states)]

            fig, ax = plt.subplots(figsize=(7, 4.5))
            fig.patch.set_facecolor("#1e293b")
            bars = ax.barh(
                states, values, color="#6366f1", height=0.6, edgecolor="none"
            )
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_width() + max(values) * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    f"${val:,.0f}",
                    va="center",
                    color="#f1f5f9",
                    fontsize=9,
                )

            _style_dark_axes(ax, "Top 10 States by Revenue", xlabel="Revenue ($)")
            ax.set_xlim(0, max(values) * 1.2)
            charts.append(_save_chart(fig, "revenue_states.png"))

    except Exception as e:
        logger.error(f"Revenue chart generation error: {e}")
    return charts


def generate_forecast_charts(app, periods=30):
    """Generate a historical + forecast demand chart, styled for dark theme."""
    charts = []
    try:
        result = app.analytics.forecast_demand(periods=periods)
        forecast = result.get("forecast", {})
        if not forecast:
            return charts

        import pandas as pd

        # Recent historical daily order volume, mirroring the groupby forecast_demand() does internally
        sales = app.order_items.merge(
            app.orders[["order_id", "order_purchase_timestamp"]], on="order_id"
        )
        sales["date"] = pd.to_datetime(sales["order_purchase_timestamp"]).dt.date
        daily = sales.groupby("date").size().sort_index()
        recent_history = daily.tail(60)

        forecast_dates = [pd.Timestamp(d).date() for d in forecast.keys()]
        forecast_values = list(forecast.values())

        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.patch.set_facecolor("#1e293b")
        ax.plot(
            recent_history.index,
            recent_history.values,
            color="#10b981",
            linewidth=2,
            label="Historical",
        )
        ax.plot(
            forecast_dates,
            forecast_values,
            color="#f59e0b",
            linewidth=2,
            linestyle="--",
            label="Forecast",
        )
        ax.axvline(
            recent_history.index[-1], color="#94a3b8", linestyle=":", linewidth=1
        )

        _style_dark_axes(ax, f"Demand Forecast ({periods} Days)", ylabel="Orders")
        ax.legend(
            facecolor="#1e293b", edgecolor="#334155", labelcolor="#f1f5f9", fontsize=9
        )
        fig.autofmt_xdate()
        charts.append(_save_chart(fig, "demand_forecast.png"))

    except Exception as e:
        logger.error(f"Forecast chart generation error: {e}")
    return charts
