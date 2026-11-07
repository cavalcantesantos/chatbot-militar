# Recruta Cidadão — chatbot-militar

Assistente virtual educativo sobre o Serviço Militar no Brasil. Esta evolução preserva o backend original em FastAPI e o endpoint `POST /chat`, acrescentando interface web, FAQ com fontes, busca documental local e IA híbrida.

## Arquitetura

- **FAQ:** respostas diretas para perguntas cadastradas.
- **Documentos locais:** busca lexical simples em arquivos `.txt` e `.md` dentro de `documents/fontes_oficiais/`.
- **IA híbrida:** tenta Ollama local primeiro; se falhar, tenta OpenAI quando `OPENAI_API_KEY` estiver configurada.
- **Frontend:** HTML, CSS e JavaScript servidos pelo FastAPI.

> A busca documental desta primeira versão é lexical, não uma busca vetorial por embeddings. A camada foi isolada para permitir evolução futura para RAG vetorial.

## Requisitos

- Python 3.10 ou superior.
- Ollama instalado para IA local (opcional).
- Chave da OpenAI somente se desejar o provedor de contingência (opcional).

## Executar localmente

1. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows:
   .venv\\Scripts\\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Copie `.env.example` para `.env` e configure os provedores. O backend carrega automaticamente esse arquivo por meio de python-dotenv. Não preencha nem publique sua chave OpenAI no GitHub.

4. Para IA local, instale Ollama e baixe um modelo compatível:

   ```bash
   ollama pull llama3.2
   ```

   Mantenha o serviço Ollama em execução. Se não instalar Ollama, configure `OPENAI_API_KEY` para habilitar o provedor remoto como alternativa.

5. Inicie a aplicação:

   ```bash
   uvicorn main:app --reload
   ```

6. Abra http://127.0.0.1:8000. Documentação da API: http://127.0.0.1:8000/docs.

## Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Endpoint OpenAI-compatível do Ollama |
| `OLLAMA_MODEL` | `llama3.2` | Modelo local |
| `OPENAI_API_KEY` | vazio | Habilita fallback OpenAI |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Modelo remoto |

Nunca envie chaves de API ao GitHub. O arquivo `.env` está incluído no `.gitignore`.

## Adicionar documentos

Coloque documentos revisados em `documents/fontes_oficiais/`, nos formatos TXT ou Markdown. Registre título, órgão emissor, data de atualização e URL oficial dentro do próprio documento. PDFs ainda precisam ser convertidos para texto antes da indexação. O sistema não baixa nem valida automaticamente documentos externos.

## API

- `GET /`: interface web.
- `GET /health`: verificação de disponibilidade.
- `POST /chat`: recebe `{"text": "pergunta"}` e retorna `response`, `sources` e `mode`.

## Segurança e limites

- Não solicite nem armazene CPF, senhas ou documentos pessoais.
- Não use esta ferramenta para decidir situação individual, aptidão, seleção ou incorporação.
- As respostas são educativas; confirme prazos e procedimentos nos canais oficiais.
- Antes de disponibilizar publicamente, implemente rate limiting, proteção contra abuso, logs sem dados pessoais, HTTPS e política de privacidade.
- O modo híbrido não garante disponibilidade: se Ollama e OpenAI estiverem indisponíveis, o sistema informa que não conseguiu gerar resposta.

## Próximas evoluções

1. Ingestão segura de PDF e DOCX.
2. RAG com embeddings e banco vetorial.
3. Administração de FAQ/documentos.
4. Testes automatizados e implantação.
