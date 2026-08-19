import pytest
from datetime import date, timedelta
from src.backfill import get_limits

def test_get_limits_negative():
    end = date.today()
    start = end - timedelta(days=180)
    count_stations = 5
    count_parameters = 12
    requests_interval = 10
    result = get_limits(start, end, count_stations, count_parameters, requests_interval)
    assert result == "bad"

def test_get_limits_positive():
    end = date.today()
    start = end - timedelta(days=60)
    count_stations = 5
    count_parameters = 12
    requests_interval = 10
    result = get_limits(start, end, count_stations, count_parameters, requests_interval)
    assert result == "good"