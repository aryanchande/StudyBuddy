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
    Generate a faster structured summary.

    Uses a small number of LLM calls instead of
    one call per chunk group.
    """

    chunks = get_document_chunks(source)

    if not chunks:
        return "No indexed content found for this document."

    # Combine chunks into larger sections.
    # This reduces the number of Ollama calls.
    section_size = 12

    sections = []

    for start in range(0, len(chunks), section_size):

        section = "\n\n".join(
            chunks[start:start + section_size]
        )

        sections.append(section)

    partial_summaries = []

    for index, section in enumerate(sections):

        print(
            f"Summarizing section "
            f"{index + 1}/{len(sections)}..."
        )

        prompt = f"""
You are StudyBuddy, an academic learning assistant.

Summarize ONLY the study material below.

Include:
- Important concepts
- Definitions
- Key points
- Classifications
- Important examples

Do not add outside knowledge.
Do not invent information.

Use concise bullet points.

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
            ]
        )

        partial_summaries.append(
            response["message"]["content"]
        )

    # Final synthesis
    combined = "\n\n".join(partial_summaries)

    final_prompt = f"""
You are StudyBuddy.

Create one final study summary from the
summaries below.

Use ONLY the information provided.

Structure the result as:

## 1. Main Concepts
## 2. Important Definitions
## 3. Key Points
## 4. Important Examples

Keep it concise and useful for exam revision.

Do not add outside knowledge.

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
        ]
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