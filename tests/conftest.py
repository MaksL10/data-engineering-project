import sys
import os
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_raw_doc():
    """"Normal reply from API with valid values including one null (SH in summer)"""
    return {
        "timestamps": ["2026-07-30T13:10+00:00"],
        "features": [
            {
                "properties": {
                    "station": "6",
                    "parameters": {
                        "TL": {"data": [26.4]},
                        "tl_flag": {"data": [12]},
                        "SH": {"data" : [None]}
                    }
                }
            }
        ]
    }

@pytest.fixture
def mock_empty_doc():
    """Edge case: complete empty document"""
    return {}