import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from data_pipeline.quality.check_data_quality import check_data_quality


def test_data_quality():
    check_data_quality()