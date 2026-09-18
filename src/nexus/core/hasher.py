"""
NEXUS-ANALYTICS Cryptographic Audit Hasher.

Produces SHA-256 deterministic fingerprints of analytical reports,
RFM segment definitions, and churn scoring outputs for compliance audits.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


class AuditHasher:
    """
    Computes cryptographic SHA-256 fingerprints of analytical payloads.
    """

    @staticmethod
    def hash_dict(data: Dict[str, Any]) -> str:
        """
        Generate a deterministic SHA-256 hash for a dictionary.
        Keys are sorted to guarantee reproducibility.
        """
        encoded = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def hash_string(content: str) -> str:
        """Generate a SHA-256 hash for a raw text string."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
