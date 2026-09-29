"""
NEXUS-ANALYTICS Analytics Package.

Contains algorithmic customer segmentation, churn prediction,
campaign uplift causality, and Customer Lifetime Value (CLV) modules.
"""
from nexus.analytics.rfm import RFMSegmenter, RFMResult

__all__ = ["RFMSegmenter", "RFMResult"]
