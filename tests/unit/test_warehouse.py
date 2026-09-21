"""
Unit tests for NEXUS-ANALYTICS Synthetic Generator & DuckDB Warehouse.
"""
import pytest
from nexus.data.generator import SyntheticCustomerGenerator
from nexus.data.warehouse import DataWarehouse


def test_synthetic_generator_shapes():
    gen = SyntheticCustomerGenerator(seed=123)
    c, t, p = gen.generate_dataset(num_customers=50, num_transactions=200, num_campaign_touchpoints=100)
    assert len(c) == 50
    assert len(t) == 200
    assert len(p) == 100
    assert "customer_id" in c.columns
    assert "order_amount" in t.columns
    assert "campaign_name" in p.columns


def test_warehouse_initialization_and_loading():
    warehouse = DataWarehouse(db_path=":memory:")
    gen = SyntheticCustomerGenerator(seed=42)
    c, t, p = gen.generate_dataset(num_customers=100, num_transactions=400, num_campaign_touchpoints=200)
    
    warehouse.load_dataframes(c, t, p)

    # Test SQL query execution
    df_tx = warehouse.query("SELECT COUNT(*) AS cnt, SUM(order_amount) AS total FROM fact_transactions")
    assert df_tx["cnt"].values[0] == 400
    assert df_tx["total"].values[0] > 0

    # Test KPI computation
    kpis = warehouse.get_kpis()
    assert kpis["total_customers"] == 100
    assert kpis["total_transactions"] == 400
    assert kpis["total_gross_revenue"] > 0
    assert kpis["average_order_value"] > 0
    assert kpis["purchasing_customers"] > 0
    assert 0 <= kpis["repeat_purchase_rate_pct"] <= 100

    warehouse.close()
