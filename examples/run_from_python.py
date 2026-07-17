"""Example: run the RICU -> OpenICU config converter from Python.

Usage:
    python examples/run_from_python.py \
        --concept-dict /path/to/concept-dict.json \
        --output-config generated/config \
        --source mimic eicu \
        --include-derived \
        --complex-stubs \
        --overwrite
"""

from __future__ import annotations

import argparse
from pathlib import Path

from openicu_ricu_converter import convert


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the converter from Python code.")
    parser.add_argument("--concept-dict", required=True, type=Path)
    parser.add_argument("--settings", default=None, type=Path)
    parser.add_argument("--output-config", required=True, type=Path)
    parser.add_argument("--source", nargs="+", required=True)
    parser.add_argument("--concept", nargs="*", default=None)
    parser.add_argument("--category", nargs="*", default=None)
    parser.add_argument("--include-derived", action="store_true")
    parser.add_argument("--complex-stubs", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = convert(
        concept_dict_path=args.concept_dict,
        settings_path=args.settings,
        output_config=args.output_config,
        sources=args.source,
        concepts=args.concept,
        categories=args.category,
        include_derived=args.include_derived,
        complex_stubs=args.complex_stubs,
        overwrite=args.overwrite,
    )
    print(f"Generated YAML payloads: {len(plan.files)}")
    print(f"Unsupported/report entries: {len(plan.unsupported)}")
    print(f"Wrote generated config to: {args.output_config}")


if __name__ == "__main__":
    main()
