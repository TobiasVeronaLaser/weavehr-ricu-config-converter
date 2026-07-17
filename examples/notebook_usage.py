"""Notebook-style usage example.

Copy these cells into a Jupyter/IPython notebook.
"""

# Cell 1: make package importable without installation
import sys
from pathlib import Path

PROJECT = Path("/path/to/openicu_ricu_converter_project")
sys.path.insert(0, str(PROJECT / "src"))

# Cell 2: imports
from openicu_ricu_converter import build_generation_plan, write_generation_plan, convert

# Cell 3: configure paths
concept_dict_path = Path("/path/to/concept-dict.json")
output_config = Path("/path/to/generated/config")

# Cell 4: build plan only, inspect it, then write
plan = build_generation_plan(
    concept_dict_path=concept_dict_path,
    sources=["mimic"],
    concepts=None,
    categories=None,
    include_derived=True,
    complex_stubs=True,
)

print("Generated files:", len(plan.files))
print("Unsupported/report entries:", len(plan.unsupported))

for file in plan.files[:10]:
    print(file.path)

for item in plan.unsupported[:10]:
    print(item)

write_generation_plan(plan, output_config, overwrite=True)

# Alternative: build and write in one call
# plan = convert(
#     concept_dict_path=concept_dict_path,
#     output_config=output_config,
#     sources=["mimic"],
#     include_derived=True,
#     complex_stubs=True,
#     overwrite=True,
# )
