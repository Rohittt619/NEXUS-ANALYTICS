"""
NEXUS-ANALYTICS Churn Risk Probability Scorer & Behavioral Attribution Engine.

Extracts customer behavioral signals across transactions and marketing touchpoints,
trains a calibrated ensemble classifier, and outputs individual churn risk scores
with explainable risk factor attributions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from nexus.data.warehouse import DataWarehouse
from nexus.core.logger import get_logger

logger = get_logger("nexus.analytics.churn")


@dataclass
class ChurnScoringResult:
    """
    Container for customer churn risk predictions and feature attribution.
    """
    customer_risk_scores: pd.DataFrame
    feature_importances: Dict[str, float]
    risk_tier_summary: pd.DataFrame
    model_accuracy: float
    analysis_timestamp: str


class ChurnRiskScorer:
    """
    Predictive engine estimating customer churn probability and behavioral attribution.
    """

    def __init__(self, inactivity_threshold_days: int = 90) -> None:
        self.inactivity_threshold_days = inactivity_threshold_days
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_cols = [
            "recency_days",
            "total_orders",
            "total_spend",
            "avg_order_value",
            "campaign_engagement_rate",
            "initial_loyalty_score"
        ]

    def prepare_features(
        self,
        df_customers: pd.DataFrame,
        df_transactions: pd.DataFrame,
        df_campaigns: pd.DataFrame,
        reference_date: datetime | None = None
    ) -> pd.DataFrame:
        """
        Aggregate multi-table signals into a customer feature matrix.
        """
        if reference_date is None:
            reference_date = pd.to_datetime(df_transactions["timestamp"]).max() + pd.Timedelta(days=1)

        # 1. Transaction Features
        tx_agg = df_transactions.groupby("customer_id").agg(
            last_purchase=("timestamp", "max"),
            total_orders=("transaction_id", "count"),
            total_spend=("order_amount", "sum"),
            avg_order_value=("order_amount", "mean")
        ).reset_index()

        tx_agg["recency_days"] = (reference_date - pd.to_datetime(tx_agg["last_purchase"])).dt.days

        # 2. Campaign Engagement Features
        camp_agg = df_campaigns.groupby("customer_id").agg(
            total_touchpoints=("touchpoint_id", "count"),
            clicks_conversions=("interaction_type", lambda x: (x.isin(["Clicked", "Converted"])).sum())
        ).reset_index()

        camp_agg["campaign_engagement_rate"] = np.round(
            camp_agg["clicks_conversions"] / np.maximum(camp_agg["total_touchpoints"], 1), 3
        )

        # 3. Merge with Customer Dimension
        df_features = df_customers[["customer_id", "initial_loyalty_score", "is_opted_in_marketing"]].merge(
            tx_agg, on="customer_id", how="left"
        ).merge(
            camp_agg[["customer_id", "campaign_engagement_rate"]], on="customer_id", how="left"
        )

        # Fill customers with zero transactions
        df_features["recency_days"] = df_features["recency_days"].fillna(365)
        df_features["total_orders"] = df_features["total_orders"].fillna(0)
        df_features["total_spend"] = df_features["total_spend"].fillna(0.0)
        df_features["avg_order_value"] = df_features["avg_order_value"].fillna(0.0)
        df_features["campaign_engagement_rate"] = df_features["campaign_engagement_rate"].fillna(0.0)

        # Define churn ground truth (Inactivity > threshold days)
        df_features["is_churned"] = (df_features["recency_days"] >= self.inactivity_threshold_days).astype(int)

        return df_features

    def score_customers(
        self,
        df_customers: pd.DataFrame,
        df_transactions: pd.DataFrame,
        df_campaigns: pd.DataFrame,
        reference_date: datetime | None = None
    ) -> ChurnScoringResult:
        """
        Train risk model and output customer churn probabilities with behavioral attribution.
        """
        logger.info("Extracting customer behavioral signals for churn scoring...")
        df_feat = self.prepare_features(df_customers, df_transactions, df_campaigns, reference_date)

        X = df_feat[self.feature_cols]
        y = df_feat["is_churned"]

        # Train model
        self.model.fit(X, y)
        probs = self.model.predict_proba(X)[:, 1]
        accuracy = round(float(self.model.score(X, y)), 3)

        df_feat["churn_probability"] = np.round(probs, 3)

        # Assign Risk Tiers
        conditions = [
            df_feat["churn_probability"] < 0.25,
            df_feat["churn_probability"] < 0.55,
            df_feat["churn_probability"] < 0.80,
            df_feat["churn_probability"] >= 0.80
        ]
        choices = ["Low Risk", "Moderate Risk", "High Risk", "Critical Risk"]
        df_feat["risk_tier"] = np.select(conditions, choices, default="Moderate Risk")

        # Behavioral Risk Attribution
        attributions = []
        for _, row in df_feat.iterrows():
            if row["recency_days"] >= 90:
                attributions.append("Severe Inactivity (90+ Days)")
            elif row["total_orders"] <= 1:
                attributions.append("Single-Order Vulnerability")
            elif row["campaign_engagement_rate"] == 0:
                attributions.append("Zero Marketing Engagement")
            elif row["avg_order_value"] < 30.0:
                attributions.append("Low Basket Value")
            else:
                attributions.append("Normal Healthy Trajectory")

        df_feat["primary_risk_driver"] = attributions

        # Feature Importance Map
        importances = {
            col: round(float(imp), 3)
            for col, imp in zip(self.feature_cols, self.model.feature_importances_)
        }
        importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

        # Risk Tier Summary
        summary = df_feat.groupby("risk_tier").agg(
            customer_count=("customer_id", "count"),
            avg_churn_prob=("churn_probability", "mean"),
            total_spend_at_risk=("total_spend", "sum")
        ).reset_index()

        total_c = len(df_feat)
        summary["customer_share_pct"] = np.round((summary["customer_count"] / total_c) * 100.0, 2)
        summary["avg_churn_prob"] = np.round(summary["avg_churn_prob"], 3)
        summary["total_spend_at_risk"] = np.round(summary["total_spend_at_risk"], 2)

        return ChurnScoringResult(
            customer_risk_scores=df_feat[[
                "customer_id", "recency_days", "total_orders", "total_spend",
                "campaign_engagement_rate", "churn_probability", "risk_tier", "primary_risk_driver"
            ]],
            feature_importances=importances,
            risk_tier_summary=summary,
            model_accuracy=accuracy,
            analysis_timestamp=datetime.now().isoformat()
        )

    def score_from_warehouse(self, warehouse: DataWarehouse) -> ChurnScoringResult:
        """
        Pull all datasets from DuckDB warehouse and execute churn scoring.
        """
        c = warehouse.query("SELECT * FROM dim_customers")
        t = warehouse.query("SELECT * FROM fact_transactions")
        p = warehouse.query("SELECT * FROM fact_campaign_touchpoints")
        return self.score_customers(c, t, p)
