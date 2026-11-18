# Roteamento: tarefa → terminal → modelo → raciocínio → cota

Fonte desta decisão: pesquisa de 2026-11-18 (`docs/pesquisa/2026-11-18/` do repositório da skill). Nomes e preços de modelos mudam: confirme no rodapé do terminal (`maestri check`) ou despache a um produtor a conferência nas URLs abaixo antes de decidir algo caro. `[incerto]` marca o que as fontes não confirmaram.

Regra geral: **o modelo e o raciocínio mais baratos que resolvem**. Falhou 2x: sobe o raciocínio; depois o modelo; depois o nível (SKILL.md, "Economia e escalada").

## 1. Tabela de roteamento

| Terminal | Modelo · raciocínio | Cota | Recebe | Não recebe |
|---|---|---|---|---|
| Faísca | Claude Haiku 5.5 · medium (low em lote trivial; high se instrução rígida e longa) | Claude Pro | N0–N1 não visuais: config, renomear, fixture, doc curta, extração, busca/exploração, coleta de fatos com fonte, checagens | lógica de N2+, decisões, prompt acima de 100K tokens |
| Forja | Claude Sonnet 5.5 · medium (high se difícil ou longa) | Claude Pro | N2–N3 backend, infra, segurança aplicada, escrita técnica que exige julgamento (docs, skills) | volume de UI, triviais |
| Farol | Claude Sonnet 5.5 · high | Claude Pro | N4: arquitetura, ADR, contratos, desempate, Conselho | execução de código em volume |
| Prisma | Gemini 4 Hydrogen · XHigh (High em tarefa rotineira) | Gemini (reset 5 h) | **Burro de carga**: front/UI em lotes por página ou fluxo, N1–N3 de código bem especificado, pesquisa web | tarefa vaga sem escopo fechado |
| Lente | Gemini 4 Argon · High | Gemini (teto **semanal**) | Revisão cruzada, QA, conferência visual/multimodal (prints, PDFs), refatoração longa | volume (cota semanal escassa) |
| Bigorna | Claude Opus 5.5 · High (Antigravity) | Claude e GPT (Google) | N3 mais difícil (concorrência, banco, crypto), segunda opinião Claude fora do Claude Pro; assume a Forja quando o Claude Pro aperta | trivial, volume |
| (sob demanda) | Gemini 3.8 Flash · Low/Medium | Gemini (reset 5 h) | texto, triagem, ajuste visual simples em lote | agente de terminal longo (TB 4.1: 18%) |
| (sob demanda) | Claude Sonnet 5.5 no Antigravity · Medium | Claude e GPT (Google) | transbordo da Forja sem gastar Claude Pro | — |
| Agulha | Codex · GPT (Free: GPT-6 Luna medium) | ChatGPT | **Pausável**. Quando ativa: revisão de diff com visão GPT, testes, scripts. Com Plus: Sol para revisão, Astra para segunda opinião N4, Terra rápido, Luna barato | qualquer coisa enquanto a cota estiver baixa |

Revisão cruzada (autor → revisor): Claude → Lente (Gemini); Gemini (Prisma) → Forja ou Bigorna (Claude), Faísca em N1 de UI simples, ou Agulha (GPT) quando ativa. A Lente não revisa o diff do Prisma (mesma família): fica com o QA visual e objetivo. O Maestro nunca é o revisor de diff.

Conselho N4 (só leitura, paralelo): Farol (arquitetura), Bigorna (riscos técnicos), Prisma (front), Lente (segurança e regras do domínio), Agulha quando ativa (alternativa simples e custo).

Preferência de cota: Antigravity para volume (muitos tokens); Claude Pro só para o que precisa de Claude Code (Forja, Farol, Faísca). Lente gasta teto semanal: não use para volume.

## 2. Família Claude (Claude Code)

Fontes: https://platform.claude.com/docs/en/models/overview · https://platform.claude.com/docs/en/build-with-claude/effort · https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide · https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence · https://code.claude.com/docs/en/model-config · https://code.claude.com/docs/en/sub-agents

| Modelo | Contexto · preço (US$/MTok in/out) | Quando usar | Raciocínio |
|---|---|---|---|
| Haiku 5.5 (`claude-haiku-5-5`, 2026-10-07) | 1M · 0,10/0,50 até 100K de prompt; acima disso 0,50/2,50 (5x) | Alto volume, baixa latência, saída verificável: classificação, extração, roteamento, busca/exploração, config repetitiva, lote (Batch −50%) | `medium` por padrão (inclui código agêntico); `low` em chat/curto/volume simples; `high` em agente longo ou instrução rígida |
| Sonnet 5.5 (`claude-sonnet-5-5`, 2026-09-28) | 1M · 2/10 | Código do dia a dia, análise de dados, agentes com várias ferramentas, tarefas ambíguas, lógica crítica | `medium` se bem especificada; `high` se difícil ou longa; `xhigh`/`max` só com ganho medido |
| Opus 5.5 (referência) | 1M · 4/20 | Só o Maestro no Claude Code; Bigorna no Antigravity | `high` na Bigorna |

- Haiku vs Sonnet: no GPQA Diamond, Haiku 85% contra 91% do Sonnet/Opus, a cerca de 1/10 do custo por acerto (guia de custo acima). Haiku em `low` com prompt longo de agente tende a pular busca, parar cedo ou pular checagem.
- Estratégia oficial de custo: rodar em `low` e reexecutar só as falhas em `high` (~40% mais barato com a mesma taxa de acerto).
- Restrições da API: sem `temperature`/`top_p`/`top_k`; sem `budget_tokens` (use thinking adaptativo + effort).
- A página oficial recomenda começar pelo Opus 5.5. Aqui isso fica de lado por regra de cota: só o Maestro roda Opus no Claude Code.
- `[incerto]` Padrão de effort diverge: o Claude Code diz `medium` para Sonnet/Haiku 5.5; a página de modelos da API diz `high` para o Sonnet 5.5. **Sempre defina o raciocínio explicitamente.**
- `[incerto]` Não há recomendação oficial explícita de Haiku vs Sonnet para "revisão" e "pesquisa"; a divisão acima vem das descrições oficiais.
- Claude Code: `/model haiku|sonnet|opus|opusplan|sonnet[1m]`; `/effort low|medium|high|xhigh|max|auto|status`; `--model`/`--effort`; `CLAUDE_CODE_EFFORT_LEVEL`; settings `effortLevel` (até `xhigh`), `modelSettings`, `maxEffortLevel`. Versões mínimas: Sonnet 5.5 v2.1.284, Haiku 5.5 v2.1.293.

## 3. Família Gemini (Antigravity)

Fontes: https://antigravity.google/docs/models · https://antigravity.google/docs/plans · https://antigravity.google/docs/cli/reference · https://ai.google.dev/gemini-api/docs/models

Modelos no Antigravity (runtime lido em 2026-11-18): Gemini 4 Hydrogen (Low, Medium, High, XHigh; padrão High); Gemini 4 Argon (Low–High); Orchestrator (Argon, fixo); Gemini 3.8 Flash (Low–High); Claude Opus 5.5 e Claude Sonnet 5.5 (Low–High); GPT-OSS 120B (removido em 2026-11-18). Só na doc: Gemini 4 Carbon e Orchestrator (Carbon), tipicamente Ultra/Enterprise `[incerto]`. Claude Haiku não existe no Antigravity `[incerto]`.

| Modelo | Quando usar | Raciocínio |
|---|---|---|
| Gemini 4 Hydrogen | Front/UI e protótipo rápido, loops curtos e médios de agente, N1–N3 especificado, pesquisa web. Melhor custo/benefício (US$1,50/7,50; 2–2,8x mais rápido e −12% a −23% de tokens que o 3.8 Flash) | `XHigh` (AA Index 54) para o padrão do Prisma; `High` (51) em rotina |
| Gemini 4 Argon | Revisão, tarefas de longo horizonte, refatoração ampla, multimodal (PDFs e imagens densos; LVBench 91,7%) | `High` |
| Gemini 3.8 Flash | Texto, triagem, aderência a design system, volume barato; **fraco em agente de terminal** (TB 4.1: 18,2%) | `Low`/`Medium` |
| Orchestrator (Argon) | Argon planeja e Hydrogen executa (−24% de cota) | fixo |

- Cotas (plano Google AI Pro): Hydrogen e 3.8 Flash resetam a cada 5 h; Argon e Orchestrator têm teto **semanal** separado `[incerto]`. Pool "Claude e GPT" (Opus 5.5, Sonnet 5.5): janela de 5 h sob teto semanal; o Google não publica limite fixo e High/XHigh/Max gastam mais.
- `[incerto]` Benchmarks (TB 4.1 do Hydrogen 57,0%; DeepSWE do Argon 77,9%; WebDev ~1704/~1681) vêm do relatório da pesquisa, sem conferência independente.
- `[incerto]` Effort `Max` aparece no `agy --help` para Claude 5.5, mas não no runtime.
- Dentro do agente, `/model` não é invocável e `agy models` pode falhar no sandbox: peça a um produtor (ex.: Faísca) ou ao usuário que rode `agy models` num terminal normal e traga a saída.
- Pesquisa de prompts e modos de falha: `prompts.md`.

## 4. Família OpenAI (Codex)

Fontes: https://developers.openai.com/api/docs/models/all · https://openai.com/index/introducing-gpt-6-sol-and-luna/ · https://learn.chatgpt.com/docs/pricing · https://developers.openai.com/codex/learn/best-practices · https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

Trate a família GPT como **"quando disponível"**: a Agulha fica pausada até a cota do plano renovar.

| Modelo (nome da página da OpenAI) | Quando usar | Raciocínio |
|---|---|---|
| Luna | Mais barato; o único citado no Free. Tarefas curtas, scripts, configs | `medium` (interativo padrão); `low` em curto |
| Terra | Rápido, volume | `medium` |
| Sol | Equilíbrio; **revisão de diff** com visão GPT | `medium` (padrão), `high` em revisão difícil |
| Astra | Mais capaz; segunda opinião em N4 | `high`; `xhigh`/`max` só com ganho medido |

- Escala de esforço: GPT-5.2 aceita `none`–`xhigh`; Astra e Sol sem `none`, com `low`/`medium` (padrão)/`high`/`xhigh`/`max`. `[incerto]` valores exatos por modelo.
- `[incerto]` As páginas da OpenAI se contradizem sobre a versão atual (GPT-6, 6.1 ou 6.2), sobre a variante Codex e sobre os modelos do Plus no CLI. **Leia o `/model` e o `/status` no rodapé do terminal** (`maestri check`) em vez de confiar nas páginas; no Antigravity não há doc oficial de GPT além do GPT-OSS (removido).
- Cota Plus (estimativas locais por 5 h): Luna 350–3.000; Terra 35–285; Sol 15–180; Astra 5–50. Ver uso: `/status` no CLI e chatgpt.com/codex/settings/usage.
- Prompt: objetivo, contexto, restrições e critério de pronto; regras duradouras em `AGENTS.md`; diga como rodar build e teste (`prompts.md`).
