import hashlib
from pathlib import Path

import chromadb

from embeddings import create_embedding


CHROMA_PATH = Path("chroma_db")

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_or_create_collection(
    name="study_materials"
)


def create_document_id(source: str) -> str:
    """
    Create a stable ID for a document.
    """

    return hashlib.md5(
        source.encode("utf-8")
    ).hexdigest()


def add_chunks(chunks: list[str], source: str):
    """
    Generate embeddings and store chunks in ChromaDB.
    """

    if not chunks:
        return

    document_id = create_document_id(source)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        print(
            f"Embedding chunk "
            f"{index + 1}/{len(chunks)}..."
        )

        embedding = create_embedding(chunk)

        ids.append(
            f"{document_id}_chunk_{index}"
        )

        embeddings.append(embedding)

        documents.append(chunk)

        metadatas.append({
            "source": source,
            "document_id": document_id,
            "chunk_index": index
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(
        f"\nSuccessfully stored "
        f"{len(chunks)} chunks."
    )


def document_exists(source: str) -> bool:
    """
    Check whether a document has already been indexed.
    """

    document_id = create_document_id(source)

    results = collection.get(
        where={
            "document_id": document_id
        },
        limit=1
    )

    return len(results["ids"]) > 0


def search_chunks(
    query: str,
    n_results: int = 3
):
    """
    Search ChromaDB for semantically relevant chunks.
    """

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


def list_documents():
    """
    Return the names of indexed documents.
    """

    results = collection.get()

    documents = set()

    for metadata in results["metadatas"]:

        if metadata:

            documents.add(
                metadata.get(
                    "source",
                    "Unknown"
                )
            )

    return sorted(documents)


if __name__ == "__main__":

    print("================================")
    print("StudyBuddy ChromaDB")
    print("================================")

    print(
        f"Collection: {collection.name}"
    )

    print(
        f"Total chunks: {collection.count()}"
    )

    print("\nIndexed documents:")

    for document in list_documents():

        print(f"📄 {document}")