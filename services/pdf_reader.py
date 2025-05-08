import fitz 

def extract_text_chunks_from_pdf(filepath: str, max_pages: int = 5) -> list:
    doc = fitz.open(filepath)
    text_chunks = []

    for page in doc[:max_pages]:
        text = page.get_text().strip()
        if text:
            text_chunks.append(text)

    return text_chunks
