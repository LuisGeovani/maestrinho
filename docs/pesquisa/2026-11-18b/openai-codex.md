# OpenAI / Codex CLI (2026-11-18)

Coleta: pesquisa web + cache local do Codex CLI 0.170.0 (plano Free do usuário). `[incerto]` = não confirmado em fonte oficial.

## Modelos

Versão vigente: **GPT-6.2** (17/11/2026). Não existe GPT-6 Terra; a Terra atual é a 6.1.

| Slug | Data | Posição oficial | US$/MTok (entrada/cache/saída) | Terminal-Bench 4.1 (max) |
|---|---|---|---|---|
| `gpt-6.2-astra` | 17/11/2026 | topo, "hardest projects" | 8 / 0,40 / 40 | 62,1% |
| `gpt-6.2-sol` | 17/11/2026 | "go-to model for everyday work, from coding to powering agents"; a 0,5 pt da Astra no FrontierCode 2.0 por ~1/5 do custo | 2 / 0,10 / 10 | 61,5% |
| `gpt-6.1-sol` | 29/09/2026 | perto da GPT-6 Astra por menos | 2 / 0,10 / 10 | 60,9% |
| `gpt-6-astra` | set/2026 | topo anterior | 10 / 1 / 50 | 60,3% |
| `gpt-6.1-terra` | 26/10/2026 | rápida: escrita, visão, computer use; não é a escolha para código difícil | 1 / 0,05 / 5 | 53,3% |
| `gpt-6-sol` | 22/09/2026 | Sol anterior; Coding Agent Index 57 | 2 / 0,20 / 10 | 50,3% |
| `gpt-6-luna` | 22/09/2026 | "most efficient… focused, high-volume tasks"; Coding Agent Index 41; alucinação 77% | 0,10 / 0,01 / 0,50 | 15,2% |
| `gpt-5.6-sol/-terra/-luna` | 09/07/2026 | geração anterior | 4/20 · 2/12 · 0,2/1,2 | — |

- 6.2 Astra: testadores relatam código mais limpo e testes mais focados em projetos existentes.
- `gpt-reserve` = "Luna Reserve": uso extra com GPT-5.6 Luna quando o uso normal acaba; cota própria; oficialmente para Plus/Pro selecionados (aparece no Free do usuário `[incerto]`).
- `codex-auto-review`: subagente revisor das aprovações de sandbox (`approvals_reviewer="auto_review"`); não é para trabalho.
- Aposentados no Codex com login ChatGPT: gpt-5.4/5.4-mini (31/08), gpt-5.3-codex-spark (14/09), gpt-5.5 (14/10).

Cache local do plano Free (`~/.codex/models_cache.json`): `gpt-reserve`, `gpt-6-luna`, `gpt-5.6-terra` (efforts até `ultra`), `gpt-5.6-luna`, `codex-auto-review`. Config do usuário: `model = "gpt-6-luna"`, `model_reasoning_effort = "medium"`.

## Effort

- Codex: `low` ("Light"), `medium`, `high`, `xhigh` ("Extra High"), `max`, `ultra`. `ultra` usa subagentes; "most tasks do not need Max or Ultra".
- Recomendação: low em tarefa bem delimitada; medium/high em mudança complexa e debug; xhigh em trabalho longo de raciocínio pesado.
- Luna: começar em high (vai até max). GPT-6 Astra: começar em low. 6.2: padrão do cliente. Na API, a 6.2 rejeita `none`.
- Ultrafast: até 4,5x mais rápido no Codex, gasta mais cota.

## Planos (learn.chatgpt.com/docs/pricing)

| Plano | Modelos | Limites |
|---|---|---|
| Free / Go ($8) | "GPT-6 Luna at Standard speed in the desktop app, subject to rollout" | sem números; no usuário o Maestri mostra janela **mensal** (92% usada em 18/11) |
| Plus ($20) / Business | todos | por 5 h: 6.2 Astra 6–50 · 6.2 Sol 17–180 · 6.1 Terra 35–285 · 6 Luna 350–3000; semanal pode existir |
| Pro ($100/$200/$500) | todos; Ultrafast no de $500 | sem limite de 5 h; semanal pode existir |

Uso: `/status` no CLI; chatgpt.com/codex/settings/usage; no Maestri, provedor `codex` do `.status.json`.

## CLI (learn.chatgpt.com/docs/cli/reference, /config-file/config-reference)

- `-m <slug>`, `-c model_reasoning_effort=high`, `-p/--profile`, `-s read-only|workspace-write|danger-full-access`, `-a on-request|never`, `--add-dir`, `-C/--cd`, `codex exec` (`--json`), `codex exec resume --last`. Não usar `--yolo`.
- `AGENTS.md` carrega sozinho (o mais próximo vence).
- Skills: repo `.agents/skills` (cwd, pai, raiz do repo); usuário `~/.agents/skills`; `~/.codex/skills` é legado `[incerto]`.
- Computer use: sem chave oficial na CLI para desligar; proibir no papel/prompt.
- Variáveis: `shell_environment_policy.inherit` / `.set` (o preset do Maestri repassa `MAESTRI_*`).
- Windows: o sandbox elevado roda como outro usuário e não acessa a pasta do Maestri; trocar para o sandbox não elevado no `config.toml` e liberar comandos `maestri` (themaestri.app/en/docs/troubleshooting).

## Prompt (learn.chatgpt.com/docs/learn/best-practices; developers.openai.com/api/docs/guides/latest-model)

Objetivo, contexto, restrições e "pronto quando"; tarefa complexa começa em plan mode; pedir testes, rodar os checks e revisar o diff; AGENTS.md curto; seguir no escopo, registrar suposições, parar só em bloqueio/decisão do usuário/ação irreversível; conferir cada parte do pedido antes de terminar; reaproveitar a lógica existente.

## URLs

learn.chatgpt.com/docs/models · learn.chatgpt.com/docs/pricing.md · developers.openai.com/api/docs/pricing · community.openai.com/t/gpt-6-2-astra-and-sol-are-now-available/1417531 · tbench.ai · artificialanalysis.ai/articles/gpt-6-sol-and-luna-push-the-cost-efficiency-frontier · help.openai.com/en/articles/20001499-luna-reserve-in-codex-and-chatgpt-work · alignment.openai.com/auto-review · learn.chatgpt.com/docs/agent-approvals-security · learn.chatgpt.com/docs/cli/reference · learn.chatgpt.com/docs/config-file/config-reference · learn.chatgpt.com/docs/build-skills.md · learn.chatgpt.com/docs/computer-use · learn.chatgpt.com/docs/learn/best-practices · developers.openai.com/api/docs/guides/latest-model · openai.com/index/introducing-gpt-6-1-terra
