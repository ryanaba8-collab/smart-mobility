import math
from pathlib import Path

import ollama


# =========================================================
# CONFIGURATION
# =========================================================

EMBEDDING_MODEL = "nomic-embed-text"

DOCUMENT_PATH = (
    Path(__file__).parent
    / "documents"
    / "smart_mobility_faq.txt"
)


# =========================================================
# OUTILS
# =========================================================

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    norm_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    norm_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def get_embedding(text: str):
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text,
    )

    return response["embedding"]


# =========================================================
# CHARGEMENT DU DOCUMENT
# =========================================================

def load_documents():
    content = DOCUMENT_PATH.read_text(
        encoding="utf-8"
    )

    sections = [
        section.strip()
        for section in content.split("\n\n\n")
        if section.strip()
    ]

    documents = []

    for section in sections:
        embedding = get_embedding(section)

        documents.append(
            {
                "content": section,
                "embedding": embedding,
            }
        )

    return documents


# =========================================================
# RECHERCHE RAG
# =========================================================

def search_knowledge(
    query: str,
    top_k: int = 2,
):
    documents = load_documents()

    query_embedding = get_embedding(query)

    scored_documents = []

    for document in documents:
        score = cosine_similarity(
            query_embedding,
            document["embedding"],
        )

        scored_documents.append(
            {
                "content": document["content"],
                "score": score,
            }
        )

    scored_documents.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_documents[:top_k]