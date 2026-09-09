import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text for better RAG retrieval.
    """

    # Remove repeated DBMS notes header/footer
    text = re.sub(
        r"\d+\s*\|\s*P\s*a\s*g\s*e\s*D\s*B\s*M\s*S\s*N\s*O\s*T\s*E\s*S\s*B\s*Y\s*M\s*S\s*\.\s*D\s*E\s*E\s*P\s*I\s*K\s*A\s*S\s*A\s*H\s*U.*?(?=\n|$)",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Fix spaces around punctuation
    text = re.sub(r"\s+([,.;:])", r"\1", text)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[str]:
    """
    Split text into overlapping chunks while trying
    to preserve paragraph and sentence boundaries.
    """

    if not text:
        return []

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # If adding paragraph stays within chunk size
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            current_chunk += paragraph + "\n\n"

        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            # Handle paragraphs larger than chunk size
            if len(paragraph) > chunk_size:

                start = 0

                while start < len(paragraph):

                    end = start + chunk_size

                    chunk = paragraph[start:end]

                    chunks.append(chunk.strip())

                    start = end - overlap

            else:
                current_chunk = paragraph + "\n\n"

    # Add remaining text
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


if __name__ == "__main__":
    from pdf_processor import extract_text_from_pdf

    pdf_file = input("Enter PDF path: ")

    try:
        raw_text = extract_text_from_pdf(pdf_file)

        cleaned_text = clean_text(raw_text)

        chunks = chunk_text(cleaned_text)

        print("\n========== RESULTS ==========\n")

        print(f"Raw characters     : {len(raw_text)}")
        print(f"Cleaned characters : {len(cleaned_text)}")
        print(f"Number of chunks   : {len(chunks)}")

        print("\n========== FIRST CHUNK ==========\n")
        print(chunks[0])

        print("\n========== SECOND CHUNK ==========\n")
        if len(chunks) > 1:
            print(chunks[1])

    except Exception as error:
        print(f"Error: {error}")