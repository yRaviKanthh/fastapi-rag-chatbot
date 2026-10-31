import os
from collections import OrderedDict

import faiss
import numpy as np


# EMBEDDINGS_BACKEND=sentence-transformers (default, runs locally)
# or fastembed (small ONNX model, fits on a 512 MB free host).
BACKEND = os.getenv("EMBEDDINGS_BACKEND", "sentence-transformers").lower()

EMBEDDING_DIM = 384

# Keeps memory small when many people use the site.
MAX_USERS_IN_MEMORY = 200


def _load_model():

    if BACKEND == "fastembed":
        from fastembed import TextEmbedding
        return TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


model = _load_model()


def embed(texts):

    if BACKEND == "fastembed":
        vectors = list(model.embed(texts))
    else:
        vectors = model.encode(texts)

    return np.array(vectors).astype("float32")


class UserStore:

    def __init__(self):
        # filename -> (chunks, embeddings). Uploading the same file again replaces it.
        self.documents = OrderedDict()
        self.chunks = []
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)

    def set_document(self, name, chunks, embeddings):
        self.documents[name] = (chunks, embeddings)
        self._rebuild()

    def _rebuild(self):
        self.chunks = []
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)

        for chunks, embeddings in self.documents.values():
            self.index.add(embeddings)
            self.chunks.extend(chunks)


# One store per user, so people only ever search their own documents.
stores = OrderedDict()


def get_store(user_key: str, create: bool = False):

    store = stores.get(user_key)

    if store is not None:
        stores.move_to_end(user_key)
        return store

    if not create:
        return None

    store = UserStore()
    stores[user_key] = store

    while len(stores) > MAX_USERS_IN_MEMORY:
        stores.popitem(last=False)

    return store


def split_into_chunks(text: str, size: int = 60, overlap: int = 15):
    words = text.split()
    chunks = []
    step = size - overlap
    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + size])
        if chunk:
            chunks.append(chunk)
        if start + size >= len(words):
            break
    return chunks


def create_embeddings(text: str, user_key: str, source: str = "document"):

    chunks = split_into_chunks(text)

    if not chunks:
        return 0

    embeddings = embed(chunks)

    store = get_store(user_key, create=True)

    store.set_document(source, chunks, embeddings)

    return len(chunks)


def search_query(query: str, user_key: str):

    store = get_store(user_key)

    if store is None or len(store.chunks) == 0:
        return []

    query_embedding = embed([query])

    k = min(5, len(store.chunks))

    distances, indices = store.index.search(query_embedding, k)

    results = []

    for idx in indices[0]:

        idx = int(idx)

        if 0 <= idx < len(store.chunks):

            results.append(store.chunks[idx])

    return results
