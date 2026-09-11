from pathlib import Path

from pdf_processor import extract_text_from_pdf
from text_cleaner import clean_text, chunk_text
from vector_store import add_chunks


def ingest_pdf(pdf_path: str):

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    print("\n[1/4] Extracting PDF text...")

    raw_text = extract_text_from_pdf(str(path))

    print(f"Extracted {len(raw_text)} characters.")

    print("\n[2/4] Cleaning text...")

    cleaned_text = clean_text(raw_text)

    print(f"Cleaned text: {len(cleaned_text)} characters.")

    print("\n[3/4] Creating chunks...")

    chunks = chunk_text(cleaned_text)

    print(f"Created {len(chunks)} chunks.")

    print("\n[4/4] Creating embeddings and storing in ChromaDB...")

    add_chunks(
        chunks=chunks,
        source=path.name
    )

    print("\n================================")
    print("PDF INGESTION COMPLETE")
    print("================================")


if __name__ == "__main__":

    pdf_file = input(
        "Enter PDF path: "
    )

    try:
        ingest_pdf(pdf_file)

    except Exception as error:
        print(f"\nError: {error}")