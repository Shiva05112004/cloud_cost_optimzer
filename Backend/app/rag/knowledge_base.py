from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle


INDEX_PATH = Path(__file__).parent / "tfidf_index.pkl"


def build_vector_store():
    """
    Reads all .txt files, splits into paragraph chunks,
    builds a TF-IDF index — pure Python, no compilation needed.
    """
    docs_path = Path(__file__).parent / "documents"
    chunks = []

    for file in docs_path.glob("*.txt"):
        text = file.read_text(encoding="utf-8")
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                chunks.append(para)

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(chunks)

    with open(INDEX_PATH, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}, f)

    print(f"Vector store built with {len(chunks)} chunks.")
    return chunks


def load_vector_store():
    with open(INDEX_PATH, "rb") as f:
        return pickle.load(f)


# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from pathlib import Path


# def build_vector_store() -> FAISS:
#     """
#     Reads all .txt files from documents/ folder,
#     splits into chunks, embeds, and stores in FAISS.
#     Run once offline to create the vector store.
#     """
#     docs_path = Path(__file__).parent / "documents"
#     raw_texts = []

#     for file in docs_path.glob("*.txt"):
#         raw_texts.append(file.read_text(encoding="utf-8"))

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=50,
#     )
#     chunks = splitter.create_documents(raw_texts)

#     embeddings = HuggingFaceEmbeddings(
#         model_name="all-MiniLM-L6-v2"  # free, runs locally
#     )

#     vector_store = FAISS.from_documents(chunks, embeddings)
#     vector_store.save_local("faiss_index")
#     print(f"Vector store built with {len(chunks)} chunks.")
#     return vector_store


# def load_vector_store() -> FAISS:
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     return FAISS.load_local(
#         "faiss_index", embeddings,
#         allow_dangerous_deserialization=True,
#     )

# Simulated Mock Data Structure to bypass FAISS / Chroma compilation blocks
# class MockIndex:
#     def __init__(self):
#         pass

# class MockVectorStore:
#     def __init__(self):
#         self.index = MockIndex()
    
#     def similarity_search(self, query, k=3):
#         # Returns a plain dictionary mockup structure matching LangChain Document interfaces
#         class MockDoc:
#             def __init__(self, text):
#                 self.page_content = text
#                 self.metadata = {}
#         return [MockDoc("Simulated Local Context Recommendation Data Block")]

# def load_vector_store():
#     return MockVectorStore()

# class FAISS:
#     @classmethod
#     def load_local(cls, *args, **kwargs):
#         return MockVectorStore()
