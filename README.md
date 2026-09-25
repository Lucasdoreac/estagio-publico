# Estágio Público

Um quadro público, sem login, para acompanhar o trabalho da squad. O site usa
issues públicas do GitHub como fonte de verdade e as organiza por rótulos de
status.

O site também publica o [modelo do sistema de reserva e alocação de salas e
laboratórios](modelo.html), com os casos de uso, regras propostas, limites de
privacidade e decisões que ainda dependem de validação. A versão detalhada para
implementação está em [docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md).

## Como funciona

- Pessoas podem acompanhar o quadro no GitHub Pages sem uma conta GitHub.
- Quem tem conta GitHub pode abrir uma solicitação pela página **Nova tarefa**.
- Membros da squad administram o trabalho no próprio GitHub: issues, comentários,
  rótulos, marcos e pull requests.
- O site apenas lê issues públicas. Ele não armazena dados de participantes,
  contatos ou credenciais.

## Preparar o repositório

1. Crie um repositório público chamado `estagio-publico`.
2. Em `assets/config.js`, troque `owner` e `repo` pelos valores do repositório.
3. Os rótulos `status:ideia`, `status:a-fazer`, `status:em-andamento`,
   `status:em-revisao` e `status:concluido` são criados pela Action
   `sync-quadro` na primeira execução.
4. Ative GitHub Pages em **Settings → Pages → GitHub Actions**.

Cada push para `main` publica o site em `https://<owner>.github.io/<repo>/`.

## Automação: cartões dos PRs

Mesmo desenho do [CoOps](https://github.com/LabTechUDF/CoOps): uma GitHub Action
agendada lê a API pública do GitHub com o `GITHUB_TOKEN` e grava o resultado no
próprio repositório.

- `data/fila.json` lista os PRs planejados para os repositórios da LabTechUDF
  (id, repositório, título, issues que fecha, dependências e o resultado da suíte
  medido localmente). Sem nomes nem contatos.
- `.github/workflows/sync-quadro.yml` roda a cada 6 horas, a cada mudança na fila
  e sob demanda. Para cada item, `scripts/sync_quadro.py` procura o PR na org e
  mantém um cartão (issue com o rótulo `fila-pr`):
  sem PR → **A fazer**; PR aberto → **Em revisão** (com link); PR aceito →
  **Concluído** (issue fechada); PR fechado sem merge → volta para **A fazer**.
- O quadro lê as issues direto da API ao abrir a página: não precisa republicar.
- Teste local sem escrever nada:
  `GITHUB_REPOSITORY=<dono>/estagio-publico GITHUB_REPOSITORY_OWNER=<dono> python scripts/sync_quadro.py --dry-run`.

O GitHub desliga Actions agendadas de repositório público sem commits por 60
dias; um push na fila (ou "Run workflow") religa.

## Limites deliberados

GitHub Pages é estático: ele não substitui permissões, fluxos privados,
automação interna ou notificações do Jira. Para um estágio público isso é uma
vantagem: não há contas de alunos nem dados pessoais no quadro. Use GitHub
Issues para contribuição e GitHub Actions para automações abertas.
