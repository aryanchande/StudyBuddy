import ollama


EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector using Ollama.
    """

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response["embeddings"][0]


if __name__ == "__main__":

    test_text = "What is a Database Management System?"

    print("Generating embedding...")

    try:
        embedding = create_embedding(test_text)

        print("Embedding generated successfully!")
        print(f"Vector dimensions: {len(embedding)}")
        print(f"First 10 values: {embedding[:10]}")

    except Exception as error:
        print(f"Error: {error}")