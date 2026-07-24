"""Disabled-by-default Astra AI platform foundation.

This package is intentionally not imported by FastAPI startup or runtime
routes. It provides internal contracts and deterministic Phase 1 scaffolding
only.
"""

from app.modules.astra_ai.orchestration import orchestrate_platform_request
from app.modules.astra_ai.settings import ASTRA_AI_PLATFORM_ENABLED

__all__ = ["ASTRA_AI_PLATFORM_ENABLED", "orchestrate_platform_request"]
