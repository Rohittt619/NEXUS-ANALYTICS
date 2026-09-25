"""
NEXUS-ANALYTICS Enterprise Analytical SQL Query Models.

Provides pre-compiled, optimized SQL models for DuckDB:
1. Cohort Retention Matrix (Month-over-month active retention)
2. Repeat Purchase Latency (LAG window function inter-purchase times)
3. Pareto Revenue Concentration (Cumulative spend percentiles)
4. Acquisition Channel ROI & Conversion Funnel
"""
from __future__ import annotations

import pandas as pd
from nexus.data.warehouse import DataWarehouse


class AnalyticsQueries:
    """
    Executes advanced analytical SQL models against the DuckDB DataWarehouse.
    """

    def __init__(self, warehouse: DataWarehouse) -> None:
        self.warehouse = warehouse

    def get_cohort_retention_matrix(self) -> pd.DataFrame:
        """
        Compute monthly cohort retention matrix.
        Groups customers by their first purchase month and tracks return activity
        across subsequent month offsets (0, 1, 2, ...).
        """
        sql = """
        WITH first_purchase AS (
            SELECT
                customer_id,
                MIN(DATE_TRUNC('month', timestamp)) AS cohort_month
            FROM fact_transactions
            GROUP BY customer_id
        ),
        activity AS (
            SELECT
                t.customer_id,
                fp.cohort_month,
                DATE_TRUNC('month', t.timestamp) AS activity_month,
                DATEDIFF('month', fp.cohort_month, DATE_TRUNC('month', t.timestamp)) AS month_offset
            FROM fact_transactions t
            JOIN first_purchase fp ON t.customer_id = fp.customer_id
        ),
        cohort_sizes AS (
            SELECT
                cohort_month,
                COUNT(DISTINCT customer_id) AS cohort_size
            FROM first_purchase
            GROUP BY cohort_month
        ),
        retention AS (
            SELECT
                a.cohort_month,
                cs.cohort_size,
                a.month_offset,
                COUNT(DISTINCT a.customer_id) AS active_customers,
                ROUND(COUNT(DISTINCT a.customer_id) * 100.0 / cs.cohort_size, 2) AS retention_rate_pct
            FROM activity a
            JOIN cohort_sizes cs ON a.cohort_month = cs.cohort_month
            GROUP BY a.cohort_month, cs.cohort_size, a.month_offset
        )
        SELECT
            STRFTIME(cohort_month, '%Y-%m') AS cohort,
            cohort_size,
            month_offset,
            active_customers,
            retention_rate_pct
        FROM retention
        ORDER BY cohort_month, month_offset;
        """
        return self.warehouse.query(sql)

    def get_purchase_latency_distribution(self) -> pd.DataFrame:
        """
        Calculate inter-purchase latency (days between consecutive orders)
        using the SQL LAG() window function partitioned by customer.
        """
        sql = """
        WITH ordered_transactions AS (
            SELECT
                transaction_id,
                customer_id,
                timestamp,
                order_amount,
                LAG(timestamp) OVER (
                    PARTITION BY customer_id
                    ORDER BY timestamp
                ) AS previous_order_time,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_id
                    ORDER BY timestamp
                ) AS order_sequence_num
            FROM fact_transactions
        ),
        latencies AS (
            SELECT
                customer_id,
                order_sequence_num,
                order_amount,
                DATEDIFF('day', previous_order_time, timestamp) AS days_since_last_order
            FROM ordered_transactions
            WHERE previous_order_time IS NOT NULL
        )
        SELECT
            order_sequence_num,
            COUNT(*) AS repeat_orders_count,
            ROUND(AVG(days_since_last_order), 1) AS avg_days_between_orders,
            ROUND(MIN(days_since_last_order), 0) AS min_days,
            ROUND(MAX(days_since_last_order), 0) AS max_days,
            ROUND(AVG(order_amount), 2) AS avg_order_value
        FROM latencies
        GROUP BY order_sequence_num
        ORDER BY order_sequence_num;
        """
        return self.warehouse.query(sql)

    def get_pareto_revenue_concentration(self) -> pd.DataFrame:
        """
        Compute Pareto (80/20) cumulative revenue curve:
        Calculates customer spend deciles and cumulative revenue contribution.
        """
        sql = """
        WITH customer_spend AS (
            SELECT
                customer_id,
                SUM(order_amount) AS total_spend,
                COUNT(transaction_id) AS order_count
            FROM fact_transactions
            GROUP BY customer_id
        ),
        ranked_spend AS (
            SELECT
                customer_id,
                total_spend,
                order_count,
                NTILE(10) OVER (ORDER BY total_spend DESC) AS spend_decile,
                SUM(total_spend) OVER (ORDER BY total_spend DESC) AS running_total_revenue,
                SUM(total_spend) OVER () AS total_enterprise_revenue
            FROM customer_spend
        )
        SELECT
            spend_decile,
            COUNT(customer_id) AS customers_in_decile,
            ROUND(SUM(total_spend), 2) AS decile_revenue,
            ROUND(AVG(total_spend), 2) AS avg_spend_per_customer,
            ROUND(MAX(running_total_revenue) * 100.0 / MAX(total_enterprise_revenue), 2) AS cumulative_revenue_pct
        FROM ranked_spend
        GROUP BY spend_decile
        ORDER BY spend_decile;
        """
        return self.warehouse.query(sql)

    def get_channel_roi_and_cac(self) -> pd.DataFrame:
        """
        Analyze customer acquisition channels:
        Combines marketing spend with total customer revenue to calculate ROAS (Return On Ad Spend).
        """
        sql = """
        WITH channel_customers AS (
            SELECT
                c.acquisition_channel,
                COUNT(DISTINCT c.customer_id) AS total_acquired,
                COUNT(DISTINCT t.customer_id) AS converted_customers,
                COALESCE(SUM(t.order_amount), 0.0) AS channel_gross_revenue,
                COALESCE(COUNT(t.transaction_id), 0) AS total_orders
            FROM dim_customers c
            LEFT JOIN fact_transactions t ON c.customer_id = t.customer_id
            GROUP BY c.acquisition_channel
        ),
        channel_touchpoints AS (
            SELECT
                c.acquisition_channel,
                COALESCE(SUM(tp.cost_usd), 0.0) AS total_touchpoint_cost
            FROM dim_customers c
            LEFT JOIN fact_campaign_touchpoints tp ON c.customer_id = tp.customer_id
            GROUP BY c.acquisition_channel
        )
        SELECT
            cc.acquisition_channel,
            cc.total_acquired,
            cc.converted_customers,
            ROUND(cc.channel_gross_revenue, 2) AS total_revenue,
            ROUND(ct.total_touchpoint_cost, 2) AS estimated_ad_spend,
            ROUND(cc.channel_gross_revenue / NULLIF(ct.total_touchpoint_cost, 0), 2) AS roas_multiplier,
            ROUND(cc.channel_gross_revenue / NULLIF(cc.converted_customers, 0), 2) AS revenue_per_converted_customer
        FROM channel_customers cc
        JOIN channel_touchpoints ct ON cc.acquisition_channel = ct.acquisition_channel
        ORDER BY total_revenue DESC;
        """
        return self.warehouse.query(sql)
