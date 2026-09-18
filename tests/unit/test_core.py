"""
Unit tests for NEXUS-ANALYTICS Core Module (config, hasher, logger).
"""
import pytest
from nexus.core.config import NexusSettings
from nexus.core.hasher import AuditHasher
from nexus.core.logger import get_logger


def test_nexus_config_defaults():
    settings = NexusSettings()
    assert settings.engine_name == "NEXUS-ANALYTICS v1.0"
    assert settings.environment == "production"
    assert settings.rfm_recency_window_days == 365
    assert settings.churn_inactivity_days == 90
    assert settings.high_value_customer_threshold == 1000.0
    assert settings.clv_discount_rate == 0.10


def test_audit_hasher_string():
    h1 = AuditHasher.hash_string("NEXUS-ANALYTICS")
    h2 = AuditHasher.hash_string("NEXUS-ANALYTICS")
    assert len(h1) == 64
    assert h1 == h2


def test_audit_hasher_dict():
    d1 = {"segment": "Champions", "churn_risk": 0.05}
    d2 = {"churn_risk": 0.05, "segment": "Champions"}
    assert AuditHasher.hash_dict(d1) == AuditHasher.hash_dict(d2)


def test_logger_instance():
    logger = get_logger("test_nexus")
    assert logger is not None
    assert logger.name == "test_nexus"
