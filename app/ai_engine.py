import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Você é o Recruta Cidadão, assistente educativo sobre o Serviço Militar no Brasil.
Responda em português brasileiro, com linguagem simples, respeitosa e didática.
Use prioritariamente o CONTEXTO DOCUMENTAL fornecido. Não invente leis, prazos,
requisitos, endereços, procedimentos ou exceções. Não apresente suposições como fatos.
Se o contexto não permitir responder com segurança, diga claramente que não encontrou
informação suficiente e oriente o usuário a confirmar no portal oficial ou na Junta
de Serviço Militar. Diferencie Serviço Militar Inicial Obrigatório e Serviço Militar
Inicial Feminino voluntário quando pertinente. Não solicite CPF, senha, documentos
ou outros dados pessoais sensíveis no chat.
Quando usar o contexto, mencione o título da fonte de forma breve. Não crie links.
"""

def _ask(base_url: str, api_key: str, model: str, question: str, context: str) -> str:
    client = OpenAI(base_url=base_url, api_key=api_key, timeout=45.0)
    user_content = (
        f"CONTEXTO DOCUMENTAL:\n{context or 'Nenhum documento relevante foi localizado.'}"
        f"\n\nPERGUNTA DO USUÁRIO:\n{question}"
    )
    result = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return (result.choices[0].message.content or "").strip()

def generate_answer(question: str, context: str) -> tuple[str | None, str]:
    """Tenta Ollama local primeiro e OpenAI depois, se houver configuração."""
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    try:
        answer = _ask(ollama_url, "ollama", ollama_model, question, context)
        if answer:
            return answer, "ollama"
    except Exception as exc:
        logger.info("Ollama indisponível ou sem modelo: %s", exc)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            answer = _ask(
                "https://api.openai.com/v1",
                openai_key,
                os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                question,
                context,
            )
            if answer:
                return answer, "openai"
        except Exception as exc:
            logger.exception("Falha ao consultar OpenAI: %s", exc)

    return None, "indisponivel"
