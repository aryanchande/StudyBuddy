import json
import re

import ollama

from vector_store import collection


LLM_MODEL = "qwen2.5:1.5b"


def get_document_chunks(source: str):
    """Retrieve all chunks belonging to a document."""

    results = collection.get(
        where={"source": source}
    )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    combined = list(zip(metadatas, documents))

    combined.sort(
        key=lambda item: item[0].get("chunk_index", 0)
    )

    return [
        document
        for metadata, document in combined
    ]


def extract_json(text: str):
    """Extract JSON from an LLM response."""

    match = re.search(
        r"\[.*\]",
        text,
        re.DOTALL
    )

    if not match:
        raise ValueError(
            "Could not find valid JSON in model response."
        )

    return json.loads(match.group())


def generate_quiz(
    source: str,
    number_of_questions: int = 5
):
    """
    Generate MCQs using only the selected document.
    """

    chunks = get_document_chunks(source)

    if not chunks:
        raise ValueError(
            "No indexed content found for this document."
        )

    # Use representative chunks from across the document.
    if len(chunks) > 15:

        step = len(chunks) // 15

        selected_chunks = [
            chunks[i]
            for i in range(
                0,
                len(chunks),
                step
            )
        ][:15]

    else:

        selected_chunks = chunks

    context = "\n\n".join(
        selected_chunks
    )

    prompt = f"""
You are StudyBuddy, an academic quiz generator.

Create exactly {number_of_questions}
multiple-choice questions from ONLY the
study material below.

Rules:

1. Do not use outside knowledge.
2. Do not invent facts.
3. Each question must have exactly 4 options.
4. Only one option can be correct.
5. Questions should test understanding.
6. Use the terminology from the study material.
7. Return ONLY valid JSON.
8. Do not use Markdown.
9. The answer field must contain the
   number of the correct option.

Required JSON format:

[
  {{
    "question": "Question text",
    "options": [
      "Option 1",
      "Option 2",
      "Option 3",
      "Option 4"
    ],
    "answer": 1,
    "explanation": "Short explanation"
  }}
]

Study Material:
----------------
{context}
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

    quiz = extract_json(
        response["message"]["content"]
    )

    if not isinstance(quiz, list):
        raise ValueError(
            "Invalid quiz format."
        )

    return quiz


if __name__ == "__main__":

    print("================================")
    print("StudyBuddy Quiz Generator")
    print("================================")

    source = input(
        "Enter document name: "
    )

    try:

        quiz = generate_quiz(
            source,
            number_of_questions=5
        )

        print("\n========== QUIZ ==========\n")

        for index, question in enumerate(
            quiz,
            start=1
        ):

            print(
                f"{index}. "
                f"{question['question']}"
            )

            for option_index, option in enumerate(
                question["options"],
                start=1
            ):

                print(
                    f"   {option_index}. {option}"
                )

            print(
                f"Answer: "
                f"{question['answer']}"
            )

            print(
                f"Explanation: "
                f"{question['explanation']}\n"
            )

    except Exception as error:

        print(
            f"Error: {error}"
        )