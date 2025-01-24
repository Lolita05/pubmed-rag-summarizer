import pytest
from src.embeddings import create_embeddings
from unittest.mock import patch, MagicMock

def test_create_embeddings_structure():
    chunks = ["Test chunk 1", "Test chunk 2"]
    
    # Create a mock response object that mimics OpenAI's response structure
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1, 0.2, 0.3]),
        MagicMock(embedding=[0.4, 0.5, 0.6])
    ]
    
    # Patch the embeddings.create method directly on the client
    with patch('src.embeddings.client.embeddings.create', return_value=mock_response):
        results = create_embeddings(chunks)
        
        assert len(results) == len(chunks)
        assert all(isinstance(item, tuple) for item in results)
        assert all(len(item) == 2 for item in results)
        assert all(isinstance(item[0], str) for item in results)
        assert all(isinstance(item[1], list) for item in results) 