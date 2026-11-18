# Pesquisa Claude (Forja, Sonnet, 2026-11-18)

1) LINHA ATUAL (platform.claude.com/docs/en/models/overview)
- Haiku 5.5 (claude-haiku-5-5), 2026-10-07. 1M ctx / 128K saída. US$0,10/0,50 por MTok até 100K de prompt; acima 0,50/2,50. O mais rápido. Oficial: alto volume, latência, classificação, roteamento, extração, subagentes. Tokenizer ~30% mais tokens que Haiku 4.5. Batch -50%.
- Sonnet 5.5 (claude-sonnet-5-5), 2026-09-28. 1M/128K. US$2/10. Oficial: melhor combinação velocidade/inteligência; código do dia a dia, agentes, análise de dados, conteúdo, visão, uso agêntico de ferramentas.
- Referência: Opus 5.5 US$4/20; Fable 5.2 US$8/40.
- GPQA Diamond: Haiku 85% vs Sonnet/Opus 91%; Haiku ~1/10 do custo por acerto.
- Restrições API: sem temperature/top_p/top_k; sem budget_tokens (thinking adaptive + effort). Haiku em low em prompts longos de agente tende a pular busca, parar cedo ou pular checagem.

2) EFFORT (build-with-claude/effort; sonnet-5-5/migration-guide)
- Níveis low, medium, high, xhigh, max; calibrados por modelo; sinal de comportamento, não orçamento.
- Sonnet 5.5: comece em high salvo agente/latência. Código agêntico bem especificado: medium; difícil/longo: high. Chat: medium/low. xhigh/max só com ganho medido.
- Haiku 5.5: comece em medium (inclui código agêntico). low: chat, curto, volume simples. high: conhecimento, agentes longos, instruções estritas.
- Custo: rodar em low e reexecutar só falhas em high (~40% mais barato, mesmo acerto).
- Claude Code (code.claude.com/docs/en/model-config): /model haiku|sonnet|opus|fable|opusplan|sonnet[1m]; /effort low|medium|high|xhigh|max|auto|status; --effort/--model; CLAUDE_CODE_EFFORT_LEVEL; settings model, effortLevel (até xhigh), modelSettings, maxEffortLevel. Frontmatter de subagente/skill: model e effort. Mínimos: Sonnet 5.5 v2.1.284, Haiku 5.5 v2.1.293.
- [incerto] Padrões divergem (Claude Code: medium; API: Sonnet high). Definir effort explicitamente.

3) HAIKU x SONNET
- Haiku: classificação, extração, roteamento, exploração/busca, config repetitiva, lote, saídas verificáveis. Evitar com prompt >100K (preço 5x).
- Sonnet: código do dia a dia, análise, agentes multi-ferramenta, revisão e pesquisa de maior risco, tarefas ambíguas, lógica crítica.

4) DELEGAR
- "Funcionário brilhante mas novo": o agente só tem o prompt; incluir caminhos, erros, critério de pronto, formato do relatório.
- Documento longo: pergunta no fim (+30%).
- Delegar o paralelizável/isolado; não multiplicar agentes sem necessidade.
- Pedir verificação contra critérios antes de terminar.
- Restringir ferramentas e turnos.

URLs: platform.claude.com/docs/en/models/overview; .../models/haiku-5-5/overview; .../models/sonnet-5-5/overview; .../models/sonnet-5-5/migration-guide; .../build-with-claude/effort; .../about-claude/models/optimizing-for-cost-and-intelligence; .../build-with-claude/prompt-engineering/claude-prompting-best-practices; code.claude.com/docs/en/model-config; code.claude.com/docs/en/sub-agents
