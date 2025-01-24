import pytest
from src.pubmed_api import search_pubmed, get_summaries, filter_medline_summaries, fetch_abstracts
from unittest.mock import patch, MagicMock

def test_search_pubmed():
    mock_response = MagicMock()
    mock_response.json.return_value = {"esearchresult": {"idlist": ["12345", "67890"]}}
    
    with patch('src.pubmed_api.requests.get', return_value=mock_response):
        pmids = search_pubmed("test query", "2023/01/01", "2023/12/31", retmax=2)
        assert len(pmids) == 2
        assert all(isinstance(pmid, str) for pmid in pmids)

def test_filter_medline_summaries():
    test_summaries = [
        {"pmid": "1", "pubstatus": "pubmed"},
        {"pmid": "2", "pubstatus": "medline"},
        {"pmid": "3", "pubstatus": "other"}
    ]
    
    filtered = filter_medline_summaries(test_summaries)
    assert len(filtered) == 2
    assert all(item["pubstatus"].lower() in ["pubmed", "medline"] for item in filtered)

def test_get_summaries():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "result": {
            "12345": {
                "title": "Test Title",
                "fulljournalname": "Test Journal",
                "pubdate": "2023",
                "pubstatus": "pubmed"
            }
        }
    }
    
    with patch('src.pubmed_api.requests.get', return_value=mock_response):
        summaries = get_summaries(["12345"])
        assert len(summaries) == 1
        assert all(key in summaries[0] for key in ["pmid", "title", "journal", "pubdate", "pubstatus"]) 