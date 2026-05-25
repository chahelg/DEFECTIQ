"""Service package for DefectIQ.

This module intentionally avoids importing submodules at package import time
to prevent expensive side-effects during test collection. Import submodules
directly where needed, e.g. `from app.services.ingest_service import ...`.
"""

__all__ = []

