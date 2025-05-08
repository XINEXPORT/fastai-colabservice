import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary_with_memory(question, chunks, history):
    context = "\n\n".join(chunks)
    history_prompt = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in history[-3:]])

    prompt = f"""
You are a smart financial assistant. Use the context below and the previous conversation to answer the current question.

Context:
{context}

Conversation so far:
{history_prompt}

User's current question:
{question}

Answer:"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.5
    )

    return response.choices[0].message.content
