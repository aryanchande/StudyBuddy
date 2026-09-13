import ollama

from vector_store import search_chunks


LLM_MODEL = "qwen2.5:1.5b"


def generate_answer(question: str, n_results: int = 3):
    """
    Retrieve relevant study material and generate
    a grounded answer using the local Ollama LLM.
    """

    results = search_chunks(
        query=question,
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return (
            "I couldn't find this information in the uploaded "
            "study material.",
            []
        )

    context_parts = []

    for i, document in enumerate(documents):

        context_parts.append(
            f"Source {i + 1}:\n{document}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are StudyBuddy, an AI learning assistant.

Answer the student's question using ONLY the study
material provided below.

If the answer is not present in the study material,
say:

"I couldn't find this information in the uploaded study material."

Do not use outside knowledge.
Do not invent facts.

Study Material:
----------------
{context}
----------------

Student Question:
{question}

Give a clear, concise and easy-to-understand answer.
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    sources = []

    for i, metadata in enumerate(metadatas):

        sources.append({
            "source": metadata.get("source", "Unknown"),
            "chunk_index": metadata.get("chunk_index", i)
        })

    return answer, sources