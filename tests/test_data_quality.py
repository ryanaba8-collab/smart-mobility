import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import data_pipeline.quality.check_data_quality as dq


def create_csv(path: Path, rows: int):
    with open(path, "w", encoding="utf-8") as file:
        file.write("id,name\n")

        for i in range(rows):
            file.write(f"{i},test_{i}\n")


def test_data_quality_passes_with_valid_files(tmp_path, monkeypatch):
    rules = {
        "stations.csv": 3,
        "trips.csv": 2,
    }

    create_csv(tmp_path / "stations.csv", 3)
    create_csv(tmp_path / "trips.csv", 2)

    monkeypatch.setattr(dq, "CLEAN_DIR", tmp_path)
    monkeypatch.setattr(dq, "QUALITY_RULES", rules)

    dq.check_data_quality()


def test_data_quality_fails_when_file_is_missing(tmp_path, monkeypatch):
    rules = {
        "stations.csv": 3,
    }

    monkeypatch.setattr(dq, "CLEAN_DIR", tmp_path)
    monkeypatch.setattr(dq, "QUALITY_RULES", rules)

    with pytest.raises(ValueError):
        dq.check_data_quality()


def test_data_quality_fails_when_row_count_is_too_low(tmp_path, monkeypatch):
    rules = {
        "stations.csv": 5,
    }

    create_csv(tmp_path / "stations.csv", 2)

    monkeypatch.setattr(dq, "CLEAN_DIR", tmp_path)
    monkeypatch.setattr(dq, "QUALITY_RULES", rules)

    with pytest.raises(ValueError):
        dq.check_data_quality()