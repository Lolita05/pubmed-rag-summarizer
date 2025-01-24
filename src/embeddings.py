# embeddings.py
import os
from openai import OpenAI
from typing import List, Tuple

# Instantiate the OpenAI client at the module level
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

def create_embeddings(chunks: List[str], model_name: str = "text-embedding-ada-002") -> List[Tuple[str, List[float]]]:
    """
    Creates embeddings for each text chunk using OpenAI Embeddings (v1.x).

    :param chunks: List of strings (chunks) to convert into embeddings
    :param model_name: Name of the embedding model, e.g., "text-embedding-ada-002"
    :return: List of tuples (chunk_text, embedding_vector)
    """
    results = []
    for ch in chunks:
        response = client.embeddings.create(input=ch, model=model_name)
        embedding = response.data[0].embedding
        results.append((ch, embedding))
    return results