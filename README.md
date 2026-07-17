# OpenICU RICU Config Converter

Python project for reproducibly generating **OpenICU extraction table configs** and **OpenICU concept mapping configs** from RICU's `data-sources.json` and `concept-dict.json`.

The repository follows the same working style as `openicu-yaib`: the conversion logic lives in `src/`, and `notebooks/datasets/` contains one executable notebook per RICU dataset.

## Design

The converter generates all extraction and concept configurations directly from
RICU's `data-sources.json` and `concept-dict.json`. It does not read, copy, or
reference an OpenICU checkout at runtime.

OpenICU configurations serve only as a strict development baseline: regression
tests compare converter output with known expected YAML files. The application
itself therefore remains deterministic and independent of OpenICU.

Concept mappings are generated from the RICU concept dictionary. Known derived
concepts are emitted as `type: derived`; unsupported recursive callbacks receive
explicit complex stubs and are listed in `ricu_unsupported.yml`.

## Repository structure

```text
src/openicu_ricu_converter/
  data_sources.py       # extraction/table conversion
  mapper.py             # concept mapping conversion
  project.py            # complete generation pipeline
  api.py                # concept-only lower-level API
  cli.py                # command-line interface
notebooks/datasets/
  aumc.ipynb
  eicu.ipynb
  eicu_demo.ipynb
  hirid.ipynb
  miiv.ipynb
  mimic.ipynb
  mimic_demo.ipynb
  nwicu.ipynb
  sic.ipynb
examples/input/
  concept-dict.json
  data-sources.json
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Generate all configs

```bash
openicu-ricu-convert \
  --concept-dict examples/input/concept-dict.json \
  --data-sources examples/input/data-sources.json \
  --settings examples/settings.yml \
  --output-config generated/configs \
  --version generated \
  --source aumc eicu eicu_demo hirid miiv mimic mimic_demo nwicu sic \
  --overwrite
```

For a production regeneration, set `--version` to the actual target dataset version and normally run datasets separately. That keeps output paths aligned with OpenICU's `configs/datasets/<dataset>/<version>/` layout.

## Python API

```python
from openicu_ricu_converter import generate_project

result = generate_project(
    concept_dict="examples/input/concept-dict.json",
    data_sources="examples/input/data-sources.json",
    output_config="generated/nwicu",
    sources=["nwicu"],
    version="0.1.0",
    settings="examples/settings.yml",
    overwrite=True,
)
print(result)
```

## Validation contract

- Generation requires only RICU JSON inputs and converter settings.
- Generated concept and extraction YAML is deterministic.
- Regression fixtures can assert byte-level or semantic equality with expected
  OpenICU configurations without introducing an OpenICU runtime dependency.
- `generation_manifest.yml` records the generated file counts.
- `ricu_unsupported.yml` records mappings that cannot be translated faithfully.

The dataset notebooks are intended for dataset-specific generation, inspection,
and comparison with checked-in expected fixtures.
