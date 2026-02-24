"""Feature builders for ranking founders."""

from .pipeline import FeaturePipeline
from .types import FeatureMatrix, FeatureMetadata

def get_pipeline(
    cfg,
    outcome_lookup=None,
) -> FeaturePipeline:
    """Get a cached feature pipeline."""
    return FeaturePipeline(
        cfg=cfg,
        outcome_lookup=outcome_lookup,
    )


__all__ = ["FeaturePipeline", "build_matrix", "FeatureMatrix", "FeatureMetadata"]
