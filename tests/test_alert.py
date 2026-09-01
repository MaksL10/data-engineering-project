import pytest
from src.alert import is_threshold_exceeded

def test_max_exceeded():
    assert is_threshold_exceeded(36.0, {"max": 35}) == True

def test_min_exceeded():
    assert is_threshold_exceeded(-16.0, {"min": -15}) == True

def test_normal():
    assert is_threshold_exceeded(25.9, {"max": 35.0}) == False