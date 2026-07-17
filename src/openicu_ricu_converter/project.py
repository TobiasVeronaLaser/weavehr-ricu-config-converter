"""End-to-end project generation API."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from .api import build_generation_plan, write_generation_plan
from .data_sources import build_extraction_files, load_data_sources, write_extraction_files

@dataclass(frozen=True)
class ProjectResult:
    concept_files: int
    extraction_files: int
    unsupported: int


def generate_project(*, concept_dict: str | Path, data_sources: str | Path, output_config: str | Path,
                     sources: list[str], version: str = "generated", settings: str | Path | None = None,
                     include_derived: bool = True,
                     complex_stubs: bool = True, overwrite: bool = False) -> ProjectResult:
    plan = build_generation_plan(concept_dict_path=concept_dict, sources=sources, settings_path=settings,
        include_derived=include_derived, complex_stubs=complex_stubs)
    write_generation_plan(plan, output_config, overwrite=overwrite)
    extraction = build_extraction_files(load_data_sources(data_sources), sources=sources,
        version=version)
    write_extraction_files(extraction, output_config, overwrite=overwrite)
    manifest: dict[str, Any] = {"sources": sources, "version": version,
        "concept_files": len(plan.files), "extraction_files": len(extraction),
        "unsupported": len(plan.unsupported)}
    path = Path(output_config) / "generation_manifest.yml"
    with path.open("w", encoding="utf-8") as handle: yaml.safe_dump(manifest, handle, sort_keys=False)
    return ProjectResult(manifest["concept_files"], manifest["extraction_files"],
        manifest["unsupported"])
