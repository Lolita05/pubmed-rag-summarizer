import pytest
from typing import List, Dict

@pytest.fixture
def sample_abstracts() -> List[Dict]:
    return [
        {
            "pmid": "12345",
            "abstract": "This is a test abstract about science. It contains multiple sentences. Testing chunk size.",
        },
        {
            "pmid": "67890",
            "abstract": "Another test abstract. This one is shorter.",
        }
    ]

@pytest.fixture
def mock_embedding_vector() -> List[float]:
    return [0.1, 0.2, 0.3, 0.4, 0.5]

@pytest.fixture
def mock_chunks() -> List[str]:
    return [
        "This is chunk one.",
        "This is chunk two.",
        "This is chunk three."
    ] 