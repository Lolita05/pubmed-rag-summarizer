import pytest
from src.rag_pipeline import chunk_text, build_index, find_top_k, cosine_similarity
from unittest.mock import patch

def test_chunk_text():
    text = "This is a test text that should be split into chunks of specific size."
    chunks = chunk_text(text, chunk_size=10)
    assert len(chunks) > 0
    assert all(len(chunk) <= 10 for chunk in chunks)

def test_cosine_similarity():
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0]
    vec_c = [0.0, 1.0, 0.0]
    
    assert cosine_similarity(vec_a, vec_b) == pytest.approx(1.0)
    assert cosine_similarity(vec_a, vec_c) == pytest.approx(0.0)
    assert cosine_similarity([0.0], [0.0]) == 0.0

@patch('src.rag_pipeline.create_embeddings')
def test_build_index(mock_create_embeddings, sample_abstracts, mock_embedding_vector):
    mock_create_embeddings.return_value = [
        ("chunk1", mock_embedding_vector),
        ("chunk2", mock_embedding_vector)
    ]
    
    index = build_index(sample_abstracts, chunk_size=100)
    assert len(index) > 0
    assert all(isinstance(item, dict) for item in index)
    assert all(key in item for item in index for key in ["pmid", "chunk_text", "embedding"])

@patch('src.rag_pipeline.create_embeddings')
def test_find_top_k(mock_create_embeddings, mock_embedding_vector):
    mock_create_embeddings.return_value = [("query", mock_embedding_vector)]
    
    test_index = [
        {"pmid": "1", "chunk_text": "test1", "embedding": mock_embedding_vector},
        {"pmid": "2", "chunk_text": "test2", "embedding": [0.2, 0.3, 0.4, 0.5, 0.6]},
    ]
    
    results = find_top_k("test query", test_index, k=2)
    assert len(results) == 2
    assert all(isinstance(item, dict) for item in results) 