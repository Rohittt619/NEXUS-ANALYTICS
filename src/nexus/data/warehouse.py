"""
NEXUS-ANALYTICS Embedded DuckDB Star-Schema Data Warehouse.

Provides columnar OLAP storage for enterprise analytical queries,
cohort matrices, customer lifetime value modeling, and campaign ROI tracking.
"""
from __future__ import annotations

from typing import Any, Dict
import duckdb
import pandas as pd
from nexus.core.logger import get_logger

logger = get_logger("nexus.warehouse")


class DataWarehouse:
    """
    Manages an embedded DuckDB columnar database implementing a Star-Schema.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = duckdb.connect(database=self.db_path)
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        """Create star-schema dimension and fact tables."""
        logger.info(f"Initializing DuckDB star-schema warehouse at '{self.db_path}'...")
        
        # 1. Dimension: Customers
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_customers (
                customer_id VARCHAR PRIMARY KEY,
                signup_date TIMESTAMP,
                acquisition_channel VARCHAR,
                region VARCHAR,
                initial_loyalty_score INTEGER,
                is_opted_in_marketing BOOLEAN
            );
        """)

        # 2. Dimension: Loyalty Tiers
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_loyalty_tiers (
                tier_id VARCHAR PRIMARY KEY,
                tier_name VARCHAR,
                min_spend DECIMAL(10, 2),
                cashback_percent DECIMAL(5, 2),
                priority_support BOOLEAN
            );
        """)

        # Populate Loyalty Tiers
        self.conn.execute("""
            INSERT OR REPLACE INTO dim_loyalty_tiers VALUES
            ('TIER_BRONZE', 'Bronze', 0.0, 1.0, FALSE),
            ('TIER_SILVER', 'Silver', 250.0, 2.5, FALSE),
            ('TIER_GOLD', 'Gold', 750.0, 5.0, TRUE),
            ('TIER_PLATINUM', 'Platinum (VIP)', 1500.0, 10.0, TRUE);
        """)

        # 3. Fact: Transactions
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_transactions (
                transaction_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR,
                timestamp TIMESTAMP,
                order_amount DECIMAL(10, 2),
                discount_applied DECIMAL(10, 2),
                category VARCHAR,
                payment_method VARCHAR,
                items_count INTEGER
            );
        """)

        # 4. Fact: Campaign Touchpoints
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_campaign_touchpoints (
                touchpoint_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR,
                campaign_name VARCHAR,
                channel VARCHAR,
                interaction_type VARCHAR,
                cost_usd DECIMAL(10, 3),
                timestamp TIMESTAMP
            );
        """)

    def load_dataframes(
        self,
        df_customers: pd.DataFrame,
        df_transactions: pd.DataFrame,
        df_campaigns: pd.DataFrame
    ) -> None:
        """
        Load pandas DataFrames directly into DuckDB star-schema tables.
        DuckDB reads directly from local memory without serialization overhead.
        """
        logger.info(f"Loading {len(df_customers)} customers into dim_customers...")
        self.conn.register("tmp_customers", df_customers)
        self.conn.execute("INSERT OR REPLACE INTO dim_customers SELECT * FROM tmp_customers")
        self.conn.unregister("tmp_customers")

        logger.info(f"Loading {len(df_transactions)} transactions into fact_transactions...")
        self.conn.register("tmp_transactions", df_transactions)
        self.conn.execute("INSERT OR REPLACE INTO fact_transactions SELECT * FROM tmp_transactions")
        self.conn.unregister("tmp_transactions")

        logger.info(f"Loading {len(df_campaigns)} touchpoints into fact_campaign_touchpoints...")
        self.conn.register("tmp_campaigns", df_campaigns)
        self.conn.execute("INSERT OR REPLACE INTO fact_campaign_touchpoints SELECT * FROM tmp_campaigns")
        self.conn.unregister("tmp_campaigns")

    def query(self, sql: str, params: list | None = None) -> pd.DataFrame:
        """
        Execute an analytical SQL query against the warehouse and return a Pandas DataFrame.
        """
        if params:
            return self.conn.execute(sql, params).df()
        return self.conn.execute(sql).df()

    def get_kpis(self) -> Dict[str, Any]:
        """
        Compute high-level executive KPIs across transactions, customers, and campaigns.
        """
        res = self.conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM dim_customers) AS total_customers,
                (SELECT COUNT(*) FROM fact_transactions) AS total_transactions,
                (SELECT COALESCE(SUM(order_amount), 0.0) FROM fact_transactions) AS total_gross_revenue,
                (SELECT COALESCE(AVG(order_amount), 0.0) FROM fact_transactions) AS average_order_value,
                (SELECT COALESCE(SUM(cost_usd), 0.0) FROM fact_campaign_touchpoints) AS total_campaign_spend,
                (SELECT COUNT(DISTINCT customer_id) FROM fact_transactions) AS purchasing_customers
        """).fetchone()

        total_cust = res[0] or 0
        total_tx = res[1] or 0
        gross_rev = float(res[2] or 0.0)
        aov = float(res[3] or 0.0)
        camp_spend = float(res[4] or 0.0)
        purch_cust = res[5] or 0

        repeat_rate = round((purch_cust / total_cust) * 100, 2) if total_cust > 0 else 0.0

        return {
            "total_customers": total_cust,
            "total_transactions": total_tx,
            "total_gross_revenue": round(gross_rev, 2),
            "average_order_value": round(aov, 2),
            "total_campaign_spend": round(camp_spend, 2),
            "purchasing_customers": purch_cust,
            "repeat_purchase_rate_pct": repeat_rate,
        }

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
