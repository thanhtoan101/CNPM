"""AI service prototypes for the analog-photography platform.

The package intentionally keeps the recommendation and retrieval pipelines
deterministic so that they can be evaluated offline.  The HTTP adapter in
``ai_service.api`` exposes the same application services to the future shared
backend.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
