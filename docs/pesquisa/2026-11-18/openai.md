# Pesquisa OpenAI (Faísca, Haiku, 2026-11-18)

(1) MODELOS PARA CÓDIGO/AGENTES
- Lista (resumo da página de modelos): GPT-6 Astra, GPT-6.1 Sol / GPT-6.2 Sol, GPT-6.1 Terra, GPT-6 Luna, GPT-5.6 Sol/Terra/Luna, GPT-5.5, GPT-5.5 Pro, GPT-5.4, GPT-5.4 Pro, GPT-5.4 mini, GPT-5.2, GPT-5.2 Pro. https://developers.openai.com/api/docs/models/all
- Conflito de nomes: GPT-6 vs GPT-6.1 vs GPT-6.2 aparecem em páginas diferentes. [não confirmado] qual é a versão atual.
- Mini: GPT-5.4 mini descrito para coding, computer use e subagentes. Nano: só GPT-5.4 nano, descontinuado. [não confirmado] nano atual.
- Variantes Codex: GPT-5.3-Codex descontinuado; 5.2-Codex e 5.1-Codex desligados. [não confirmado] variante Codex atual. Guia: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- Reasoning effort: GPT-5.2 none/low/medium/high/xhigh (https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.2). GPT-6 Astra e GPT-6.1 Sol sem none; Sol low/medium (padrão)/high/xhigh/max (https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra). [não confirmado] valores exatos por modelo.
- Recomendação oficial: Astra = mais capaz; Sol = equilíbrio; Terra = rápido; Luna = mais barato. https://openai.com/index/introducing-gpt-6-sol-and-luna/

(2) CODEX CLI E PLANOS
- https://learn.chatgpt.com/docs/pricing: Plus inclui Codex CLI, IDE e web. Pro sem limite de 5 h, limite semanal pode existir.
- Plus, mensagens locais por 5 h (estimativas): GPT-6.2 Astra 6-50; GPT-6.2 Sol 17-180; GPT-6 Astra 5-45; GPT-6.1 Sol 15-160; GPT-6.1 Terra 35-285; GPT-6 Sol 15-150; GPT-6 Luna 350-3.000.
- Free: só GPT-6 Luna citado no app desktop, sujeito a liberação. CLI no Free: [não confirmado].
- Modelos do Plus no CLI: página se contradiz. [não confirmado].
- Ver uso: /status no CLI; chatgpt.com/codex/settings/usage.

(3) GPT NO ANTIGRAVITY
- Sem doc oficial listando GPT no Antigravity. Lançamento (nov/2025): Gemini, Claude Sonnet 4.5 e GPT-OSS (Wikipedia). Fórum: reclamação de falta de GPT-5.3 Codex. [não confirmado] — verificar no /model do Antigravity.

(4) PROMPT PARA AGENTES DE CÓDIGO (OpenAI)
- Codex prompting guide: regras de autonomia, escolha de ferramenta, leituras paralelas, disciplina de edição, formato da mensagem final; raciocínio medium como padrão interativo.
- Best practices: objetivo, contexto, restrições, critério de pronto; planejar antes do complexo; regras duradouras no AGENTS.md; dizer como rodar build e teste. https://developers.openai.com/codex/learn/best-practices
- https://developers.openai.com/codex/prompting: nomear o comportamento, apontar código/repro, restrições, como verificar.
- Tarefas longas: arquivo de spec e plano como fonte da verdade, validação por marco, diffs pequenos. https://developers.openai.com/blog/run-long-horizon-tasks-with-codex
- OpenAI interno: modo Ask para plano antes do Code. https://openai.com/business/guides-and-resources/how-openai-uses-codex
