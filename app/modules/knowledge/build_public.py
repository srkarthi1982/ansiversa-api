"""CLI for generating public AI knowledge artifacts."""

from __future__ import annotations

from time import perf_counter

from app.modules.ai_seo_compiler.integration import (
    AI_SEO_CONTROLLED_INTEGRATION_DEFAULT,
    run_controlled_integration,
)
from app.modules.knowledge.publisher import validate_public_artifacts, write_public_artifacts


def main() -> None:
    started = perf_counter()
    integration = run_controlled_integration(control=AI_SEO_CONTROLLED_INTEGRATION_DEFAULT)
    artifacts = integration.artifacts
    validate_public_artifacts(artifacts)
    result = write_public_artifacts(artifacts)
    changed = [name for name, did_change in result["changed"].items() if did_change]
    elapsed_ms = (perf_counter() - started) * 1000
    print(
        "public knowledge artifacts: "
        f"apps={result['appCount']} categories={result['categoryCount']} "
        f"changed={','.join(changed) if changed else 'false'} "
        f"elapsed_ms={elapsed_ms:.1f}"
    )


if __name__ == "__main__":
    main()
