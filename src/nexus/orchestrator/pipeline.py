"""
NEXUS-ANALYTICS Master Customer Intelligence Pipeline Orchestrator.

Orchestrates end-to-end analytical execution:
1. Data Ingestion (DuckDB Star-Schema)
2. SQL Analytical Query Modeling (Cohorts, Pareto, Channels)
3. Algorithmic RFM Segmentation
4. Machine Learning Churn Risk Scoring & Behavioral Attribution
5. Causal Uplift Archetype Classification & Campaign Budget Simulation
6. Predictive Customer Lifetime Value (CLV) Forecasting
7. Unified Customer 360 View Compilation
8. Cryptographic SHA-256 Audit Fingerprint Generation
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

from nexus.core.hasher import AuditHasher
from nexus.core.logger import get_logger
from nexus.data.generator import SyntheticCustomerGenerator
from nexus.data.warehouse import DataWarehouse
from nexus.data.queries import AnalyticsQueries
from nexus.analytics.rfm import RFMSegmenter, RFMResult
from nexus.analytics.churn import ChurnRiskScorer, ChurnScoringResult
from nexus.analytics.uplift import (
    CampaignUpliftEngine,
    UpliftResult,
    CLVForecaster,
    CLVResult
)

logger = get_logger("nexus.orchestrator")


@dataclass
class PipelineExecutionResult:
    """
    Standardized result payload of a full Customer Intelligence Pipeline run.
    """
    run_id: str
    timestamp: str
    kpis: Dict[str, Any]
    rfm_result: RFMResult
    churn_result: ChurnScoringResult
    uplift_result: UpliftResult
    clv_result: CLVResult
    customer_360: pd.DataFrame
    sha256_audit_hash: str
    execution_duration_ms: float
    summary_dict: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize audit summary for JSON export."""
        return self.summary_dict


class CustomerIntelligencePipeline:
    """
    Master pipeline orchestrating all analytical modules and producing audit-ready intelligence.
    """

    def __init__(self, db_path: str = ":memory:", seed: int = 42) -> None:
        self.db_path = db_path
        self.seed = seed
        self.warehouse = DataWarehouse(db_path=self.db_path)
        self.generator = SyntheticCustomerGenerator(seed=self.seed)
        self.queries = AnalyticsQueries(self.warehouse)
        self.rfm_segmenter = RFMSegmenter(self.warehouse)
        self.churn_scorer = ChurnRiskScorer()
        self.uplift_engine = CampaignUpliftEngine(random_state=self.seed)
        self.clv_forecaster = CLVForecaster()

    def run_full_pipeline(
        self,
        num_customers: int = 300,
        num_transactions: int = 1500,
        num_campaigns: int = 800
    ) -> PipelineExecutionResult:
        """
        Execute end-to-end analytical pipeline.
        """
        run_id = str(uuid.uuid4())
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        logger.info(f"Starting NEXUS-ANALYTICS Pipeline Run [ID: {run_id[:8]}...]")

        # Step 1: Ingest & Populate Warehouse
        logger.info("Stage 1/7: Generating enterprise events and loading DuckDB star-schema...")
        df_cust, df_tx, df_camp = self.generator.generate_dataset(
            num_customers=num_customers,
            num_transactions=num_transactions,
            num_campaign_touchpoints=num_campaigns
        )
        self.warehouse.load_dataframes(df_cust, df_tx, df_camp)

        # Step 2: Compute Executive KPIs & SQL Models
        logger.info("Stage 2/7: Computing high-level KPIs and analytical SQL metrics...")
        kpis = self.warehouse.get_kpis()

        # Step 3: Algorithmic RFM Segmentation
        logger.info("Stage 3/7: Running RFM quintile segmentation engine...")
        rfm_res = self.rfm_segmenter.calculate_from_warehouse()

        # Step 4: Churn Risk & Attribution
        logger.info("Stage 4/7: Training churn classifier and scoring behavioral risk...")
        churn_res = self.churn_scorer.score_from_warehouse(self.warehouse)

        # Step 5: Campaign Uplift & ROI Simulation
        logger.info("Stage 5/7: Estimating causal uplift and simulating budget ROI...")
        uplift_res = self.uplift_engine.estimate_uplift(df_cust, df_tx, df_camp)

        # Step 6: CLV Forecasting
        logger.info("Stage 6/7: Forecasting 3-year discounted retention Customer Lifetime Value...")
        clv_res = self.clv_forecaster.calculate_clv(
            df_cust, df_tx, churn_res.customer_risk_scores
        )

        # Step 7: Compile Customer 360 View
        logger.info("Stage 7/7: Compiling unified Customer 360 View...")
        c360 = df_cust.merge(
            rfm_res.customer_scores[["customer_id", "recency", "frequency", "monetary", "r_score", "f_score", "m_score", "segment", "action_strategy"]],
            on="customer_id", how="left"
        ).merge(
            churn_res.customer_risk_scores[["customer_id", "churn_probability", "risk_tier", "primary_risk_driver"]],
            on="customer_id", how="left"
        ).merge(
            uplift_res.customer_uplift_scores[["customer_id", "incremental_uplift_score", "causal_archetype"]],
            on="customer_id", how="left"
        ).merge(
            clv_res.customer_clv_forecasts[["customer_id", "annual_retention_rate", "projected_3yr_clv"]],
            on="customer_id", how="left"
        )

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Build Summary Dictionary for Audit Hashing
        summary_dict = {
            "run_id": run_id,
            "timestamp": timestamp,
            "engine": "NEXUS-ANALYTICS v1.0",
            "kpis": kpis,
            "rfm_summary": rfm_res.segment_summary.to_dict(orient="records"),
            "churn_summary": churn_res.risk_tier_summary.to_dict(orient="records"),
            "uplift_roi_simulation": uplift_res.simulated_roi_targeted_vs_blast,
            "total_portfolio_clv_usd": clv_res.enterprise_projected_portfolio_value,
            "total_customers_evaluated": len(c360),
            "execution_duration_ms": duration_ms
        }

        # Cryptographic SHA-256 Fingerprint
        audit_hash = AuditHasher.hash_dict(summary_dict)
        logger.info(f"Pipeline complete! SHA-256 Audit Digest: {audit_hash[:16]}... ({duration_ms} ms)")

        return PipelineExecutionResult(
            run_id=run_id,
            timestamp=timestamp,
            kpis=kpis,
            rfm_result=rfm_res,
            churn_result=churn_res,
            uplift_result=uplift_res,
            clv_result=clv_res,
            customer_360=c360,
            sha256_audit_hash=audit_hash,
            execution_duration_ms=duration_ms,
            summary_dict=summary_dict
        )

    def close(self) -> None:
        """Close underlying warehouse connection."""
        self.warehouse.close()
