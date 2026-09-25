const config = window.ESTAGIO_CONFIG;
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
        ${issue.body ? `<p>${escapeHtml(issue.body.replace(/[*_`]/g, "")).slice(0, 150)}</p>` : ""}
      </a>`).join("") : `<p class="empty">${escapeHtml(column.hint || "Sem tarefas.")}</p>`;
    const hint = cards.length && column.hint ? `<p class="hint">${escapeHtml(column.hint)}</p>` : "";
    return `<article class="column"><h2>${column.title} <span class="count">${cards.length}</span></h2>${hint}${items}</article>`;
  }).join("");
}

// Cartões da fila de PRs ([ID] no título) na ordem de data/fila.json; o resto
// depois, da issue mais antiga para a mais nova.
async function inQueueOrder(issues) {
  let order = [];
  try {
    order = (await (await fetch("data/fila.json")).json()).fila.map((item) => item.id);
  } catch {
    // sem a fila, só a ordem por número
  }
  const position = (issue) => {
    const match = issue.title.match(/^\[([A-Z]+-\d+)\]/);
    const index = match ? order.indexOf(match[1]) : -1;
    return index === -1 ? order.length + issue.number : index;
  };
  return [...issues].sort((a, b) => position(a) - position(b));
}

async function loadBoard() {
  const status = document.querySelector("#status");
  try {
    const response = await fetch(`https://api.github.com/repos/${config.owner}/${config.repo}/issues?state=all&per_page=100`);
    if (!response.ok) throw new Error(`GitHub respondeu ${response.status}`);
    const issues = (await response.json()).filter((item) => !item.pull_request);
    render(await inQueueOrder(issues));
    status.textContent = `${issues.length} tarefa(s) carregada(s) do GitHub.`;
  } catch (error) {
    render([]);
    status.textContent = `Não foi possível carregar as issues públicas: ${error.message}.`;
  }
}

loadBoard();
