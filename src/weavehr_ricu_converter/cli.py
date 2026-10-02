"""Command line interface."""
from __future__ import annotations

import argparse

from .project import generate_project


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="weavehr-ricu-convert")
    p.add_argument("--concept-dict", required=True)
    p.add_argument("--data-sources", required=True)
    p.add_argument("--output-config", required=True)
    p.add_argument("--source", nargs="+", required=True)
    p.add_argument("--settings")
    p.add_argument("--no-derived", action="store_true")
    p.add_argument("--no-complex-stubs", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    r = generate_project(
        concept_dict=a.concept_dict,
        data_sources=a.data_sources,
        output_config=a.output_config,
        sources=a.source,
        settings=a.settings,
        include_derived=not a.no_derived,
        complex_stubs=not a.no_complex_stubs,
        overwrite=a.overwrite,
    )
    print(f"Concept files: {r.concept_files}")
    print(f"Extraction files: {r.extraction_files}")
    print(f"Unsupported/report entries: {r.unsupported}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
