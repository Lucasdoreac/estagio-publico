window.ESTAGIO_CONFIG = {
  owner: "Lucasdoreac",
  repo: "estagio-publico",
  title: "Quadro público do estágio",
  description: "Acompanhe tarefas, entregas e decisões da squad.",
  columns: [
    { label: "status:ideia", title: "Ideias", hint: "Decisões e dados que dependem de pessoas; saem daqui quando resolvidos." },
    { label: "status:a-fazer", title: "A fazer", hint: "Entregas prontas na fila, esperando a anterior do mesmo repositório." },
    { label: "status:em-andamento", title: "Em andamento", hint: "Próxima entrega de cada repositório (pronta e testada) ou revisão pedindo mudança." },
    { label: "status:em-revisao", title: "Em revisão", hint: "Aberta na organização, aguardando revisão." },
    { label: "status:concluido", title: "Concluído", hint: "Aceita na organização (merge). Nenhuma ainda: aparece aqui assim que a primeira for aceita." }
  ]
};
