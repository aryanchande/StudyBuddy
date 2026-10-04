import ollama

from vector_store import collection


LLM_MODEL = "qwen2.5:1.5b"


def get_document_chunks(source: str):
    """Retrieve all chunks for a document in correct order."""

    results = collection.get(
        where={"source": source}
    )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    combined = list(zip(metadatas, documents))

    combined.sort(
        key=lambda item: item[0].get("chunk_index", 0)
    )

    return [document for metadata, document in combined]


def summarize_document(source: str):
    """
    Generate a fast, grounded summary.

    Uses at most 3 Ollama calls:
    - 2 section summaries
    - 1 final synthesis
    """

    chunks = get_document_chunks(source)

    if not chunks:
        return "No indexed content found for this document."

    # Limit the amount of context per call.
    # This keeps generation manageable for Qwen 1.5B.
    midpoint = len(chunks) // 2

    sections = [
        "\n\n".join(chunks[:midpoint]),
        "\n\n".join(chunks[midpoint:])
    ]

    partial_summaries = []

    for index, section in enumerate(sections):

        print(
            f"Summarizing section "
            f"{index + 1}/{len(sections)}..."
        )

        prompt = f"""
You are StudyBuddy, an academic learning assistant.

Summarize ONLY the study material provided below.

Include:
- Important concepts
- Definitions
- Key points
- Classifications
- Important examples

Rules:
- Use ONLY the provided material.
- Do not add outside knowledge.
- Do not invent information.
- Use concise bullet points.
- Preserve important terminology from the material.

Study Material:
----------------
{section}
----------------
"""

        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2,
                "num_predict": 500
            }
        )

        partial_summaries.append(
            response["message"]["content"]
        )

    combined = "\n\n".join(
        partial_summaries
    )

    print("Creating final summary...")

    final_prompt = f"""
You are StudyBuddy.

Create one concise exam-revision summary
from the two summaries below.

Use ONLY the information provided.

Structure:

## 1. Main Concepts
## 2. Important Definitions
## 3. Key Points
## 4. Important Examples

Rules:
- Do not add outside knowledge.
- Do not invent information.
- Remove repetition.
- Keep important technical terminology.
- Keep the final answer concise.

Summaries:
----------------
{combined}
----------------
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": final_prompt
            }
        ],
        options={
            "temperature": 0.2,
            "num_predict": 700
        }
    )

    return response["message"]["content"]
if __name__ == "__main__":

    print("================================")
    print("StudyBuddy Document Summarizer")
    print("================================")

    source = input(
        "Enter document name: "
    )

    print("\nGenerating summary...\n")

    try:

        summary = summarize_document(source)

        print("\n========== SUMMARY ==========\n")
        print(summary)

    except Exception as error:

        print(f"Error: {error}")