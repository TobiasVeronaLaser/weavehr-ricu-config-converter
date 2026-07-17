"""Compare resulting Concept Parquet outputs from Python.

Adjust paths before running.
"""

from pathlib import Path

from openicu_ricu_converter.validation import (
    compare_output_dirs,
    summarize_results,
    write_json_report,
    write_markdown_report,
)

OLD_OUTPUT = Path("/home/q039tl/OpenICU.example/output/project/workspace/concept-cur")
NEW_OUTPUT = Path("/home/q039tl/OpenICU.example/output/project/workspace/concept")
CONFIG_ROOT = Path("/home/q039tl/OpenICU.example/generated/config")

results = compare_output_dirs(
    old_root=OLD_OUTPUT,
    new_root=NEW_OUTPUT,
    config_root=CONFIG_ROOT,
    key_columns=["subject_id", "time", "code"],
    ignore_columns=["dataset", "table"],
    normalize_code="hyphen-to-underscore",
)

print(summarize_results(results))

# Inspect only changed derived/complex concepts.
for result in results:
    if result.concept_type in {"derived", "complex"} and result.status != "unchanged":
        print(result.status, result.concept_type, result.path)
        for check in result.dependency_checks:
            print("  dependency", check.concept, "new exists:", check.exists_in_new)

write_markdown_report(results, "concept_output_diff_report.md")
write_json_report(results, "concept_output_diff_report.json")
