"""
Run this ONCE to build the TF-IDF knowledge base index.
Usage: python scripts/build_knowledge_base.py
"""
from app.rag.knowledge_base import build_vector_store

if __name__ == "__main__":
    build_vector_store()