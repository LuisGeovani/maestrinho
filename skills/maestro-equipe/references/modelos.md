# Catálogo de modelos: quem é bom em quê

Atualizado em **2026-11-18**. Fontes e números completos: `docs/pesquisa/2026-11-18b/` do repositório da skill. `[incerto]` = não confirmado em fonte oficial. Preço de API (US$/MTok entrada/saída) serve para comparar o "peso" do modelo dentro do mesmo pool de assinatura; o que manda no dia a dia é a cota (`scripts/cotas.py`).

Nomes e IDs mudam rápido. Antes de criar presets, confira com `python <skill>/scripts/inventario.py` (lista o que o ambiente tem de verdade). Seção final: como atualizar este catálogo.

## Escadas por família

| Família | Degrau | Forte em | Evite |
|---|---|---|---|
| Claude | **Haiku 5.5** | Batedor, conversão de binário, abertura de URL e verificação com shell e prova bruta | lógica N2+ e tarefas que outro pool elegível cobre |
| | **Sonnet 5.5** | produção cuidadosa, revisão de outra família, verificação com shell no Claude Code | volume que cabe no Hydrogen ou no Sol |
| | **Opus 5.5** | redação de registro formal, N3/N4, voz Claude no Conselho | rotina e uso do Claude Pro fora das condições de `roteamento.md` §4 |
| Gemini | **Gemini 3.8 Flash** | triagem e classificação N0 de texto já convertido | agente de terminal, código e verificação de fonte/fato |
| | **Hydrogen** | código e UI bem especificados em lote, QA visual correto e barato, pesquisa ampla, comandos com aprovação | escopo vago e servidor MCP grande em modo Eager (corte por tamanho de schema) |
| | **Argon** | tarefa longa, redação ou engenharia cuidadosa, diff curto | N3 decisivo |
| | **Neon** | N3, diagnóstico, edição via MCP (modo Lazy), revisão de diff e de texto, QA visual, multimodal | trivial e xhigh sem necessidade |
| GPT | **Luna** | script, configuração e checagem N0–N1 com passos fechados e teste automático obrigatório | engenharia aberta, redação e verificação de fonte/fato |
| | **Terra** | escrita rápida, resumo, conversão de formato e visão | código difícil |
| | **Sol** | degrau médio GPT: código por especificação, revisão de diff e verificação com shell e prova bruta | tarefa sem critério de aceite e N0–N1 que cabem em Luna ou Terra |
| | **Astra** | N3/N4, testes focados em base existente e voz GPT no Conselho | rotina e lotes grandes |
| Abertos | **OpenCode grátis** (ex.: `deepseek-v4.1-flash-free`) | Batedor de custo zero: leitura, resumo, testes com saída verificável | agente longo e código em modelo que treina com os dados |
| | **OpenCode pago** (quando contratado) | implementação média com um modelo disponível e adequado ao perfil | assumir equivalência ou cota com base só no provedor |

Os abertos são a quarta família para roteamento. O catálogo de OpenCode abaixo detalha as opções. O pool "Claude and GPT" do Antigravity atende Agy Sonnet e Agy Opus. Hydrogen e Neon usam "Gemini Models", Argon tem teto semanal próprio e os quatro GPT compartilham o medidor Codex. O Gemini 3.8 Flash tem medidor desconhecido até confirmação do vínculo no provedor. Só use a folga de "Gemini Models" para ele se esse vínculo for confirmado.

A qualidade relativa de Argon × Neon e Argon × Sonnet segue sem medida [incerto]. **Divisão interna do Gemini:** trabalho importante ou decisivo (**N2 de risco, N3, revisão decisiva, diagnóstico difícil, edição em serviço externo/MCP**) vai primeiro ao **Neon high**; **Hydrogen** fica com volume bem especificado (código/UI em lote, Batedor, QA visual barato, pesquisa); **Argon** fica com tarefa longa de cuidado, poupando seu teto semanal próprio. Veja a matriz e as regras de cota em `roteamento.md`.

## Claude (Opus e Sonnet: PRIMEIRO no Antigravity, pool "Claude and GPT"; SÓ DEPOIS no Claude Code)

Gemini é a família preferida por padrão (cota enche bem mais devagar). Claude entra quando a ferramenta exige (`--chrome`), quando o pool Gemini estiver apertado (semanal ≥ 80% ou 5 h ≥ 90%), ou quando a revisão cruzada pedir outra família. Na família Claude, use primeiro Agy Sonnet / Agy Opus no medidor "Claude and GPT". Com esse medidor bloqueado (ou quando a tarefa exigir `--chrome`), os candidatos Claude entram na comparação pela folga do Claude Pro (que inclui o Maestro) e a trava de equilíbrio de `roteamento.md` §4 vale para eles; volte ao Antigravity no reset.

| Modelo | Bom em | Evite | Effort |
|---|---|---|---|
| **Fable 5.2** ($8/$40) | o mais capaz: raciocínio muito difícil, agente de longo horizonte | rotina; prompt prescritivo demais (piora); no plano Pro só com créditos | high; xhigh só com ganho medido |
| **Opus 5.5** ($4/$20) | o Maestro; arquitetura, N3/N4, refatoração grande, agentes longos; OSWorld 87% | volume, trivial | medium (padrão); high em decisão difícil |
| **Sonnet 5.5** ($2/$10) | código do dia a dia, agentes com várias ferramentas, tarefas bem delimitadas, olho para design (WebDev 1773 em xhigh), revisão de código de outra família | — | medium em código agêntico; high se difícil ou longo; low em chat |
| **Haiku 5.5** ($0,10/$0,50 até 100K de prompt) | exploração, busca, extração, resumo de código para o Maestro, config repetitiva, lote, checagens com saída verificável | lógica N2+, prompt acima de 100K (preço 5x), instrução longa em low (pula checagens) | medium; low em lote trivial; high em instrução rígida e longa |

- Claude Code: `--model haiku|sonnet|opus|fable` e `--effort low|medium|high|xhigh|max`. O padrão do Claude Code é medium para os quatro; declare sempre.
- Anthropic mediu: Opus orquestrando Sonnet ≈ 1/3 mais barato com a mesma nota; Fable orquestrando, 19% mais caro sem ganho; trabalhadores Haiku −32% de custo e −4 pts. Por isso o Maestro roda Opus, e Haiku entra como Batedor em tarefas compatíveis no Claude Code com Pro utilizável.
- Plano: Pro e Max dividem 5 h + semanal entre o chat e o Claude Code (e com o Maestro). Max = 5x Pro; Ultra (ex-Max 20x) = 10x Pro por semana.

## Gemini (Antigravity `agy`; pool "Gemini Models" 5 h + semanal; Argon tem teto semanal próprio no Pro)

IDs = `<modelo>-<effort>` (ex.: `gemini-4-neon-high`). Effort maior gasta mais cota.

| Modelo | Bom em | Evite | Effort |
|---|---|---|---|
| **Gemini 4 Neon** (18/11/2026; $3/$15; 512K no agy) | o mais forte do plano Pro: implementação e refatoração difíceis, **diagnóstico** e **edição via MCP** de primeira (carrega ferramentas em modo Lazy; comprovado com 44 ferramentas do Canva + `curl`/Python), multimodal e documentos longos, **revisão** (menor fabricação medida, honestidade 99,2%), QA visual; Coding Agent Index 59 (Opus 5.5 max: 58); Terminal-Bench 4.1 65,2% | tarefa simples em xhigh (pensa demais) | high; xhigh só em problema difícil de vários passos |
| **Gemini 4 Hydrogen** ($1,50/$7,50) | o "burro de carga": volume de código bem especificado, UI em lotes por página/fluxo, **QA visual correto e barato**, edições cirúrgicas (até 81% menos overreach), pesquisa web; TB 4.1 57%; ~2,5x mais rápido que o 3.8 Flash | tarefa vaga, sem escopo fechado; servidor MCP grande em modo Eager (corta ferramentas acima de ~10,5 KB) | high; medium em código interativo e protótipo de UI; low em trivial |
| **Orchestrator (Neon)** `gemini-pro-orchestrator-neon` | features, bugs, refatoração e debug **multi-arquivo**: Neon planeja só-leitura e revisa, Hydrogen executa (na versão Carbon: −24% de cota) | design de sistemas, concorrência, migrações (use o modelo puro) | fixo |
| **Orchestrator (Argon)** `gemini-pro-orchestrator-g1-pro` | o mesmo, com Argon planejando | — | fixo |
| **Gemini 4 Argon** (30/09/2026) | **modelo principal de nível médio** da escada Gemini: tarefa longa e de redação/engenharia que pede mais cuidado que o Hydrogen, refatoração ampla, segunda voz Gemini com o Neon ocupado; AA 50, DeepSWE 77,9%, multimodal denso (LVBench 91,7%); **teto semanal próprio** (não gasta o pool Gemini principal) | N3 de risco alto e revisão decisiva (o Neon supera o Argon em qualidade `[incerto]`); volume trivial (gasta o teto à toa) | medium; high no difícil; low só em trivial |
| **Gemini 3.8 Flash** | triagem e classificação N0 de texto já convertido; disponível em todos os planos | agente de terminal (TB 4.1 18%), código e verificação de fonte/fato | low/medium |
| **Gemini 4 Carbon** | o mais forte para tarefas longas | só Ultra/Enterprise (aparece "Unavailable" no Pro); lento | medium |
| **Claude Opus 5.5 / Sonnet 5.5 no agy** | os mesmos modelos da Anthropic **sem gastar o Claude Pro** (pool "Claude and GPT"); **1ª escolha dentro da família Claude**, antes do Claude Code | — | até high |
| **GPT-OSS 120B** | — | sendo removido ("Notice", 18/11/2026) | não rotear |

- Prompt: XML ou Markdown, contexto primeiro, restrições e formato no fim; não pedir "pense passo a passo" (o thinking é nativo); escopo fechado (ver `prompts.md`).

## GPT (Codex CLI; e via OpenCode com login ChatGPT ou chave de API)

Versão vigente: **GPT-6.2** (17/11/2026). Efforts no Codex: `low`, `medium`, `high`, `xhigh`, `max`, `ultra` (ultra usa subagentes; quase nunca vale).

| Modelo | Bom em | Evite | Effort |
|---|---|---|---|
| **gpt-6.2-astra** ($8/$40) | N3/N4, código e testes focados em base existente; voz GPT no Conselho | rotina (Plus: só 6–50 msgs por 5 h) | high em N3/N4; xhigh só com ganho real |
| **gpt-6.2-sol** ($2/$10) | degrau médio GPT: código por especificação, verificação com shell e **revisão de diff** (a 0,5 pt da Astra por ~1/5 do custo) | N0–N1 simples que cabem em Luna ou Terra | medium; high em revisão difícil |
| **gpt-6.1-terra** ($1/$5) | escrita rápida, resumo, conversão de formato e visão | código difícil (TB 53%) | medium; low em triagem textual |
| **gpt-6-luna** ($0,10/$0,50) | volume N0–N1: scripts, configs e checagens com passos fechados e teste automático obrigatório | engenharia aberta, redação e verificação de fonte/fato (alucinação 77%, TB 15%) | high para scripts; medium em N0 trivial |
| gpt-5.6 sol/terra/luna | geração anterior (aparecem no plano Free) | — | — |
| gpt-reserve | "Luna Reserve": uso extra com 5.6 Luna quando a cota acaba | não é modelo de trabalho | — |
| codex-auto-review | revisor automático de pedidos de sandbox | não despachar tarefas | — |

- Planos: Free/Go = Luna (cota mensal pequena); Plus/Business = todos (por 5 h: Astra 6–50, Sol 17–180, Terra 35–285, Luna 350–3000); Pro sem janela de 5 h.
- Codex: `-m <slug>`, `-c model_reasoning_effort=<nível>`, `-s workspace-write`, `-a on-request`, `--add-dir`. Proíba computer use no papel (a CLI não tem chave para desligar).

## Modelos abertos (OpenCode)

OpenCode v2 (`opencode`): modelo no formato `provider/model#variante`; na interface interativa o modelo vem do `"model"` do `opencode.json`. Agentes `build` (padrão), `plan` (não edita), subagentes `general` e `explore`.

| Modelo | Bom em | Cuidado |
|---|---|---|
| **Grátis do Zen** (por tempo limitado): `opencode/deepseek-v4.1-flash-free` (TB 4.1 38,5% na versão paga), `mimo-v2.6-flash-free`, `nemotron-3.5-lightning-free`, `nemotron-3.5-super-vl-free` (visão), `longcat-2.5-free`, `hy4-flash-free`, `beam-free`, `tidepool-alpha-free` | Batedor de custo zero: exploração, resumo, triagem, testes e docs simples, checagens; um "terceiro olhar" de outra família | fracos em agente longo; o preset da skill (`deepseek-v4.1-flash-free`) está aprovado para o projeto: use sem perguntar |
| `opencode/big-pickle`, `iceman-free`, `flint-40b-free`, `inkling-2-small-free` | o mesmo | **podem usar os dados para treino**: nunca com código ou dado sensível |
| Pagos (Zen ou OpenCode Go, se a pessoa assinar): Kimi K3.1 Pro (TB 59,7%), GLM-5.3 (41%), DeepSeek V4 Pro, Qwen | implementação média como quarta família | custo por token |

- Se o OpenCode enxergar `OPENAI_API_KEY` ou login ChatGPT, os modelos `openai/*` aparecem e **gastam a conta paga**: fixe um modelo `opencode/*-free` no `opencode.json` do terminal, a menos que a pessoa queira usar a API.
- Na v2 o padrão de permissões é liberar tudo: ver `setup.md` (permissões do OpenCode).

## Como atualizar este catálogo

1. Despache ao Batedor: `python <skill>/scripts/inventario.py` e "compare a lista de modelos com `references/modelos.md`; reporte só o que é novo ou sumiu".
2. Modelo novo relevante: despache uma pesquisa curta a 2 famílias (fontes oficiais + um benchmark independente), em paralelo, só leitura; o Batedor consolida em `docs/pesquisa/<data>/`.
3. Um produtor de escrita atualiza esta tabela e a matriz de `roteamento.md`; outra família revisa; o Maestro faz o commit.
