# OpenCode (2026-11-18)

Coleta: pesquisa web. `[incerto]` = não confirmado em fonte oficial. No ambiente do usuário havia só o app desktop; o CLI é instalado nos testes (ver `docs/testes/`).

## Versões e instalação

- Repositório: github.com/anomalyco/opencode. v1.19.6 marcada "Latest" (17/11) e v2.3.2 (18/11). Upgrade: `opencode upgrade --major`.
- Doc atual (opencode.ai/docs) é da v2; a da v1 fica em opencode.ai/v1/docs.
- Windows v1: `npm i -g opencode-ai` (também scoop/choco; a doc recomenda WSL). Windows v2: binário standalone ou `npm i -g @opencode/cli`.
- O Maestri tem preset "OpenCode" (`opencode`) e corrigiu `maestri ask` entre agentes OpenCode no Windows (changelog Windows 0.22.0).

## Modelos

**Zen grátis "por tempo limitado"** (opencode.ai/docs/zen): `big-pickle` (modelo "stealth"), `deepseek-v4.1-flash-free`, `mimo-v2.6-flash-free`, `longcat-2.5-free`, `hy4-flash-free`, `iceman-free`, `flint-40b-free`, `beam-free`, `inkling-2-small-free`, `nemotron-3.5-lightning-free`, `nemotron-3.5-super-vl-free`, `jev-1.13-free`.
- Big Pickle, Iceman, Flint e Inkling **podem usar os dados para treino**: não usar com código sensível.
- Esconder os grátis: `OPENCODE_DISABLE_FREE_MODELS=1`.

**Zen pagos** (US$/MTok entrada/saída): glm-5.3 1,40/4,40 · kimi-k2.7-code 0,95/4 · kimi-k3 3/15 · qwen3.8-max 2/6 · deepseek-v4-pro 1,74/3,48 · deepseek-v4.1-flash 0,30/1,20 · minimax-m3 0,30/1,20 · grok-build-0.1 1/2.

**OpenCode Go** (opencode.ai/docs/go): US$10/mês (Go Plus US$40); 5 h = 20% da cota mensal, semanal = 50% (reinicia segunda 00:00 UTC); Kimi K3.1 Pro, GLM-5.3, Qwen4 Max, DeepSeek V4 Pro, GPT 6 Luna e outros; IDs `opencode-go/<id>`.

**Logins** (opencode.ai/docs/providers): "Sign in with ChatGPT" (conta na cota do plano), GitHub Copilot, Google Vertex (ADC), Ollama/LM Studio/vLLM locais. Claude Pro/Max: não documentado `[incerto]`.

**Terminal-Bench 4.1** (tbench.ai, quase todos no harness Claude Code): Kimi K3.1 Pro 59,7% · GLM-5.3 41,2% · DeepSeek V4.1 Flash 38,5% · GLM-5.3-Flash 37,0% · Qwen3.8-Max 27,0% · Kimi K3 23,0% · MiniMax M3 7,6% · DeepSeek V4 Pro 6,7%. Fora o Kimi K3.1 Pro, bem abaixo dos fechados: usar para tarefas simples e baratas (inferência). Big Pickle sem benchmark.

## CLI, agentes, permissões, skills

- v1: `opencode -m provider/model --agent plan`; `opencode run "..." -m provider/model --agent build --variant high --format json -f arq`; `opencode models [provider]`; `opencode auth login`.
- v2: variante no próprio ID do modelo (`openai/gpt-6.1-sol#high`); flags do `run` na v2 `[incerto]`.
- Atalhos: Ctrl+T troca a variante; Shift+Tab troca o agente (v2).
- Agentes embutidos: `build` (padrão), `plan` (não edita), subagentes `general` e `explore` (só leitura).
- Permissões: v1 `"permission":{"*":"ask","bash":"allow","edit":"deny"}` (a última regra que casa vence). **v2 é allow em tudo por padrão**, inclusive diretórios externos: `"permissions":[{"action":"shell","resource":"git push *","effect":"deny"}]`.
- `AGENTS.md` do projeto até a raiz + global `~/.config/opencode/AGENTS.md`; sem AGENTS.md usa CLAUDE.md.
- Skills: `.opencode/skills`, `~/.config/opencode/skills`, `.claude/skills`, `~/.claude/skills`, `.agents/skills`, `~/.agents/skills` (v1 exige `name` igual ao nome da pasta).
- Variáveis: `{env:VAR}` e `{file:path}` na config; `OPENCODE_CONFIG`, `OPENCODE_CONFIG_CONTENT`, `OPENCODE_PERMISSION` (JSON inline), `OPENCODE_DISABLE_AUTOUPDATE`, `OPENCODE_GIT_BASH_PATH` (Windows).

## URLs

opencode.ai/docs/zen · opencode.ai/docs/go · github.com/anomalyco/opencode/releases · opencode.ai/v1/docs · opencode.ai/docs · opencode.ai/v1/docs/cli · opencode.ai/docs/models · opencode.ai/docs/agents · opencode.ai/docs/permissions · opencode.ai/v1/docs/permissions · opencode.ai/docs/skills · opencode.ai/docs/rules · opencode.ai/docs/providers · opencode.ai/docs/config · opencode.ai/docs/migrate-v1
