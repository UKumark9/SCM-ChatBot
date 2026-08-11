"""
Chart rendering for the forecasting engine.

Single Responsibility: turn forecast/historical series into styled PNG charts
(base64-encoded). ForecastingEngine owns data prep and SARIMA fitting; this
module owns matplotlib rendering only, so the two can change independently.
"""

import base64
import io
from typing import Any, Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


class ForecastChartRenderer:
    """Renders SARIMA forecast charts using the app's dark theme palette."""

    # Chart palette — matches app dark theme
    CHART_BG = "#1e293b"
    CHART_TEXT = "#f1f5f9"
    CHART_GRID = "#334155"
    CHART_PRIMARY = "#6366f1"
    CHART_ACCENT = "#06b6d4"
    CHART_FORECAST = "#10b981"

    CATEGORY_COLORS = [
        "#6366f1",
        "#06b6d4",
        "#10b981",
        "#f59e0b",
        "#ef4444",
        "#8b5cf6",
        "#ec4899",
        "#14b8a6",
        "#f97316",
        "#84cc16",
    ]

    def generate_forecast_bar_chart(
        self,
        forecast_df,
        title: str,
        y_label: str,
        color: str = None,
    ) -> str:
        """Bar chart of weekly forecast values — returns base64-encoded PNG."""
        if color is None:
            color = self.CHART_FORECAST

        fig, ax = plt.subplots(figsize=(10, 5), facecolor=self.CHART_BG)
        ax.set_facecolor(self.CHART_BG)

        weeks = [d.strftime("%b %d") for d in forecast_df.index]
        values = forecast_df["forecast"].values

        bars = ax.bar(
            weeks,
            values,
            color=color,
            width=0.55,
            edgecolor="none",
            alpha=0.88,
        )

        # Value labels on top of each bar
        v_max = max(values) if len(values) else 1
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + v_max * 0.02,
                f"{val:,.0f}",
                ha="center",
                va="bottom",
                color=self.CHART_TEXT,
                fontweight="bold",
                fontsize=9,
            )

        ax.set_title(
            title, color=self.CHART_TEXT, fontsize=13, fontweight="bold", pad=16
        )
        ax.set_ylabel(y_label, color=self.CHART_TEXT, fontsize=11)
        ax.tick_params(colors=self.CHART_TEXT, labelsize=8)
        ax.grid(True, alpha=0.15, color=self.CHART_GRID, axis="y")
        ax.set_ylim(0, v_max * 1.18)

        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color(self.CHART_GRID)

        fig.autofmt_xdate(rotation=30)
        plt.tight_layout()

        return self._save_to_base64(fig)

    def generate_pie_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str,
        colors: List[str] = None,
    ) -> str:
        """Pie chart with dark theme styling — returns base64-encoded PNG."""
        fig, ax = plt.subplots(figsize=(6, 6), facecolor=self.CHART_BG)
        ax.set_facecolor(self.CHART_BG)

        if colors is None:
            colors = self.CATEGORY_COLORS

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors[: len(values)],
            autopct="%1.1f%%",
            startangle=90,
            pctdistance=0.78,
            textprops={"color": self.CHART_TEXT, "fontsize": 10},
            wedgeprops={"edgecolor": self.CHART_BG, "linewidth": 1.5},
        )

        for autotext in autotexts:
            autotext.set_fontweight("bold")
            autotext.set_fontsize(11)

        ax.set_title(
            title, color=self.CHART_TEXT, fontsize=13, fontweight="bold", pad=18
        )

        plt.tight_layout()

        return self._save_to_base64(fig)

    def generate_category_comparison_bar(
        self,
        category_results: Dict[str, Any],
        periods: int,
    ) -> str:
        """Horizontal bar chart comparing avg forecast across categories."""
        colors = self.CATEGORY_COLORS

        cats = []
        avgs = []
        cols = []
        for i, (cat_name, res) in enumerate(category_results.items()):
            cats.append(cat_name.replace("_", " ").title()[:24])
            avgs.append(res["avg_forecast"])
            cols.append(colors[i % len(colors)])

        # Reverse for top-down display in horizontal bar
        cats.reverse()
        avgs.reverse()
        cols.reverse()

        fig, ax = plt.subplots(
            figsize=(10, max(4, len(cats) * 0.9)), facecolor=self.CHART_BG
        )
        ax.set_facecolor(self.CHART_BG)

        bars = ax.barh(cats, avgs, color=cols, height=0.55, edgecolor="none")

        v_max = max(avgs) if avgs else 1
        for bar, val in zip(bars, avgs):
            ax.text(
                bar.get_width() + v_max * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}",
                va="center",
                color=self.CHART_TEXT,
                fontweight="bold",
                fontsize=10,
            )

        ax.set_xlabel("Avg Forecast (orders/week)", color=self.CHART_TEXT, fontsize=11)
        ax.set_title(
            f"Category Forecast Comparison — Next {periods} Days",
            color=self.CHART_TEXT,
            fontsize=13,
            fontweight="bold",
            pad=16,
        )
        ax.tick_params(colors=self.CHART_TEXT, labelsize=9)
        ax.set_xlim(0, v_max * 1.2)

        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color(self.CHART_GRID)

        ax.grid(True, alpha=0.15, color=self.CHART_GRID, axis="x")
        plt.tight_layout()

        return self._save_to_base64(fig)

    def generate_multi_category_chart(
        self, category_results: Dict[str, Any], periods: int
    ) -> str:
        """Multi-line forecast chart — one coloured line per category."""
        colors = self.CATEGORY_COLORS

        fig, ax = plt.subplots(figsize=(12, 6), facecolor=self.CHART_BG)
        ax.set_facecolor(self.CHART_BG)

        forecast_start = None

        for i, (cat_name, res) in enumerate(category_results.items()):
            color = colors[i % len(colors)]
            label = cat_name.replace("_", " ").title()[:24]

            # Historical line (thinner, slightly transparent)
            ax.plot(
                res["series"].index,
                res["series"].values,
                color=color,
                linewidth=1.2,
                alpha=0.7,
            )
            # Forecast line (dashed, labelled)
            ax.plot(
                res["forecast_df"].index,
                res["forecast_df"]["forecast"],
                color=color,
                linewidth=2.0,
                linestyle="--",
                label=label,
            )
            # Confidence band (very subtle)
            ax.fill_between(
                res["forecast_df"].index,
                res["forecast_df"]["lower"],
                res["forecast_df"]["upper"],
                alpha=0.07,
                color=color,
            )
            if forecast_start is None:
                forecast_start = res["series"].index[-1]

        if forecast_start is not None:
            ax.axvline(
                x=forecast_start,
                color="#94a3b8",
                linestyle=":",
                alpha=0.6,
                linewidth=1,
            )

        n = len(category_results)
        ax.set_title(
            f"Category Demand Forecast — Next {periods} Days  (Top {n} Categories)",
            color=self.CHART_TEXT,
            fontsize=13,
            fontweight="bold",
            pad=18,
        )
        ax.text(
            0.5,
            1.02,
            "SARIMA  |  Weekly Aggregation  |  Dashed = Forecast  |  Shaded = 95% CI",
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            color="#94a3b8",
            fontsize=9,
        )
        ax.set_xlabel("Date", color=self.CHART_TEXT, fontsize=11)
        ax.set_ylabel("Weekly Orders", color=self.CHART_TEXT, fontsize=11)
        ax.tick_params(colors=self.CHART_TEXT, labelsize=9)
        ax.grid(True, alpha=0.15, color=self.CHART_GRID)

        legend = ax.legend(
            facecolor=self.CHART_BG,
            edgecolor=self.CHART_GRID,
            labelcolor=self.CHART_TEXT,
            fontsize=8.5,
            loc="upper left",
            framealpha=0.9,
            ncol=2 if n > 3 else 1,
        )
        legend.get_frame().set_linewidth(0.5)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        fig.autofmt_xdate(rotation=30)

        for spine in ax.spines.values():
            spine.set_color(self.CHART_GRID)

        plt.tight_layout()

        return self._save_to_base64(fig)

    def generate_chart(
        self,
        historical,
        forecast,
        title: str,
        subtitle: str,
        y_label: str = "Weekly Orders",
    ) -> str:
        """Styled forecast chart — returns base64-encoded PNG."""
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=self.CHART_BG)
        ax.set_facecolor(self.CHART_BG)

        ax.plot(
            historical.index,
            historical.values,
            color=self.CHART_PRIMARY,
            linewidth=1.5,
            alpha=0.9,
            label="Historical",
        )

        ax.plot(
            forecast.index,
            forecast["forecast"],
            color=self.CHART_FORECAST,
            linewidth=2,
            linestyle="--",
            label="SARIMA Forecast",
        )

        ax.fill_between(
            forecast.index,
            forecast["lower"],
            forecast["upper"],
            alpha=0.15,
            color=self.CHART_FORECAST,
            label="95% Confidence Interval",
        )

        ax.axvline(
            x=historical.index[-1],
            color=self.CHART_ACCENT,
            linestyle=":",
            alpha=0.7,
            linewidth=1,
            label="Forecast Start",
        )

        ax.set_title(
            title, color=self.CHART_TEXT, fontsize=14, fontweight="bold", pad=20
        )
        ax.text(
            0.5,
            1.02,
            subtitle,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            color="#94a3b8",
            fontsize=9,
        )
        ax.set_xlabel("Date", color=self.CHART_TEXT, fontsize=11)
        ax.set_ylabel(y_label, color=self.CHART_TEXT, fontsize=11)
        ax.tick_params(colors=self.CHART_TEXT, labelsize=9)
        ax.grid(True, alpha=0.2, color=self.CHART_GRID)

        legend = ax.legend(
            facecolor=self.CHART_BG,
            edgecolor=self.CHART_GRID,
            labelcolor=self.CHART_TEXT,
            fontsize=9,
            loc="upper left",
            framealpha=0.9,
        )
        legend.get_frame().set_linewidth(0.5)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        fig.autofmt_xdate(rotation=30)

        for spine in ax.spines.values():
            spine.set_color(self.CHART_GRID)

        plt.tight_layout()

        return self._save_to_base64(fig)

    def _save_to_base64(self, fig) -> str:
        buf = io.BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=120,
            bbox_inches="tight",
            facecolor=self.CHART_BG,
            edgecolor="none",
        )
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return img_b64
