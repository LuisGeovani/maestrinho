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

| Preset | Comando |
|---|---|
| Haiku | `claude --model haiku --effort medium --add-dir ../../..` |
| Sonnet | `claude --model sonnet --effort medium --add-dir ../../..` |
| Sonnet High | `claude --model sonnet --effort high --add-dir ../../..` |
| Agy Flash | `agy --model gemini-3.8-flash --add-dir ../../..` (triagem N0; confirme o ID e prefira low quando oferecido em `agy models`) |
| Agy Hydrogen | `agy --model gemini-4-hydrogen-high --add-dir ../../..` |
| Agy Argon | `agy --model gemini-4-argon-high --add-dir ../../..` |
| Agy Neon | `agy --model gemini-4-neon-high --add-dir ../../..` |
| Agy Orchestrator Neon | `agy --model gemini-pro-orchestrator-neon --add-dir ../../..` |
| Agy Opus | `agy --model claude-opus-5-5-high --add-dir ../../..` |
| Agy Sonnet | `agy --model claude-sonnet-5-5-medium --add-dir ../../..` |
| Codex Luna | `codex -m gpt-6-luna -c model_reasoning_effort=high --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) |
| Codex Terra | `codex -m gpt-6.1-terra -c model_reasoning_effort=medium --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) |
| Codex Sol | `codex -m gpt-6.2-sol -c model_reasoning_effort=medium --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) |
| Codex Astra | `codex -m gpt-6.2-astra -c model_reasoning_effort=high --add-dir ../../..` + variáveis `MAESTRI_*` ([§6](#6-codex)) |
| OpenCode Gratis | `$env:OPENCODE_CONFIG="<SKILL>/maestro/opencode-gratis.json"; opencode --standalone` (seção 7) |

```
maestri preset create "Haiku" --command "claude --model haiku --effort medium --add-dir ../../.." --quick-start off
```

- **Produtor Claude: Agy Sonnet / Agy Opus primeiro** (Antigravity, pool "Claude and GPT"). O Claude Pro é reserva do Maestro. Sonnet, Sonnet High e Haiku no Claude Code seguem as regras de elegibilidade de `roteamento.md` §4.
- `../../..` só vale com `--role`. Sem papel, o agente abre na pasta do workspace: use `--dir <RAIZ>` e nenhum `--add-dir`.
- Presets antigos com caminho de projeto fixo continuam funcionando, mas pare de criar novos; prefira os genéricos. Use nomes que não colidam com presets antigos (ex.: "Haiku" em vez de um "Claude Haiku" que já aponta para outro projeto).
- **Preset com caminho fixo:** o `inventario.py` lista, uma linha por preset, os que têm `--add-dir`/`--dir` com caminho absoluto (ou do diretório pessoal), que quase sempre é de outro projeto. Corrija com `maestri preset set "<Nome>" --command "<comando genérico da tabela acima>"` (ou crie o genérico e apague o antigo) e reabra os terminais que o usam com `recruit --replace`. `--dir <RAIZ>` de um preset sem papel é uso legítimo: o aviso só pede que você confirme que a pasta é deste projeto.
- Presets de produtor podem ficar fora do Quick Start (`--quick-start off`): quem os usa é o Maestro. O Quick Start tem limite; se estiver cheio, o preset novo não aparece lá, mas funciona no `--preset`.
- Para variar um effort só uma vez, `recruit` aceita `--command` junto com `--preset` (o preset dá o tipo e o ícone): `maestri recruit "Nome" --preset "Claude Code" --command "claude --model haiku --effort low --add-dir ../../.." --role "Papel"`.
- IDs de modelo mudam: confira no `inventario.py` (para o Antigravity, `agy models`) antes de criar.
- Nunca `--dangerously-skip-permissions` (agy) nem `--yolo` (codex) num preset de produtor.

### Formação padrão (o que propor ao usuário)

Proponha, confirme e anote em `.maestri/equipe.md` uma vaga por degrau ativo. Efforts em `roteamento.md` §3. Para variar o effort entre tarefas, use `recruit --command` com o preset.

**Com três planos pagos (Claude, Gemini e Codex): 7 a 8 vagas de produção.** Sete vagas base e uma oitava se houver demanda por Batedor no OpenCode grátis.

| Vaga | Preset | Função típica |
|---|---|---|
| Luna high | Codex Luna | Batedor: script utilitário, configuração e checagem fechada com teste automático |
| Sol medium | Codex Sol | Volume de código e verificação de fonte/fato. High para revisão de autor Gemini e N3 conforme a matriz |
| Sonnet 5.5 medium | Agy Sonnet | Produção cuidadosa, revisão de outra família conforme a matriz e QA visual |
| Opus 5.5 high | Agy Opus | Redação de registro formal, Crítico N3 e voz Claude do Conselho |
| Hydrogen high | Agy Hydrogen | Volume de código, UI especificada e pesquisa ampla |
| Argon high (medium via `--command`) | Agy Argon | Volume de cuidado, com teto semanal próprio |
| Neon high | Agy Neon | Crítico, Revisor e QA visual. Xhigh para o Conselho |
| OpenCode grátis (opcional) | OpenCode Gratis | Batedor de leitura, triagem e comandos pequenos quando o preset estiver disponível |

**Sob demanda:** recrute ou use `recruit --replace` entre tarefas para Astra (N3/N4 e Conselho), Terra (escrita, resumo, formato) ou Gemini 3.8 Flash (triagem textual N0). Haiku no Claude Code só entra se a reserva permitir. Orchestrator Neon e terminais extras entram conforme o volume e a cota.

**Com menos planos:** monte a equipe com os degraus disponíveis que a demanda pede. Aplique a reserva do Claude Pro mesmo na formação reduzida. Acrescente OpenCode grátis quando houver tarefa compatível. Se faltar outra família qualificada para revisar, avise o usuário e registre a revisão como pendente.

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
- **Limites do sandbox:** o `read_file` do agy **recusa arquivos binários** (PDF, Office, zip...) e o sandbox bloqueia rodar scripts e listar pastas fora da pasta de papel. Efeito já visto: tarefa bloqueada e checagem que não rodou. Regra: converta o binário para texto em terminal com shell elegível **antes** de despachar ao Antigravity e rode scripts bloqueados **fora** dele. Texto e imagem o agy lê. Detalhe em `roteamento.md` e `prompts.md` §1.

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
- Commits pequenos, só no nome do usuário. Push e PR só com autorização explícita para aquele push.
- Repositório compartilhado: não commite em `develop`/`main`; o trabalho de outra pessoa é a referência; antes de descartar algo, `git diff --stat`, patch no `.maestri/` e `stash` como backup; `git pull --ff-only`; trazer arquivos de outra branch sem commit: `git restore --source=<ref> --worktree -- <pasta>`; reescrita de histórico só com confirmação e `--force-with-lease`.

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
| Terminal Antigravity bloqueado ao ler PDF/Office/zip ou ao rodar script de checagem | `read_file` recusa binário e o sandbox bloqueia scripts (seção 5) | converta o binário para texto e rode a checagem em terminal com shell elegível pela matriz |
| Banner "Introducing …" no Antigravity | novidade de modelo | some com o primeiro prompt; não precisa de ação |
| Produtor reporta despacho "truncado" ou o texto fica na caixa de entrada | despacho enviado enquanto o terminal abria | usar `maestri_batch.py` (espera o terminal ficar pronto e recupera o texto parado); com `maestri ask` direto, espere o prompt aparecer no `check` |
| Relatório ou pesquisa vira instrução de projeto de repente | no Windows (e no macOS padrão) `claude.md` = `CLAUDE.md`, `agents.md` = `AGENTS.md`, `gemini.md` = `GEMINI.md`: as ferramentas carregam o arquivo como regra | nunca dê esses nomes a relatórios, pesquisas ou notas (use `anthropic.md`, `pesquisa-claude.md`...) |
| Terminais Gemini ignoram o fim do `AGENTS.md` | o Antigravity corta cada arquivo de regras em 24.000 **bytes** (acentos contam 2) e as regras globais dividem 20.000 tokens | mantenha o `AGENTS.md` abaixo de ~20 KB (`wc -c AGENTS.md`); detalhes vão para arquivos que o despacho cita. Não use "Sincronizar" do Maestri às cegas: `CLAUDE.md` e `AGENTS.md` podem ter papéis diferentes |
| PowerShell: `python -c "..."` ou `maestri ask "..."` perde aspas internas | PowerShell 5.1 remove aspas de argumentos de programas nativos | script em arquivo ou heredoc no Bash; relatório em arquivo |
| Kit do Maestro bloqueia um laço `for … do maestri check …` | versão antiga do `guarda.py` | atualize a skill (`git pull`); laços e `sed -n` em arquivos permitidos são liberados |
