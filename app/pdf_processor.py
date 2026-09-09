import pymupdf
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from all pages of a PDF.
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = pymupdf.open(path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


if __name__ == "__main__":
    pdf_file = input("Enter PDF path: ")

    try:
        text = extract_text_from_pdf(pdf_file)

        print("\n--- Extracted Text ---\n")
        print(text[:5000])

        print(f"\nTotal characters: {len(text)}")

    except Exception as error:
        print(f"Error: {error}")