# Briefing do Maestro: reescrita da skill maestro-equipe (2026-11-18)

Fontes desta pasta: `claude.md` (Forja), `antigravity-gemini.md` (Prisma), `prompts-gemini.md` (Lente), `openai.md` (Faísca, com conflitos de nome; o que a Agulha confirmou está abaixo).

## 1. Mudança central: o Maestro comanda, não executa

O usuário pediu explicitamente: o Maestro (Claude Opus, no Claude Code) **não faz as tarefas**. Ele:
- entende o pedido, quebra em tarefas, classifica o nível (N0–N4);
- **escolhe o modelo e o raciocínio certos** para cada tarefa (tabela abaixo) e escreve o prompt de despacho no formato da família do modelo;
- despacha, acompanha, responde a permissões, lê relatórios;
- decide (sintetiza visões, escolhe entre propostas, escala quando algo falha);
- cuida do git (commit no nome do usuário) e das configurações do Maestri.

O que muda em relação à versão atual da skill:
- Sai "N0: você mesmo se for uma só". **Até tarefa trivial vai para alguém** (Faísca ou Flash). Exceções que ficam com o Maestro: git, comandos do Maestri, responder permissões, ler um arquivo curto para decidir o despacho, e escrever o próprio briefing/quadro.
- O Maestro **não revisa diff linha a linha**: quem revisa é o revisor de outra família. O Maestro lê o relatório do revisor e decide.
- Pesquisa também é delegada (cada família pesquisa seus próprios modelos/docs quando fizer sentido).
- Princípio de economia: **não mandar tarefa simples para modelo caro, nem tarefa difícil para modelo leve.** Começar no modelo/raciocínio mais barato que resolve; se falhar 2x, subir primeiro o raciocínio, depois o modelo (recomendação oficial da Anthropic: rodar barato e reexecutar só as falhas mais alto).
- O Maestro escreve **sempre o raciocínio esperado** no cartão/despacho (os padrões divergem entre ferramentas) e ajusta `/effort` entre tarefas, nunca no meio.

## 2. Regras de modelo decididas com o usuário

- Só o Maestro roda Opus no Claude Code. Os outros terminais Claude Code usam **apenas Sonnet 5.5 e Haiku 5.5**, com o raciocínio recomendado pela Anthropic.
- Farol passou de Opus para **Sonnet 5.5, raciocínio high**.
- Bigorna continua **Claude Opus 5.5 no Antigravity** (cota "Claude e GPT" da Google, separada do Claude Pro).
- Agulha (Codex, plano Free, GPT-6 Luna medium, 8% da cota mensal) fica **pausada até a cota renovar**. A skill deve tratar a família GPT como "quando disponível", com a tabela de modelos OpenAI para quando houver Plus.
- O Antigravity tem muitos tokens: **preferir o Antigravity para volume**. O Claude Pro é dividido com o Maestro: usar Forja/Farol/Faísca para o que realmente precisa de Claude Code.

## 3. Tabela de roteamento (decisão do Maestro)

| Terminal | Modelo · raciocínio | Cota | Recebe | Não recebe |
|---|---|---|---|---|
| Faísca | Haiku 5.5 · medium (low em lote trivial; high se instrução rígida e longa) | Claude Pro | N0–N1 não visuais: config, renomear, fixture, doc curta, extração, busca/exploração, coleta de fatos com fonte, checagens | lógica de N2+, decisões, prompt >100K tokens |
| Forja | Sonnet 5.5 · medium (high se difícil/longa) | Claude Pro | N2–N3 backend, infra, segurança aplicada, escrita técnica que exige julgamento (docs, skills) | volume de UI, triviais |
| Farol | Sonnet 5.5 · high | Claude Pro | N4: arquitetura, ADR, contratos, desempate, Conselho | execução de código em volume |
| Prisma | Gemini 4 Hydrogen · XHigh (High em tarefa rotineira) | Gemini (5 h) | **burro de carga**: front/UI em lotes por página ou fluxo, N1–N3 de código bem especificado, pesquisa web | tarefa vaga sem escopo fechado |
| Lente | Gemini 4 Argon · High | Gemini (teto **semanal**) | revisão cruzada, QA, conferência visual/multimodal (prints, PDFs), refatoração longa | volume (cota semanal escassa) |
| Bigorna | Claude Opus 5.5 · High (Antigravity) | Claude e GPT (Google) | N3 mais difícil (concorrência, banco, crypto), segunda opinião Claude fora do Claude Pro, assume a Forja quando o Claude Pro aperta | trivial, volume |
| (sob demanda) | Gemini 3.8 Flash · Low/Medium | Gemini (5 h) | texto, triagem, ajuste visual simples em lote | agente de terminal longo (TB 4.1: 18%) |
| (sob demanda) | Claude Sonnet 5.5 no Antigravity · Medium | Claude e GPT (Google) | transbordo da Forja sem gastar Claude Pro | — |
| Agulha | Codex · GPT (hoje GPT-6 Luna medium, Free) | ChatGPT | **pausada**. Quando ativa: revisão de diff com visão GPT, testes, scripts. Com Plus: Sol para revisão, Astra para segunda opinião N4, Terra rápido, Luna barato | qualquer coisa enquanto a cota estiver baixa |

Revisão cruzada (autor → revisor): Claude → Lente (Gemini); Gemini → Forja ou Bigorna (Claude), ou Agulha (GPT) quando ativa; o Maestro nunca é o revisor de diff.

Conselho N4 (só leitura, paralelo): Farol (arquitetura), Bigorna (riscos técnicos), Prisma (front), Lente (segurança, LGPD/domínio), Agulha quando ativa (alternativa simples e custo).

## 4. Prompt por família (o Maestro escolhe o formato pelo destinatário)

- **Gemini (Prisma, Lente):** usar o modelo XML de `prompts-gemini.md`: contexto e arquivos no começo, `<proibido>`, `<criterio_de_pronto>` e `<saida>` no **fim**; "SOMENTE LEITURA" no topo e no fim das consultas; lotes curtos (1 página/fluxo); caminhos absolutos; disjuntor "erro 2x → pare"; não pedir "pense passo a passo"; `/plan` para multi-arquivo. Motivo: o Gemini perde escopo, edita vizinhos, inventa caminhos e esquece restrições depois de muitas chamadas de ferramenta.
- **Claude (Faísca, Forja, Farol, Bigorna):** "funcionário brilhante mas novo": o agente só tem o prompt; dar caminhos, objetivo, critério de pronto, formato do relatório e pedir verificação contra os critérios antes de terminar. Para o Haiku, escopo bem fechado e explícito (em low ele tende a pular checagens).
- **GPT/Codex (Agulha):** objetivo, contexto, restrições, critério de pronto e como validar; regras duradouras no AGENTS.md; **proibir controle do computador** (a Agulha tentou usar computer use para abrir o próprio `/model`). O agente não enxerga o próprio `/model`: quem lê modelo e cota é o Maestro, pelo rodapé, com `maestri check`.

## 5. Lições operacionais desta sessão (vão para a skill)

- O Maestro descobre modelo, raciocínio e cota de cada terminal lendo o rodapé com `maestri check`, não perguntando ao agente.
- Relatório longo enviado com `maestri ask "Maestro"` pode chegar **cortado** (aspas no texto); pedir relatórios sem aspas e, se cortar, pedir só o restante.
- O Antigravity pede confirmação a cada `maestri ask "Maestro"`, mesmo com regra em `settings.json` (investigação em andamento com o Prisma). Até resolver: o Maestro checa os terminais Antigravity quando um relatório demora e aprova com "permitir uma vez".
- Terminal que sai da ferramenta depois de atualização (ex.: Codex volta ao PowerShell): religar com `maestri recruit "Nome" --preset P --replace "Nome"`.
- Não pedir ao agente para rodar `/model` dentro dele mesmo: no Antigravity o `/model` não é invocável pelo agente; no Codex ele tenta controlar o computador.
