"""Generate WeavEHR extraction table configurations from RICU data sources."""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .settings import ConverterSettings

SPEC_TO_TYPE = {
    "col_integer": "int64", "col_double": "float64", "col_number": "float64",
    "col_logical": "bool", "col_character": "string", "col_datetime": "datetime",
    "col_date": "date", "col_time": "time",
}

@dataclass(frozen=True)
class ExtractionFile:
    path: str
    content: dict[str, Any]
    origin: str


def load_data_sources(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, list):
        raise ValueError("data-sources.json must contain a list")
    return value



def _column(name: str, cfg: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"name": name, "type": SPEC_TO_TYPE.get(str(cfg.get("spec")), "string")}
    if cfg.get("format"):
        out["params"] = {"format": cfg["format"]}
    if cfg.get("name") and cfg["name"] != name:
        out["source_name"] = cfg["name"]
    return out


def _path(files: Any) -> str:
    if isinstance(files, list):
        return str(files[0]) if files else ""
    return str(files or "")


def infer_table_config(table_name: str, table: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    """Create an WeavEHR table configuration from RICU source metadata."""
    defaults = table.get("defaults") if isinstance(table.get("defaults"), dict) else {}
    cols = table.get("cols") or {}
    result: dict[str, Any] = {
        "path": _path(table.get("files")),
        "columns": [_column(name, cfg) for name, cfg in cols.items()],
    }
    id_cfg = source.get("id_cfg") or {}
    id_names = [cfg.get("id") for cfg in id_cfg.values() if isinstance(cfg, dict) and cfg.get("id") in cols]
    subject = id_names[0] if id_names else next((x for x in ("subject_id", "patientunitstayid", "patientid") if x in cols), None)
    index = defaults.get("index_var") or next((x for x in defaults.get("time_vars", []) if x in cols), None)
    value = defaults.get("val_var")
    unit = defaults.get("unit_var")
    code = next((x for x in ("itemid", "variableid", "pharmaid", "drugname", "labname", "DataID", "LaboratoryID") if x in cols), None)
    event_name = table_name.upper()
    event: dict[str, Any] = {"name": event_name, "columns": {}}
    if index: event["columns"]["time"] = f"col({index})"
    if code: event["columns"]["code"] = [f"col({code})"]
    elif value: event["columns"]["code"] = [f'const("{event_name}")']
    if value:
        spec = str((cols.get(value) or {}).get("spec", ""))
        event["columns"]["numeric_value" if spec in {"col_integer", "col_double", "col_number"} else "text_value"] = f"col({value})"
    if unit and code: event["columns"].setdefault("code", []).append(f"col({unit})")
    if subject:
        result["event_defaults"] = {"subject_id": f"col({subject})"}
        extensions = {name: f"col({name})" for name in id_names[1:]}
        if extensions: result["event_defaults"]["extension"] = extensions
    result["events"] = [event]
    return result


def build_extraction_files(
    data_sources: list[dict[str, Any]],
    *,
    sources: list[str],
    settings: ConverterSettings,
) -> list[ExtractionFile]:
    out: list[ExtractionFile] = []
    by_name = {src.get("name"): src for src in data_sources}
    if "nwicu" not in by_name and "miiv" in by_name:
        by_name["nwicu"] = copy.deepcopy(by_name["miiv"])
        by_name["nwicu"]["name"] = "nwicu"
    for name in sources:
        if name not in by_name:
            raise KeyError(f"RICU source not found: {name}")
        target = settings.source_target(name)
        if target is None:
            raise KeyError(
                f"No target dataset/version configured for RICU source: {name}"
            )
        source = by_name[name]
        for table_name, table in sorted((source.get("tables") or {}).items()):
            rel = (
                f"datasets/{target.dataset}/{target.version}/tables/"
                f"{table_name}.yml"
            )
            content = infer_table_config(table_name, table, source)
            out.append(ExtractionFile(rel, content, "generated"))
    return out


def write_extraction_files(files: list[ExtractionFile], output: str | Path, *, overwrite: bool = False) -> list[Path]:
    root = Path(output); written = []
    for file in files:
        path = root / file.path
        if path.exists() and not overwrite: raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(file.content, handle, sort_keys=False, allow_unicode=True)
        written.append(path)
    return written
