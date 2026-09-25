// Evidências de testes: lê data/fila.json (suíte medida na ponta de cada PR) e, se
// der, o quadro público (issues "[ID] ..." com rótulo status:*) para a situação.
const cfg = window.ESTAGIO_CONFIG;
const SERVICO = { "shared-resources": "Catálogo e login", "python-services": "API de reservas",
  "interfaces-usuario": "Interface", "teachers-allocation": "Alocação de professores",
  "supreme-test-framework": "Teste no navegador" };
const SITUACAO = { "status:a-fazer": ["na fila", "none"], "status:em-revisao": ["em revisão", "rev"],
  "status:concluido": ["aceito", "done"] };

const esc = (v = "") => { const s = document.createElement("span"); s.textContent = v; return s.innerHTML; };

// "internal:verde (13 passed, 8 warnings) auth:verde (4 passed)" -> [{nome, ok, n}]
function suites(texto) {
  return [...(texto || "").matchAll(/(\w+):(verde|falhando) \((?:Tests)?\s*(\d+) passed/g)]
    .map(([, nome, estado, n]) => ({ nome, ok: estado === "verde", n: Number(n) }));
}

function suiteHtml(texto) {
  const s = suites(texto);
  if (!s.length) return `<span class="tag none">sem suíte</span>`;
  return s.map((x) => `<span class="tag ${x.ok ? "ok" : "fail"}">${esc(x.nome)}: ${x.ok ? "verde" : "falhando"} (${x.n})</span>`).join(" ");
}

async function situacoes() {
  try {
    const r = await fetch(`https://api.github.com/repos/${cfg.owner}/${cfg.repo}/issues?state=all&per_page=100&labels=fila-pr`);
    if (!r.ok) return {};
    const out = {};
    for (const issue of await r.json()) {
      const id = (issue.title.match(/^\[([A-Z]+-\d+)\]/) || [])[1];
      const label = issue.labels.map((l) => l.name).find((n) => SITUACAO[n]);
      if (id && label) out[id] = SITUACAO[label];
    }
    return out;
  } catch { return {}; }
}

async function main() {
  const fila = (await (await fetch("data/fila.json")).json()).fila;
  const sit = await situacoes();

  // Resumo: a última entrega de cada serviço tem a suíte mais completa.
  const ultima = {};
  fila.forEach((item) => { if (suites(item.suite).length) ultima[item.repo] = item; });
  const verdes = fila.filter((i) => suites(i.suite).length && suites(i.suite).every((s) => s.ok)).length;
  const medidas = fila.filter((i) => suites(i.suite).length).length;
  const cards = [`<article class="panel"><strong>${fila.length}</strong><span>entregas na fila</span></article>`,
    `<article class="panel"><strong>${verdes}/${medidas}</strong><span>com suíte medida e verde</span></article>`];
  for (const [repo, item] of Object.entries(ultima)) {
    const total = suites(item.suite).reduce((a, s) => a + s.n, 0);
    cards.push(`<article class="panel"><strong>${total}</strong><span>testes: ${esc(SERVICO[repo] || repo)} (${esc(item.id)})</span></article>`);
  }
  document.querySelector("#resumo").innerHTML = cards.join("");

  document.querySelector("#linhas").innerHTML = fila.map((item) => {
    const [txt, cls] = sit[item.id] || ["na fila", "none"];
    return `<tr><td><b>${esc(item.id)}</b></td><td>${esc(SERVICO[item.repo] || item.repo)}</td>
      <td>${esc(item.titulo)}</td><td class="suite">${suiteHtml(item.suite)}</td>
      <td><span class="tag ${cls}">${txt}</span></td></tr>`;
  }).join("");
}

main().catch(() => {
  document.querySelector("#linhas").innerHTML = `<tr><td colspan="5">Não foi possível carregar os dados.</td></tr>`;
});
