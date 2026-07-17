"""Template transformer module for generated RICU complex concept stubs.

Copy this file into your OpenICU checkout, for example:

    OpenICU/src/open_icu/concepts/ricu_transformers.py

The converter can generate ``type: complex`` config files that point to
``open_icu.concepts.ricu_transformers.UnsupportedRICUTransformer``. That class
is deliberately non-operational: it prevents accidentally treating a placeholder
as a clinically valid concept. Replace it with real transformer classes or change
``concept_transformer`` in the generated YAML to your implementation.
"""

from __future__ import annotations

from typing import Any


class UnsupportedRICUTransformer:
    """Placeholder for a generated complex RICU concept.

    OpenICU will instantiate complex transformers with
    ``(concept, complex_config, **kwargs)`` and then call the instance with the
    project. This placeholder raises a clear error when accidentally executed.
    """

    def __init__(self, concept: Any, complex_config: Any, **kwargs: Any) -> None:
        self.concept = concept
        self.config = complex_config
        self.kwargs = kwargs

    def __call__(self, project: Any) -> None:
        ricu_key = self.kwargs.get("ricu_key", "<unknown>")
        ricu_callback = self.kwargs.get("ricu_callback", "<unknown>")
        deps = self.kwargs.get("ricu_dependencies", [])
        raise NotImplementedError(
            "Generated RICU complex concept stub was executed. "
            f"ricu_key={ricu_key!r}, callback={ricu_callback!r}, dependencies={deps!r}. "
            "Implement a real transformer and update concept_transformer in the generated YAML."
        )
