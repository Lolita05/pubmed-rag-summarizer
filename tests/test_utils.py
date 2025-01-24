from src.utils import parse_date
from io import StringIO
import sys

def test_parse_date():
    assert parse_date("2023-01-01") == "2023/01/01"
    assert parse_date("invalid-date") is None
    assert parse_date("") is None
    assert parse_date(None) is None