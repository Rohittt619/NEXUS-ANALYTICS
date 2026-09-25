"""
Unit tests for NEXUS-ANALYTICS Enterprise SQL Query Models.
"""
import pytest
from nexus.data.generator import SyntheticCustomerGenerator
from nexus.data.warehouse import DataWarehouse
from nexus.data.queries import AnalyticsQueries


@pytest.fixture
def analytics_fixture():
    warehouse = DataWarehouse(db_path=":memory:")
    gen = SyntheticCustomerGenerator(seed=42)
    c, t, p = gen.generate_dataset(num_customers=150, num_transactions=600, num_campaign_touchpoints=300)
    warehouse.load_dataframes(c, t, p)
    queries = AnalyticsQueries(warehouse)
    yield queries
    warehouse.close()


def test_cohort_retention_matrix(analytics_fixture):
    df_cohort = analytics_fixture.get_cohort_retention_matrix()
    assert not df_cohort.empty
    assert "cohort" in df_cohort.columns
    assert "retention_rate_pct" in df_cohort.columns
    assert "cohort_size" in df_cohort.columns
    # Month offset 0 should always have 100% retention
    offset_zero = df_cohort[df_cohort["month_offset"] == 0]
    assert (offset_zero["retention_rate_pct"] == 100.0).all()


def test_purchase_latency(analytics_fixture):
    df_latency = analytics_fixture.get_purchase_latency_distribution()
    assert not df_latency.empty
    assert "order_sequence_num" in df_latency.columns
    assert "avg_days_between_orders" in df_latency.columns
    assert (df_latency["avg_days_between_orders"] >= 0).all()


def test_pareto_revenue_concentration(analytics_fixture):
    df_pareto = analytics_fixture.get_pareto_revenue_concentration()
    assert not df_pareto.empty
    assert len(df_pareto) <= 10
    assert "spend_decile" in df_pareto.columns
    assert "cumulative_revenue_pct" in df_pareto.columns
    # Cumulative revenue should increase across deciles and reach 100%
    assert df_pareto["cumulative_revenue_pct"].iloc[-1] == 100.0


def test_channel_roi_and_cac(analytics_fixture):
    df_channels = analytics_fixture.get_channel_roi_and_cac()
    assert not df_channels.empty
    assert "acquisition_channel" in df_channels.columns
    assert "roas_multiplier" in df_channels.columns
    assert "total_revenue" in df_channels.columns
