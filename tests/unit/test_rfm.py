"""
Unit tests for NEXUS-ANALYTICS RFM Segmentation Engine.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from nexus.analytics.rfm import RFMSegmenter, RFMResult
from nexus.data.generator import SyntheticCustomerGenerator
from nexus.data.warehouse import DataWarehouse


@pytest.fixture
def transactions_data():
    gen = SyntheticCustomerGenerator(seed=42)
    c, t, p = gen.generate_dataset(num_customers=100, num_transactions=500, num_campaign_touchpoints=200)
    return t


def test_rfm_calculation_from_df(transactions_data):
    segmenter = RFMSegmenter()
    result = segmenter.calculate_from_transactions(transactions_data)

    assert isinstance(result, RFMResult)
    assert result.total_customers_analyzed > 0
    df = result.customer_scores

    assert "recency" in df.columns
    assert "frequency" in df.columns
    assert "monetary" in df.columns
    assert "r_score" in df.columns
    assert "f_score" in df.columns
    assert "m_score" in df.columns
    assert "segment" in df.columns
    assert "action_strategy" in df.columns

    # Verify score ranges 1 to 5
    assert df["r_score"].between(1, 5).all()
    assert df["f_score"].between(1, 5).all()
    assert df["m_score"].between(1, 5).all()

    # Verify summary
    summary = result.segment_summary
    assert not summary.empty
    assert "customer_count" in summary.columns
    assert "revenue_share_pct" in summary.columns
    assert round(summary["customer_share_pct"].sum(), 0) == 100.0


def test_rfm_from_warehouse():
    warehouse = DataWarehouse(db_path=":memory:")
    gen = SyntheticCustomerGenerator(seed=123)
    c, t, p = gen.generate_dataset(num_customers=80, num_transactions=400, num_campaign_touchpoints=150)
    warehouse.load_dataframes(c, t, p)

    segmenter = RFMSegmenter(warehouse=warehouse)
    result = segmenter.calculate_from_warehouse()

    assert result.total_customers_analyzed > 0
    assert len(result.customer_scores) > 0
    assert "Champions" in result.segment_summary["segment"].values or len(result.segment_summary) > 0

    warehouse.close()
