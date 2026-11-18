# Pesquisa Antigravity (Prisma, Gemini 4 Hydrogen XHigh, 2026-11-18) — parte 1 (chegou cortada)

(1) MODELOS NO ANTIGRAVITY (runtime ao vivo via swarm models + doc oficial)
- Gemini 4 Hydrogen: Low, Medium, High (padrão), XHigh
- Gemini 4 Argon: Low, Medium, High
- Orchestrator (Argon): fixo
- Gemini 3.8 Flash: Low, Medium, High
- Claude Opus 5.5: Low, Medium, High
- Claude Sonnet 5.5: Low, Medium, High
- GPT-OSS 120B: Medium (doc marca remoção em 2026-11-18)
- Só na doc (não no nosso runtime): Gemini 4 Carbon e Orchestrator (Carbon), tipicamente Ultra/Enterprise [incerto]. Legados: Gemini 3.7/3.6 Flash, 3.1 Pro.
- Effort Max listado no `agy --help` para Claude 5.5, mas não aparece no runtime [incerto]. Claude Haiku não existe no Antigravity [incerto].
- Observação: dentro do agente, /model (TUI) não é invocável; `agy models` falhou no sandbox.

(2) COTAS (Google AI Pro, US$19,99/mês)
- Cota Gemini: Hydrogen e 3.8 Flash resetam em 5 h; Argon e Orchestrator (Argon) resetam em 7 dias (pool/teto semanal separado) [incerto].
- Cota Claude: (relatório cortado aqui)

# Parte 2
(2) COTA CLAUDE E GPT: pool único de Claude Opus 5.5, Claude Sonnet 5.5 (exigem AI Pro pago) e GPT-OSS 120B (sai em 2026-11-18); reset 5 h. Google não publica limite fixo; gasto dinâmico (High/XHigh/Max gastam mais). Janela móvel de 5 h sob teto semanal por pool; zerado o semanal, o reset de 5 h pausa até o semanal. Overage via AI Credits.

(3) RECOMENDAÇÕES GEMINI (oficiais Google)
- Front/UI: Carbon (Ultra) > Hydrogen (protótipo rápido) > 3.8 Flash (aderência a design system).
- Volume/custo: 3.5 Flash-Lite (não no runtime) < 3.8 Flash < Hydrogen ($1,50/$7,50; 2-2,8x mais rápido e -12 a -23% tokens que 3.8 Flash).
- Agentes longos: Argon (long-horizon, refatoração ampla); Orchestrator (Argon planeja + Hydrogen executa, -24% cota); Hydrogen (loops curtos/médios).
- Raciocínio: AA Index Hydrogen High 51, XHigh 54; Argon 50.
- Multimodal/visual: Argon (LVBench 91,7%, PDFs/imagens densos); 3.8 Flash (CharXiv 86,2%).
- Benchmarks: Hydrogen TB 4.1 57,0%, TB 4.0 56,4%, WebDev ~1704 [incerto]; Argon DeepSWE 77,9%, TB 4.0 55,5%, WebDev ~1681 [incerto]; 3.8 Flash TB 4.1 18,2% (fraco em agente de terminal), SWE-bench Pro 61,6% [incerto].
Fontes: antigravity.google/docs/models, /docs/plans, /docs/cli/reference, /changelog; blog.google (Hydrogen 2026-11-12, Carbon 2026-10-28, Argon 2026-09-30); model cards em storage.googleapis.com/deepmind-media/Model-Cards/; ai.google.dev/docs/models.
