const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");
const send = document.querySelector("#send");
const messages = document.querySelector("#messages");

function addMessage(text, role, sources = []) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "assistant" ? "RC" : "Você";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  bubble.appendChild(paragraph);

  if (sources.length) {
    const sourceBox = document.createElement("div");
    sourceBox.className = "sources";
    const label = document.createElement("strong");
    label.textContent = "Fontes consultadas";
    sourceBox.appendChild(label);
    sources.forEach((source) => {
      const line = document.createElement("div");
      const title = source.title || "Documento consultado";
      if (source.url && /^https:\/\//i.test(source.url)) {
        const link = document.createElement("a");
        link.href = source.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = title;
        line.appendChild(link);
      } else {
        line.textContent = title;
      }
      sourceBox.appendChild(line);
    });
    bubble.appendChild(sourceBox);
  }
  article.append(avatar, bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

async function ask(question) {
  addMessage(question, "user");
  const waiting = addMessage("Estou consultando as informações disponíveis...", "assistant");
  send.disabled = true;
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: question })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Não foi possível processar sua pergunta.");
    waiting.remove();
    addMessage(data.response || "Não recebi uma resposta.", "assistant", data.sources || []);
  } catch (error) {
    waiting.remove();
    addMessage(error.message || "Ocorreu um erro. Tente novamente.", "assistant");
  } finally {
    send.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  input.value = "";
  ask(question);
});

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => ask(button.dataset.question));
});
