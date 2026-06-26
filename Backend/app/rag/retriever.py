from app.rag.knowledge_base import load_vector_store
from sklearn.metrics.pairwise import cosine_similarity

_index = None


def retrieve_context(query: str, k: int = 3) -> str:
    """
    Retrieves top-k most relevant document chunks
    using TF-IDF cosine similarity — no external vector DB needed.
    """
    global _index
    if _index is None:
        _index = load_vector_store()

    vectorizer = _index["vectorizer"]
    matrix     = _index["matrix"]
    chunks     = _index["chunks"]

    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, matrix).flatten()

    top_k_idx = similarities.argsort()[-k:][::-1]
    top_chunks = [chunks[i] for i in top_k_idx if similarities[i] > 0]

    return "\n\n".join(top_chunks) if top_chunks else "No relevant documentation found."

# from app.rag.knowledge_base import load_vector_store


# _store = None


# def get_retriever(k: int = 3):
#     """
#     Returns a LangChain retriever that fetches top-k
#     most semantically similar document chunks.
#     """
#     global _store
#     if _store is None:
#         _store = load_vector_store()
#     return _store.as_retriever(search_kwargs={"k": k})


# def retrieve_context(query: str, k: int = 3) -> str:
#     """
#     Given a user query, retrieves top-k relevant
#     document chunks and returns them as a single string.
#     """
#     retriever = get_retriever(k)
#     docs = retriever.get_relevant_documents(query)
#     return "\n\n".join([doc.page_content for doc in docs])