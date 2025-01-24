import pytest
from src.summarizer import generate_answer
from unittest.mock import patch, MagicMock

def test_generate_answer():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Test summary response"))]
    
    with patch('src.summarizer.openai.chat.completions.create', return_value=mock_response):
        result = generate_answer(
            context_chunks=["Test context 1", "Test context 2"],
            user_query="What are the main findings?"
        )
        
        assert isinstance(result, str)
        assert len(result) > 0 