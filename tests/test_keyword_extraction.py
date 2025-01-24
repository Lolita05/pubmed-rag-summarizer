import pytest
from src.keyword_extraction import extract_keywords
from unittest.mock import patch, MagicMock

def test_extract_keywords():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="microbiology, microbiota, health"))]
    
    with patch('src.keyword_extraction.openai.chat.completions.create', return_value=mock_response):
        result = extract_keywords("Tell me about the latest news in microbiology and human health")
        
        assert isinstance(result, str)
        assert "," in result
        assert "news" not in result.lower()
        assert "latest" not in result.lower() 