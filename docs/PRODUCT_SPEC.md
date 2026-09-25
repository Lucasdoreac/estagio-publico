# Sistema de reservas de salas da UDF: como é, o que falta e o que é ideia

Conferido no código dos repositórios da LabTechUDF. O que está em **Ideias ainda
sem decisão** não foi pedido nem validado pela UDF. Versão para leitura:
[modelo.html](../modelo.html).

## Escopo confirmado

- O sistema gerencia salas e laboratórios e permite reserva e alocação.
- Utilizável no contexto da instituição, com ferramentas gratuitas ou abertas.

## Estado atual (setembro de 2026)

O sistema de reservas já existe nos repositórios da LabTechUDF e roda de ponta a
ponta em ambiente de desenvolvimento, com testes automáticos. Ainda não está
implantado para uso real: falta definir a hospedagem. "Em revisão" = pronto e
testado, aguardando aceitação no repositório da organização.

- **Pesquisa de disponibilidade: parcial.** Salas livres por data e horário, busca
  por nome da sala. Filtros de capacidade, recursos e acessibilidade ainda não.
- **Pedido avulso: existe.** Assistente em etapas, com rascunho salvo. Data ou
  horário que já passou é recusado; a agenda só oferece períodos que ainda não
  começaram (em revisão).
- **Conflito: existe.** Um segundo pedido para a mesma sala e horário é recusado,
  inclusive com pedidos simultâneos.
- **Aprovação: existe.** Palestra e oficina passam pela Coordenação e depois pela
  Reitoria, por link no e-mail de uso único; aula e prova são aprovadas direto,
  com aviso por e-mail à Reitoria. A Coordenação pode pedir mudança escrevendo o
  que precisa mudar; a pessoa solicitante recebe a mensagem por e-mail, com o link
  para editar e reenviar, e a vê na lista dos seus eventos (em revisão).
- **Aulas do semestre ocupando salas: parcial.** Aula com dia da semana definido
  bloqueia a sala. Tela para marcar os dias de cada turma, restrita a quem a UDF
  indicar (em revisão); o calendário acadêmico com os dias de todas as turmas
  ainda não foi entregue.
- **Ainda não:** reserva recorrente, cancelamento e remarcação, bloqueio e
  realocação, check-in e ausência, relatórios.
- **Auditoria: parcial.** Registros técnicos sem dados sensíveis; trilha por ação
  ainda não.

Como é construído hoje: interface em React; API em Python (Flask); MongoDB; entrada
por link enviado ao e-mail institucional (@udf.edu.br), sem senha; catálogo de
salas, cursos e turmas como serviço próprio (REST e GraphQL, com chave de acesso);
PDF do pedido em armazenamento compatível com S3.

## Quem usa

- **Pessoa solicitante:** entra pelo link enviado ao e-mail institucional
  (@udf.edu.br), cria o evento em etapas, escolhe data, período e sala livre e
  acompanha seus eventos.
- **Coordenação do curso:** recebe o pedido de palestra ou oficina por e-mail e
  aprova, recusa ou pede mudança, por link de uso único.
- **Reitoria:** aprovação final de palestras e oficinas; é avisada das aulas e
  provas.
- **Quem marca os dias das aulas:** pessoas indicadas pela UDF (lista configurada
  no sistema) marcam o dia da semana de cada turma (em revisão).

Não há conta de visitante, gestor de espaço nem administrador. O login não tem
senha nem papéis: Coordenação e Reitoria agem pelos links dos e-mails.

## Caminho de um pedido

`rascunho → aguardando → aprovado | recusado pela Coordenação → aprovado | recusado pela Reitoria`

Esse é o caminho de palestra e oficina. Aula e prova são aprovadas direto ao
enviar, com aviso à Reitoria. Com pedido de mudança, o evento fica em
`mudança pedida` e volta para a Coordenação quando é reenviado. A sala fica
reservada desde o envio; um segundo pedido para a mesma sala e horário é recusado.

## Dados que o sistema guarda

- **Evento:** tipo (palestra, oficina, aula, prova), título, descrição, curso, ODS,
  público-alvo, participantes, recursos, logo, organizador e estado.
- **Reserva:** sala, evento, início e fim.
- **Sala e campus:** número da sala e campus. Sem capacidade, recursos nem
  acessibilidade no catálogo.
- **Curso, disciplina, professor e oferta:** catálogo da UDF; a oferta tem sala,
  período e, quando marcados, os dias da semana.
- **Token de aprovação:** link de uso único para Coordenação e Reitoria.

## Pendências que dependem de pessoas

Hospedagem; coordenador de cada curso; calendário acadêmico; painel de pendências
para Coordenação e Reitoria; substituto do armazenamento de arquivos; modelo de
grade da Alocação de Professores. Ficam na coluna Ideias do quadro até serem
resolvidas.

## Ideias ainda sem decisão

- Filtros de capacidade, recursos e acessibilidade (exigem cadastrar esses dados).
- Reserva recorrente.
- Cancelar e remarcar pela própria pessoa solicitante.
- Bloqueio de sala e realocação de reservas afetadas.
- Agenda pública de disponibilidade, sem identificar quem reservou.
- Check-in, relatórios de ocupação e trilha de auditoria por ação.

## Privacidade

O site e o quadro não mostram nomes, e-mails nem contas. No sistema, só entra
quem tem e-mail institucional; os links de aprovação valem uma vez; tokens e
chaves não vão para os logs.
