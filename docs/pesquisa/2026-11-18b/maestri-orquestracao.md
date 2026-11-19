# Maestri e boas práticas de orquestração (2026-11-18)

Coleta: pesquisa web + `maestri help` e `maestri ask --help` locais + logs das sessões do Maestro (projetos Dra e regex). `[incerto]` = não confirmado.

## Maestri: o que a ajuda local confirma

- `maestri ask` **bloqueia até o alvo ficar ocioso**; ao estourar o timeout, não reenvie: `maestri check` e espere de novo.
- **Ask back:** o produtor responde com `maestri ask "<nome do Maestro>" "<resultado>"`; isso resolve o `ask` pendente do Maestro e chega **inteiro** como nova mensagem, em vez de cortado na última tela.
- `--batch` recebe um JSON `{agente: prompt}` com escape JSON padrão, roda em paralelo e devolve `[{name, output}]` (ou `{name, error}`) quando todos terminam.
- **Argumentos de prompt decodificam `\n` e `\t`** (`\\n` envia literal): caminho do Windows dentro de um `maestri ask` pode virar quebra de linha ou tab.
- Agente em floor/workspace descarregado é acordado; se a resposta disser que ainda está iniciando, perguntar de novo.
- O nome do Maestro é o que aparece em `You:` no `maestri list` (neste terminal, "Claude Code"); agentes de outro workspace são `Nome @ Workspace`.
- Comandos de Maestro (`recruit`, `preset`, `role`, `band`, `partitura`, `floor`, `routine`, `workspace`) exigem o modo Maestro ligado no terminal.

## Maestri: documentação pública (themaestri.app/en/docs, changelog)

- Mensagem que chega com o agente ocupado é entregue quando ele fica pronto (0.53.0); dois prompts seguidos chegam como duas mensagens (0.49.0); colagem grande vira "pill" (0.46.0); asks simultâneos e cadeias de ask back ficaram confiáveis (0.30.15).
- Roles: o agente abre num subdiretório do projeto com o próprio CLAUDE.md/AGENTS.md e `role.json` (no disco: `<projeto>/.maestri/roles/<id>/`, com `<working_directory>` apontando o projeto e `.gemini/settings.json` com `includeDirectories`).
- Floors: git worktree por padrão; no Windows é checkout simples só com arquivos rastreados (usar hook de setup para dependências); `maestri floor status --state working|blocked|review|done`; land/delete só do Ground.
- Notas são arquivos .md; "Lock Contents" deixa a nota só-leitura para agentes (bom para specs); fichários funcionam como raias (Backlog, Building, Review, Shipped).
- Recomendações oficiais (docs/maestro): brief único numa nota ligada ao Maestro e conectada aos recrutas; papéis claros; equipe mista para "play the strengths of each tool against each other" (exemplo: Codex revisa, Claude constrói, OpenCode escreve); dispensar recruta ao terminar; floors quando os agentes editariam os mesmos arquivos.
- Codex: sandbox bloqueia a conexão do `maestri` → liberar comandos que começam com `maestri`; no Windows, o sandbox elevado não acessa a pasta do Maestri → usar o não elevado no `%USERPROFILE%\.codex\config.toml` (docs/troubleshooting). O Maestri adiciona `--no-daemon` no Codex 0.157+.
- OpenCode: `maestri ask` entre agentes OpenCode não trava mais no Windows (Windows 0.22.0).
- Uso/cota por provedor: o Maestri mantém `%MAESTRI_DATA_DIR%/usage/providers/.status.json` (Claude: `claude -p` com `get_usage`; Codex: `codex app-server` `account/rateLimits/read`; Antigravity: `agy -p /usage --output-format json`).

## Maestri: falhas vistas nos logs do usuário

- Nome "Maestro" fixo em papéis/prompts/regra do Antigravity.
- Relatório de produtor digitado no TUI do Maestro **atropelou um AskUserQuestion** aberto.
- PowerShell 5.1 remove aspas de argumentos de programas nativos (reproduzido): relatório com aspas quebra.
- Antigravity gastando 2–3 min "pensando" para rodar `maestri ask` no sandbox.
- Classificador do auto mode do Claude Code bloqueou `maestri recruit --replace` e `git commit` do Maestro.
- Presets duplicados por projeto (`--add-dir` fixo) e papéis copiados de outro projeto.
- O Maestro fazia o trabalho sozinho quando a skill não estava carregada.

## Orquestração: evidências

- Anthropic, multi-agent research system (anthropic.com/engineering/multi-agent-research-system): agentes ~4x os tokens de um chat, multi-agente ~15x; volume de tokens explica 80% da variância; Opus líder + Sonnet subagentes superou Opus sozinho em 90,2%; escala de esforço (simples: 1 agente, 3–10 chamadas; comparação: 2–4 subagentes; complexa: 10+); cada delegação precisa de objetivo, formato de saída, orientação de ferramentas/fontes e limites; saídas em armazenamento externo passadas por referência leve; **não compensa** com contexto compartilhado, muitas dependências e a maioria das tarefas de código.
- Building effective agents: começar simples; perguntas fáceis para modelos menores; orquestrador-trabalhadores e avaliador-otimizador.
- Context engineering: menor conjunto de tokens de alto sinal; subagentes devolvem resumos de 1–2 mil tokens.
- Claude Code costs: Sonnet atende a maior parte do código; agent teams ~7x mais tokens.
- OpenAI, practical guide to building agents: começar com um agente; padrão manager ou handoffs; linha de base com o modelo mais capaz e depois trocar por menores (via resumos de terceiros).
- Google ADK: generator-critic; agentes em paralelo gravam cada um numa chave própria; "start with a sequential chain, debug it, then add complexity".
- Autopreferência de juiz LLM: GPT-4 +10%, Claude-v1 +25% (arxiv 2306.05685); reconhecer o próprio texto correlaciona com o viés (arxiv 2404.13076).
- Diversidade: debate entre modelos de famílias diferentes 91% no GSM-8K contra 82% com três iguais (arxiv 2410.12853).
- Cascata/roteamento: FrugalGPT até 98% menos custo (arxiv 2305.05176); RouteLLM corta custo >2x sem perder qualidade (arxiv 2406.18665).

## URLs

themaestri.app/en/changelog · themaestri.app/en/windows/changelog · themaestri.app/en/docs/{maestro,terminals,connections,floors,notes,ficharios,routines,partituras,bands,environments,troubleshooting,wire} · themaestri.app/en/learn · anthropic.com/engineering/multi-agent-research-system · anthropic.com/engineering/building-effective-agents · anthropic.com/engineering/effective-context-engineering-for-ai-agents · code.claude.com/docs/en/{model-config,sub-agents,costs} · cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf · developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/
