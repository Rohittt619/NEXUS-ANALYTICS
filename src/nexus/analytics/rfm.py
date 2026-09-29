"""
NEXUS-ANALYTICS Algorithmic RFM Customer Segmentation Engine.

Calculates Recency, Frequency, and Monetary quintile scores (1 to 5)
and maps customers into standard business segmentation tiers with marketing action strategies.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

from nexus.data.warehouse import DataWarehouse
from nexus.core.logger import get_logger

logger = get_logger("nexus.analytics.rfm")


@dataclass
class RFMResult:
    """
    Container for RFM analysis outputs.
    """
    customer_scores: pd.DataFrame
    segment_summary: pd.DataFrame
    analysis_timestamp: str
    total_customers_analyzed: int


class RFMSegmenter:
    """
    Computes algorithmic RFM scores and segments customers.
    """

    def __init__(self, warehouse: DataWarehouse | None = None) -> None:
        self.warehouse = warehouse

    @staticmethod
    def _assign_segment(row: pd.Series) -> Tuple[str, str]:
        """
        Map R and F/M score combinations to industry-standard customer tiers.
        Returns: (segment_name, recommended_strategy)
        """
        r = row["r_score"]
        f = row["f_score"]
        m = row["m_score"]

        if r >= 4 and f >= 4 and m >= 4:
            return (
                "Champions",
                "Reward loyalty, invite to exclusive VIP previews, encourage brand advocacy."
            )
        elif r >= 3 and f >= 3:
            return (
                "Loyal Customers",
                "Upsell higher-value products, offer loyalty bonus points, request reviews."
            )
        elif r >= 4 and f <= 2:
            return (
                "Potential Loyalists",
                "Offer membership programs, recommend complementary products to trigger 2nd purchase."
            )
        elif r >= 3 and f == 1:
            return (
                "Promising New",
                "Send onboarding sequences, educational content, and timely first-reorder discount."
            )
        elif r == 3 and f == 2:
            return (
                "Needs Attention",
                "Limited-time reactivation offers, personalized recommendations based on past category."
            )
        elif r <= 2 and f >= 3 and m >= 3:
            return (
                "At Risk (High Value)",
                "Send urgent win-back campaigns, personalized outreach, high-incentive renewal vouchers."
            )
        elif r == 1 and f >= 4:
            return (
                "Can't Lose Them",
                "Direct VIP account manager contact, aggressive discount, survey why they stopped buying."
            )
        elif r <= 2 and f <= 2 and m >= 3:
            return (
                "About to Sleep",
                "Share popular trending products, low-friction re-engagement emails."
            )
        elif r <= 2 and f <= 2:
            return (
                "Hibernating",
                "Low-cost email drip campaigns with deep discounts, reduce high-cost paid ads."
            )
        else:
            return (
                "Lost Customers",
                "Ignore for expensive outbound ads, test one final exit survey / reactivation coupon."
            )

    def calculate_from_transactions(
        self,
        df_transactions: pd.DataFrame,
        reference_date: datetime | None = None
    ) -> RFMResult:
        """
        Compute RFM scores from raw transactions DataFrame.
        """
        if reference_date is None:
            reference_date = pd.to_datetime(df_transactions["timestamp"]).max() + pd.Timedelta(days=1)

        logger.info(f"Computing RFM metrics for {len(df_transactions)} transactions (Reference: {reference_date})...")

        # 1. Aggregate R, F, M per customer
        df_rfm = df_transactions.groupby("customer_id").agg(
            recency=("timestamp", lambda x: (reference_date - pd.to_datetime(x).max()).days),
            frequency=("transaction_id", "count"),
            monetary=("order_amount", "sum")
        ).reset_index()

        # 2. Compute 1-5 quintiles using rank-based quantiles (prevents duplicate bin errors)
        # Recency: Lower days = Better (higher score 5)
        df_rfm["r_score"] = pd.qcut(
            df_rfm["recency"].rank(method="first", ascending=False),
            q=5,
            labels=[1, 2, 3, 4, 5]
        ).astype(int)

        # Frequency: Higher count = Better (higher score 5)
        df_rfm["f_score"] = pd.qcut(
            df_rfm["frequency"].rank(method="first", ascending=True),
            q=5,
            labels=[1, 2, 3, 4, 5]
        ).astype(int)

        # Monetary: Higher spend = Better (higher score 5)
        df_rfm["m_score"] = pd.qcut(
            df_rfm["monetary"].rank(method="first", ascending=True),
            q=5,
            labels=[1, 2, 3, 4, 5]
        ).astype(int)

        # 3. Composite RFM Score
        df_rfm["rfm_composite"] = (
            df_rfm["r_score"].astype(str) +
            df_rfm["f_score"].astype(str) +
            df_rfm["m_score"].astype(str)
        )

        # 4. Map to Actionable Business Segments
        applied = df_rfm.apply(self._assign_segment, axis=1)
        df_rfm["segment"] = [a[0] for a in applied]
        df_rfm["action_strategy"] = [a[1] for a in applied]

        # 5. Segment Summary
        summary = df_rfm.groupby("segment").agg(
            customer_count=("customer_id", "count"),
            total_revenue=("monetary", "sum"),
            avg_monetary=("monetary", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_recency_days=("recency", "mean")
        ).reset_index()

        total_rev = summary["total_revenue"].sum()
        total_cust = summary["customer_count"].sum()

        summary["revenue_share_pct"] = np.round((summary["total_revenue"] / total_rev) * 100.0, 2)
        summary["customer_share_pct"] = np.round((summary["customer_count"] / total_cust) * 100.0, 2)
        summary["avg_monetary"] = np.round(summary["avg_monetary"], 2)
        summary["avg_frequency"] = np.round(summary["avg_frequency"], 1)
        summary["avg_recency_days"] = np.round(summary["avg_recency_days"], 1)

        summary = summary.sort_values("total_revenue", ascending=False).reset_index(drop=True)

        return RFMResult(
            customer_scores=df_rfm,
            segment_summary=summary,
            analysis_timestamp=datetime.now().isoformat(),
            total_customers_analyzed=len(df_rfm)
        )

    def calculate_from_warehouse(self) -> RFMResult:
        """
        Load transactions from the DuckDB warehouse and compute RFM metrics.
        """
        if self.warehouse is None:
            raise ValueError("DataWarehouse instance must be provided to use calculate_from_warehouse()")
        df_tx = self.warehouse.query("SELECT * FROM fact_transactions")
        return self.calculate_from_transactions(df_tx)
