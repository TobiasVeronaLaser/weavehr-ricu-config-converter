# Usage

This project converts RICU `concept-dict.json` entries into OpenICU-style YAML config files.

It can be started in two ways:

1. From the command line through `openicu-ricu-convert`.
2. Directly from Python or Jupyter notebooks.

## Install

```bash
cd openicu_ricu_converter_project
pip install -e .
```

For tests:

```bash
pip install -e '.[dev]'
pytest
```

## CLI usage

Generate simple concepts for MIMIC:

```bash
openicu-ricu-convert \
  --concept-dict /path/to/concept-dict.json \
  --source mimic \
  --output-config generated/config \
  --overwrite
```

Generate simple + known derived concepts:

```bash
openicu-ricu-convert \
  --concept-dict /path/to/concept-dict.json \
  --source mimic \
  --output-config generated/config \
  --include-derived \
  --overwrite
```

Generate simple + known derived concepts + complex stubs:

```bash
openicu-ricu-convert \
  --concept-dict /path/to/concept-dict.json \
  --source mimic eicu mimic_demo \
  --output-config generated/config \
  --include-derived \
  --complex-stubs \
  --overwrite
```

Limit to selected concepts:

```bash
openicu-ricu-convert \
  --concept-dict /path/to/concept-dict.json \
  --source mimic \
  --concept dbp alb abx bmi gcs \
  --output-config generated/config \
  --include-derived \
  --overwrite
```

Limit to selected categories:

```bash
openicu-ricu-convert \
  --concept-dict /path/to/concept-dict.json \
  --source mimic \
  --category vitals chemistry hematology \
  --output-config generated/config \
  --overwrite
```

## Python usage

```python
from pathlib import Path

from openicu_ricu_converter import build_generation_plan, write_generation_plan

plan = build_generation_plan(
    concept_dict_path=Path("/path/to/concept-dict.json"),
    sources=["mimic", "eicu"],
    settings_path=Path("examples/settings.yml"),
    concepts=None,
    categories=None,
    include_derived=True,
    complex_stubs=True,
)

print("Generated YAML payloads:", len(plan.files))
print("Unsupported/report entries:", len(plan.unsupported))

write_generation_plan(
    plan=plan,
    output_config=Path("generated/config"),
    overwrite=True,
)
```

## Notebook usage without installation

```python
import sys
from pathlib import Path

PROJECT = Path("/path/to/openicu_ricu_converter_project")
sys.path.insert(0, str(PROJECT / "src"))
```

Then use the normal Python API:

```python
from openicu_ricu_converter import build_generation_plan, write_generation_plan

plan = build_generation_plan(
    concept_dict_path=Path("/path/to/concept-dict.json"),
    sources=["mimic"],
    settings_path=PROJECT / "examples/settings.yml",
    concepts=None,
    categories=None,
    include_derived=True,
    complex_stubs=True,
)

for file in plan.files[:10]:
    print(file.path)

for item in plan.unsupported[:10]:
    print(item)

write_generation_plan(plan, Path("generated/config"), overwrite=True)
```

## Output structure

The generated config is written under `--output-config`:

```text
generated/config/
├── concept/<category>/<concept>.yml
└── dataset/<dataset>/<version>/concept/<concept>.yml
```

Unsupported RICU callbacks and skipped entries are written into a report file.

## Concept types

### simple

Generated from direct RICU source mappings with `ids`, `regex`, `table`, `sub_var`, or `val_var`.

### derived

Generated only for known rules in `derived_rules.py`, for example BMI-like formula concepts.

### complex

Generated only as stubs when `--complex-stubs` is passed. These YAML files point to an `UnsupportedRICUTransformer` placeholder. They are intentionally not clinically executable until real OpenICU transformer implementations are written.

## Comparing resulting Concept Parquet outputs

The project also includes a validation command for comparing the **resulting
Concept outputs**, not just the YAML configs. This is useful when you run OpenICU
once with old hand-written configs and once with generated RICU configs.

Basic comparison:

```bash
openicu-ricu-compare-outputs \
  --old /home/q039tl/OpenICU.example/output/project/workspace/concept-cur \
  --new /home/q039tl/OpenICU.example/output/project/workspace/concept \
  --report-md concept_output_diff_report.md \
  --report-json concept_output_diff_report.json
```

Keyed comparison is usually more informative for MEDS-like outputs:

```bash
openicu-ricu-compare-outputs \
  --old /home/q039tl/OpenICU.example/output/project/workspace/concept-cur \
  --new /home/q039tl/OpenICU.example/output/project/workspace/concept \
  --key subject_id time code \
  --report-md concept_output_diff_report_keyed.md \
  --report-json concept_output_diff_report_keyed.json
```

If old and new outputs only differ in code formatting, normalize the code column
before comparing. This example treats hyphens and underscores as equivalent:

```bash
openicu-ricu-compare-outputs \
  --old /home/q039tl/OpenICU.example/output/project/workspace/concept-cur \
  --new /home/q039tl/OpenICU.example/output/project/workspace/concept \
  --key subject_id time code \
  --normalize-code hyphen-to-underscore \
  --report-md concept_output_diff_report_code_normalized.md \
  --report-json concept_output_diff_report_code_normalized.json
```

If old outputs lack extension columns that new outputs contain, ignore those
columns before schema and value comparison:

```bash
openicu-ricu-compare-outputs \
  --old /home/q039tl/OpenICU.example/output/project/workspace/concept-cur \
  --new /home/q039tl/OpenICU.example/output/project/workspace/concept \
  --key subject_id time code \
  --ignore-columns dataset table
```

Both options can be combined:

```bash
openicu-ricu-compare-outputs \
  --old /home/q039tl/OpenICU.example/output/project/workspace/concept-cur \
  --new /home/q039tl/OpenICU.example/output/project/workspace/concept \
  --key subject_id time code \
  --ignore-columns dataset table \
  --normalize-code hyphen-to-underscore
```

If you pass the generated or active OpenICU config root, the comparator also
classifies concepts as `simple`, `derived`, or `complex` and checks whether
`derived`/`complex` input dependency outputs exist:

```bash
openicu-ricu-compare-outputs \
  --old /home/q039tl/OpenICU.example/output/project/workspace/concept-cur \
  --new /home/q039tl/OpenICU.example/output/project/workspace/concept \
  --config-root /home/q039tl/OpenICU.example/generated/config \
  --key subject_id time code
```

Only inspect derived and complex concepts:

```bash
openicu-ricu-compare-outputs \
  --old /home/q039tl/OpenICU.example/output/project/workspace/concept-cur \
  --new /home/q039tl/OpenICU.example/output/project/workspace/concept \
  --config-root /home/q039tl/OpenICU.example/generated/config \
  --concept-type derived complex \
  --key subject_id time code
```

Python API:

```python
from pathlib import Path
from openicu_ricu_converter.validation import (
    compare_output_dirs,
    summarize_results,
    write_json_report,
    write_markdown_report,
)

results = compare_output_dirs(
    old_root=Path("/path/to/old/workspace/concept"),
    new_root=Path("/path/to/new/workspace/concept"),
    config_root=Path("/path/to/generated/config"),
    key_columns=["subject_id", "time", "code"],
    ignore_columns=["dataset", "table"],
    normalize_code="hyphen-to-underscore",
)

summary = summarize_results(results)
print(summary)

write_markdown_report(results, "concept_output_diff_report.md")
write_json_report(results, "concept_output_diff_report.json")
```

### Is derived/recursive validation different from the normal comparator?

The final output of every concept is still a Parquet file, so the normal row,
schema, and value comparison applies to `simple`, `derived`, and `complex`
concepts alike.

The extra derived/complex logic is dependency-aware validation:

- `derived` concepts are checked for required `table.concept` and `join[].concept` outputs.
- `complex` concepts are checked for required top-level `concepts` outputs.
- The report shows the concept type and missing dependency outputs.

This does not prove clinical equivalence of a complex transformer. It only shows
whether its produced Parquet output matches a previous run and whether its input
concept outputs are present.


## Compatibility options for hand-written OpenICU configs

The converter defaults are conservative so generated simple configs stay close to existing hand-written OpenICU configs:

```bash
openicu-ricu-convert \
  --concept-dict /path/to/concept-dict.json \
  --source mimic \
  --output-config generated/config \
  --regex-prefix-mode none \
  --logical-columns-mode preserve \
  --overwrite
```

`--regex-prefix-mode none` emits RICU regex mappings as `code: (regex)`. It does **not** prepend `.*?`. Use `--regex-prefix-mode contains` only when the regex should match anywhere inside the OpenICU code string.

`--logical-columns-mode preserve` maps matching events with `numeric_value: col(numeric_value)` and `text_value: col(text_value)`. Use `--logical-columns-mode boolean` only when RICU logical concepts with `set_val(TRUE)` should become explicit boolean outputs: `const(1)` and `const("true")`.
