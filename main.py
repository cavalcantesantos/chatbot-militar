import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.ai_engine import generate_answer
from app.knowledge_base import retrieve_documents

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
FAQ_PATH = BASE_DIR / "faq.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recruta-cidadao")

app = FastAPI(
    title="Recruta Cidadão",
    description="Assistente virtual de orientação sobre o Serviço Militar no Brasil.",
    version="1.0.0",
)

def carregar_faq() -> list[dict[str, Any]]:
    import json

    try:
        with FAQ_PATH.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return dados if isinstance(dados, list) else []
    except (OSError, ValueError) as exc:
        logger.warning("Não foi possível carregar faq.json: %s", exc)
        return []

faq = carregar_faq()

def normalizar(texto: str) -> str:
    import re
    import unicodedata

    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", texto).strip()

def buscar_resposta(pergunta: str) -> dict[str, Any] | None:
    consulta = normalizar(pergunta)
    for item in faq:
        expressoes = [item.get("pergunta", "")] + item.get("aliases", [])
        for expressao in expressoes:
            termo = normalizar(expressao)
            if termo and termo in consulta:
                return item
    return None

class Message(BaseModel):
    text: str = Field(min_length=2, max_length=2000)

@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "online", "service": "recruta-cidadao", "version": "1.0.0"}

@app.post("/chat")
def chat(msg: Message):
    resposta_base = buscar_resposta(msg.text)
    if resposta_base:
        fonte = resposta_base.get("fonte")
        sources = [fonte] if fonte else []
        return {
            "response": resposta_base["resposta"],
            "sources": sources,
            "mode": "faq",
        }

    documentos = retrieve_documents(msg.text, top_k=3)
    contexto = "\n\n".join(
        f"FONTE: {item['title']}\nCONTEÚDO: {item['content']}"
        for item in documentos
    )

    resposta, provedor = generate_answer(msg.text, contexto)
    if not resposta:
        if documentos:
            resposta = (
                "Encontrei materiais que podem ajudar, mas não há um mecanismo de IA "
                "disponível neste momento para sintetizar uma resposta com segurança. "
                "Consulte as fontes abaixo ou tente novamente quando o serviço de IA estiver ativo."
            )
        else:
            resposta = (
                "Não encontrei uma resposta suficientemente fundamentada na base de conhecimento. "
                "Para evitar informações incorretas, consulte o portal oficial do Serviço Militar "
                "ou a Junta de Serviço Militar do seu município."
            )
        provedor = "sem_ia"

    return {
        "response": resposta,
        "sources": [
            {"title": item["title"], "url": item.get("url"), "type": item["type"]}
            for item in documentos
        ],
        "mode": provedor,
    }

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
