import chromadb
from pathlib import Path

from embeddings import create_embedding


CHROMA_PATH = Path("chroma_db")

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_or_create_collection(
    name="study_materials"
)


def add_chunks(chunks: list[str], source: str):
    """
    Generate embeddings for chunks and store them in ChromaDB.
    """

    if not chunks:
        return

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        print(f"Embedding chunk {index + 1}/{len(chunks)}...")

        embedding = create_embedding(chunk)

        ids.append(f"{source}_{index}")
        embeddings.append(embedding)
        documents.append(chunk)

        metadatas.append({
            "source": source,
            "chunk_index": index
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    print(f"\nSuccessfully stored {len(chunks)} chunks.")


def search_chunks(query: str, n_results: int = 3):
    """
    Search ChromaDB for chunks semantically similar to a query.
    """

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


if __name__ == "__main__":

    print("ChromaDB initialized successfully.")

    print(f"Collection: {collection.name}")
    print(f"Existing documents: {collection.count()}")

query = input("\nAsk StudyBuddy something: ")

results = search_chunks(query, n_results=3)

print("\n========== SEARCH RESULTS ==========\n")

for i, document in enumerate(results["documents"][0]):

    print(f"--- Result {i + 1} ---")
    print(document)
    print()