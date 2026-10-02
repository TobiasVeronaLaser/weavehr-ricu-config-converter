from __future__ import annotations

import json
from pathlib import Path

import yaml

from weavehr_ricu_converter.cli import build_parser
from weavehr_ricu_converter.data_sources import build_extraction_files
from weavehr_ricu_converter.settings import ConverterSettings


def test_cli_has_no_version_option() -> None:
    parser = build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }
    assert "--version" not in option_strings


def test_extraction_path_uses_settings_target(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.yml"
    settings_path.write_text(
        yaml.safe_dump(
            {
                "sources": {
                    "miiv": {
                        "dataset": "mimic-iv",
                        "version": "3.1",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    settings = ConverterSettings.from_file(settings_path)
    data_sources = [
        {
            "name": "miiv",
            "id_cfg": {},
            "tables": {
                "labevents": {
                    "files": "labevents.csv.gz",
                    "defaults": {},
                    "cols": {},
                }
            },
        }
    ]

    files = build_extraction_files(
        data_sources,
        sources=["miiv"],
        settings=settings,
    )

    assert [file.path for file in files] == [
        "datasets/mimic-iv/3.1/tables/labevents.yml"
    ]


def test_missing_source_target_fails() -> None:
    settings = ConverterSettings.with_defaults()
    data_sources = [{"name": "custom", "tables": {}}]

    try:
        build_extraction_files(data_sources, sources=["custom"], settings=settings)
    except KeyError as exc:
        assert "No target dataset/version configured" in str(exc)
    else:
        raise AssertionError("Expected missing target configuration to fail")
