"""
Unit tests for NEXUS-ANALYTICS Customer Intelligence Pipeline Orchestrator.
"""
import pytest
from nexus.orchestrator.pipeline import CustomerIntelligencePipeline, PipelineExecutionResult
from nexus.core.hasher import AuditHasher


def test_pipeline_execution():
    pipeline = CustomerIntelligencePipeline(db_path=":memory:", seed=42)
    result = pipeline.run_full_pipeline(num_customers=50, num_transactions=200, num_campaigns=100)

    assert isinstance(result, PipelineExecutionResult)
    assert len(result.run_id) > 0
    assert result.execution_duration_ms >= 0

    # Test Customer 360 View
    c360 = result.customer_360
    assert len(c360) == 50
    assert "segment" in c360.columns
    assert "churn_probability" in c360.columns
    assert "risk_tier" in c360.columns
    assert "incremental_uplift_score" in c360.columns
    assert "causal_archetype" in c360.columns
    assert "projected_3yr_clv" in c360.columns

    # Test Cryptographic SHA-256 Hash
    assert len(result.sha256_audit_hash) == 64
    assert result.sha256_audit_hash == AuditHasher.hash_dict(result.summary_dict)

    # Test KPIs
    assert result.kpis["total_customers"] == 50
    assert result.kpis["total_transactions"] == 200
    assert result.kpis["total_gross_revenue"] > 0

    pipeline.close()
