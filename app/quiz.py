import json
import re

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

    return [
        document
        for metadata, document in combined
    ]


def extract_json(text: str):
    """Extract a JSON array from the model response."""

    text = text.strip()

    # Remove markdown code fences if present
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON array found in model response."
        )

    json_text = text[start:end + 1]

    return json.loads(json_text)


def validate_question(question):
    """
    Validate one generated MCQ.

    Returns:
        (True, None) if valid
        (False, reason) if invalid
    """

    if not isinstance(question, dict):
        return False, "Question is not an object."

    required_fields = [
        "question",
        "options",
        "answer",
        "explanation"
    ]

    for field in required_fields:

        if field not in question:

            return False, (
                f"Missing field: {field}"
            )

    # Question text
    question_text = str(
        question["question"]
    ).strip()

    if len(question_text) < 10:

        return False, "Question is too short."

    # Options
    options = question["options"]

    if not isinstance(options, list):

        return False, "Options are not a list."

    if len(options) != 4:

        return False, (
            f"Expected 4 options, got {len(options)}."
        )

    cleaned_options = []

    for option in options:

        option = str(option).strip()

        if not option:

            return False, "Empty option found."

        cleaned_options.append(
            option.lower()
        )

    # Duplicate options
    if len(set(cleaned_options)) != 4:

        return False, "Duplicate options found."

    # Correct answer
    try:

        answer = int(
            question["answer"]
        )

    except (ValueError, TypeError):

        return False, (
            "Answer must be a number from 1 to 4."
        )

    if answer not in [1, 2, 3, 4]:

        return False, (
            "Answer must be between 1 and 4."
        )

    # Explanation
    explanation = str(
        question["explanation"]
    ).strip()

    if len(explanation) < 10:

        return False, (
            "Explanation is too short."
        )

    # Normalize the data
    question["question"] = question_text
    question["options"] = [
        str(option).strip()
        for option in options
    ]
    question["answer"] = answer
    question["explanation"] = explanation

    return True, None

def validate_quiz(quiz):
    """
    Validate the complete quiz.
    """

    if not isinstance(quiz, list):
        return False, "Quiz is not a list."

    if len(quiz) == 0:
        return False, "Quiz is empty."

    valid_questions = []

    for index, question in enumerate(quiz, start=1):

        valid, reason = validate_question(question)

        if not valid:
            return False, (
                f"Question {index}: {reason}"
            )

        valid_questions.append(question)

    return True, valid_questions

def validate_answer_explanation(question):
    """
    Check that the explanation refers to the selected answer.
    """

    answer = question["answer"]
    selected_option = question["options"][answer - 1].lower()
    explanation = question["explanation"].lower()

    # Important words from the selected answer
    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        selected_option
    )

    # Remove generic words
    ignored = {
        "data",
        "database",
        "system",
        "using",
        "provides",
        "allows",
        "management"
    }

    meaningful_words = [
        word for word in words
        if word not in ignored
    ]

    matches = sum(
        1 for word in meaningful_words
        if word in explanation
    )

    # Require at least one meaningful connection
    if meaningful_words and matches == 0:
        return False, (
            "Explanation does not match the selected answer."
        )

    return True, None

def build_context(chunks, max_chunks=15):
    """
    Select representative chunks from across
    the document.
    """

    if len(chunks) <= max_chunks:

        selected = chunks

    else:

        step = len(chunks) / max_chunks

        selected = [
            chunks[
                int(i * step)
            ]
            for i in range(max_chunks)
        ]

    return "\n\n".join(selected)

def check_duplicate_questions(quiz):
    """Check whether the quiz contains duplicate questions."""

    seen = set()

    for question in quiz:

        normalized = normalize_question(
            question["question"]
        )

        if normalized in seen:

            return False, (
                f"Duplicate question found: "
                f"{question['question']}"
            )

        seen.add(normalized)

    return True, None

def normalize_question(text):
    """Normalize question text for duplicate detection."""

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text

def generate_quiz(
    source: str,
    number_of_questions: int = 5
):
    chunks = get_document_chunks(source)
    print("QUIZ DEBUG")
    print("Source:", source)
    print("Chunks found:", len(chunks))

    if not chunks:
        raise ValueError(
            "No indexed content found for this document."
        )

    context = build_context(chunks)

    last_error = None

    # Try up to 3 times
    for attempt in range(1, 3):

        prompt = f"""
You are an academic quiz generator for a college
learning application.

Create exactly {number_of_questions} multiple-choice
questions using ONLY the study material provided below.


CONTENT ACCURACY RULES:

1. Every question MUST be answerable directly from
   the study material.

2. The correct answer MUST be explicitly stated
   or directly described in the study material.

3. Do NOT infer the answer from general knowledge.

4. Do NOT create questions requiring comparison,
   interpretation, or reasoning beyond the material.

5. Do NOT create questions about information that
   is only implied.

6. Prefer questions based on explicit definitions,
   lists, examples, advantages, disadvantages,
   characteristics, and statements from the material.

7. The correct option MUST be supported by a specific
   statement in the study material.

8. The explanation MUST use the same meaning as the
   supporting statement.

9. If you cannot find clear support for a question
   and its answer in the study material, discard that
   question and create another one.

10. Avoid ambiguous questions.

11. Avoid questions containing:
    NOT
    EXCEPT
    FALSE
    INCORRECT
    LEAST
    MOST.

STRICT FORMAT RULES:

1. Create up to {number_of_questions} questions.

Quality is more important than quantity.

If there are not enough clearly supported questions,
create fewer questions rather than inventing answers.
2. Exactly 4 options for every question.
3. "answer" MUST be an integer.
4. "answer" MUST be exactly 1, 2, 3, or 4.
5. The answer number represents the position of the
   correct option in the options array.
6. Options must be unique.

IMPORTANT OPTION RULES:
- Never repeat an option.
- Do not use the same sentence with minor wording changes.
- Each option must represent a different possible answer.
- Before returning the question, compare all 4 options.
- If any two options mean the same thing, rewrite one.
- The four options must be clearly distinguishable.
7. Return ONLY valid JSON.
8. Do NOT use Markdown.

VERY IMPORTANT:

The answer number, selected option, and explanation
MUST describe exactly the same idea.

For example, if:

"answer": 2

then the explanation MUST explain option 2,
NOT option 1, 3, or 4.

Before returning each question:

1. Identify the correct option.
2. Set the answer number to that option's position.
3. Write the explanation specifically about that option.
4. Verify that the explanation does not describe another option.

Required format:

[
  {{
    "question": "What is a database?",
    "options": [
      "An organized collection of related data",
      "A programming language",
      "An operating system",
      "A computer network"
    ],
    "answer": 1,
    "explanation": "A database is an organized collection of related data."
  }}
]

Before returning each question, verify:

- The question is supported by the material.
- Exactly one option is correct.
- The answer number points to that option.
- The explanation describes that exact option.
- No other option could reasonably be correct.
Before returning the quiz, perform this final check
for EVERY question:

A. Are there exactly 4 options?
B. Are all 4 options different?
C. Does exactly 1 option answer the question?
D. Does the answer number point to that option?
E. Does the explanation describe that exact option?
F. Is the question directly supported by the study material?

If any answer is NO, regenerate that question before
returning the final JSON.

STUDY MATERIAL:
----------------
{context}
----------------
"""

        try:

            response = ollama.chat(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            raw_response = response[
                "message"
            ]["content"]

            quiz = extract_json(
                raw_response
            )

            # -----------------------------
            # VALIDATE QUIZ
            # -----------------------------

            valid, result = validate_quiz(
                quiz
            )

            if not valid:

                last_error = result

                print(
                    f"Attempt {attempt} failed validation: "
                    f"{result}"
                )

                continue
            print("VALID QUIZ GENERATED")
            print("Questions:", len(result))

            return result[:number_of_questions]

            # -----------------------------
            # CHECK DUPLICATES
            # -----------------------------

            duplicate_free, duplicate_error = (
                check_duplicate_questions(result)
            )

            if not duplicate_free:

                last_error = duplicate_error

                print(
                    f"Attempt {attempt} failed duplicate check: "
                    f"{duplicate_error}"
                )

                continue

            # -----------------------------
            # SUCCESS
            # -----------------------------
            print("VALID QUIZ GENERATED")
            print("Questions:", len(result))
            return result[
                :number_of_questions
            ]

        except Exception as error:

            last_error = str(error)

            print(
                f"Attempt {attempt} failed: "
                f"{error}"
            )

            continue

    # -----------------------------
    # ALL ATTEMPTS FAILED
    # -----------------------------

    raise ValueError(
        "Quiz generation failed after 3 attempts. "
        f"Last error: {last_error}"
    )


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

        print(
            "\n========== VALID QUIZ ==========\n"
        )

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
                f"Answer: {question['answer']}"
            )

            print(
                f"Explanation: "
                f"{question['explanation']}\n"
            )

    except Exception as error:

        print(
            f"\n❌ Quiz generation failed:"
        )

        print(error)