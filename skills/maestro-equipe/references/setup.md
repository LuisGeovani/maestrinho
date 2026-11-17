# Setup da equipe no Maestri

Confirme cada bloco com o usuário antes de executar. `<RAIZ>` é o caminho absoluto do projeto (ex.: `C:\Users\<user>\Documents\Projeto`).

## 1. Inventário

```
maestri list            # quem já está conectado (não recrute de novo quem existe)
maestri preset list     # presets disponíveis (exige modo Maestro ligado)
maestri role list       # papéis do workspace atual
maestri preset show "Nome"   # ver o comando de um preset
agy models              # IDs dos modelos do Antigravity (para --model)
```

## 2. Presets

Os presets são **globais**: valem para todos os workspaces. Para cada projeto, inclua `--add-dir "<RAIZ>"`, para o agente enxergar o projeto (ele abre na pasta do papel, `.maestri/roles/<id>`). Se houver vários projetos, crie presets com o nome do projeto (ex.: `Regex Claude Opus`).

```
maestri preset create "<Proj> Claude Opus"   --command 'claude --model opus   --add-dir "<RAIZ>"'
maestri preset create "<Proj> Claude Sonnet" --command 'claude --model sonnet --add-dir "<RAIZ>"'
maestri preset create "<Proj> Claude Haiku"  --command 'claude --model haiku  --add-dir "<RAIZ>"'
maestri preset create "Agy Claude Opus · <proj>"     --command 'agy --model claude-opus-5-5-high    --add-dir "<RAIZ>"'
maestri preset create "Agy Gemini Hydrogen · <proj>" --command 'agy --model gemini-4-hydrogen-xhigh --add-dir "<RAIZ>"'
maestri preset create "Agy Gemini Argon · <proj>"    --command 'agy --model gemini-4-argon-high     --add-dir "<RAIZ>"'
```

Codex (repassa as variáveis do Maestri, que o Codex não herda):

```
codex -c "shell_environment_policy.set.MAESTRI_PIPE='$env:MAESTRI_PIPE'" -c "shell_environment_policy.set.MAESTRI_TERMINAL_ID='$env:MAESTRI_TERMINAL_ID'" -c "shell_environment_policy.set.MAESTRI_WORKSPACE_ID='$env:MAESTRI_WORKSPACE_ID'" -c "shell_environment_policy.set.MAESTRI_DATA_DIR='$env:MAESTRI_DATA_DIR'" -c "shell_environment_policy.set.MAESTRI_CLI='$env:MAESTRI_CLI'"
```

Confira os IDs de modelo com `agy models` antes de criar. Eles mudam com o tempo.

## 3. Papéis

Os papéis são **do workspace atual**: só o Maestro daquele workspace cria. Use os modelos de `papeis.md`, trocando projeto, caminho, pastas e especialidades.

```
maestri role create "Nome do papel" "<prompt>"
maestri role edit "Nome" "texto antigo" "texto novo"   # ajuste pontual
```

## 4. Recrutar

```
maestri recruit "Farol"   --preset "<Proj> Claude Opus"   --role "Arquiteto"
maestri recruit "Forja"   --preset "<Proj> Claude Sonnet" --role "Produtor Critico"
maestri recruit "Faísca"  --preset "<Proj> Claude Haiku"  --role "Agil"
maestri recruit "Bigorna" --preset "Agy Claude Opus · <proj>"     --role "Produtor Reforco"
maestri recruit "Prisma"  --preset "Agy Gemini Hydrogen · <proj>" --role "Produtor Volume"
maestri recruit "Lente"   --preset "Agy Gemini Argon · <proj>"    --role "Revisor"
maestri recruit "Agulha"  --preset "Codex"                        --role "Produtor Leve"
```

- **Trocar o agente de um produtor** sem perder papel e conexões: `maestri recruit "Nome" --preset P --replace "Nome"`.
- **Depois de recrutar:**
  - `maestri check "Nome"` para conferir o modelo na tela;
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
3. responde `maestri ask "Maestro" "PING <nome>: leitura ok/falhou, maestri ok/falhou, modelo <nome>"`.

Todos precisam responder pelo `maestri`. Quem falhar entra em "Problemas conhecidos".

## 7. Git do projeto

Se ainda não for repositório e o usuário autorizar:
- `git init`;
- `.gitignore` com `node_modules`, `dist`, builds, `.env*` (menos `!.env.example`), backups, `.maestri/` e `.worktrees/`;
- commits pequenos, só no nome do usuário.

Num repositório remoto que já tem commit inicial:
- `git fetch` + `git reset origin/main` para basear o histórico local no remoto;
- junte o `.gitignore` do remoto com o local;
- faça um commit por bloco.

## Problemas conhecidos

| Sintoma | Causa | Correção |
|---|---|---|
| Produtor pede permissão para ler cada arquivo do projeto | Abre em `.maestri/roles/<id>`, e o projeto fica fora da área de trabalho | `--add-dir "<RAIZ>"` no preset. No Antigravity, também `"allowNonWorkspaceAccess": true` em `~/.gemini/antigravity-cli/settings.json` |
| Antigravity: `maestri` dá `access denied (err 5)` | Os comandos rodam no sandbox, com integridade Low | Em `~/.gemini/antigravity-cli/settings.json`, `"permissions": {"allow": ["command(maestri)", "command(regex:maestri .*)"]}`, e no papel: "se der access denied, rode o maestri fora do sandbox". Mesmo assim, o agente pode pedir confirmação a cada `maestri ask "Maestro"`: aprove |
| Codex: `maestri: only available inside Maestri terminals (MAESTRI_PIPE not set)` | O Codex abre sem as variáveis `MAESTRI_*` | Preset do Codex repassando as variáveis (seção 2). `[shell_environment_policy] inherit = "all"` em `~/.codex/config.toml` ajuda, mas sozinho não basta. Faça backup antes de editar |
| `maestri: command not found` no terminal do produtor | CLI fora do PATH | Adicionar `%LOCALAPPDATA%\Programs\Maestri\resources\cli` ao PATH do usuário e reabrir o terminal |
| `maestri ask --batch` dá "Invalid --batch JSON" | Escape quebrado por caminho do Windows ou aspas | Gerar o JSON num arquivo e enviar com `scripts/maestri_batch.py` |
| Mensagem enviada some | O agente ainda estava abrindo | Esperar o prompt aparecer e reenviar (só se não foi recebida) |
| Arquivo com caractere estranho no início | O PowerShell 5.1 grava UTF-8 com BOM | Remover o BOM (`sed -i '1s/^\xEF\xBB\xBF//' arquivo`) e pedir para gravar com `-Encoding utf8` sem BOM |
| `recruit --dir` não muda a pasta | Com papel definido, o Maestri usa a pasta do papel | Citar o caminho absoluto em toda tarefa |
| Mudança em configuração global bloqueada pelo modo automático do Claude Code | É uma ação sensível (permissões de outra ferramenta) | Explicar ao usuário o que e por quê; aplicar só com autorização explícita dele |
