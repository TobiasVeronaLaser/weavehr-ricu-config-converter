from weavehr_ricu_converter.loader import load_concept_dict
from weavehr_ricu_converter.mapper import RICUToWeavEHRMapper
from weavehr_ricu_converter.settings import ConverterSettings


def test_mapper_generates_mimic_dbp(tmp_path):
    concept_dict = tmp_path / "concept-dict.json"
    concept_dict.write_text(
        """
        {
          "dbp": {
            "unit": ["mmHg", "mm Hg"],
            "description": "diastolic blood pressure",
            "category": "vitals",
            "sources": {
              "mimic": [
                {"ids": [220051, 220180], "table": "chartevents", "sub_var": "itemid"}
              ]
            }
          }
        }
        """,
        encoding="utf-8",
    )
    concepts = load_concept_dict(concept_dict)
    settings = ConverterSettings.with_defaults()
    settings.concept_names["dbp"] = "diastolic_blood_pressure"
    mapper = RICUToWeavEHRMapper(settings)
    files = mapper.build_files(concepts, sources=["mimic"])

    paths = {file.path for file in files}
    assert "concepts/vitals/diastolic_blood_pressure.yml" in paths
    assert "datasets/mimic-iv/3.1/mappings/diastolic_blood_pressure.yml" in paths
