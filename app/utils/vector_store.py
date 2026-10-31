from collections import OrderedDict

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")

EMBEDDING_DIM = 384

# Keeps memory small when many people use the site.
MAX_USERS_IN_MEMORY = 200


class UserStore:

    def __init__(self):
        self.chunks = []
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)


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


def create_embeddings(text: str, user_key: str):

    chunks = split_into_chunks(text)

    if not chunks:
        return 0

    embeddings = model.encode(chunks)

    embeddings = np.array(embeddings).astype("float32")

    store = get_store(user_key, create=True)

    store.index.add(embeddings)

    store.chunks.extend(chunks)

    return len(chunks)


def search_query(query: str, user_key: str):

    store = get_store(user_key)

    if store is None or len(store.chunks) == 0:
        return []

    query_embedding = model.encode([query])

    query_embedding = np.array(query_embedding).astype("float32")

    k = min(5, len(store.chunks))

    distances, indices = store.index.search(query_embedding, k)

    results = []

    for idx in indices[0]:

        idx = int(idx)

        if 0 <= idx < len(store.chunks):

            results.append(store.chunks[idx])

    return results
