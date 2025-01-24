# rag_pipeline.py
from typing import List, Dict
from .embeddings import create_embeddings
import numpy as np

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Splits a long text (e.g., abstract or article) into chunks of approximately chunk_size.
    
    :param text: Original text
    :param chunk_size: Size of each chunk (in characters)
    :return: List of chunks (strings)
    """
    # Simple approach: slice by characters
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks

def build_index(abstracts: List[Dict], chunk_size: int = 500) -> List[Dict]:
    index = []
    for item in abstracts:
        pmid = item["pmid"]
        text = item.get("abstract", "")
        # 1) split text into chunks
        chunks = chunk_text(text, chunk_size=chunk_size)
        # 2) create embeddings in batch
        # create_embeddings returns e.g. [(chunk_str, emb_vec), (chunk_str, emb_vec), ...]
        chunk_and_embs = create_embeddings(chunks)  
        for (chunk_text_str, emb_vec) in chunk_and_embs:
            # each emb_vec is a 1D list of floats
            index.append({
                "pmid": pmid,
                "chunk_text": chunk_text_str,
                "embedding": emb_vec
            })
    return index

def find_top_k(query: str, index: List[Dict], k: int = 3) -> List[Dict]:
    # query_vec = create_embeddings(...) -> returns e.g. [(q_str, vec)]
    q_pairs = create_embeddings([query])
    query_vec = q_pairs[0][1]  # single embedding vector

    scored = []
    for item in index:
        vec = item["embedding"]   # must be a 1D list of floats
        score = cosine_similarity(query_vec, vec)
        scored.append((item, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in scored[:k]]

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    import numpy as np
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))