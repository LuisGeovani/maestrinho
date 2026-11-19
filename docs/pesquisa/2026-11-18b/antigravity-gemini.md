# Antigravity e Gemini (2026-11-18)

Coleta: pesquisa web + `agy models` (agy 1.5.11) no ambiente do usuário. Benchmarks em geral são do próprio fornecedor; independentes: Artificial Analysis (AA) e WebDev Arena. `[incerto]` = não confirmado em fonte oficial.

## Modelos (IDs reais do `agy models`)

`gemini-4-neon-{low,medium,high,xhigh}` · `gemini-4-argon-{low,medium,high}` · `gemini-4-hydrogen-{low,medium,high,xhigh}` · `gemini-pro-orchestrator-neon` (Orchestrator Neon) · `gemini-pro-orchestrator-g1-pro` (Orchestrator Argon) · `gemini-3.8-flash-{low,medium,high}` · `claude-opus-5-5-{low,medium,high}` · `claude-sonnet-5-5-{low,medium,high}` · `gpt-oss-120b-medium`. No app: Gemini 4 Carbon "Unavailable" e GPT-OSS "Notice".

| Modelo | Papel oficial | Números | US$/MTok | Effort |
|---|---|---|---|---|
| **Neon** | lançado 18/11/2026; entre Carbon (projetos longos) e Hydrogen (dia a dia); padrão de conversas novas; 512K no Antigravity, 1M na API | AA 61 (xhigh, 3º geral); Coding Agent Index 59 (Opus 5.5 max: 58); Terminal-Bench 4.1 65,2% (Opus 5.5: 65,8%); menor fabricação já medida no Antigravity; honestidade 99,2%; LVBench 89%; WebDev 1764 | 3 / 15 | padrão high; xhigh só em problema difícil de vários passos |
| **Argon** | 30/09; "frontier" de engenharia; possivelmente substituído pelo Neon `[incerto]` | AA 50; TB 4.0 57,1% | 2/10 até 30/11, depois 4/20 | padrão medium; high no difícil |
| **Hydrogen** | 12/11; "daily driver", substitui o 3.8 Flash; no Pro só em assinatura paga | AA 51 (high) e 54 (xhigh); TB 4.1 57%; edições cirúrgicas, leituras em paralelo, até 81% menos overreach; ~2,5x mais rápido que o 3.8 Flash; WebDev 1703 | 1,50 / 7,50 | padrão high; medium em código interativo e protótipo de UI; low trivial |
| **Carbon** | o mais forte para tarefas longas e cibersegurança; exige Ultra/Enterprise | AA 59–60; TB 4.0 65,2%; pode ficar lento/timeout | 2/10, depois 4/20 | padrão medium |
| **3.8 Flash** | "workhorse"; único em todos os planos | TB 4.1 18,2% (fraco em agente de terminal); fabrica 5x mais que o Hydrogen | 0,75/3,75 até 31/12 | padrão medium |
| Claude Opus 5.5 / Sonnet 5.5 | mesmos modelos da Anthropic, no pool "Claude and GPT" | effort até high no agy | — | — |
| GPT-OSS 120B | "Will be removed on November 18, 2026" (talvez adiado para 30/11 `[incerto]`) | — | — | não rotear |

**Orchestrator:** o planejador (Neon, Argon ou Carbon) planeja só-leitura e revisa; o Hydrogen edita, atualiza pacotes e roda testes; se o Hydrogen trava, volta ao planejador. Versão Carbon: ~resultado do Carbon com −24% de cota e −19% de tempo (TB 4.1). Recomendado para features, bugs, refatoração e debug multi-arquivo; modelos puros para design de sistemas, concorrência e migrações; Hydrogen puro para rotina. Effort fixo.

## Cotas (antigravity.google/docs/plans, /docs/models)

| Plano | O que tem |
|---|---|
| Free | renova semanalmente; só 3.8 Flash e modelos saindo |
| Pro | 5 h até o limite semanal; Neon e Argon, Hydrogen e Claude 5.5 (sem trial), Orchestrator Neon/Argon |
| Ultra | maior cota; inclui Carbon e Orchestrator Carbon |

Medidores: "Gemini Models" e "Claude and GPT models", cada um com 5 h + semanal; o Pro ganhou cota semanal só do Argon (confirmada no `.status.json` do usuário: medidor "Gemini 4 Argon / Semanal"). Effort maior consome mais (não há tabela oficial). Excedente via créditos de IA (`useG1Credits`).

## CLI `agy` (antigravity.google/docs/cli/reference)

- `--model`, `--effort low..max` (conforme o modelo), `--mode accept-edits|auto|plan` (`auto` exige sandbox), `-p/--print` com `--output-format text|json|stream-json`, `--add-dir` (repetível), `--sandbox`, `--settings` (JSON de settings só para a sessão; aparece no `agy --help` local), `-c/--continue`.
- Comandos: `/usage` (= `/quota`), `/model <m> <prompt>` (um prompt em outro modelo), `/plan`, `/swarm`.
- Permissões em `~/.gemini/antigravity-cli/settings.json`, bloco `permissions` com `allow`/`ask`/`deny` (deny > ask > allow). Regras: `command(git)`, `command(regex:...)`, `write_file(src/)`, `read_url(dominio)`, `mcp(server/*)`. Regra `unsandboxed(...)` não existe (o agy avisa e ignora). Não usar `--dangerously-skip-permissions`.
- Skills: workspace `.agents/skills/<nome>/SKILL.md`; global `~/.gemini/config/skills/` (também lê `~/.gemini/antigravity-cli/skills/` e `~/.gemini/skills/`). `~/.agents/skills` não aparece na doc `[incerto]`.
- Regras: `AGENTS.md`/`GEMINI.md` na pasta e nas pastas-pai, `.agents/rules/*.md` (precisam de frontmatter `trigger`), globais em `~/.gemini/`. Cada arquivo cortado em 24.000 bytes; regras globais e `always_on` dividem 20.000 tokens.

## Prompt para Gemini 4 (aistudio.google.com/docs/prompting-strategies, /thinking)

- Um formato só: tags XML ou cabeçalhos Markdown.
- Papel, restrições e formato no início ou nas instruções de sistema; com contexto longo, contexto primeiro e a pergunta no fim ("Com base nas informações acima…").
- Não pedir para listar o raciocínio (pensa nativamente); para tarefa pesada, subir o effort.
- Template agêntico: planejar antes de cada ação, não repetir chamada que falhou, persistir até esgotar opções.
- Responde conciso por padrão: pedir detalhe quando precisar.
- Modos de falha: xhigh pensa demais em tarefa simples; saída cortada por `max_output_tokens`; Carbon lento; para ações destrutivas, usar regras de permissão e não só o prompt. Da pesquisa anterior (`docs/pesquisa/2026-11-18/prompts-gemini.md`): perde escopo em tarefa vaga, edita vizinhos, inventa caminhos, esquece restrições após muitas chamadas de ferramenta.

## URLs

blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/ · deepmind.google/models/model-cards/gemini-4-neon/ · antigravity.google/blog/gemini-4-neon-in-google-antigravity/ · antigravity.google/docs/models · antigravity.google/docs/plans · antigravity.google/pricing/ · deepmind.google/models/model-cards/gemini-4-carbon/ · blog.google/.../introducing-gemini-4-hydrogen/ · antigravity.google/blog/gemini-4-hydrogen-in-google-antigravity/ · antigravity.google/blog/gemini-4-argon-in-google-antigravity/ · aistudio.google.com/docs/pricing · artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain · arena.ai/leaderboard/webdev · aistudio.google.com/docs/thinking.md · antigravity.google/docs/cli/reference · antigravity.google/docs/permissions?tab=cli · antigravity.google/docs/skills · antigravity.google/docs/rules · aistudio.google.com/docs/prompting-strategies
