"""
Unit tests for NEXUS-ANALYTICS Campaign Uplift & CLV Forecasting Engine.
"""
import pytest
from nexus.data.generator import SyntheticCustomerGenerator
from nexus.analytics.uplift import CampaignUpliftEngine, UpliftResult, CLVForecaster, CLVResult


@pytest.fixture
def dataset_fixture():
    gen = SyntheticCustomerGenerator(seed=42)
    return gen.generate_dataset(num_customers=120, num_transactions=500, num_campaign_touchpoints=250)


def test_campaign_uplift_engine(dataset_fixture):
    c, t, p = dataset_fixture
    engine = CampaignUpliftEngine(random_state=42)
    result = engine.estimate_uplift(c, t, p)

    assert isinstance(result, UpliftResult)
    df = result.customer_uplift_scores
    assert len(df) == len(c)
    assert "incremental_uplift_score" in df.columns
    assert "causal_archetype" in df.columns

    # Verify archetypes
    valid_archetypes = {
        "Persuadables (Priority Target)",
        "Sure Things (Do Not Discount)",
        "Sleeping Dogs (Do Not Disturb)",
        "Lost Causes (Low ROI)"
    }
    assert set(df["causal_archetype"].unique()).issubset(valid_archetypes)

    # Verify ROI simulation dictionary
    sim = result.simulated_roi_targeted_vs_blast
    assert "targeted_strategy" in sim
    assert "blast_strategy" in sim
    assert sim["targeted_strategy"]["roi_percentage"] > sim["blast_strategy"]["roi_percentage"]


def test_clv_forecaster(dataset_fixture):
    c, t, p = dataset_fixture
    forecaster = CLVForecaster(annual_discount_rate=0.10)
    result = forecaster.calculate_clv(c, t)

    assert isinstance(result, CLVResult)
    df = result.customer_clv_forecasts
    assert len(df) == len(c)
    assert "projected_3yr_clv" in df.columns
    assert "annual_retention_rate" in df.columns

    # Verify positive enterprise value
    assert result.enterprise_projected_portfolio_value > 0
    assert (df["projected_3yr_clv"] > 0).all()

    # Verify segment summary
    summary = result.segment_clv_summary
    assert not summary.empty
    assert "acquisition_channel" in summary.columns
    assert "total_projected_clv" in summary.columns
