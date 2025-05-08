from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from services.pdf_reader import extract_text_chunks_from_pdf
from services.openai_chat import generate_summary_with_memory
import tempfile
import shutil

app = FastAPI()

@app.post("/ask-pdf")
def ask_question_about_pdf(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            shutil.copyfileobj(file.file, temp_pdf)
            temp_path = temp_pdf.name


        chunks = extract_text_chunks_from_pdf(temp_path)


        answer = generate_summary_with_memory(question, chunks, history=[])

        return {"question": question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
