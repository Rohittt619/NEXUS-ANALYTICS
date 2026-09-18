"""
NEXUS-ANALYTICS Core Configuration Module.

Uses Pydantic BaseSettings for strict type validation of analytical parameters,
database connection settings, and segmentation thresholds.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NexusSettings(BaseSettings):
    """
    Centralized configuration settings for the NEXUS-ANALYTICS engine.
    """
    engine_name: str = Field(default="NEXUS-ANALYTICS v1.0", description="Engine display name")
    environment: str = Field(default="production", description="Environment stage: development/production")
    database_path: str = Field(default=":memory:", description="DuckDB database path (default in-memory)")
    
    # Analytical Parameters
    rfm_recency_window_days: int = Field(default=365, description="Lookback window for RFM analysis in days")
    churn_inactivity_days: int = Field(default=90, description="Inactivity threshold to classify a customer as churned")
    high_value_customer_threshold: float = Field(default=1000.0, description="Minimum spend for VIP status")
    clv_discount_rate: float = Field(default=0.10, description="Annual discount rate for CLV calculations")
    
    # Logging
    log_level: str = Field(default="INFO", description="Console logging verbosity")

    model_config = SettingsConfigDict(
        env_prefix="NEXUS_",
        env_file=".env",
        extra="ignore"
    )


settings = NexusSettings()
