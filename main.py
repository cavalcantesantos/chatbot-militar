from fastapi import FastAPI
from pydantic import BaseModel
import json
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# carregar FAQ
with open("faq.json", "r", encoding="utf-8") as f:
    faq = json.load(f)

def buscar_resposta(pergunta):
    for item in faq:
        if item["pergunta"].lower() in pergunta.lower():
            return item["resposta"]
    return None

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "online"}

@app.post("/chat")
def chat(msg: Message):
    resposta_base = buscar_resposta(msg.text)

    if resposta_base:
        return {"response": resposta_base}

    resposta = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Você responde dúvidas sobre serviço militar no Brasil. Seja direto e nunca invente."},
            {"role": "user", "content": msg.text}
        ]
    )

    return {"response": resposta.choices[0].message.content}