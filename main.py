from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAIError
import openai
from pydantic import BaseModel
import tempfile
import shutil
import os

from services.pdf_reader import extract_text_chunks_from_pdf
from services.openai_chat import generate_summary_with_memory
from services.chart_generator import generate_revenue_chart, extract_chart_data

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


def generate_image(prompt: str) -> str:
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return response.data[0].url
    except OpenAIError as e:
        return None


@app.post("/analyze-pdf")
def analyze_pdf(
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

        data = extract_chart_data(answer)

        if len(data) < 2:
            followup_question = (
                "Can you list the annual revenue from FY20 to FY24 in the format: "
                "FY20: [value], FY21: [value], FY22: [value], FY23: [value], FY24: [value]?"
            )
            retry_answer = generate_summary_with_memory(followup_question, chunks, history=[[question, answer]])
            retry_data = extract_chart_data(retry_answer)

            if len(retry_data) >= 2:
                answer += "\n\n" + retry_answer
                data = retry_data

        if len(data) < 2:
            image_url = generate_image(f"Infographic illustration about: {answer}")
            return {
                "question": question,
                "answer": answer,
                "chart_available": False,
                "image_generated": bool(image_url),
                "image_url": image_url,
                "message": "No chartable data found. An illustrative image was generated instead." if image_url else "No chartable data or image available."
            }

        chart_path = "chart.png"
        with open(chart_path, "wb") as f:
            f.write(generate_revenue_chart(data).read())

        return {
            "question": question,
            "answer": answer,
            "chart_available": True,
            "chart_url": "/chart"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chart")
def get_chart():
    chart_path = "chart.png"
    if os.path.exists(chart_path):
        return FileResponse(chart_path, media_type="image/png", filename="chart.png")
    raise HTTPException(status_code=404, detail="Chart not found.")
