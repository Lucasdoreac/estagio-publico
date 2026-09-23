const config = window.ESTAGIO_CONFIG;
const configured = !config.owner.startsWith("SEU_") && config.repo !== "estagio-publico";
const repoUrl = `https://github.com/${config.owner}/${config.repo}`;

document.title = config.title;
document.querySelector("#title").textContent = config.title;
document.querySelector("#description").textContent = config.description;
document.querySelector("#repository").href = repoUrl;
document.querySelector("#new-issue").href = `${repoUrl}/issues/new/choose`;

function escapeHtml(value = "") {
  const element = document.createElement("span");
  element.textContent = value;
  return element.innerHTML;
}

function render(issues) {
  const board = document.querySelector("#board");
  board.innerHTML = config.columns.map((column) => {
    const cards = issues.filter((issue) => issue.labels.some((label) => label.name === column.label));
    const items = cards.length ? cards.map((issue) => `
      <a class="card" href="${issue.html_url}" target="_blank" rel="noreferrer">
        <small>#${issue.number}</small>
        <h3>${escapeHtml(issue.title)}</h3>
        ${issue.body ? `<p>${escapeHtml(issue.body).slice(0, 150)}</p>` : ""}
      </a>`).join("") : '<p class="empty">Sem tarefas.</p>';
    return `<article class="column"><h2>${column.title} <span class="count">${cards.length}</span></h2>${items}</article>`;
  }).join("");
}

async function loadBoard() {
  const status = document.querySelector("#status");
  if (!configured) {
    const response = await fetch("data/board.json");
    render((await response.json()).issues);
    status.textContent = "Modo de demonstração: configure assets/config.js para conectar as issues públicas do repositório.";
    return;
  }
  try {
    const response = await fetch(`https://api.github.com/repos/${config.owner}/${config.repo}/issues?state=all&per_page=100`);
    if (!response.ok) throw new Error(`GitHub respondeu ${response.status}`);
    const issues = (await response.json()).filter((item) => !item.pull_request);
    render(issues);
    status.textContent = `${issues.length} tarefa(s) carregada(s) do GitHub.`;
  } catch (error) {
    render([]);
    status.textContent = `Não foi possível carregar as issues públicas: ${error.message}.`;
  }
}

loadBoard();
