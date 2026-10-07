"""
NEXUS-ANALYTICS Analytics Package.
"""
from nexus.analytics.rfm import RFMSegmenter, RFMResult
from nexus.analytics.churn import ChurnRiskScorer, ChurnScoringResult
from nexus.analytics.uplift import (
    CampaignUpliftEngine,
    UpliftResult,
    CLVForecaster,
    CLVResult
)

__all__ = [
    "RFMSegmenter",
    "RFMResult",
    "ChurnRiskScorer",
    "ChurnScoringResult",
    "CampaignUpliftEngine",
    "UpliftResult",
    "CLVForecaster",
    "CLVResult"
]
