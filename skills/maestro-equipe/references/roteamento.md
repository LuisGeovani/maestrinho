# Roteamento: tarefa → perfil → terminal, modelo e effort → cota

Escolha o terminal pela capacidade, o modelo e o effort pelo perfil e o pool pela folga. Famílias diferentes se conferem. Catálogo dos modelos: `modelos.md`. Fluxos por tipo de pedido: `fluxos.md`.

## Princípios

1. **Ferramenta → nível → cota.** Binários, abertura direta de URL e scripts bloqueados pelo sandbox vão para Codex, Claude Code ou OpenCode conforme a matriz. Antigravity recebe texto ou imagem já preparados.
2. **Claude Pro é reserva do Maestro.** Produtor no Claude Code só para tarefa sem outro terminal elegível, com 5 h < 50% e semanal dentro do ritmo. De 50% a menos de 70% na janela de 5 h, só para bloqueio técnico crítico sem alternativa, ainda com a semanal no ritmo. Com 5 h ≥ 70%, nenhum produtor usa Claude Code.
3. **Preserve o degrau exigido pelo perfil.** Para poupar cota, troque de pool entre opções equivalentes.
4. **Verificação exige prova bruta.** Registre comando e saída, com código HTTP e trecho literal quando verificar fonte. Fonte ou fato só com Sol, Sonnet ou Haiku em terminal com shell. Luna, Flash e Antigravity ficam fora dessa verificação. Sem prova, registre como pendente.

## 1. Classifique a tarefa (4 perguntas)

1. **Tipo:** código back · front/UI · infra/config · testes · docs · pesquisa · revisão · QA visual · decisão.
2. **Nível:**

| Nível | Exemplos | Revisão |
|---|---|---|
| N0 trivial | typo, renomear, config de uma linha, rodar um comando | validação por comando no próprio despacho (grep, build); sem revisor |
| N1 simples | README, fixture, script pequeno ou utilitário fechado, componente simples | validação por comando; revisor de outra família só se tocar lógica ou UI |
| N2 médio | tela, endpoint CRUD, migração simples, refatoração local | revisor de outra família (+ QA visual se for UI) |
| N3 complexo | concorrência, idempotência, segurança, dinheiro, dados pessoais, consulta pesada, refatoração ampla | especificação executável + testes por uma família, implementação por outra, revisão (+ red team se houver risco) |
| N4 crítico | stack, modelo de dados, arquitetura, custo | Conselho (uma voz por família, só leitura) → o usuário decide → ADR |

- **Script utilitário fechado é N1 e cabe no Luna ou no Haiku:** especificação (entrada → saída) e teste automático definidos no despacho. Se o despacho autoriza explicitamente, o produtor faz; recusa por "passar de N1" só vale quando falta especificação ou teste.

3. **Risco:** segurança, dinheiro, dado pessoal → sobe um nível e pede red team em N3.
4. **Tamanho e dependência:** quantos arquivos? Depende de outra tarefa? **Cadeia dependente fica no mesmo terminal**; só tarefas independentes vão em paralelo para terminais diferentes (multi-agente custa ~15x os tokens de um chat e só compensa em trabalho independente).

## 2. Escolha o modelo pelo tipo de tarefa

Monte a equipe com o inventário (`scripts/inventario.py`). A matriz detalha tipos de tarefa. Para montar papéis, use os sete perfis de `papeis.md`. Entre candidatos que atendem à capacidade, ao nível e à independência exigidos, use a 1ª escolha e depois as alternativas. Quando a matriz der opções equivalentes, use a folga da §4.

Pools: [Gem] = Gemini Models no Antigravity. [Argon] = teto semanal próprio. [AgyC] = "Claude and GPT" no Antigravity. [Codex] = medidor compartilhado pelos GPT do Codex. [Pro] = reserva do Maestro no Claude Code. [0] = OpenCode grátis. Para Gemini 3.8 Flash, confirme se [Gem] se aplica [incerto]. Sem medidor identificado, trate a cota como desconhecida (§4).

| Tipo de tarefa | 1ª escolha | Alternativas, em ordem |
|---|---|---|
| Batedor: script, checagem, comando | Luna high [Codex], com teste automático | OpenCode grátis [0] → Haiku 5.5 medium [Pro] → Hydrogen low [Gem] apenas em tarefa compatível com o Antigravity, sem binário ou script bloqueado |
| Batedor: leitura e triagem | OpenCode grátis [0] | Gemini 3.8 Flash low [Gem] [incerto] (só texto N0) → Terra low [Codex] → Haiku 5.5 medium [Pro] |
| Converter binário / abrir URL | Sol low ou Luna high [Codex], com ferramenta adequada (ex.: PyMuPDF ou curl) e teste automático se for Luna | Haiku 5.5 medium [Pro] → OpenCode grátis [0] se o shell tiver as ferramentas. Para verificar fonte ou fato, siga a linha própria |
| Volume: código | Hydrogen high [Gem] ↔ Sol medium [Codex], escolha pela maior folga | Sonnet 5.5 medium [AgyC] → Sonnet 5.5 medium [Pro] |
| Volume: texto/pesquisa | Terra medium [Codex] para texto / Hydrogen high [Gem] para pesquisa | Sol medium [Codex] → Argon medium [Argon] |
| Volume de cuidado | Argon medium [Argon] (high se difícil) | Sol high [Codex] → Sonnet 5.5 medium [AgyC] → Neon medium [Gem] |
| Redação de registro formal | Opus 5.5 high [AgyC] | Opus 5.5 high [Pro] só após esgotar [AgyC] e se [Pro] for elegível. Argon high [Argon] ou Sol high [Codex] só após A/B em seção curta aprovado pelo usuário [incerto] |
| Verificação de fonte/fato | Sol medium [Codex] | Sonnet 5.5 medium ou Haiku 5.5 medium [Pro], com shell. Antigravity pode ler o resultado |
| Crítico | Neon high [Gem] (Orchestrator Neon [Gem] se a tarefa multi-arquivo couber) | Astra high [Codex] → Opus 5.5 high [AgyC] → Sol high [Codex] |
| Arquiteto / Conselho | Neon xhigh [Gem] + Astra high [Codex] + Opus 5.5 high [AgyC] | Voz Claude: Opus 5.5 high [Pro] só com [AgyC] ≥ 100%, [Pro] com 5 h < 50% e semanal dentro do ritmo |
| Revisor | Autor Gemini → Sol high [Codex]. Autor Claude, GPT ou aberto → Neon high [Gem] | Sonnet 5.5 medium/high [AgyC] → Argon medium [Argon] para diff curto. Sonnet 5.5 medium/high [Pro] só se Antigravity e Codex travarem e [Pro] for elegível. Em todos os casos, filtre pela família do autor |
| Revisão de texto | Família ≠ autor. Autor Gemini → Sol medium [Codex]. Autor Claude, GPT ou aberto → Neon medium [Gem] | Autor Gemini → Sonnet 5.5 medium [AgyC]. Autor Claude, GPT ou aberto → Argon medium [Argon] |
| QA visual | Neon high [Gem] | Terra medium [Codex] para imagens fornecidas [incerto] → Sonnet 5.5 medium [AgyC] |

- **Famílias diferentes se conferem.** Autor e revisor de diff ou texto sempre de famílias diferentes. Em N3, testes por uma terceira família quando houver. Se faltar revisor elegível, informe a pendência.
- **Claude de produção começa no Antigravity.** Use Agy Sonnet e Agy Opus quando forem elegíveis. Claude Code entra nas condições da §4, incluindo tarefas exclusivas da ferramenta. A reserva também vale para Haiku.
- **Prepare os insumos.** PDF, Office e zip vão para conversão em terminal elegível com shell. Despache ao Antigravity o texto convertido ou a imagem pronta. Scripts bloqueados pelo sandbox também vão para outro terminal.
- **Dado sensível** (código fechado de cliente, segredos, dados pessoais) nunca vai para modelo grátis que treina com os dados (Big Pickle, Iceman, Flint, Inkling).

## 3. Escolha o effort

| Nível | Claude | Gemini | GPT | OpenCode |
|---|---|---|---|---|
| N0 | Haiku low | Gemini 3.8 Flash low (triagem textual); Hydrogen low | Luna medium; Terra low (triagem) | grátis |
| N1 | Haiku medium; Sonnet low | Hydrogen medium | Luna high; Sol low | grátis |
| N2 | Sonnet medium | Hydrogen high; Argon medium; Neon medium | Sol medium; Terra medium (texto) | pago, se houver |
| N3 | Sonnet high; Opus high | Neon high; Argon high `[incerto]` | Sol high; Astra high | — |
| N4 | Opus high | Neon xhigh | Astra high (Conselho); xhigh só com ganho real | — |

- Escreva **sempre** o modelo e o effort esperados no cartão e na 1ª linha do despacho: os padrões divergem entre ferramentas.
- `max`/`ultra` quase nunca: pensam demais e gastam mais. xhigh só com ganho real.
- Mude effort ou modelo **só entre tarefas** (no meio quebra o cache e o agente relê tudo). Se um perfil precisa de dois efforts com frequência, tenha dois terminais em vez de trocar toda hora.

## 4. Consulte a cota antes de decidir

`python <SKILL>/scripts/cotas.py` antes de cada lote, no início da sessão e a cada rodada. Aplique as regras a todas as janelas aplicáveis do pool.

1. **Leitura desconhecida.** Estado diferente de `ready`, leitura com mais de 1 h ou valor ausente significa cota desconhecida. Tire o pool de "Gaste primeiro". Despache uma única tarefa pequena de sondagem e releia, ou confira o banner com `maestri check "<Terminal>"`. Para Claude Pro, confirme primeiro as condições da reserva.
2. **Ritmo semanal/mensal.** Uso permitido = percentual do tempo decorrido da janela + 10 pontos percentuais. Acima do ritmo, reserve o pool para as tarefas que exigem sua capacidade.
3. **Faixas por pool pago.** Abaixo de 80%, rotina se o ritmo permitir. De 80% a menos de 95%, só o insubstituível. A partir de 95%, encerre novos despachos e deixe o que já está rodando terminar. Em 100%, ponha a tarefa em fila se faltar alternativa elegível e avise o usuário com a hora do reset.
4. **Escolha entre equivalentes.** Compare a folga na janela mais apertada de cada pool, contando a carga já reservada que a leitura ainda não reflete. Em empate, use o pool com reset mais próximo. Preserve a capacidade, o degrau e a independência exigidos pelo perfil.
5. **Claude Pro é reserva do Maestro.** Produtor no Claude Code só para tarefa sem outro terminal elegível, com 5 h < 50% e semanal dentro do ritmo. De 50% a menos de 70% na janela de 5 h, só para bloqueio técnico crítico sem alternativa, ainda com a semanal no ritmo. Com 5 h ≥ 70%, nenhum produtor usa Claude Code. Nas linhas que exigem esgotamento de [AgyC], confirme também 5 h ou semanal de [AgyC] ≥ 100%. Retorne ao Antigravity quando ele voltar a ficar elegível.
6. **Codex compartilha um medidor** entre os quatro modelos [incerto: peso de cada um]. Até medir, limite Astra a duas tarefas por janela de 5 h. Use Sol como padrão e Luna/Terra para o volume que cabe nos perfis deles.
7. **Calibração.** Estime o tamanho P/M/G por tarefa e divida entre pools elegíveis o lote que projetar uso acima de 80% em algum deles. Sem estimativa confiável, faça uma tarefa curta e releia antes de reservar o lote. O Batedor registra o delta de cada tarefa em `.maestri/cotas-log.md` com modelo, effort e tamanho.

## 5. Escalada quando falha

Falhou 2x (o produtor reportou bloqueado ou a revisão reprovou duas vezes):
1. Suba o **effort** no mesmo modelo (Haiku medium → high; Hydrogen high → xhigh).
2. Suba o **modelo** na escada da mesma família (`modelos.md`) quando houver um degrau elegível. Se a ferramenta ou a cota impedir a subida, procure outro pool que preserve a qualidade mínima. Autor e revisor continuam de famílias diferentes.
3. Suba o **nível** da tarefa e reavalie o escopo (talvez falte especificação: despache ao Arquiteto).

## 6. Economia de tokens (custo por tarefa concluída, não por chamada)

- **Contexto do Maestro é o mais caro:** leia só o veredito e o `head` das saídas; nada de código ou diff; peça resumos curtos ao Batedor.
- **Passe caminhos, não conteúdo:** o produtor lê os arquivos; resultados voltam por arquivo em `.maestri/relatorios/`.
- **Afinidade de cache:** tarefas relacionadas no mesmo terminal, em sequência; `/clear` só ao mudar de assunto; nunca troque modelo ou effort no meio de uma tarefa.
- **Lote coeso:** várias tarefas pequenas do mesmo assunto num despacho só, para o mesmo terminal.
- **Fatos confirmados no despacho** ("o endpoint X existe e foi testado"), para ninguém redescobrir.
- **Ninguém é chamado por chamar:** toda tarefa tem entregável verificável; se uma etapa não muda a decisão, ela não existe.
- **Barato não é economia se refaz:** tarefa difícil em modelo leve que falha 3x custa mais que acertar de primeira no modelo certo.
