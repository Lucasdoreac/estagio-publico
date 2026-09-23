# Estágio Público

Um quadro público, sem login, para acompanhar o trabalho da squad. O site usa
issues públicas do GitHub como fonte de verdade e as organiza por rótulos de
status.

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
3. Crie estes rótulos nas issues:
   - `status:ideia`
   - `status:a-fazer`
   - `status:em-andamento`
   - `status:em-revisao`
   - `status:concluido`
4. Ative GitHub Pages em **Settings → Pages → GitHub Actions**.

Cada push para `main` publica o site em `https://<owner>.github.io/<repo>/`.

## Limites deliberados

GitHub Pages é estático: ele não substitui permissões, fluxos privados,
automação interna ou notificações do Jira. Para um estágio público isso é uma
vantagem: não há contas de alunos nem dados pessoais no quadro. Use GitHub
Issues para contribuição e GitHub Actions para automações abertas.
