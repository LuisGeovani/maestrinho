# Claude: modelos, effort e cota (2026-11-18)

Fontes: skill `claude-api` do Claude Code 2.1.328 (tabela de modelos em cache de 2026-11-03), platform.claude.com e code.claude.com, support.claude.com. `[incerto]` = não confirmado em fonte oficial.

## Modelos atuais

| Modelo | ID | Contexto | US$/MTok (entrada/saída) | Posição oficial |
|---|---|---|---|---|
| Fable 5.2 | `claude-fable-5-2` | 1M | 8 / 40 | o mais capaz de uso geral: raciocínio difícil e agente de longo horizonte; turnos longos; prompts prescritivos demais reduzem a qualidade |
| Opus 5.5 | `claude-opus-5-5` | 1M | 4 / 20 | Opus atual e modelo padrão; agentes longos, refatoração grande |
| Sonnet 5.5 | `claude-sonnet-5-5` | 1M | 2 / 10 | velocidade + capacidade para código do dia a dia, agentes e trabalho corporativo |
| Haiku 5.5 | `claude-haiku-5-5` | 1M | 0,10 / 0,50 até 100K de prompt; 0,50 / 2,50 acima | volume, latência, classificação, extração, roteamento, subagentes |

- GPQA Diamond: Haiku 85% contra 91% de Sonnet/Opus, a cerca de 1/10 do custo por acerto (pesquisa anterior, `docs/pesquisa/2026-11-18/anthropic.md`).
- Sonnet 5.5 tem "bom olho para design" (anthropic.com/claude-sonnet-5-5); WebDev Arena 1773 em xhigh, 1716 em high (arena.ai/leaderboard/webdev).
- Opus 5.5: OSWorld-2.1 87,2% (deepmind.google model card do Carbon, tabela comparativa).

## Effort

- Níveis `low|medium|high|xhigh|max`, calibrados por modelo (o mesmo nome não é o mesmo esforço).
- Padrões: Opus 5.5 e Haiku 5.5 `medium`; Sonnet 5.5 `high` na API, mas o Claude Code usa `medium` para Fable/Opus/Sonnet/Haiku 5.5 (code.claude.com/docs/en/model-config). **Sempre declarar o effort.**
- Sonnet 5.5: `medium` para código agêntico e uso de várias ferramentas; `low` para chat; `high` se difícil ou longo.
- Haiku 5.5: `medium` por padrão (inclui código agêntico); `low` em volume simples; `high` em agente longo ou instrução rígida (em `low` com prompt longo tende a pular busca/checagem).
- Fable 5.2: começar em `high`; `xhigh` só com ganho medido; `max` quase nunca.
- `max` "prone to overthinking" (model-config). Todo token de thinking é cobrado.
- "Tuning effort is often a better lever than switching models" (platform.claude.com/docs/en/about-claude/models/choosing-a-model).
- Custo por tarefa concluída, não por requisição; trocar effort ou modelo no meio da conversa invalida o cache (skill claude-api, prompt caching).

## Orquestração (Anthropic)

- Medido pela Anthropic (platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence): Opus 5.5 com subagentes Sonnet 5.5 ≈ 1/3 mais barato com a mesma nota; Fable como orquestrador 19% mais caro com a mesma nota; subagentes Haiku −32% de custo e −4 pts de acerto; em cadeia dependente, um modelo só com effort menor saiu na frente.
- `opusplan`: Opus planeja, Sonnet executa (model-config).
- Subagentes herdam o modelo da sessão; `model` e `effort` no frontmatter mudam isso (code.claude.com/docs/en/sub-agents).

## Planos e cota

- Pro e Max: janela de 5 h + limite semanal, compartilhados entre o chat do Claude e o Claude Code (support.claude.com/en/articles/11145838).
- Max = 5x o Pro (…/11049741). O antigo Max 20x agora se chama **Ultra**: 10x o Pro por semana; contas verificadas sem janela de 5 h (…/17728952).
- Fable: em Max e Ultra, limite semanal próprio (até 50% da semana); consome cota mais rápido; no **Pro só com créditos de uso** (…/15424964).
- Limite semanal só de Opus: não aparece nos artigos oficiais `[incerto]`; o Claude Code mostra mensagens "You've hit your Opus/Sonnet limit" (code.claude.com/docs/en/costs).
- Cota ao vivo no Maestri: `%MAESTRI_DATA_DIR%/usage/providers/.status.json` (provedor `claude`, janelas `five_hour` e `seven_day`).

## Claude Code (CLI 2.1.328)

`--model <alias|id>`, `--effort <nível>`, `--add-dir`, `--append-system-prompt[-file]`, `--settings <arquivo|json>`, `--permission-mode`, `--fallback-model`. Mínimos: Sonnet 5.5 v2.1.284, Haiku 5.5 v2.1.293.
