# Estágio Público

Vitrine pública, sem login, do trabalho de estágio no sistema de reservas de salas
da UDF (repositórios da [LabTechUDF](https://github.com/LabTechUDF)). Nada aqui
identifica pessoas: sem nomes, e-mails ou contas.

Site: https://lucasdoreac.github.io/estagio-publico/

| Página | O que mostra | De onde vem |
|---|---|---|
| [Quadro](index.html) | Cada entrega (PR) e cada pendência, por situação | Issues deste repositório, mantidas pela Action `sync-quadro` |
| [Modelo do sistema](modelo.html) | Como o sistema é hoje, o que falta e o que é só ideia | Conferido no código; versão em texto: [docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md) |
| [Evidências de testes](evidencias.html) | Suíte de testes medida na versão final de cada entrega | `data/fila.json` + quadro |

## Como o quadro se atualiza

O trabalho vai para a organização como uma fila de PRs, feitos a partir de um
fork. `data/fila.json` lista a fila (id, repositório, título, issues que fecha,
dependências e o resultado da suíte medido em container limpo) e
`data/pendencias.json`, o que depende de decisão ou dado de pessoas. Os dois são
gerados fora deste repositório e publicados aqui.

A Action `.github/workflows/sync-quadro.yml` (mesmo desenho do
[CoOps](https://github.com/LabTechUDF/CoOps): Action agendada + `GITHUB_TOKEN` +
API pública do GitHub) roda a cada 6 horas, a cada mudança nesses arquivos e sob
demanda. `scripts/sync_quadro.py` mantém uma issue por item:

| Coluna | O que entra |
|---|---|
| Ideias | Pendências que dependem de decisão ou dado de pessoas (fecham quando resolvidas) |
| A fazer | PRs da fila esperando o anterior do mesmo repositório |
| Em andamento | Próximo PR de cada repositório (pronto e testado) ou PR com mudança pedida na revisão |
| Em revisão | PR aberto na organização |
| Concluído | PR aceito (merge) e pendência resolvida |

O quadro lê as issues direto da API ao abrir a página. Teste local sem escrever
nada:
`GH_TOKEN=$(gh auth token) GITHUB_REPOSITORY=<dono>/estagio-publico GITHUB_REPOSITORY_OWNER=<dono> python scripts/sync_quadro.py --dry-run`.

O GitHub desliga Actions agendadas de repositório público sem commits por 60
dias; um push em `data/` (ou "Run workflow") religa.
