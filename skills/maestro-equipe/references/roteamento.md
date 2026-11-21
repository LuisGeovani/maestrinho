# Roteamento: tarefa → perfil → terminal, modelo e effort → cota

Escolha o terminal pela capacidade, o modelo e o effort pelo perfil e o pool pela folga. Famílias diferentes se conferem. Catálogo dos modelos: `modelos.md`. Fluxos por tipo de pedido: `fluxos.md`.

## Princípios

1. **Ferramenta → nível → cota.** Binários, abertura direta de URL e scripts bloqueados pelo sandbox vão para Codex, Claude Code ou OpenCode conforme a matriz. Antigravity recebe texto ou imagem já preparados.
2. **Escolhida a família Claude, use Sonnet ou Opus no Antigravity (Claude and GPT).** Se a cota bloquear novos despachos, passe para Claude Code enquanto todas as janelas conhecidas do Pro estiverem abaixo de 95% e o provedor não vetar uso. Volte ao Antigravity no reset. Compare a folga entre famílias igualmente aptas antes da escolha.
3. **Preserve o degrau exigido pelo perfil.** Entre famílias que entregam o mesmo aceite, escolha pela folga depois das reservas. Mantenha a preferência técnica nas tarefas especializadas.
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

Monte a equipe com o inventário (`scripts/inventario.py`). A matriz detalha tipos de tarefa. Para montar papéis, use os sete perfis de `papeis.md`. Filtre por ferramenta, nível, critérios de aceite e independência. **↔** liga candidatos capazes de entregar o mesmo aceite no subcaso indicado. Compare a folga após as reservas da §4 entre famílias aptas e elegíveis. Para Claude, use a folga do medidor que atenderia à tarefa pela ordem da §4. **→** indica preferência técnica em tarefa especializada ou recurso de reserva sujeito às condições da linha.

Pools: [Gem] = Gemini Models no Antigravity. [Argon] = teto semanal próprio. [AgyC] = "Claude and GPT" no Antigravity. [Codex] = medidor compartilhado pelos GPT do Codex. [Pro] = Claude Pro compartilhado com o Maestro no Claude Code. [AgyC → Pro] = ordem interna da família Claude (§4). [0] = OpenCode grátis. [medidor desconhecido] = vínculo ainda sem confirmação. Para Gemini 3.8 Flash, confirme no provedor o vínculo com um medidor antes de compará-lo por folga. Use a folga de [Gem] apenas se esse vínculo for confirmado.

| Tipo de tarefa | Candidatos para o mesmo aceite ou preferência técnica | Condições e reserva |
|---|---|---|
| Batedor: script, checagem, comando | Luna high [Codex] ↔ OpenCode grátis [0] para passos e teste fechados. Para comando simples compatível com Antigravity, Hydrogen low [Gem] também entra | Luna exige teste automático. Haiku 5.5 medium [Pro] quando couber no perfil e o Pro estiver utilizável. Binário ou script bloqueado exige terminal com shell elegível |
| Batedor: leitura e triagem | OpenCode grátis [0] ↔ Terra low [Codex]. Para triagem de texto já convertido N0, Gemini 3.8 Flash low [medidor desconhecido] entrega o mesmo aceite quando cumprir o formato pedido | Flash fica fora da comparação por folga enquanto o medidor não for confirmado. Haiku 5.5 medium [Pro] quando couber no perfil e o Pro estiver utilizável |
| Converter binário / abrir URL | Sol low [Codex] ↔ Luna high [Codex] ↔ OpenCode grátis [0] quando entregarem a mesma extração com as ferramentas exigidas | Luna exige teste automático. Haiku 5.5 medium [Pro] quando couber no perfil e o Pro estiver utilizável. Para confirmar fonte ou fato, use a linha de verificação |
| Volume: código | Hydrogen high [Gem] ↔ Sol medium [Codex] para código N1–N2 com contrato e testes definidos. Sonnet 5.5 medium [AgyC → Pro] entra quando cumprir o mesmo contrato e validação | Escolha a família pela folga e aplique a ordem Claude |
| Volume: texto/pesquisa | Texto comum: Terra medium [Codex] ↔ Sol medium [Codex] ↔ Argon medium [Argon]. Pesquisa ampla: Hydrogen high [Gem] ↔ Sol medium [Codex] ↔ Argon medium [Argon] | Na pesquisa, compare quem tem acesso às fontes pedidas e entrega a mesma síntese. Para confirmar fonte ou fato, use a linha própria |
| Volume de cuidado | Argon medium [Argon] ↔ Sol high [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro] ↔ Neon medium [Gem] para escopo fechado com o mesmo aceite | Argon high se difícil. Para risco N3 ou registro formal, use a linha especializada |
| Redação de registro formal | Preferência técnica: Opus 5.5 high [AgyC → Pro] | Argon high [Argon] ou Sol high [Codex] só após A/B em seção curta aprovado pelo usuário [incerto] |
| Verificação de fonte/fato | Sol medium [Codex] por padrão, com shell e prova bruta | → Sonnet 5.5 medium ou Haiku 5.5 medium [Pro] com Pro utilizável. Antigravity pode ler o resultado |
| Crítico | Preferência técnica N3: Neon high [Gem] → Astra high [Codex] → Opus 5.5 high [AgyC → Pro] → Sol high [Codex] | Orchestrator Neon [Gem] no lugar de Neon puro quando a tarefa multi-arquivo couber |
| Arquiteto / Conselho | Vozes complementares: Neon xhigh [Gem] + Astra high [Codex] + Opus 5.5 high [AgyC → Pro] | A voz Claude segue a ordem da §4 |
| Revisor | Diff curto de baixo risco: Neon high [Gem] ↔ Argon medium [Argon] ↔ Sol high [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro], filtrados pela família do autor e pelo mesmo checklist. Outros diffs N2: Neon high [Gem] ↔ Sol high [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro], filtrados pela família e pelo mesmo checklist | Em N3, preferência técnica por Sol high [Codex] para autor Gemini ou Neon high [Gem] para os demais, com Sonnet 5.5 high [AgyC → Pro] se elegível. Uma vez escolhida a voz Claude, use a ordem da §4 |
| Revisão de texto | Autor Gemini: Sol medium [Codex] ↔ Sonnet 5.5 medium [AgyC → Pro]. Autor Claude, GPT ou aberto: Neon medium [Gem] ↔ Argon medium [Argon] | Família diferente do autor em todos os casos |
| QA visual | Neon high [Gem] ↔ Sonnet 5.5 medium [AgyC → Pro] quando ambos tiverem acesso ao portal ou às imagens e cumprirem o mesmo checklist | Terra medium [Codex] entra para imagens fornecidas quando demonstrar o mesmo aceite [incerto] |

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
4. **Escolha entre equivalentes.** Compare a folga na janela mais apertada de cada pool, descontando a carga já reservada que a leitura ainda não reflete. Em empate, use o pool com reset mais próximo. No preset grátis, considere a capacidade confirmada para o lote. Sem sinal de capacidade, aplique a regra de leitura desconhecida. Preserve a capacidade, o degrau e a independência exigidos pelo perfil.
5. **Ordem interna da família Claude.** Use Agy Sonnet / Agy Opus primeiro. Se Claude and GPT atingir a faixa sem novos despachos (janela conhecida ≥ 95%) ou o provedor vetar uso por cota, passe ao Claude Code. Pro utilizável significa todas as janelas conhecidas < 95% e nenhum veto do provedor. O ritmo semanal e a faixa de 80% seguem como sinais de consumo nesse repasse. Cota livre em Codex ou Gemini não impede a passagem após escolher Claude. No reset, confirme a leitura e volte ao Antigravity quando o medidor voltar a aceitar despachos. O Maestro também roda no Pro. Acompanhe a janela de 5 h ao passar tarefas ao Claude Code.
6. **Codex compartilha um medidor** entre os quatro modelos [incerto: peso de cada um]. Até medir, limite Astra a duas tarefas por janela de 5 h. Dentro do Codex, use Sol como padrão e Luna/Terra para o volume que cabe nos perfis deles. Para escolher entre pools, aplique a matriz e a regra de folga.
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
