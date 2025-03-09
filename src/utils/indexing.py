from typing import List
import faiss
import numpy as np


def create_faiss_index(logger, embeddings: List[List[float]]) -> faiss.IndexFlatL2:
    logger.info("Criando índice FAISS.")
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    return index


def search_index(
    logger, index: faiss.IndexFlatL2, query_embedding: List[float], k: int = 5
):
    logger.info("Pesquisando no índice FAISS por embeddings similares.")
    query_embedding = np.array(query_embedding).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_embedding, k)
    return indices[0], distances[0]
