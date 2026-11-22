# Roteamento: tarefa → perfil → terminal, modelo e effort → cota

Escolha o terminal pela capacidade, o modelo e o effort pelo perfil e o pool pela folga. Famílias diferentes se conferem. Catálogo dos modelos: `modelos.md`. Fluxos por tipo de pedido: `fluxos.md`.

## Princípios

1. **Equilíbrio entre provedores.** A meta é manter os pools pagos (Claude Pro, Codex, Gemini Models, Argon, Claude and GPT do Antigravity) em percentuais parecidos; nenhuma família é padrão. O Claude Pro já carrega o Maestro, então começa mais gasto: produtor no Claude Code só com (a) recurso exclusivo (Chrome via `--chrome`; SSH/LAN quando nenhum outro terminal tem acesso), (b) nenhum apto de outra família com folga, ou (c) pools comprovadamente equilibrados (leitura fresca e próxima; pool desconhecido só avisa e passa, então "trava não disparada" não prova equilíbrio) e Claude entre os aptos. Pergunta de controle: "antes de despachar para Claude: qual terminal GPT, Gemini ou aberto apto foi descartado, e por quê?" (essa resposta vira a linha `Motivo pool:` quando a trava disparar).
2. **Ordem de decisão: ferramenta (requisito duro) → degrau mínimo apto → família pela folga (equalizar) → ordem interna da família.** A família não é escolhida antes da comparação. Binários, abertura direta de URL e scripts bloqueados pelo sandbox vão para Codex, Claude Code ou OpenCode conforme a matriz; Antigravity recebe texto ou imagem já preparados. Na família Claude, mantenha a ordem interna Antigravity (Claude and GPT) → Claude Code → volta ao Antigravity no reset: com o Claude and GPT do Antigravity bloqueado, os candidatos Claude entram na comparação pela folga do Claude Pro (que inclui o Maestro) e a trava vale para eles.
3. **Degrau mínimo apto.** Escolha o menor modelo que entrega o aceite de primeira e preserve o degrau exigido pelo perfil. N0/N1 vão primeiro ao degrau básico (Luna, Hydrogen low/medium, Flash após medidor confirmado, OpenCode grátis; Haiku quando o Pro não estiver retido). Quando a rodada tem partes mecânicas (levantar, contar, listar, converter, rodar testes e coletar a saída, conferir checklist mecânico), separe-as em tarefas N0/N1 para o degrau básico só quando isso poupa trabalho do modelo caro. Nunca invente tarefa e nunca mande N2+ a modelo básico para equilibrar ("barato não é economia se refaz"). Mantenha a preferência técnica nas tarefas especializadas.
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

- **Fronteira Batedor × Volume (degrau mínimo apto e partes mecânicas):** escolha o menor modelo que entrega o aceite de primeira. Scripts, alterações mecânicas e checagens N0/N1 com passos fechados e teste automático vão primeiro ao **Batedor** (degrau básico: Luna, Hydrogen low/medium, Flash após medidor confirmado, OpenCode grátis; Haiku quando o Pro não estiver retido); a linha **Volume: código** fica para implementação que exige o degrau intermediário. N1 não é motivo automático para usar Sol, nem para baixar tarefa complexa para Luna ("barato não é economia se refaz" continua valendo). Quando a rodada tem partes mecânicas (levantar, contar, listar, converter, rodar testes e coletar a saída, conferir checklist mecânico), separe-as em tarefas N0/N1 para o degrau básico só quando isso poupa trabalho do modelo caro. Nunca invente tarefa.
- **Script utilitário fechado é N1 e cabe no Luna, no OpenCode grátis ou no Haiku:** especificação (entrada → saída) e teste automático definidos no despacho. Se o despacho autoriza explicitamente, o produtor faz; recusa por "passar de N1" só vale quando falta especificação ou teste.

3. **Risco:** segurança, dinheiro, dado pessoal → sobe um nível e pede red team em N3.
4. **Tamanho e dependência:** quantos arquivos? Depende de outra tarefa? **Cadeia dependente fica no mesmo terminal**; só tarefas independentes vão em paralelo para terminais diferentes (multi-agente custa ~15x os tokens de um chat e só compensa em trabalho independente).

## 2. Escolha o modelo pelo tipo de tarefa

Monte a equipe com o inventário (`scripts/inventario.py`). A matriz detalha tipos de tarefa para os sete perfis de `papeis.md`. Aplique a ordem de decisão: ferramenta (requisito duro) → degrau mínimo apto → família pela folga (equalizar) → ordem interna da família. **↔** liga candidatos aptos em pé de igualdade capazes de entregar o mesmo aceite no subcaso indicado; nenhuma família é padrão. Para Claude, compare a folga do medidor que atenderia à tarefa pela ordem da [§4](#4-consulte-a-cota-antes-de-decidir) (`[AgyC]` ou, se bloqueado ou se exigir shell/Chrome, `[Pro]`). **→** indica preferência técnica com condição própria. Se a trava da [§4](#4-consulte-a-cota-antes-de-decidir) reter qualquer destino pago (Claude, GPT ou Gemini), libere a seção só quando houver justificativa válida em linha iniciada por `Motivo pool:`.

Pools: [Gem] = Gemini Models no Antigravity. [Argon] = teto semanal próprio. [AgyC] = "Claude and GPT" no Antigravity. [Codex] = medidor compartilhado pelos GPT do Codex. [Pro] = Claude Pro compartilhado com o Maestro no Claude Code. [AgyC → Pro] = ordem interna da família Claude (§4), comparando pela folga do pool efetivo. [0] = OpenCode grátis. [medidor desconhecido] = vínculo ainda sem confirmação. Para Gemini 3.8 Flash, confirme no provedor o vínculo com um medidor antes de compará-lo por folga. Use a folga de [Gem] apenas se esse vínculo for confirmado.

| Tipo de tarefa | Candidatos em pé de igualdade (↔) ou preferência técnica (→) | Condições próprias |
|---|---|---|
| Batedor: script, checagem, comando | Luna high [Codex] ↔ OpenCode grátis [0] ↔ Hydrogen low/medium [Gem] (comandos compatíveis com Antigravity) ↔ Haiku 5.5 medium [Pro] (quando o Pro não estiver retido) | Degrau básico primeiro. Luna exige passos fechados e teste automático. Binário ou script bloqueado pelo sandbox exige terminal com shell |
| Batedor: leitura e triagem | OpenCode grátis [0] ↔ Terra low [Codex] ↔ Hydrogen low [Gem] ↔ Gemini 3.8 Flash low [medidor desconhecido] (texto já convertido N0) ↔ Haiku 5.5 low/medium [Pro] (quando o Pro não estiver retido) | Degrau básico primeiro. Flash fica fora da comparação por folga enquanto o medidor não for confirmado |
| Converter binário / abrir URL | Luna high [Codex] ↔ OpenCode grátis [0] ↔ Sol low [Codex] ↔ Haiku 5.5 medium [Pro] (quando o Pro não estiver retido), quando entregarem a mesma extração com as ferramentas exigidas | Degrau mínimo apto primeiro (Luna com teste automático ou OpenCode grátis). Para confirmar fonte ou fato, use a linha de verificação |
| Navegador / site | (a) CLI ou API com shell (`gh` para PR, issue e checks; CLI do provedor para deploy) no menor degrau apto → (b) Portal do Maestri operado por terminal Gemini ou GPT (sites públicos ou com login feito no Portal) → (c) Claude Code com `--chrome` [Pro] | `--chrome` só quando o site exige a sessão logada no Chrome do usuário e nem (a) nem (b) atendem (com `Motivo pool: recurso exclusivo: Chrome` se a trava disparar) |
| Volume: código | Hydrogen medium/high [Gem] ↔ Sol low/medium [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro] para código N1–N2 que exige o degrau intermediário (contrato e testes definidos) | Scripts, alterações mecânicas e checagens N0/N1 com passos fechados e teste automático ficam no Batedor; N1 não é motivo automático para usar Sol |
| Volume: texto/pesquisa | Texto comum: Terra medium [Codex] ↔ Argon medium [Argon] ↔ Sol medium [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro]. Pesquisa ampla: Hydrogen high [Gem] ↔ Sol medium [Codex] ↔ Argon medium [Argon] | Em resumo ou conversão simples, Terra primeiro. Na pesquisa, compare quem tem acesso às fontes pedidas. Para confirmar fonte ou fato, use a linha própria |
| Volume de cuidado | Argon medium/high [Argon] ↔ Sol high [Codex] ↔ Neon medium [Gem] ↔ Sonnet 5.5 medium/high [AgyC → Pro] para escopo fechado com o mesmo aceite | Escolha pela folga entre os pools aptos. Para risco N3 ou registro formal, use a linha especializada |
| Redação de registro formal | Preferência técnica: Opus 5.5 high [AgyC → Pro] → Argon high [Argon] ↔ Sol high [Codex] após A/B em seção curta aprovado pelo usuário `[incerto]` | Ordem interna Claude pela §4 |
| Verificação de fonte/fato | Sol medium [Codex] ↔ Haiku 5.5 medium [Pro] ↔ Sonnet 5.5 medium [Pro], em terminal com shell e prova bruta | Escolha pela folga entre Codex e Pro (Haiku antes de Sonnet quando couber no degrau). Antigravity só lê o resultado |
| Crítico | Neon high [Gem] ↔ Astra high [Codex] ↔ Opus 5.5 high [AgyC → Pro] ↔ Sol high [Codex] | Orchestrator Neon [Gem] no lugar de Neon puro quando a tarefa multi-arquivo couber |
| Arquiteto / Conselho | Conselho (uma voz por família): Neon xhigh [Gem] + Astra high [Codex] + Opus 5.5 high [AgyC → Pro]. Especificação N3 individual: Neon high/xhigh [Gem] ↔ Astra high [Codex] ↔ Opus 5.5 high [AgyC → Pro] | No Conselho, uma voz obrigatória por família; a voz Claude segue a ordem da §4 |
| Revisor | Diff curto de baixo risco: Neon high [Gem] ↔ Argon medium [Argon] ↔ Sol high [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro]. Outros diffs N2: Neon high [Gem] ↔ Sol high [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro]. Em N3: Neon high [Gem] ↔ Sol high [Codex] ↔ Astra high [Codex] ↔ Sonnet 5.5 high [AgyC → Pro] | Família ≠ autor e mesmo checklist. Claude não é revisor padrão; entra quando o autor não é Claude e o equilíbrio permite |
| Revisão de texto | Autor Gemini: Sol medium [Codex] ↔ Terra medium [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro]. Autor Claude: Neon medium [Gem] ↔ Argon medium [Argon] ↔ Sol medium [Codex]. Autor GPT ou aberto: Neon medium [Gem] ↔ Argon medium [Argon] ↔ Sonnet 5.5 medium [AgyC → Pro] | Família ≠ autor em todos os casos. Claude não é revisor padrão; entra quando o autor não é Claude e o equilíbrio permite |
| QA visual | Neon high [Gem] ↔ Argon high [Argon] ↔ Terra medium [Codex] (imagens fornecidas `[incerto]`) ↔ Sonnet 5.5 medium [AgyC → Pro] quando tiverem acesso ao portal ou às imagens e cumprirem o mesmo checklist | Escolha pela folga entre os terminais com acesso ao Portal ou às imagens |

- **Famílias diferentes se conferem.** Autor e revisor de diff ou texto sempre de famílias diferentes. Em N3, testes por uma terceira família quando houver. Se faltar revisor elegível, informe a pendência.
- **A ferramenta precisa cumprir o aceite.** Nas tarefas Claude que exigem shell ou outro recurso indisponível no Antigravity, use o Claude Code com Pro utilizável. Haiku cabe quando a matriz o prevê para esse perfil.
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

1. **Leitura desconhecida.** Estado diferente de `ready`, leitura com mais de 1 h ou valor ausente significa cota desconhecida. Tire o pool de "Gaste primeiro". Despache uma única tarefa pequena de sondagem e releia, ou confira o banner com `maestri check "<Terminal>"`. Se houver veto do provedor ou janela conhecida ≥ 95%, apenas reconfira o estado. Para Claude Pro, confirme o estado no banner se a leitura estiver incompleta.
2. **Ritmo semanal/mensal.** O limite de uso é o maior entre 25% e o percentual do tempo decorrido da janela mais 10 pontos percentuais. Acima desse limite, reserve o pool para as tarefas que exigem sua capacidade.
3. **Faixas por pool pago.** Abaixo de 80%, rotina se o ritmo permitir. De 80% a menos de 95%, só o insubstituível. A partir de 95%, encerre novos despachos e deixe o que já está rodando terminar. Em 100%, ponha a tarefa em fila se faltar alternativa elegível e avise o usuário com a hora do reset. Para a passagem Claude ao Pro, aplique a regra específica abaixo.
4. **Escolha do Maestro × trava de equilíbrio do script.** Separe as duas decisões: (a) **Maestro:** escolhe entre os candidatos aptos pela folga na janela mais apertada de cada pool, descontando as reservas (itens 2 e 3) e a carga já planejada; em empate, use o reset mais próximo (no preset grátis, considere a capacidade confirmada ou aplique a regra de leitura desconhecida). (b) **Trava do `maestri_batch.py` (`comunicacao.md` §2):** independente de quem é apto para a tarefa, compara cada destino pago com leitura confiável (qualquer família: Claude, GPT ou Gemini) contra o **menor uso global** entre todos os pools pagos elegíveis (`ready`, leitura fresca, sem veto), usando a janela mais apertada de cada pool. Com diferença de 15 pontos percentuais ou mais e sem uma linha `Motivo pool:` com texto, a seção fica `RETIDO (equilíbrio)` e as outras seguem; se o pool de referência global não atender àquela tarefa ou não houver alternativa apta mais folgada, o caminho é justificar na seção com uma linha que começa com `Motivo pool:` seguido de texto na mesma linha (sem diferenciar maiúsculas; exemplos de redação: `recurso exclusivo: qual` ou `sem alternativa: por quê`). OpenCode grátis nunca é retido. Pool desconhecido ou leitura desatualizada só gera aviso e passa (portanto, "trava não disparada" não prova equilíbrio); veja `comunicacao.md` §2 para `--mostrar`, log em `.maestri/distribuicao.log` e contagem no `cotas.py`.
5. **Ordem interna da família Claude (Antigravity → Claude Code → volta ao Antigravity no reset).** A ordem de decisão é ferramenta (requisito duro) → degrau mínimo apto → família pela folga (equalizar) → ordem interna da família. Quando o pool "Claude and GPT" do Antigravity estiver utilizável (janelas conhecidas < 95%, sem veto) e a tarefa não exigir shell ou `--chrome`, os candidatos Sonnet/Opus entram na comparação pela folga de "Claude and GPT" (Agy Sonnet / Agy Opus). Com o Claude and GPT do Antigravity bloqueado (ou quando a tarefa exige shell/`--chrome`), os candidatos Claude entram na comparação pela folga do Claude Pro (que inclui o Maestro) e a trava do item 4 vale para eles. Como o Claude Pro já carrega o Maestro, produtor no Claude Code só entra com Pro utilizável (todas as janelas conhecidas < 95% e nenhum veto do provedor) e quando houver: (a) recurso exclusivo (Chrome via `--chrome`; SSH/LAN quando nenhum outro terminal tem acesso), (b) nenhum apto de outra família com folga, ou (c) pools comprovadamente equilibrados e Claude entre os aptos. Antes de despachar para Claude, responda à pergunta de controle do princípio 1 (que fundamenta a justificativa do item 4 se a trava disparar). No reset, confirme a leitura e volte ao Antigravity.
6. **Codex compartilha um medidor** entre os quatro modelos [incerto: peso de cada um]. Até medir, limite Astra a duas tarefas por janela de 5 h. Dentro do Codex, respeite a fronteira Batedor × Volume: scripts, alterações mecânicas e checagens N0–N1 com passos fechados e teste automático vão primeiro a Luna (e leitura/texto simples a Terra); Sol fica para código que exige o degrau intermediário, verificação de fonte e revisão; Astra fica para N3/N4. Para escolher entre pools, aplique a matriz e a regra de folga.
7. **Calibração.** Estime o tamanho P/M/G por tarefa e divida entre pools elegíveis o lote que projetar uso acima de 80% em algum deles. Sem estimativa confiável, faça uma tarefa curta e releia antes de reservar o lote. O Batedor registra o delta de cada tarefa em `.maestri/cotas-log.md` com modelo, effort e tamanho.

## 5. Escalada quando falha

- **Diagnóstico antes de retentar:** tarefa que falhou ou voltou `parcial` não é reenviada antes de um diagnóstico: o que já foi feito, a causa da falha e o que falta (de preferência por um Batedor do degrau básico, lendo relatório, tela ou log). Só então o Maestro reencaminha o restante.

Se a parte restante falhar 2x (o produtor reportou bloqueado ou a revisão reprovou duas vezes):
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
