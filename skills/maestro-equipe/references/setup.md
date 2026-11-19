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

Pergunte o que só o usuário sabe: planos (Claude Pro/Max/Ultra, Google AI Free/Pro/Ultra, ChatGPT Free/Plus/Pro, OpenCode Go), se o código pode ir para modelos grátis que treinam com os dados, regras de git do repositório.

## 2. Presets: um por modelo, nunca por projeto

Presets são **globais** (valem em todos os workspaces). Não grave o caminho do projeto neles: o projeto vem do papel. Ao recrutar com `--role`, o agente abre em `<RAIZ>/.maestri/roles/<id>/`, então **`--add-dir ../../..` aponta para a raiz do projeto em qualquer projeto** (testado no Claude Code e no Antigravity).

| Preset | Comando |
|---|---|
| Haiku | `claude --model haiku --effort medium --add-dir ../../..` |
| Sonnet | `claude --model sonnet --effort medium --add-dir ../../..` |
| Sonnet High | `claude --model sonnet --effort high --add-dir ../../..` |
| Agy Hydrogen | `agy --model gemini-4-hydrogen-high --add-dir ../../..` |
| Agy Neon | `agy --model gemini-4-neon-high --add-dir ../../..` |
| Agy Orchestrator Neon | `agy --model gemini-pro-orchestrator-neon --add-dir ../../..` |
| Agy Opus | `agy --model claude-opus-5-5-high --add-dir ../../..` |
| Agy Sonnet | `agy --model claude-sonnet-5-5-medium --add-dir ../../..` |
| Codex Luna | `codex -m gpt-6-luna -c model_reasoning_effort=high` + variáveis do Maestri (seção 6); com Plus, crie também "Codex Sol" (`gpt-6.2-sol`, medium) |
| OpenCode Gratis | `$env:OPENCODE_CONFIG="<SKILL>/maestro/opencode-gratis.json"; opencode --standalone` (seção 7) |

```
maestri preset create "Haiku" --command "claude --model haiku --effort medium --add-dir ../../.." --quick-start off
```

- `../../..` só vale com `--role`. Sem papel, o agente abre na pasta do workspace: use `--dir <RAIZ>` e nenhum `--add-dir`.
- Presets antigos com caminho de projeto fixo continuam funcionando, mas pare de criar novos; prefira os genéricos. Use nomes que não colidam com presets antigos (ex.: "Haiku" em vez de um "Claude Haiku" que já aponta para outro projeto).
- Presets de produtor podem ficar fora do Quick Start (`--quick-start off`): quem os usa é o Maestro. O Quick Start tem limite; se estiver cheio, o preset novo não aparece lá, mas funciona no `--preset`.
- Para variar um effort só uma vez, `recruit` aceita `--command` junto com `--preset` (o preset dá o tipo e o ícone): `maestri recruit "Nome" --preset "Claude Code" --command "claude --model haiku --effort low --add-dir ../../.." --role "Papel"`.
- IDs de modelo mudam: confira no `inventario.py` (para o Antigravity, `agy models`) antes de criar.
- Nunca `--dangerously-skip-permissions` (agy) nem `--yolo` (codex) num preset de produtor.

## 3. Papéis

Papéis são do workspace atual. Modelos em `papeis.md`. Dois terminais com o **mesmo papel compartilham a mesma pasta de papel**; isso funciona, mas um papel por terminal deixa cada um com sua identidade.

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
2. **Confiança de pasta** (Antigravity e Codex perguntam na primeira vez em cada pasta de papel; o Claude Code não perguntou): aprove com `maestri ask "<Codinome>" --raw "\r"` e confira de novo com `check` (o retorno do `--raw` pode mostrar a tela antiga).
3. Avisos no banner (regra inválida, MCP sem autenticação, cota baixa): anote; os de cota viram decisão de roteamento.
4. Só então o primeiro despacho. Despachar para quem ainda está abrindo perde o Enter ou corta o texto (testado); o `maestri_batch.py` já espera a tela ficar pronta, mas um `maestri ask` direto não espera.

Trocar o agente ou o modelo de um terminal sem perder conexões: `maestri recruit "<Codinome>" --preset P --replace "<Codinome>"` (aceita `--command`). O processo reinicia sem o histórico da ferramenta: reenvie o contexto. Dispense quem ficou ocioso por muito tempo: `maestri dismiss "<Codinome>"` (apaga o nó; para trocar, use `--replace`).

Não crie band sem o usuário pedir, e não conecte produtores entre si: tudo passa pelo Maestro (o revisor lê o relatório do autor pelo caminho do arquivo).

## 5. Antigravity (`agy`)

- **Regra para o aviso de relatório** em `~/.gemini/antigravity-cli/settings.json` (faça backup antes; config global, só com ok do usuário). Em `permissions.allow`, exatamente:

  ```
  "command(regex:^maestri ask \"[^\"]+\" \"[^\"$`;&|<>]*\"$)"
  ```

  Serve para qualquer nome de Maestro e só aceita o aviso curto: bloqueia encadeamento (`;`, `&&`, `|`), substituição (`$(...)`, crase) e redirecionamento. Não use `(?s)...(\s+.*)?$`: aceitava `maestri ask "X" "y"; outro-comando`. Regra `unsandboxed(...)` não existe (o agy avisa que ignora).
- A regra só vale para terminais abertos **depois** da mudança: `recruit --replace`.
- `"allowNonWorkspaceAccess": true` no mesmo arquivo evita pedido de permissão para ler fora da pasta de papel.
- O papel do Antigravity leva o bloco "Antigravity" de `papeis.md` (se der access denied, rode SOMENTE o comando maestri fora do sandbox).
- O agy abre em modo `auto` (edições e comandos seguros aprovados). Ao lançar modelo novo, aparece um banner "Introducing …"; ele some sozinho com o primeiro prompt.
- Skills globais do agy: `~/.gemini/config/skills/` (também lê `~/.gemini/skills/`).

## 6. Codex

Preset com as variáveis do Maestri (o Codex não as herda sozinho):

```
codex -m <modelo> -c model_reasoning_effort=<effort> -c "shell_environment_policy.set.MAESTRI_PIPE='$env:MAESTRI_PIPE'" -c "shell_environment_policy.set.MAESTRI_TERMINAL_ID='$env:MAESTRI_TERMINAL_ID'" -c "shell_environment_policy.set.MAESTRI_WORKSPACE_ID='$env:MAESTRI_WORKSPACE_ID'" -c "shell_environment_policy.set.MAESTRI_DATA_DIR='$env:MAESTRI_DATA_DIR'" -c "shell_environment_policy.set.MAESTRI_CLI='$env:MAESTRI_CLI'"
```

- O comando do preset roda no PowerShell no Windows (por isso `$env:`); em macOS/Linux use `$MAESTRI_PIPE` etc.
- Sandbox no Windows: o sandbox elevado roda como outro usuário e não alcança a pasta do Maestri (doc de troubleshooting do Maestri). Opções: o modo sem sandbox que o usuário já usa, ou o sandbox não elevado em `[windows]` do `~/.codex/config.toml` `[incerto: nome exato do valor; confira em codex doctor]`. Libere comandos que começam com `maestri`.
- Primeira vez numa pasta de papel: "Trust this folder?" (aprove com `--raw "\r"`).
- O banner mostra a cota restante ("monthly limit: 8% left"): com pouca cota, só tarefas curtas.
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

Sintoma: papéis citando outro projeto, presets com `--add-dir` de outra pasta, rodapé com caminho antigo. Correção (com ok do usuário): um Batedor reescreve os papéis a partir de `papeis.md` em `.maestri/papeis/`; o Maestro aplica com `maestri role write`; troque os presets por modelo (seção 2) e reabra cada terminal com `recruit --replace`.

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
| Banner "Introducing …" no Antigravity | novidade de modelo | some com o primeiro prompt; não precisa de ação |
| Produtor reporta despacho "truncado" ou o texto fica na caixa de entrada | despacho enviado enquanto o terminal abria | usar `maestri_batch.py` (espera o terminal ficar pronto e recupera o texto parado); com `maestri ask` direto, espere o prompt aparecer no `check` |
| Relatório ou pesquisa vira instrução de projeto de repente | no Windows (e no macOS padrão) `claude.md` = `CLAUDE.md`, `agents.md` = `AGENTS.md`, `gemini.md` = `GEMINI.md`: as ferramentas carregam o arquivo como regra | nunca dê esses nomes a relatórios, pesquisas ou notas (use `anthropic.md`, `pesquisa-claude.md`...) |
| PowerShell: `python -c "..."` ou `maestri ask "..."` perde aspas internas | PowerShell 5.1 remove aspas de argumentos de programas nativos | script em arquivo ou heredoc no Bash; relatório em arquivo |
| Kit do Maestro bloqueia um laço `for … do maestri check …` | versão antiga do `guarda.py` | atualize a skill (`git pull`); laços e `sed -n` em arquivos permitidos são liberados |
