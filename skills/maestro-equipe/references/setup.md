# Setup da equipe no Maestri

Confirme cada bloco com o usuário antes de executar. `<RAIZ>` é o caminho absoluto do projeto (ex.: `C:\Users\<user>\Documents\Projeto`).

## 1. Inventário

```
maestri list            # quem já está conectado (não recrute de novo quem existe)
maestri preset list     # presets disponíveis (exige modo Maestro ligado)
maestri role list       # papéis do workspace atual
maestri preset show "Nome"   # ver o comando de um preset
```

## 2. Presets

Os presets são **globais**: valem para todos os workspaces. Para cada projeto, inclua `--add-dir "<RAIZ>"`, para o agente enxergar o projeto (ele abre na pasta do papel, `.maestri/roles/<id>`). Se houver vários projetos, crie presets com o nome do projeto (ex.: `<Proj> Claude Sonnet`).

Cada preset fixa **modelo e raciocínio** (os padrões divergem entre ferramentas). Os terminais Claude Code recrutados usam só Sonnet e Haiku; o Opus fica com o Maestro (e com a Bigorna, no Antigravity).

```
maestri preset create "<Proj> Claude Sonnet"      --command 'claude --model sonnet --effort medium --add-dir "<RAIZ>"'
maestri preset create "<Proj> Claude Sonnet High" --command 'claude --model sonnet --effort high   --add-dir "<RAIZ>"'
maestri preset create "<Proj> Claude Haiku"       --command 'claude --model haiku  --effort medium --add-dir "<RAIZ>"'
maestri preset create "Agy Claude Opus · <proj>"     --command 'agy --model claude-opus-5-5-high    --add-dir "<RAIZ>"'
maestri preset create "Agy Gemini Hydrogen · <proj>" --command 'agy --model gemini-4-hydrogen-xhigh --add-dir "<RAIZ>"'
maestri preset create "Agy Gemini Argon · <proj>"    --command 'agy --model gemini-4-argon-high     --add-dir "<RAIZ>"'
```

Sob demanda (um produtor ou o usuário roda `agy models` para confirmar o ID exato antes): `claude-sonnet-5-5-medium` (transbordo da Forja) e o Gemini 3.8 Flash em Low/Medium. `--effort` valores: `low|medium|high|xhigh|max`; o Claude Code exige versão mínima para Sonnet 5.5 (v2.1.284) e Haiku 5.5 (v2.1.293).

Codex (repassa as variáveis do Maestri, que o Codex não herda; **crie só quando a Agulha estiver ativa**):

```
codex -c "shell_environment_policy.set.MAESTRI_PIPE='$env:MAESTRI_PIPE'" -c "shell_environment_policy.set.MAESTRI_TERMINAL_ID='$env:MAESTRI_TERMINAL_ID'" -c "shell_environment_policy.set.MAESTRI_WORKSPACE_ID='$env:MAESTRI_WORKSPACE_ID'" -c "shell_environment_policy.set.MAESTRI_DATA_DIR='$env:MAESTRI_DATA_DIR'" -c "shell_environment_policy.set.MAESTRI_CLI='$env:MAESTRI_CLI'"
```

Confira os IDs de modelo com `agy models` antes de criar, pedindo a um produtor (ex.: Faísca) ou ao usuário que rode num terminal normal (dentro do agente ele falha no sandbox). Os IDs mudam com o tempo.

## 3. Papéis

Os papéis são **do workspace atual**: só o Maestro daquele workspace cria. Use os modelos de `papeis.md`, trocando projeto, caminho, pastas e especialidades.

```
maestri role create "Nome do papel" "<prompt>"
maestri role edit "Nome" "texto antigo" "texto novo"   # ajuste pontual
```

## 4. Recrutar

```
maestri recruit "Farol"   --preset "<Proj> Claude Sonnet High" --role "Arquiteto"
maestri recruit "Forja"   --preset "<Proj> Claude Sonnet"      --role "Produtor Critico"
maestri recruit "Faísca"  --preset "<Proj> Claude Haiku"       --role "Agil"
maestri recruit "Bigorna" --preset "Agy Claude Opus · <proj>"     --role "Produtor Reforco"
maestri recruit "Prisma"  --preset "Agy Gemini Hydrogen · <proj>" --role "Produtor Volume"
maestri recruit "Lente"   --preset "Agy Gemini Argon · <proj>"    --role "Revisor"
maestri recruit "Agulha"  --preset "Codex"                        --role "Produtor Leve"   # só com cota; pode ficar pausada
```

- **Trocar o agente de um produtor** sem perder papel e conexões: `maestri recruit "Nome" --preset P --replace "Nome"`.
- **Depois de recrutar:**
  - `maestri check "Nome"` para conferir **modelo, raciocínio e cota no rodapé** (não pergunte ao agente: ele não enxerga o próprio `/model`);
  - aceite o "Do you trust the contents of this project?" do Antigravity (`maestri ask "Nome" --raw "\r"`), que aponta para a pasta de papel gerada pelo próprio Maestri;
  - espere o banner virar prompt antes do primeiro `ask`.
- **Não crie band** sem o usuário pedir, e **não conecte produtores entre si**: tudo passa pelo Maestro.

## 5. Quadro e partitura

```
maestri note create "<modelo do quadro, ver modelos.md>" --name "Quadro Modelo" --stack "Rodadas"
maestri partitura create "Equipe <Proj>" --description "Maestro + produtores em 3 famílias"
```

## 6. Teste de ambiente (ping)

Mande um lote só de leitura (via `scripts/maestri_batch.py`). Cada um:
1. lê a primeira linha de `<RAIZ>\docs\PROJETO.md`;
2. roda `maestri list`;
3. responde `maestri ask "Maestro" "PING <nome>: leitura ok/falhou, maestri ok/falhou"`.

Todos precisam responder pelo `maestri`. Quem falhar entra em "Problemas conhecidos". Modelo e raciocínio você confere no rodapé (`maestri check`), não pelo ping.

## 7. Git do projeto

Se ainda não for repositório e o usuário autorizar:
- `git init`;
- `.gitignore` (despachado a um produtor) com `node_modules`, `dist`, builds, `.env*` (menos `!.env.example`), backups, `.maestri/` e `.worktrees/`;
- commits pequenos, só no nome do usuário.

Num repositório remoto que já tem commit inicial:
- `git fetch` + `git reset origin/main` para basear o histórico local no remoto;
- despache a um produtor juntar o `.gitignore` do remoto com o local;
- faça um commit por bloco.

## Problemas conhecidos

| Sintoma | Causa | Correção |
|---|---|---|
| Produtor pede permissão para ler cada arquivo do projeto | Abre em `.maestri/roles/<id>`, e o projeto fica fora da área de trabalho | `--add-dir "<RAIZ>"` no preset. No Antigravity, também `"allowNonWorkspaceAccess": true` em `~/.gemini/antigravity-cli/settings.json` |
| Antigravity: `maestri` dá `access denied (err 5)` ou pede confirmação a cada `maestri ask "Maestro"` | O comando roda no sandbox (integridade Low) e a permissão `command(...)` do `maestri ask "Maestro"` não está liberada | Regra aplicada e funcionando: ver bloco "Regra do Antigravity" logo abaixo da tabela. Só vale para terminais abertos **depois** da mudança (religue com `--replace`). No papel, mantenha só "se der access denied, rode SOMENTE o comando maestri fora do sandbox" (instrução ampla "saia do sandbox" foi bloqueada). `[incerto]` o modo auto ainda pode pedir confirmação: se pedir, aprove com "permitir uma vez" |
| Codex: `maestri: only available inside Maestri terminals (MAESTRI_PIPE not set)` | O Codex abre sem as variáveis `MAESTRI_*` | Preset do Codex repassando as variáveis (seção 2). `[shell_environment_policy] inherit = "all"` em `~/.codex/config.toml` ajuda, mas sozinho não basta. Despache a edição a um produtor (escopo fechado, backup antes) |
| `maestri: command not found` no terminal do produtor | CLI fora do PATH | Adicionar `%LOCALAPPDATA%\Programs\Maestri\resources\cli` ao PATH do usuário e reabrir o terminal |
| `maestri ask --batch` dá "Invalid --batch JSON" | Escape quebrado por caminho do Windows ou aspas | Gerar o JSON num arquivo e enviar com `scripts/maestri_batch.py` |
| Mensagem enviada some | O agente ainda estava abrindo | Esperar o prompt aparecer e reenviar (só se não foi recebida) |
| Arquivo com caractere estranho no início | O PowerShell 5.1 grava UTF-8 com BOM | Despachar a um produtor remover o BOM (com `sed`) e pedir para gravar com `-Encoding utf8` sem BOM |
| `recruit --dir` não muda a pasta | Com papel definido, o Maestri usa a pasta do papel | Citar o caminho absoluto em toda tarefa |
| Mudança em configuração global bloqueada pelo modo automático do Claude Code | É uma ação sensível (permissões de outra ferramenta) | Explicar ao usuário o que e por quê; com autorização explícita dele, despachar a mudança a um produtor (o Maestro não edita). Ex.: `inherit = "all"` e `ignore_default_excludes = true` no `~/.codex/config.toml` repassam também variáveis com TOKEN/KEY; prefira `include_only = ["MAESTRI_*", "PATH", ...]` (testar o que o Codex exige) ou o preset com as variáveis |
| Relatório longo chega **cortado** | Aspas no texto do `maestri ask "Maestro"` ou relatório extenso | Pedir relatórios curtos (10–12 linhas) e sem aspas dentro do texto; se cortar, pedir só o restante |
| Terminal volta ao PowerShell depois de atualização da ferramenta (ex.: Codex) | A ferramenta fechou ao atualizar | Religar com `maestri recruit "Nome" --preset P --replace "Nome"` |
| Agente tenta rodar `/model` ou controlar o computador para ver o próprio modelo | Ele não enxerga o `/model`: no Antigravity o comando não é invocável pelo agente; o Codex tenta usar computer use | Não peça isso. O Maestro lê modelo e cota no rodapé (`maestri check`); proíba computer use no papel |

### Regra do Antigravity para o `maestri ask "Maestro"`

Em `~/.gemini/antigravity-cli/settings.json`, `permissions.allow` com **exatamente**:

```
"command(regex:(?s)^maestri ask \"Maestro\"(\\s+.*)?$)"
```

O texto acima já está escapado para JSON (`\"` e `\\s`): copie-o como está para dentro do array.

- O `(?s)` faz o ponto casar quebras de linha, para relatórios multilinha passarem.
- `command(maestri)` genérico libera demais (qualquer subcomando); a regra acima cobre só `maestri ask "Maestro"`.
- Regra `unsandboxed(...)` não existe: o Antigravity avisa ao abrir que `Invalid unsandboxed permission rules found; they are ignored and grant nothing`.
- A regra só vale para terminais abertos depois da mudança (religue com `--replace`). Confira o aviso de settings no banner com `maestri check`.
- Fonte: https://antigravity.google/docs/permissions. `[incerto]` se o modo auto ainda pedir confirmação.

## Edição de configuração de outras ferramentas

`settings.json`, `config.toml` e afins **não são editados pelo Maestro**. Despache a um produtor (ex.: Faísca) com escopo fechado: o arquivo exato, backup antes e o texto a mudar. O Maestro só confere o resultado pelo relatório e pelo banner do terminal (`maestri check`). Mudança em configuração global exige autorização do usuário antes do despacho.

## Reforço por hook `[a validar]`

Ideia: um hook `PreToolUse` nas configurações do Claude Code do terminal do Maestro, bloqueando `Edit`, `Write`, `NotebookEdit`, `WebSearch`, `WebFetch` e `Agent`. Limites: o hook não alcança os produtores Claude Code (eles abrem em `.maestri/roles/<id>`, com outra configuração) e precisa ser testado antes de confiar nele. Não há hook pronto aqui; peça a um produtor para redigi-lo e teste.
