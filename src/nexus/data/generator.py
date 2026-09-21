"""
NEXUS-ANALYTICS Synthetic Enterprise Customer Event Generator.

Generates deterministic, high-throughput synthetic customer profiles,
transaction event logs, and multi-channel campaign interactions.

Privacy Guarantee:
    All generated data is strictly synthetic and generated locally via mathematical distributions.
    Zero external APIs or private personal data is used.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


class SyntheticCustomerGenerator:
    """
    Generates synthetic enterprise customer records, transaction histories,
    and marketing campaign engagement touchpoints.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

        self.channels = ["Organic Search", "Google Ads", "Meta Ads", "Email Referral", "Direct"]
        self.regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
        self.categories = ["Electronics", "Apparel", "Home & Living", "Beauty", "Grocery"]
        self.payment_methods = ["Credit Card", "UPI", "PayPal", "NetBanking", "Debit Card"]
        self.campaign_names = [
            "Summer_Loyalty_Boost",
            "VIP_Retention_Winback",
            "Fall_Flash_Sale",
            "Black_Friday_Preview",
            "Re_Engagement_Q3"
        ]

    def generate_dataset(
        self,
        num_customers: int = 500,
        num_transactions: int = 3000,
        num_campaign_touchpoints: int = 2000,
        end_date: datetime | None = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate complete relational dataset conforming to the star-schema.

        Returns:
            Tuple of (df_customers, df_transactions, df_campaigns)
        """
        if end_date is None:
            end_date = datetime(2026, 9, 15, 12, 0, 0)
        start_date = end_date - timedelta(days=365)

        # 1. Generate Customers (Dimension Table)
        customer_ids = [f"CUST_{i:05d}" for i in range(1, num_customers + 1)]
        signup_dates = [
            start_date + timedelta(days=random.randint(0, 300))
            for _ in range(num_customers)
        ]
        
        df_customers = pd.DataFrame({
            "customer_id": customer_ids,
            "signup_date": signup_dates,
            "acquisition_channel": [random.choice(self.channels) for _ in range(num_customers)],
            "region": [random.choice(self.regions) for _ in range(num_customers)],
            "initial_loyalty_score": np.random.randint(10, 100, size=num_customers),
            "is_opted_in_marketing": np.random.choice([True, False], size=num_customers, p=[0.75, 0.25])
        })

        # 2. Generate Transactions (Fact Table)
        # Create Pareto distribution: 20% of customers generate 80% of volume
        weights = np.random.pareto(a=1.5, size=num_customers)
        weights /= weights.sum()

        chosen_custs = np.random.choice(customer_ids, size=num_transactions, p=weights)
        
        tx_dates = []
        for cid in chosen_custs:
            cust_signup = df_customers.loc[df_customers["customer_id"] == cid, "signup_date"].values[0]
            cust_signup_dt = pd.to_datetime(cust_signup).to_pydatetime()
            max_days = max(1, (end_date - cust_signup_dt).days)
            tx_dt = cust_signup_dt + timedelta(days=random.randint(0, max_days), hours=random.randint(0, 23))
            tx_dates.append(tx_dt)

        order_amounts = np.round(np.random.gamma(shape=2.5, scale=40.0, size=num_transactions) + 15.0, 2)
        discounts = np.round(np.random.choice([0.0, 5.0, 10.0, 15.0, 25.0], size=num_transactions, p=[0.4, 0.2, 0.2, 0.1, 0.1]), 2)

        df_transactions = pd.DataFrame({
            "transaction_id": [f"TX_{i:07d}" for i in range(1, num_transactions + 1)],
            "customer_id": chosen_custs,
            "timestamp": tx_dates,
            "order_amount": order_amounts,
            "discount_applied": discounts,
            "category": [random.choice(self.categories) for _ in range(num_transactions)],
            "payment_method": [random.choice(self.payment_methods) for _ in range(num_transactions)],
            "items_count": np.random.randint(1, 8, size=num_transactions)
        }).sort_values("timestamp").reset_index(drop=True)

        # 3. Generate Campaign Touchpoints (Fact Table)
        touchpoint_dates = [
            start_date + timedelta(days=random.randint(0, 360), hours=random.randint(0, 23))
            for _ in range(num_campaign_touchpoints)
        ]
        touchpoint_custs = np.random.choice(customer_ids, size=num_campaign_touchpoints)
        interaction_types = np.random.choice(
            ["Sent", "Delivered", "Opened", "Clicked", "Converted"],
            size=num_campaign_touchpoints,
            p=[0.15, 0.25, 0.30, 0.20, 0.10]
        )
        costs = np.round(np.random.uniform(0.02, 0.50, size=num_campaign_touchpoints), 3)

        df_campaigns = pd.DataFrame({
            "touchpoint_id": [f"TP_{i:06d}" for i in range(1, num_campaign_touchpoints + 1)],
            "customer_id": touchpoint_custs,
            "campaign_name": [random.choice(self.campaign_names) for _ in range(num_campaign_touchpoints)],
            "channel": [random.choice(["Email", "SMS", "Push Notification", "In-App Banner"]) for _ in range(num_campaign_touchpoints)],
            "interaction_type": interaction_types,
            "cost_usd": costs,
            "timestamp": touchpoint_dates
        }).sort_values("timestamp").reset_index(drop=True)

        return df_customers, df_transactions, df_campaigns
