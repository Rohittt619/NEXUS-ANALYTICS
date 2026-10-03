"""
Unit tests for NEXUS-ANALYTICS Churn Risk Probability Scorer.
"""
import pytest
from nexus.data.generator import SyntheticCustomerGenerator
from nexus.data.warehouse import DataWarehouse
from nexus.analytics.churn import ChurnRiskScorer, ChurnScoringResult


@pytest.fixture
def dataset_fixture():
    gen = SyntheticCustomerGenerator(seed=42)
    return gen.generate_dataset(num_customers=100, num_transactions=400, num_campaign_touchpoints=200)


def test_prepare_features(dataset_fixture):
    c, t, p = dataset_fixture
    scorer = ChurnRiskScorer(inactivity_threshold_days=90)
    df_feat = scorer.prepare_features(c, t, p)

    assert len(df_feat) == len(c)
    assert "recency_days" in df_feat.columns
    assert "total_orders" in df_feat.columns
    assert "total_spend" in df_feat.columns
    assert "campaign_engagement_rate" in df_feat.columns
    assert "is_churned" in df_feat.columns


def test_score_customers(dataset_fixture):
    c, t, p = dataset_fixture
    scorer = ChurnRiskScorer(inactivity_threshold_days=90)
    result = scorer.score_customers(c, t, p)

    assert isinstance(result, ChurnScoringResult)
    df = result.customer_risk_scores
    assert len(df) == len(c)
    assert "churn_probability" in df.columns
    assert "risk_tier" in df.columns
    assert "primary_risk_driver" in df.columns

    # Verify probability range [0.0, 1.0]
    assert df["churn_probability"].between(0.0, 1.0).all()

    # Verify risk tiers
    valid_tiers = {"Low Risk", "Moderate Risk", "High Risk", "Critical Risk"}
    assert set(df["risk_tier"].unique()).issubset(valid_tiers)

    # Verify feature importances
    assert len(result.feature_importances) > 0
    assert "recency_days" in result.feature_importances

    # Model accuracy
    assert 0.70 <= result.model_accuracy <= 1.0


def test_score_from_warehouse(dataset_fixture):
    c, t, p = dataset_fixture
    warehouse = DataWarehouse(db_path=":memory:")
    warehouse.load_dataframes(c, t, p)

    scorer = ChurnRiskScorer()
    res = scorer.score_from_warehouse(warehouse)
    assert res.customer_risk_scores is not None
    assert len(res.customer_risk_scores) == len(c)

    warehouse.close()
