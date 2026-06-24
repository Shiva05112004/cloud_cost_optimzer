from app.rag.knowledge_base import load_vector_store


_store = None


def get_retriever(k: int = 3):
    """
    Returns a LangChain retriever that fetches top-k
    most semantically similar document chunks.
    """
    global _store
    if _store is None:
        _store = load_vector_store()
    return _store.as_retriever(search_kwargs={"k": k})


def retrieve_context(query: str, k: int = 3) -> str:
    """
    Given a user query, retrieves top-k relevant
    document chunks and returns them as a single string.
    """
    retriever = get_retriever(k)
    docs = retriever.get_relevant_documents(query)
    return "\n\n".join([doc.page_content for doc in docs])