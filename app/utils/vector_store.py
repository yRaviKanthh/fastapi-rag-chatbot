from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")


document_chunks = []

index = faiss.IndexFlatL2(384)


def create_embeddings(text: str):

    chunks = [chunk.strip() for chunk in text.split(".") if chunk.strip()]

    if not chunks:
        return 0

    embeddings = model.encode(chunks)

    embeddings = np.array(embeddings).astype("float32")

    index.add(embeddings)

    document_chunks.extend(chunks)

    return len(chunks)


def search_query(query: str):

    if len(document_chunks) == 0:
        return []

    query_embedding = model.encode([query])

    query_embedding = np.array(query_embedding).astype("float32")

    k = min(3, len(document_chunks))

    distances, indices = index.search(query_embedding, k)

    results = []

    for idx in indices[0]:

        idx = int(idx)

        if 0 <= idx < len(document_chunks):

            results.append(document_chunks[idx])

    return results