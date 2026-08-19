import pytest
from src.transformer import transform_document

def test_transform_document_normal(mock_raw_doc):
    result = transform_document(mock_raw_doc)
    assert len(result) == 1
    assert result[0]["station_id"] == "6"
    assert result[0]["TL"] == 26.4
    assert result[0]["SH"] is None

def test_transform_empty(mock_empty_doc):
    result = transform_document(mock_empty_doc)
    assert result == []
   