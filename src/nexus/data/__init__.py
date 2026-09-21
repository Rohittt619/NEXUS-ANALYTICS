"""
NEXUS-ANALYTICS Data Engineering Package.

Includes synthetic customer event generator and DuckDB star-schema data warehouse.
"""
from nexus.data.generator import SyntheticCustomerGenerator
from nexus.data.warehouse import DataWarehouse

__all__ = ["SyntheticCustomerGenerator", "DataWarehouse"]
