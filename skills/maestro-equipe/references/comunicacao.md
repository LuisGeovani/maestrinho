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
Tamanho: P
Roteamento: Hydrogen medium | custo 30 | descartado: Hydrogen low porque exige código N2
<prompt da tarefa>
### Faísca | R03-T2
Tamanho: M
Roteamento: Sol medium | custo 120 | descartado: Hydrogen medium porque revisão pede outra família
<prompt da tarefa>
```

O script confere se os destinos estão conectados, **espera cada terminal ficar pronto** (tela estável com o campo de prompt; até 90 s), cria `.maestri/relatorios/`, acrescenta a cada prompt o **rodapé de relatório** com o seu nome real, monta o JSON com o escape certo, envia com `maestri ask --batch` (dividindo lotes grandes por causa do limite de linha de comando do Windows) e resume cada retorno lendo o STATUS do arquivo de relatório.

Antes do envio, o script aplica **duas travas** por seção:
- **Trava de equilíbrio (`RETIDO (equilíbrio)`):** identifica o pool do destino pela formação em `.maestri/equipe.md` (ou pelo rodapé da tela no Antigravity) e compara contra o pool pago elegível mais folgado. A trava vale igual para todos os pools pagos (Gemini, GPT e Claude): uma diferença de 15 pontos percentuais ou mais retém a seção. Para liberar, comece uma linha da própria seção com `Motivo pool:` seguido da justificativa na mesma linha. OpenCode grátis sempre passa; pool desconhecido ou leitura desatualizada gera aviso.
- **Trava de custo (`RETIDO (custo)`):** lê as linhas obrigatórias `Tamanho: P|M|G` e `Roteamento: <modelo> <effort> | custo <n> | descartado: <par mais barato> porque <motivo>` (`roteamento.md` §4) e retém como `RETIDO (custo)` apenas quando **`custo ≥ 300` e falta justificativa válida no campo de descarte** — o script valida **texto não vazio depois de `descartado:` e depois de `porque`, dentro do mesmo campo entre `|`** (`high` em modelo leve com tamanho `P`/`M`, como `Hydrogen high` M = 180, passa). Para liberar: quebre tarefa `G` em fatias `P`/`M`, escolha um par mais barato, ou preencha esse campo na linha `Roteamento:` explicando qual par mais barato foi descartado e por quê.

O resumo mostra os envios por família e cada entrega confirmada entra em `.maestri/distribuicao.log` (com custo estimado, tamanho e uso do pool). Com `--mostrar`, o resumo e os prompts refletem o que passaria pelas duas travas, sem envio nem registro.

Por que esperar: nos testes, despachar para um terminal que ainda abria (logo após `recruit` ou `--replace`) **perdeu o Enter** (o texto ficou parado na caixa de entrada) ou **cortou o começo** do prompt. Se mesmo assim o texto ficar parado, o script manda um Enter e espera o arquivo de relatório. Pedido de confiança de pasta na tela: o script não envia e avisa.

Nunca:
- monte JSON na mão nem passe o prompt como argumento de `maestri ask` com caminho do Windows: o CLI decodifica `\n` e `\t` nos argumentos (`C:\novo` vira quebra de linha);
- reenvie um prompt porque o `ask` demorou: rode `maestri check "Nome"` uma vez e espere.

## 3. Retorno: relatório em arquivo + aviso curto

Cada produtor, ao terminar (ou ao bloquear):
1. grava o relatório completo em `.maestri/relatorios/<ID>.md` (TAREFA, STATUS, ARQUIVOS, VALIDAÇÃO, PENDÊNCIAS, VISÃO opcional);
2. avisa com `maestri ask "<seu nome>" "<ID> <pronto|parcial|bloqueado>: .maestri/relatorios/<ID>.md"`.

Por que assim: o aviso curto não tem aspas internas (o PowerShell 5.1 come aspas de argumentos), nem barras invertidas (`\n`/`\t`), nem tamanho para cortar; o relatório completo fica em disco para o revisor ler direto e para auditoria. O aviso resolve o `ask` pendente do lote, então a notificação do background chega com o status.

IDs: use um ID novo para cada rodada de correção (`R03-T1-C1`); continuação após `parcial` usa `<ID>-P1` (depois `-P2` etc.), para não confundir com o relatório anterior.

## 4. Esperar sem gastar

- Depois de despachar: responda ao usuário em poucas linhas e **encerre o turno**. Sem polling, sem `sleep`, sem `maestri check` em loop.
- Quando a notificação do background chegar, leia só o resumo do script. Casos:

| O resumo diz | Faça |
|---|---|
| `pronto` / `parcial` (+ `veredito` em revisão) | leia o relatório (só o necessário para decidir) |
| `bloqueado` | leia o motivo no relatório; produtor que recebeu despacho cortado ou vago reporta bloqueado: reenvie completo |
| `RETIDO (equilíbrio)` | reencaminhe para um pool mais folgado ou justifique o destino em uma linha que começa com `Motivo pool:` |
| `RETIDO (custo)` | quebre a tarefa (se `Tamanho: G`), escolha um par modelo × effort mais barato, ou preencha na linha `Roteamento:` um campo entre `|` com texto não vazio depois de `descartado:` e depois de `porque` (`custo ≥ 300` exige justificativa) |
| aviso: aprovei a confiança da pasta de papel | normal na 1ª vez de cada terminal Antigravity/Codex; nada a fazer |
| NÃO ENVIADO, confiança de pasta fora de `.maestri/roles` | olhe com `maestri check`; aprove só se a pasta for do projeto e rode o despacho de novo só para ele |
| relatório ANTERIOR a este despacho | o produtor não gravou o novo: `maestri check "Nome"` uma vez; use ID novo por rodada |
| `PERMISSAO pendente: <terminal>` ou `PENDENTE, pedido de permissão` | `maestri check "Nome"`; dentro do escopo, aprove (`--raw "\r"` ou a tecla da opção; para `agy`, veja §6); fora, negue ou pergunte ao usuário |
| terminou sem relatório (tela mostra outra coisa, ex.: comando do usuário) | o despacho se perdeu: confira com `git status` que nada mudou e reenvie |
| ERRO / sem resposta em N min | `maestri check "Nome"`; se travou, `maestri recruit "Nome" --preset P --replace "Nome"` e reenvie |

- Avisos que chegam enquanto você está ocupado ficam na fila e entram como mensagens novas.
- Se precisar esperar algo fora do lote, espere pelo **arquivo** (`.maestri/relatorios/<ID>.md`), nunca por um texto na tela do terminal: a tela rola e o texto some.

## 5. Perguntar ao usuário

- **Com tarefa em andamento, não abra diálogo de pergunta (AskUserQuestion):** o aviso de um terminal é digitado no seu terminal e pode responder ou fechar o diálogo. Faça a pergunta em texto, no fim da resposta, e continue só o que não depende dela.
- Sem nada em andamento, o diálogo é o melhor jeito (opção recomendada primeiro).

## 6. Permissões dos produtores

- **Aprovar (uma vez):** leitura; edição e comandos dentro das pastas da tarefa; build, teste, lint; o próprio `maestri ask` de aviso; dependência que a tarefa pediu e existe no registro oficial.
- **Negar:** escrita fora do escopo; git feito por produtor (inclusive commit e push); pacote ou `npx` não pedido; `.env` reais, chaves, credenciais; rede para destino desconhecido; comando destrutivo; mudança de configuração global; controle do computador.
- `gh` só leitura (checks, view, status) é permitido quando o despacho autoriza; `gh pr create` só se o despacho disser que o usuário autorizou aquele PR e a branch já foi enviada pelo Maestro.
- Na dúvida, pergunte ao usuário. "Sempre permitir" só para padrões seguros e repetidos.

### Permissões no Antigravity (`agy`)

- O `agy` pede permissão para quase tudo: ferramenta MCP, leitura/acesso a arquivo fora da pasta de papel e comandos fora do sandbox.
- Não existe modo "aprovar tudo": `shift+tab` cicla apenas `auto → plan → default → accept-edits`.
- Depois de despachar para um `agy`, o Maestro deve vigiar a tela (ou o aviso `PERMISSAO pendente: <terminal>` do `maestri_batch.py`), conferir o pedido com `maestri check "<nome>"` e aprovar o que estiver no escopo:
  - **Ferramenta / MCP (leitura):** `maestri ask "<nome>" --raw "2"` (sempre nesta conversa) ou `"3"` (persistir nas configurações).
  - **Ferramenta que escreve em serviço externo** (ex.: editar design no Canva, publicar): preferir `"2"` (só nesta conversa).
  - **Acesso a arquivo fora da pasta:** `maestri ask "<nome>" --raw "1"`.
  - **Comando de shell fora do sandbox** (`curl`, `python`, PowerShell autorizado no escopo): `maestri ask "<nome>" --raw "1"` (uma vez) ou `"2"` (sempre nesta conversa, se o menu oferecer; confirme o número da opção na tela).

## 7. Notas do Maestri como quadro

- Quadro da rodada: `maestri note create --name "Quadro RNN" --stack "Rodadas"`; **só o Maestro escreve** (`maestri note edit`), a partir dos relatórios. Modelo em `documentos.md`.
- Brief grande e estável (contrato, decisões): nota própria, travada pelo usuário, e o despacho cita o nome da nota (o produtor precisa estar conectado a ela: `maestri connect "Brief" "Nome"`).

## 8. Quando o Maestri falha

- Qualquer erro de conexão ou pipe: `maestri debug` primeiro.
- Agente em floor ou workspace descarregado é acordado pelo `ask`; se disser que ainda está iniciando, o script reenvia uma vez.
- Terminal que voltou ao shell depois de uma atualização da ferramenta: `maestri recruit "Nome" --preset P --replace "Nome"` (mantém papel, conexões e posição; o histórico se perde, então reenvie o contexto).
- O classificador do modo automático do Claude Code pode bloquear `recruit --replace`, `git commit` ou `push` do Maestro: explique ao usuário e peça que ele aprove ou rode.
