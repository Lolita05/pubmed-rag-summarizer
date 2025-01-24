# utils.py
import datetime
from typing import Optional

def parse_date(date_str: str) -> Optional[str]:
    """
    Attempts to parse a date in YYYY-MM-DD format,
    and return it in YYYY/MM/DD format for PubMed,
    otherwise returns None.
    """
    if not date_str:
        return None
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y/%m/%d")
    except ValueError:
        return None