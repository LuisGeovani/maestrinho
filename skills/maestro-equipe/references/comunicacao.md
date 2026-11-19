# Comunicação com os terminais

Protocolo para o despacho chegar, o produtor saber o que fazer e o retorno voltar inteiro, sem gastar o contexto do Maestro. Resultados dos testes que embasam isto: `docs/testes/` do repositório da skill.

## 1. Nomes

- **Seu nome** para o ask back é o que aparece em `You:` no `maestri list` (ex.: "Claude Code", "Maestro"). Nunca assuma "Maestro". O `maestri_batch.py` descobre sozinho.
- **Nomes dos produtores:** exatamente como o `maestri list` imprime; de outro workspace, `Nome @ Workspace`.

## 2. Despachar

Escreva o despacho em `.maestri/despachos/<rodada>.md` (Write) ou passe pelo stdin, e rode **em background**:

```
python <skill>/scripts/maestri_batch.py .maestri/despachos/R03.md
```

Formato (texto puro; aspas, acentos e `C:\caminhos` vão como estão):

```
Contexto comum opcional: vai no início de todos os prompts.
### Prisma | R03-T1
<prompt da tarefa>
### Faísca | R03-T2
<prompt da tarefa>
```

O script confere se os destinos estão conectados, **espera cada terminal ficar pronto** (tela estável com o campo de prompt; até 90 s), cria `.maestri/relatorios/`, acrescenta a cada prompt o **rodapé de relatório** com o seu nome real, monta o JSON com o escape certo, envia com `maestri ask --batch` (dividindo lotes grandes por causa do limite de linha de comando do Windows) e resume cada retorno lendo o STATUS do arquivo de relatório. `--mostrar` só imprime os prompts finais, sem enviar.

Por que esperar: nos testes, despachar para um terminal que ainda abria (logo após `recruit` ou `--replace`) **perdeu o Enter** (o texto ficou parado na caixa de entrada) ou **cortou o começo** do prompt. Se mesmo assim o texto ficar parado, o script manda um Enter e espera o arquivo de relatório. Pedido de confiança de pasta na tela: o script não envia e avisa.

Nunca:
- monte JSON na mão nem passe o prompt como argumento de `maestri ask` com caminho do Windows: o CLI decodifica `\n` e `\t` nos argumentos (`C:\novo` vira quebra de linha);
- reenvie um prompt porque o `ask` demorou: rode `maestri check "Nome"` uma vez e espere.

## 3. Retorno: relatório em arquivo + aviso curto

Cada produtor, ao terminar (ou ao bloquear):
1. grava o relatório completo em `.maestri/relatorios/<ID>.md` (TAREFA, STATUS, ARQUIVOS, VALIDAÇÃO, PENDÊNCIAS, VISÃO opcional);
2. avisa com `maestri ask "<seu nome>" "<ID> <pronto|parcial|bloqueado>: .maestri/relatorios/<ID>.md"`.

Por que assim: o aviso curto não tem aspas internas (o PowerShell 5.1 come aspas de argumentos), nem barras invertidas (`\n`/`\t`), nem tamanho para cortar; o relatório completo fica em disco para o revisor ler direto e para auditoria. O aviso resolve o `ask` pendente do lote, então a notificação do background chega com o status.

IDs: use um ID novo para cada rodada de correção (`R03-T1-C1`), para não confundir com o relatório anterior.

## 4. Esperar sem gastar

- Depois de despachar: responda ao usuário em poucas linhas e **encerre o turno**. Sem polling, sem `sleep`, sem `maestri check` em loop.
- Quando a notificação do background chegar, leia só o resumo do script. Casos:

| O resumo diz | Faça |
|---|---|
| `pronto` / `parcial` (+ `veredito` em revisão) | leia o relatório (só o necessário para decidir) |
| `bloqueado` | leia o motivo no relatório; produtor que recebeu despacho cortado ou vago reporta bloqueado: reenvie completo |
| NÃO ENVIADO, pedido de confiança de pasta | `maestri ask "Nome" --raw "\r"`, confira com `check` e rode o despacho de novo só para ele |
| relatório ANTERIOR a este despacho | o produtor não gravou o novo: `maestri check "Nome"` uma vez; use ID novo por rodada |
| PENDENTE, pedido de permissão | `maestri check "Nome"`; dentro do escopo, aprove uma vez (`maestri ask "Nome" --raw "\r"` ou a tecla da opção); fora, negue ou pergunte ao usuário |
| terminou sem relatório (tela mostra outra coisa, ex.: comando do usuário) | o despacho se perdeu: confira com `git status` que nada mudou e reenvie |
| ERRO / sem resposta em N min | `maestri check "Nome"`; se travou, `maestri recruit "Nome" --preset P --replace "Nome"` e reenvie |

- Avisos que chegam enquanto você está ocupado ficam na fila e entram como mensagens novas.
- Se precisar esperar algo fora do lote, espere pelo **arquivo** (`.maestri/relatorios/<ID>.md`), nunca por um texto na tela do terminal: a tela rola e o texto some.

## 5. Perguntar ao usuário

- **Com tarefa em andamento, não abra diálogo de pergunta (AskUserQuestion):** o aviso de um terminal é digitado no seu terminal e pode responder ou fechar o diálogo. Faça a pergunta em texto, no fim da resposta, e continue só o que não depende dela.
- Sem nada em andamento, o diálogo é o melhor jeito (opção recomendada primeiro).

## 6. Permissões dos produtores

- **Aprovar (uma vez):** leitura; edição e comandos dentro das pastas da tarefa; build, teste, lint; o próprio `maestri ask` de aviso; dependência que a tarefa pediu e existe no registro oficial.
- **Negar:** escrita fora do escopo; git feito por produtor; pacote ou `npx` não pedido; `.env` reais, chaves, credenciais; rede para destino desconhecido; comando destrutivo; mudança de configuração global; controle do computador.
- Na dúvida, pergunte ao usuário. "Sempre permitir" só para padrões seguros e repetidos.

## 7. Notas do Maestri como quadro

- Quadro da rodada: `maestri note create --name "Quadro RNN" --stack "Rodadas"`; **só o Maestro escreve** (`maestri note edit`), a partir dos relatórios. Modelo em `documentos.md`.
- Brief grande e estável (contrato, decisões): nota própria, travada pelo usuário, e o despacho cita o nome da nota (o produtor precisa estar conectado a ela: `maestri connect "Brief" "Nome"`).

## 8. Quando o Maestri falha

- Qualquer erro de conexão ou pipe: `maestri debug` primeiro.
- Agente em floor ou workspace descarregado é acordado pelo `ask`; se disser que ainda está iniciando, o script reenvia uma vez.
- Terminal que voltou ao shell depois de uma atualização da ferramenta: `maestri recruit "Nome" --preset P --replace "Nome"` (mantém papel, conexões e posição; o histórico se perde, então reenvie o contexto).
- O classificador do modo automático do Claude Code pode bloquear `recruit --replace`, `git commit` ou `push` do Maestro: explique ao usuário e peça que ele aprove ou rode.
