# Especificação do produto: reserva e alocação de espaços UDF

## Propósito

Disponibilizar uma aplicação institucional para pesquisar, reservar, aprovar e
alocar salas e laboratórios, com transparência sobre disponibilidade e proteção
dos dados das pessoas que solicitam os espaços.

## Premissas confirmadas

- O produto abrange gestão de salas e laboratórios.
- Deve permitir reserva e alocação de espaços.
- Deve ser utilizável na instituição e priorizar ferramentas gratuitas ou de
  código aberto quando isso for viável.

## Limite da demonstração pública

O GitHub Pages deste repositório é a vitrine pública do projeto: documentação,
agenda não identificável e planejamento por Issues. Reservas reais, aprovação,
dados de contato, autenticação e auditoria precisam de uma aplicação com API e
banco de dados próprios.

## Estado atual (setembro de 2026)

O sistema de reservas já existe nos repositórios da LabTechUDF e roda de ponta a
ponta em ambiente de desenvolvimento, com testes automáticos. Ainda não está
implantado para uso real: falta definir a hospedagem.

- **Pesquisa de disponibilidade: parcial.** Salas livres por data e horário, busca
  por nome da sala. Filtros de capacidade, recursos e acessibilidade ainda não.
- **Pedido avulso: existe.** Assistente em etapas, com rascunho salvo.
- **Conflito: existe.** Um segundo pedido para a mesma sala e horário é recusado,
  inclusive com pedidos simultâneos.
- **Aprovação: existe.** Palestra e oficina passam pela Coordenação e depois pela
  Reitoria, por link no e-mail de uso único; aula e prova são aprovadas direto,
  com aviso por e-mail à Reitoria. A Coordenação pode pedir mudança; o formulário
  para a pessoa solicitante atender o pedido está em revisão.
- **Aulas do semestre ocupando salas: aguarda dados.** Passam a bloquear salas
  assim que o calendário acadêmico informar o dia da semana de cada turma.
- **Ainda não:** reserva recorrente, cancelamento e remarcação, bloqueio e
  realocação, check-in e ausência, relatórios.
- **Auditoria: parcial.** Registros técnicos sem dados sensíveis; trilha por ação
  ainda não.

Como é construído hoje: interface em React; API em Python (Flask); MongoDB; entrada
por link enviado ao e-mail institucional (@udf.edu.br), sem senha; catálogo de
salas, cursos e turmas como serviço próprio (REST e GraphQL, com chave de acesso);
PDF do pedido em armazenamento compatível com S3.

## Requisitos funcionais

1. Cadastrar espaços com campus, localização, tipo, capacidade, equipamentos,
   características de acessibilidade, horários de funcionamento e estado.
2. Pesquisar disponibilidade por data, horário, campus, capacidade, tipo,
   recurso e acessibilidade.
3. Criar solicitações avulsas e recorrentes.
4. Detectar sobreposição de reservas, bloqueios e indisponibilidades.
5. Oferecer alternativas compatíveis quando houver conflito.
6. Encaminhar solicitações para aprovação conforme regra configurável.
7. Permitir cancelar, remarcar e acompanhar o estado da solicitação.
8. Bloquear espaços para manutenção, segurança ou evento institucional.
9. Apoiar realocação de reservas afetadas por bloqueio posterior.
10. Registrar check-in e ausência quando a política institucional o adotar.
11. Produzir relatórios agregados de ocupação, conflitos, ausências e capacidade.
12. Registrar auditoria das mudanças relevantes.

## Estados

`rascunho → solicitada → em análise → aprovada | recusada | cancelada`

Após o horário reservado, uma reserva aprovada pode terminar como `utilizada`,
`ausência` ou `concluída`, conforme a política de check-in escolhida.

## Política a decidir com a UDF

- Quem pode solicitar e quem pode aprovar cada categoria de espaço.
- Ordem de prioridade entre aula, atividade acadêmica, evento, laboratório,
  acessibilidade e outros usos.
- Antecedência mínima e máxima, prazo de cancelamento e limites de recorrência.
- Situações que dispensam aprovação manual.
- Critério para liberar um espaço quando não há check-in.
- Período de retenção dos dados e responsáveis pela administração.

## Segurança e privacidade

- A agenda pública só apresenta disponibilidade e informação operacional sem
  identificação de solicitantes.
- Reservas e dados de usuários exigem autenticação e autorização por perfil.
- Senhas, tokens e dados pessoais não entram no repositório, Issues ou GitHub
  Pages.
- Cada criação, aprovação, cancelamento, bloqueio e realocação deve gerar um
  evento de auditoria.

## Arquitetura de referência

1. Portal público estático: GitHub Pages para documentação, backlog e agenda
   anonimizada.
2. Aplicação autenticada: interface para solicitantes, aprovadores e gestores.
3. API: aplica autorização, regras de conflito, filas e notificações.
4. Banco de dados: hoje MongoDB. Espaços, horários, reservas, séries, bloqueios e
   auditoria continuam sendo as entidades necessárias, independentemente do banco.
5. Integrações futuras: identidade institucional e calendário, somente após
   requisitos e autorização definidos.

## Critérios de aceite do MVP

- Um espaço disponível pode ser encontrado pelos filtros fundamentais.
- Uma solicitação válida não cria uma dupla ocupação.
- O aprovador recebe somente as solicitações sob sua responsabilidade.
- Uma reserva aprovada aparece na agenda autenticada e na disponibilidade
  pública sem expor a pessoa solicitante.
- Cancelamento e bloqueio atualizam a disponibilidade e deixam auditoria.
- Os fluxos principais funcionam com teclado e informações acessíveis.
