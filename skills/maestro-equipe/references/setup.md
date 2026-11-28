# Setup da equipe no Maestri

Confirme cada bloco com o usuário antes de executar (presets, papéis, recrutamento e qualquer configuração global). `<SKILL>` é a pasta desta skill; `<RAIZ>`, o caminho absoluto do projeto. Testado em 2026-11-18 (Windows 11, Maestri e80f02c7, Claude Code 2.1.328, agy 1.5.12, Codex 0.170.0, OpenCode 2.3.2): `docs/testes/` do repositório da skill.

## 1. Inventário (sempre primeiro)

```
python <SKILL>/scripts/inventario.py      # CLIs, modelos disponíveis, seu nome no Maestri, cotas
maestri list                              # quem já está conectado (não recrute de novo quem existe)
maestri preset list                       # presets (comando de Maestro)
maestri role list                         # papéis do workspace
```

Comandos de Maestro (`preset`, `role`, `recruit`...) respondendo "This terminal is not the Maestro": o modo Maestro não está ligado **neste** terminal. Peça ao usuário para ligar a opção Maestro no terminal certo do canvas; a mudança pode levar alguns segundos para valer.

Planos e cotas vêm do `inventario.py` e do `cotas.py`: não pergunte. Pergunte só o que não dá para descobrir e muda o trabalho, como regras de git de um repositório compartilhado (branch protegida, quem faz push). Modelos grátis que treinam com os dados (Big Pickle, Iceman, Flint, Inkling) ficam fora da equipe; os demais presets da skill estão aprovados.

## 2. Presets: um por modelo, nunca por projeto

Presets são **globais** (valem em todos os workspaces). Não grave o caminho do projeto neles: o projeto vem do papel. Ao recrutar com `--role`, o agente abre em `<RAIZ>/.maestri/roles/<id>/`, então **`--add-dir ../../..` aponta para a raiz do projeto em qualquer projeto** (testado no Claude Code e no Antigravity).

| Preset | Comando | Peso do par `[incerto]` / uso |
|---|---|---|
| Haiku | `claude --model haiku --effort medium --add-dir ../../..` | 2 · Batedor no Claude Code |
| Sonnet | `claude --model sonnet --effort medium --add-dir ../../..` | 40 · generalista Claude Code (quando Agy indisponível) |
| Opus | `claude --model opus --effort medium --add-dir ../../..` | 80 · sob demanda (Conselho/N3 de risco; `high` só via `recruit --command --replace` com avaliação) |
| Agy Flash | `agy --model gemini-3.8-flash-low --add-dir ../../..` | 1 · triagem N0 (medidor desconhecido até confirmação; outros efforts via `--command`) |
| Agy Hydrogen Low | `agy --model gemini-4-hydrogen-low --add-dir ../../..` | 15 · Batedor N0–N1, levantamento barato |
| Agy Hydrogen | `agy --model gemini-4-hydrogen-medium --add-dir ../../..` | 30 · Volume de código/UI bem especificado, fatias `P`/`M` e QA visual barato |
| Agy Hydrogen High | `agy --model gemini-4-hydrogen-high --add-dir ../../..` | 60 · sob demanda (leve e barato: entra quando lógica/depuração de muitos passos justificar) |
| Agy Argon | `agy --model gemini-4-argon-medium --add-dir ../../..` | 30 · tarefa longa de cuidado em `medium` (teto semanal próprio) |
| Agy Neon | `agy --model gemini-4-neon-medium --add-dir ../../..` | 60 · especificação curta, julgamento/contexto amplo e MCP Lazy (`high` só sob demanda via `recruit --command --replace`) |
| Agy Orchestrator Neon | `agy --model gemini-pro-orchestrator-neon --add-dir ../../..` | fixo · multi-arquivo sob demanda |
| Agy Sonnet | `agy --model claude-sonnet-5-5-medium --add-dir ../../..` | 40 · Volume/revisão cruzada no Antigravity |
| Agy Opus | `agy --model claude-opus-5-5-medium --add-dir ../../..` | 80 · sob demanda (Conselho/N3 de risco no Agy; `high` só via `recruit --command --replace` com avaliação) |
| Codex Luna | `codex -m gpt-6-luna -c model_reasoning_effort=high --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) | 4 · scripts/checagens N0–N1 com teste (`high` em modelo leve, peso 1) |
| Codex Terra | `codex -m gpt-6.1-terra -c model_reasoning_effort=low --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) | 10 · triagem/leitura rápida (`medium` via `--command` para texto) |
| Codex Sol | `codex -m gpt-6.2-sol -c model_reasoning_effort=medium --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) | 40 · código por spec, verificação com shell e revisão |
| Codex Astra | `codex -m gpt-6.2-astra -c model_reasoning_effort=medium --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) | 160 · sob demanda (Conselho/N3 de risco/escalada; `high` só via `recruit --command --replace` com avaliação) |
| OpenCode Gratis | `$env:OPENCODE_CONFIG="<SKILL>/maestro/opencode-gratis.json"; opencode --standalone` (seção 7) | 0 · Batedor custo zero (não sensível) |

```
maestri preset create "Haiku" --command "claude --model haiku --effort medium --add-dir ../../.." --quick-start off
```

- **Família Claude (única regra parcial):** aplique a árvore de decisão do `SKILL.md` (sem família favorita; o passo 5 só ordena dentro da família Claude depois que Claude foi escolhido e não desempata o passo 4). O modelo pedido roda no Antigravity (`Agy Sonnet` / `Agy Opus`, pool "Claude and GPT", com shell sob aprovação) se ele existir lá e houver cota; **Haiku** e recursos exclusivos (`--chrome`) vão direto ao Claude Code (Pro utilizável). Sonnet/Opus só vão ao Claude Code se "Claude and GPT" estiver vetado/indisponível e o Pro estiver utilizável, sujeitos às mesmas travas `RETIDO (equilíbrio)` e `RETIDO (custo)` de `roteamento.md` §4. Volte ao Antigravity no reset.
- `../../..` só vale com `--role`. Sem papel, o agente abre na pasta do workspace: use `--dir <RAIZ>` e nenhum `--add-dir`.
- Presets antigos com caminho de projeto fixo continuam funcionando, mas pare de criar novos; prefira os genéricos. Use nomes que não colidam com presets antigos (ex.: "Haiku" em vez de um "Claude Haiku" que já aponta para outro projeto).
- **Preset com caminho fixo:** o `inventario.py` lista, uma linha por preset, os que têm `--add-dir`/`--dir` com caminho absoluto (ou do diretório pessoal), que quase sempre é de outro projeto. Corrija com `maestri preset set "<Nome>" --command "<comando genérico da tabela acima>"` (ou crie o genérico e apague o antigo) e reabra os terminais que o usam com `recruit --replace`. `--dir <RAIZ>` de um preset sem papel é uso legítimo: o aviso só pede que você confirme que a pasta é deste projeto.
- Presets de produtor podem ficar fora do Quick Start (`--quick-start off`): quem os usa é o Maestro. O Quick Start tem limite; se estiver cheio, o preset novo não aparece lá, mas funciona no `--preset`.
- **Effort fixo por terminal e escalada sob demanda:** não troque effort no meio do chat (quebra o cache). Para abrir um par pesado em `high` sob demanda (ex.: `Neon high`, `Astra high`, `Opus high` quando a avaliação do par em `roteamento.md` justificar), use `recruit` com `--command` e `--replace` e volte ao par base (ou dispense) ao terminar: `maestri recruit "<Nome>" --preset "Agy Neon" --command "agy --model gemini-4-neon-high --add-dir ../../.." --role "Papel" --replace "<Nome>"`.
- IDs de modelo mudam: confira no `inventario.py` (para o Antigravity, `agy models`) antes de criar.
- Nunca `--dangerously-skip-permissions` (agy) nem `--yolo` (codex) num preset de produtor.

### Formação padrão (pares deliberados com effort fixo)

Proponha, confirme e anote em `.maestri/equipe.md` (incluindo a coluna **Peso do par**, `documentos.md`) uma formação fixa com **effort fixo por terminal em pares deliberados**, evitando terminais pesados em `high` ociosos (**pesado** = Neon, Opus, Astra, Fable; **leve** = Hydrogen, Argon, Sol, Sonnet, Terra, Luna, Haiku, Flash, OpenCode). Efforts por tipo de dificuldade em `roteamento.md` §3; pesos `[incerto]` em `modelos.md`.

**Com três planos pagos (Claude, Gemini e Codex) + OpenCode grátis: 10 vagas fixas em pares deliberados (Hydrogen high, pesados em `high` e Conselho/N3 entram sob demanda e saem depois).**

| Família | Par fixo (modelo · effort) | Peso do par `[incerto]` | Preset | Função típica |
|---|---|---|---|---|
| Abertos | OpenCode grátis | 0 | OpenCode Gratis | Batedor de custo zero (não sensível): leitura, triagem, resumo e testes fechados |
| Claude | Haiku 5.5 · medium | 2 | Haiku | Batedor no Claude Code (shell, conversão, URL, verificação de fonte) quando o Pro não estiver retido |
| GPT | Luna · high | 4 | Codex Luna | Batedor N0–N1: script utilitário, config e checagem fechada com teste (`high` em modelo leve, peso 1) |
| GPT | Terra · low | 10 | Codex Terra | Batedor de leitura/triagem rápida (`medium` via `--command` para texto/visão) |
| Gemini | Hydrogen · low | 15 | Agy Hydrogen Low | Batedor N0–N1 Gemini: levantamento/resumo barato, leitura, checagem |
| Gemini | Hydrogen · medium | 30 | Agy Hydrogen | Volume de código/UI bem especificado, fatias `P`/`M`, QA visual barato e pesquisa ampla |
| Gemini | Argon · medium | 30 | Agy Argon | Tarefa longa de cuidado (`Volume de cuidado`), redação e revisão de texto/diff, poupando o teto próprio |
| GPT | Sol · medium | 40 | Codex Sol | Volume de código por spec, fatias, verificação de fonte com shell e revisão de outra família |
| Claude | Sonnet 5.5 · medium | 40 | Agy Sonnet | Volume, revisão quando autor ≠ Claude e equilíbrio permite, QA visual (no Antigravity) |
| Gemini | Neon · medium | 60 | Agy Neon | Especificação curta, julgamento/contexto amplo, edição via MCP em modo Lazy e revisão de baixa fabricação |

- **Pesados em `high` e modelos de Conselho/N3 — SOB DEMANDA (`recruit --command ... --replace`, e saem depois):** `Neon high` (peso 120), `Astra medium/high` (peso 160/320), `Opus 5.5 medium/high` (`Agy Opus` ou Claude Code, peso 80/160) e `Fable` (escalada extrema) **não ficam fixos em `high`**. Entram sob demanda com `recruit --command ... --replace` somente quando a avaliação do par (`roteamento.md` Princípio 3) justificar (Conselho N4, N3 de risco ou escalada), e voltam ao par base (ou são dispensados) ao terminar.
- **Onde rodam os modelos Claude e limite no Claude Code:** quando a escolha for Claude, Sonnet e Opus rodam primeiro no Antigravity (`Agy Sonnet` e `Agy Opus`, pool "Claude and GPT") se houver cota; **Haiku** (não existe no Antigravity) e eventual terminal com recurso exclusivo (`--chrome` logado, quando CLI/API com shell e Portal do Maestri não atendem) vão direto ao Claude Code (Pro utilizável). Quando Sonnet/Opus não puderem rodar no Antigravity (bloqueio ou ausência do plano), mantenha **no máximo um produtor Claude Code generalista**: por custo/cota no Claude Pro compartilhado com o Maestro, **Sonnet `medium`** (peso 40) ocupa a vaga fixa e **Opus** (peso 80/160) entra só sob demanda (`recruit --command ... --replace`) e sai depois. Terminal mantido por recurso exclusivo (Chrome, SSH/LAN) não conta no limite enquanto só recebe tarefas que exigem o recurso; se receber tarefa geral, ele é o generalista. No reset, volte ao Antigravity.
- **Extras sob demanda:** `Agy Hydrogen High` (`high`, peso 60 — leve e barato; entra quando lógica/depuração de muitos passos justificar), `Sol low` (se precisar de fatia GPT trivial sob demanda), `Agy Orchestrator Neon` para tarefa multi-arquivo no Antigravity e `Agy Flash` separado para triagem textual N0 após confirmação do medidor.
- **Com menos planos:** monte a equipe com os pares deliberados dos planos disponíveis mais o OpenCode grátis, mantendo effort fixo por terminal e pesados em `high` apenas sob demanda. Aplique a mesma ordem de decisão e o limite de produtores no Claude Code. Se faltar outra família qualificada para revisar, avise o usuário e registre a revisão como pendente.

### Manutenção da formação

- **Revisão a cada sessão:** compare `.maestri/equipe.md` (incluindo a coluna **Peso do par**) com a formação padrão; recrute o par que falta, reverta ou dispense terminais pesados em `high` abertos sob demanda em rodadas anteriores e corte o excesso (mais de um generalista no Claude Code ou dois terminais do mesmo par e função sem trabalho paralelo real).
- **Por que manter terminal parado:** terminal ocioso não gasta tokens; manter pares deliberados com effort fixo evita trocar modelo ou effort no meio da conversa (quebra o cache) e deixa o par barato sempre à mão.
- **Ocioso não é sobra:** terminal básico parado por várias rodadas indica que o Maestro está pulando o degrau mínimo. Confira a linha "Despachos nas últimas 5 h por família" do `cotas.py`.
- **Recurso exclusivo fica:** terminal com Chrome, SSH/LAN ou Portal conectado permanece mesmo ocioso; anote o recurso na coluna Perfis de `equipe.md`.
- **Substituição temporária:** quando um pool bloqueia, troque o terminal afetado pelo modelo que falta na formação (ex.: Opus no Claude Code vira Astra no Codex), em vez de manter um generalista caro no Claude Pro; anote em `equipe.md` a data do reset e, nela, recrute de novo o terminal original.
- **Como trocar:** rode `criar_papel.py --aplicar` com o modelo novo, depois `maestri recruit "Nome" --preset "<preset>" --replace "Nome"` e atualize `equipe.md` na hora (o banner com o modelo some com o uso). Se o classificador do Claude Code bloquear o `--replace`, peça a aprovação ao usuário.

## 3. Papéis

Papéis são do workspace atual. Modelos em `papeis.md`. Dois terminais com o **mesmo papel compartilham a mesma pasta de papel**; isso funciona, mas um papel por terminal deixa cada um com sua identidade.

Monte o papel com o script (monta o texto a partir dos blocos de `papeis.md`, sem copiar o texto para o script):

```
python <SKILL>/scripts/criar_papel.py "<Nome>" --projeto "<Projeto>" --raiz "<RAIZ>" --modelo "<Modelo>" --effort <e> --familia <Claude|Gemini|GPT|aberto> --perfis "<Batedor,Volume,...>" [--pastas "..."] [--entrega "<pasta>"] [--ferramenta agy|codex|opencode] [--aplicar]
```

- Grava `<RAIZ>/.maestri/papeis/<Nome>.md` (UTF-8 sem BOM). Sem `--aplicar`, só grava e mostra o resumo; revise e rode de novo com `--aplicar`.
- `--aplicar` roda `maestri role create`, ou `maestri role write` se o `role show` achar o papel (só no terminal Maestro). Use em `--perfis` os rótulos dos [perfis de papel](papeis.md). Sem `--pastas`: "as do despacho"; sem `--entrega`: "nenhuma". `--ferramenta` junta o bloco do Antigravity, Codex ou OpenCode.
- Os campos de caminho (`<RAIZ>`, `--pastas`, `--entrega`) vão com barras normais (o CLI decodifica `\n` e `\t` nos argumentos). Depois do `--aplicar` o script confere com `role show` e avisa (saída 3) se o texto ficou truncado.

À mão (ajustes e papéis fora do padrão):

```
maestri role create "Nome do papel" "<texto>"
maestri role write "Nome do papel" "$(cat .maestri/papeis/<arquivo>.md)"   # texto longo, gravado por um produtor
maestri role show "Nome do papel"
```

## 4. Recrutar

```
maestri recruit "<Codinome>" --preset "<preset por modelo>" --role "<papel>"
```

Depois de recrutar, para cada terminal:
1. Espere ~15 s e rode `maestri check "<Codinome>"`. Confira: **modelo, effort, conta/plano e pasta** (`.maestri/roles/<id>` deste projeto). Anote a linha do terminal em `.maestri/equipe.md` (`documentos.md`): no Claude Code o modelo só aparece no banner do topo, que some depois do primeiro trabalho, e o `maestri list` não mostra modelo.
2. **Confiança de pasta** (Antigravity e Codex perguntam na primeira vez em cada pasta de papel; o Claude Code não perguntou): o `maestri_batch.py` aprova sozinho quando a pasta é de papel do Maestri (`.maestri/roles/<id>`) e o "sim" já está destacado; não pergunte ao usuário. Na mão: `maestri ask "<Codinome>" --raw "\r"` e confira com `check` (o retorno do `--raw` pode mostrar a tela antiga). Pasta fora de `.maestri/roles`: não aprove sem olhar.
3. Avisos no banner (regra inválida, MCP sem autenticação, cota baixa): anote; os de cota viram decisão de roteamento.
4. Só então o primeiro despacho. Despachar para quem ainda está abrindo perde o Enter ou corta o texto (testado); o `maestri_batch.py` já espera a tela ficar pronta, mas um `maestri ask` direto não espera.

Trocar o agente ou o modelo de um terminal sem perder conexões: `maestri recruit "<Codinome>" --preset P --replace "<Codinome>"` (aceita `--command`). O processo reinicia sem o histórico da ferramenta: reenvie o contexto. Dispense quem ficou ocioso por muito tempo: `maestri dismiss "<Codinome>"` (apaga o nó; para trocar, use `--replace`).

Não crie band sem o usuário pedir, e não conecte produtores entre si: tudo passa pelo Maestro (o revisor lê o relatório do autor pelo caminho do arquivo).

## 5. Antigravity (`agy`)

- **Configure com o script, sem perguntar:** `python <SKILL>/scripts/configurar_antigravity.py` (idempotente, faz backup, só muda o que falta; `--checar` só confere; o `inventario.py` já mostra o estado). Ele garante a regra abaixo e o `allowNonWorkspaceAccess`, e remove a regra antiga do nome fixo. É uma regra estreita (só o aviso curto), por isso faz parte do setup padrão; avise o usuário em uma linha.
- **Regra para o aviso de relatório** em `~/.gemini/antigravity-cli/settings.json`, `permissions.allow`, exatamente:

  ```
  "command(regex:^maestri ask \"[^\"]+\" \"[^\"$`;&|<>]*\"$)"
  ```

  Serve para qualquer nome de Maestro e só aceita o aviso curto: bloqueia encadeamento (`;`, `&&`, `|`), substituição (`$(...)`, crase) e redirecionamento. Não use `(?s)...(\s+.*)?$`: aceitava `maestri ask "X" "y"; outro-comando`. Regra `unsandboxed(...)` não existe (o agy avisa que ignora).
- A regra só vale para terminais abertos **depois** da mudança: `recruit --replace`.
- `"allowNonWorkspaceAccess": true` no mesmo arquivo evita pedido de permissão para ler fora da pasta de papel.
- O papel do Antigravity leva o bloco "Antigravity" de `papeis.md` (se der access denied, rode SOMENTE o comando maestri fora do sandbox).
- O agy abre em modo `auto` (edições e comandos seguros aprovados). Ao lançar modelo novo, aparece um banner "Introducing …"; ele some sozinho com o primeiro prompt.
- Skills globais do agy: `~/.gemini/config/skills/` (também lê `~/.gemini/skills/`).
- **Shell, MCP e limites reais:** o agy **roda shell** (`curl`, `python`, PowerShell) no sandbox ou fora dele com aprovação do Maestro, e **usa servidores MCP** (ex.: Canva). Atenção ao carregamento MCP: o mesmo servidor pode carregar em modo **Lazy** num terminal (ex.: Neon, todas as ferramentas) e em modo **Eager** em outro (ex.: Hydrogen, cortando ferramentas maiores por limite de tamanho). O `read_file` do agy continua **recusando binários** (PDF, Office, zip...): converta binários para texto/imagem antes; texto e imagem o agy lê normalmente. Permissões do agy: `comunicacao.md` §6.

## 6. Codex

Os quatro presets Codex reutilizam o bloco `MAESTRI_*` abaixo na configuração do comando, pois o Codex não herda essas variáveis sozinho. Use o modelo e o effort da tabela de presets, mantendo todas as opções `shell_environment_policy.set.MAESTRI_*` do bloco.

```
codex -m <modelo> -c model_reasoning_effort=<effort> --add-dir ../../.. -c "shell_environment_policy.set.MAESTRI_PIPE='$env:MAESTRI_PIPE'" -c "shell_environment_policy.set.MAESTRI_TERMINAL_ID='$env:MAESTRI_TERMINAL_ID'" -c "shell_environment_policy.set.MAESTRI_WORKSPACE_ID='$env:MAESTRI_WORKSPACE_ID'" -c "shell_environment_policy.set.MAESTRI_DATA_DIR='$env:MAESTRI_DATA_DIR'" -c "shell_environment_policy.set.MAESTRI_CLI='$env:MAESTRI_CLI'"
```

- Com `--role`, o Codex abre em `<RAIZ>/.maestri/roles/<id>/`. Use `--add-dir ../../..` para incluir a raiz do projeto, como nos outros presets com papel. Sem `--role`, omita essa opção.
- O comando do preset roda no PowerShell no Windows (por isso `$env:`); em macOS/Linux use `$MAESTRI_PIPE` etc.
- Sandbox no Windows: o sandbox elevado roda como outro usuário e não alcança a pasta do Maestri (doc de troubleshooting do Maestri). Opções: o modo sem sandbox que o usuário já usa, ou o sandbox não elevado em `[windows]` do `~/.codex/config.toml` `[incerto: nome exato do valor; confira em codex doctor]`. Libere comandos que começam com `maestri`.
- Primeira vez numa pasta de papel: "Trust this folder?" (aprove com `--raw "\r"`).
- O banner mostra a cota restante ("monthly limit: 8% left"): aplique as faixas da cota de `roteamento.md` §4.
- Proíba computer use e `/model` no papel.

## 7. OpenCode

- Instalação: `npm i -g @opencode/cli` (v2). Se a pessoa usa o app desktop do OpenCode, **não use a v1** (`opencode-ai`): ela falha com "Database is not empty and has no session table" no banco que o app cria.
- Na v2 a interface interativa **não tem `--model`**: o modelo vem da config. E ela usa um serviço em segundo plano que **ignora** variáveis do terminal; com `--standalone` a config por terminal vale (testado: sem `--standalone` abriu em "Tidepool Alpha Free"; com ele, no modelo configurado).
- Config do terminal: `<SKILL>/maestro/opencode-gratis.json` (modelo grátis fixo + permissões que negam git e pacotes). Preset: `$env:OPENCODE_CONFIG="<SKILL>/maestro/opencode-gratis.json"; opencode --standalone` (macOS/Linux: `OPENCODE_CONFIG=<...> opencode --standalone`).
- Se houver `OPENAI_API_KEY` no ambiente, o OpenCode lista os modelos `openai/*` e eles **gastam a conta paga**: mantenha o modelo grátis fixo na config.
- Não interativo (para scripts): `opencode run -m opencode/<modelo> --archived "<mensagem>"`.

## 8. Kit do Maestro (blindagem)

```
python <SKILL>/maestro/instalar.py
```

Gera `maestro/settings.gerado.json` (hook que bloqueia ferramentas de trabalho) e imprime o comando do Maestro e a linha `maestri preset create "Maestro" ... --maestro on`. Com o preset, o Maestro abre já com a regra no system prompt (`sistema.md`) e o hook ativo. Teste: `python <SKILL>/maestro/guarda.py --teste`. Emergência: abrir o terminal com `MAESTRO_GUARDA=off`. Rode o instalador de novo se mover a skill de lugar.

## 9. Git do projeto

- `.gitignore` com `.maestri/` (papéis, despachos, relatórios, contexto), `node_modules`, builds, `.env*` (menos `!.env.example`) e `.worktrees/`; quem edita é um produtor.
- Commits pequenos, só no nome do usuário. Commit e push são do Maestro; push e abertura de PR exigem autorização explícita para aquele push ou PR. Produtor só pode abrir PR com `gh pr create` se o despacho disser que o usuário autorizou aquele PR e a branch já foi enviada pelo Maestro.
- Em repositório compartilhado, preserve alterações fora do escopo do despacho. Confira os caminhos contra todos os despachos ativos e identifique o responsável. Peça autorização explícita do usuário antes de descartar. Após a autorização, confira com `git diff --stat` e faça backup da alteração afetada antes do descarte.
- Em repositório compartilhado, não commite em `develop`/`main` e use `git pull --ff-only`. Para trazer arquivos de outra branch sem commit, use `git restore --source=<ref> --worktree -- <pasta>`. Reescrita de histórico exige confirmação e `--force-with-lease`.

## Workspace copiado de outro projeto

Sintoma: papéis citando outro projeto, presets com `--add-dir` de outra pasta, rodapé com caminho antigo. Correção (com ok do usuário): o Maestro refaz cada papel com `scripts/criar_papel.py ... --aplicar` (ele usa `role write` nos que já existem); troque os presets por modelo (seção 2) e reabra cada terminal com `recruit --replace`.

## Problemas conhecidos

| Sintoma | Causa | Correção |
|---|---|---|
| "This terminal is not the Maestro" | modo Maestro desligado neste terminal | o usuário liga a opção Maestro no terminal certo; espere alguns segundos |
| Produtor pede permissão para ler cada arquivo do projeto | abre na pasta de papel, fora do projeto | `--add-dir ../../..` no preset (com papel); no Antigravity também `allowNonWorkspaceAccess` |
| Aviso do produtor não chega ou chega a outro | nome "Maestro" fixo no papel/regra | nome real do `maestri list` (`You:`); o `maestri_batch.py` já usa |
| Relatório cortado, sem aspas ou com quebras estranhas | aspas no PowerShell 5.1, `\n`/`\t` decodificados pelo CLI | relatório em arquivo + aviso curto (`comunicacao.md`) |
| Antigravity demora minutos ou pede confirmação a cada aviso | `maestri ask` no sandbox sem regra | regra da seção 5 e `--replace` |
| Codex: `MAESTRI_PIPE not set` | Codex não herda as variáveis | preset da seção 6 |
| OpenCode abre em outro modelo | serviço em segundo plano ignora a config do terminal | `--standalone` + `OPENCODE_CONFIG` |
| OpenCode v1: "Database is not empty and has no session table" | banco criado pelo app desktop (v2) | instalar a v2 (`@opencode/cli`) |
| `maestri: command not found` | CLI fora do PATH | adicionar `%LOCALAPPDATA%\Programs\Maestri\resources\cli` ao PATH, ou usar `$MAESTRI_CLI` |
| Arquivo com caractere estranho no início | PowerShell 5.1 grava UTF-8 com BOM | o produtor remove o BOM e grava com `-Encoding utf8` (ou via Python) |
| Terminal voltou ao shell após atualização | a ferramenta fechou ao atualizar | `recruit --replace` |
| Classificador do Claude Code bloqueia `recruit --replace`, `git commit` ou push do Maestro | ação sensível no modo automático | explicar ao usuário e pedir que aprove ou rode |
| Pergunta ao usuário some ou é respondida sozinha | aviso de produtor digitado em cima do diálogo | sem AskUserQuestion com tarefa em andamento |
| Terminal Antigravity bloqueado ao ler PDF/Office/zip ou fora da pasta no sandbox | `read_file` recusa binário; rede ou escrita fora da pasta de papel pede aprovação fora do sandbox | converta binários para texto em terminal com shell antes; para `curl`/Python/PowerShell no escopo, aprove a execução fora do sandbox (`comunicacao.md` §6) |
| Antigravity MCP: `tool X is not enabled for server Y` | o servidor carregou em modo Eager naquele terminal e cortou ferramentas maiores por limite de tamanho (~10,5 KB no Canva: só as 11 menores passam) | troque para um terminal em que o servidor carregue em modo Lazy (ex.: Neon) em vez de editar a configuração; o Antigravity bloqueia ler `settings.json` e `config.json` por regra fixa |
| Banner "Introducing …" no Antigravity | novidade de modelo | some com o primeiro prompt; não precisa de ação |
| Produtor reporta despacho "truncado" ou o texto fica na caixa de entrada | despacho enviado enquanto o terminal abria | usar `maestri_batch.py` (espera o terminal ficar pronto e recupera o texto parado); com `maestri ask` direto, espere o prompt aparecer no `check` |
| Relatório ou pesquisa vira instrução de projeto de repente | no Windows (e no macOS padrão) `claude.md` = `CLAUDE.md`, `agents.md` = `AGENTS.md`, `gemini.md` = `GEMINI.md`: as ferramentas carregam o arquivo como regra | nunca dê esses nomes a relatórios, pesquisas ou notas (use `anthropic.md`, `pesquisa-claude.md`...) |
| Terminais Gemini ignoram o fim do `AGENTS.md` | o Antigravity corta cada arquivo de regras em 24.000 **bytes** (acentos contam 2) e as regras globais dividem 20.000 tokens | mantenha o `AGENTS.md` abaixo de ~20 KB (`wc -c AGENTS.md`); detalhes vão para arquivos que o despacho cita. Não use "Sincronizar" do Maestri às cegas: `CLAUDE.md` e `AGENTS.md` podem ter papéis diferentes |
| PowerShell: `python -c "..."` ou `maestri ask "..."` perde aspas internas | PowerShell 5.1 remove aspas de argumentos de programas nativos | script em arquivo ou heredoc no Bash; relatório em arquivo |
| Kit do Maestro bloqueia um laço `for … do maestri check …` | versão antiga do `guarda.py` | atualize a skill (`git pull`); laços e `sed -n` em arquivos permitidos são liberados |
