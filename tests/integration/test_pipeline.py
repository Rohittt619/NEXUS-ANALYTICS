"""
End-to-End Integration Tests for NEXUS-ANALYTICS Pipeline.

Verifies end-to-end data flow:
Synthetic Generator -> DuckDB Star-Schema Warehouse -> SQL Analytical Engines
-> RFM Segmentation -> Churn Risk ML -> Uplift Causality & CLV -> SHA-256 Audit.
"""
from __future__ import annotations

import pytest

from nexus.orchestrator.pipeline import CustomerIntelligencePipeline
from nexus.core.hasher import AuditHasher


@pytest.fixture
def executed_pipeline():
    """Fixture that initializes and runs the master intelligence pipeline."""
    pipeline = CustomerIntelligencePipeline(db_path=":memory:", seed=42)
    result = pipeline.run_full_pipeline(
        num_customers=50,
        num_transactions=250,
        num_campaigns=150
    )
    yield pipeline, result
    pipeline.close()


def test_end_to_end_pipeline_execution(executed_pipeline):
    """Test full execution flow and verify artifact integrity."""
    pipeline, result = executed_pipeline

    # 1. Verify Pipeline Run Metadata
    assert result.run_id is not None
    assert len(result.run_id) > 10
    assert result.execution_duration_ms > 0
    assert len(result.sha256_audit_hash) == 64

    # 2. Verify Warehouse State
    tables = [r[0] for r in pipeline.warehouse.conn.execute("SHOW TABLES").fetchall()]
    assert "dim_customers" in tables
    assert "fact_transactions" in tables
    assert "fact_campaign_touchpoints" in tables
    assert "dim_loyalty_tiers" in tables

    # 3. Verify KPIs
    kpis = result.kpis
    assert kpis["total_customers"] == 50
    assert kpis["total_transactions"] == 250
    assert kpis["total_gross_revenue"] > 0
    assert kpis["average_order_value"] > 0
    assert 0 <= kpis["repeat_purchase_rate_pct"] <= 100

    # 4. Verify RFM Output
    rfm = result.rfm_result
    assert 0 < len(rfm.customer_scores) <= 50
    valid_segments = {
        "Champions",
        "Loyal Customers",
        "Potential Loyalists",
        "Promising New",
        "Needs Attention",
        "At Risk (High Value)",
        "Can't Lose Them",
        "About to Sleep",
        "Hibernating",
        "Lost Customers",
    }
    actual_segments = set(rfm.customer_scores["segment"].unique())
    assert actual_segments.issubset(valid_segments)

    # 5. Verify Churn Output
    churn = result.churn_result
    assert len(churn.customer_risk_scores) == 50
    assert 0.70 <= churn.model_accuracy <= 1.0
    assert (churn.customer_risk_scores["churn_probability"] >= 0.0).all()
    assert (churn.customer_risk_scores["churn_probability"] <= 1.0).all()
    assert len(churn.feature_importances) > 0

    # 6. Verify Uplift Output
    uplift = result.uplift_result
    assert len(uplift.customer_uplift_scores) == 50
    valid_archetypes = {
        "Persuadables (Priority Target)",
        "Sure Things (Do Not Disturb)",
        "Sure Things (Do Not Discount)",
        "Sleeping Dogs (Do Not Disturb)",
        "Lost Causes (Low ROI)"
    }
    actual_archetypes = set(uplift.customer_uplift_scores["causal_archetype"].unique())
    assert actual_archetypes.issubset(valid_archetypes)

    # 7. Verify CLV Output
    clv = result.clv_result
    assert len(clv.customer_clv_forecasts) == 50
    assert clv.enterprise_projected_portfolio_value > 0
    assert (clv.customer_clv_forecasts["projected_3yr_clv"] > 0).all()

    # 8. Verify Customer 360 View Unified DataFrame
    c360 = result.customer_360
    assert len(c360) == 50
    expected_c360_cols = [
        "customer_id", "acquisition_channel", "region", "segment", "churn_probability",
        "risk_tier", "incremental_uplift_score", "causal_archetype", "projected_3yr_clv"
    ]
    for col in expected_c360_cols:
        assert col in c360.columns


def test_pipeline_audit_hasher_cryptographic_integrity():
    """Verify cryptographic SHA-256 integrity and determinism of AuditHasher."""
    test_dict_a = {"run_id": "test_1", "kpis": {"total_customers": 100, "revenue": 50000.0}}
    test_dict_b = {"run_id": "test_1", "kpis": {"total_customers": 100, "revenue": 50000.0}}
    test_dict_c = {"run_id": "test_2", "kpis": {"total_customers": 100, "revenue": 50000.0}}

    hash_a = AuditHasher.hash_dict(test_dict_a)
    hash_b = AuditHasher.hash_dict(test_dict_b)
    hash_c = AuditHasher.hash_dict(test_dict_c)

    assert len(hash_a) == 64
    assert hash_a == hash_b
    assert hash_a != hash_c


def test_star_schema_referential_integrity(executed_pipeline):
    """Verify DuckDB warehouse foreign key referential integrity."""
    pipeline, _ = executed_pipeline

    # Check that all transactions link to valid customers
    orphan_tx = pipeline.warehouse.conn.execute("""
        SELECT COUNT(*)
        FROM fact_transactions t
        LEFT JOIN dim_customers c ON t.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """).fetchone()[0]
    assert orphan_tx == 0, "Found orphan transactions without matching customer"

    # Check that all campaign events link to valid customers
    orphan_campaigns = pipeline.warehouse.conn.execute("""
        SELECT COUNT(*)
        FROM fact_campaign_touchpoints ce
        LEFT JOIN dim_customers c ON ce.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """).fetchone()[0]
    assert orphan_campaigns == 0, "Found orphan campaign events without matching customer"

    # Check data sanity: no negative amounts in fact_transactions
    invalid_amounts = pipeline.warehouse.conn.execute("""
        SELECT COUNT(*)
        FROM fact_transactions
        WHERE order_amount <= 0
    """).fetchone()[0]
    assert invalid_amounts == 0, "Found transactions with non-positive amounts"
