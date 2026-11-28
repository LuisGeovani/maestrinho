# Prompts de despacho por família

O formato é escolhido pelo **destinatário**, não pelo autor da tarefa. O papel permanente (`papeis.md`) fornece identidade e regras estáveis; o despacho define o escopo desta tarefa; o rodapé do relatório (arquivo + aviso curto) é acrescentado pelo `maestri_batch.py` — não o escreva à mão nem duplique regras fixas.

## 0. Padrão obrigatório — PACIF com aceite verificável

Todo despacho segue o **molde PACIF** (**P**apel, **A**ção, **C**ontexto, **I**ntenção, **F**ormato) com **Aceite e prova** e **plano B**. Nas seções §§1–4, ajuste apenas o que difere por família.

```text
### <Terminal> | <ID>
Tamanho: <P|M|G> (G só com linha `Indivisível: <motivo>` em consulta/auditoria indivisível; G de implementação: quebrar)
Leitura ampla: <opcional — quando lê muito mas altera pouco>
Roteamento: <modelo> <effort> | custo <n> | <mínimo apto | descartado: <par mais barato> porque <motivo>>

Papel e limites: <perfil nesta tarefa>, N<0-4>, <EDIÇÃO | SOMENTE LEITURA>. Raiz: <RAIZ> (branch <b>; não troque). Leitura: <arquivos/pastas exatos>. Escrita: <arquivos/pastas permitidos | só o relatório do rodapé>. Permissões: <por operação, ex.: git só diff; rodar suíte; sem instalar pacotes>. Não explore além das pastas listadas; mesmo erro 2x: pare e reporte bloqueado.
Ação: <verbo + entrega concreta>.
Contexto: <insumos acessíveis, fatos confirmados de relatório — nunca palpite — e decisões anteriores; amostra literal quando necessária>.
Intenção: <quem usará a entrega e qual decisão precisa tomar>.
Formato: <artefato, esquema, limite de linhas (ex.: até 25 linhas); em revisão: VEREDITO e orçamento de achados>.
Aceite e prova: <por critério: entrada ou comando → resultado esperado → prova bruta>. Se faltar <insumo essencial>, <alternativa autorizada ou STATUS parcial/bloqueado e decisão pendente>.
```

Regras do molde:
1. **Cabeçalho:** `Tamanho: <P|M|G>` mede a alteração (G só com linha `Indivisível: <motivo>` em consulta/auditoria indivisível; G de implementação: quebrar; leitura ampla vai em linha própria). `Roteamento:` usa `mínimo apto` quando não há conflito, ou `descartado: <par mais barato> porque <motivo>` (obrigatório quando `custo ≥ 300` ou houver alternativa real em conflito).
2. **Leitura e Escrita sempre separadas** em todos os moldes. Nunca use uma lista única de escopo que impeça o produtor de ler arquivos de referência fora da lista de escrita. Em consulta/revisão, `Escrita: só o relatório do rodapé` e marque **SOMENTE LEITURA** no início (e no fim se o texto for longo).
3. **Permissões por operação:** autorize o que o aceite pede em vez de proibir tudo e contradizer no critério (ex.: `git: só diff` em vez de "não faça git" + "cole `git diff`").
4. **Checklist antes de enviar:**
   - **O produtor consegue obter cada prova com os acessos e dados listados?** Se a resposta for não ou incerta, anexe a entrada literal no `Contexto:` ou troque o responsável pela coleta.
   - **Teste do colega sem contexto (Anthropic):** um colega competente, só com o papel e este despacho, entregaria de primeira?
5. **Exemplos de entrada→saída (condicionais):** omita em tarefas claras. Inclua **somente quando o aceite for ambíguo** — e, nesses casos, dê **um caso que deve passar e um que deve ser recusado** (fronteira), separados do material principal.

**Exemplo real curto** (baseado em `.maestri/despachos/AUD-R10.md`):

```text
### Neblina | AUD-F1-R
Tamanho: P
Leitura ampla: diff dos scripts e testes
Roteamento: Hydrogen medium | custo 30 | mínimo apto (revisão de outra família, autor GPT)

Papel e limites: revisora, N2, SOMENTE LEITURA. Leitura: git diff -- skills/maestro-equipe/scripts skills/maestro-equipe/tests, .maestri/relatorios/AUD-F1.md e AUD-F1-P1.md, seção "Sol | AUD-F1" de .maestri/despachos/AUD-R4.md, .maestri/despachos/AUD-R9.md. Permissões: git só diff; rodar suíte; rodar prévia `python skills/maestro-equipe/scripts/maestri_batch.py --mostrar .maestri/despachos/AUD-R9.md`. Escrita: só o seu relatório.
Ação: revisar se os 5 itens da AUD-F1 foram implementados como pedido e sem regressão.
Contexto: o batch é o que o Maestro lê para decidir; erro aqui esconde pendência ou deixa passar despacho caro/vetado.
Intenção: o Maestro commita a F1 se você aprovar.
Formato: até 15 linhas; VEREDITO aprovado | aprovado com ajustes | reprovado; até 5 apontamentos com arquivo:linha.
Aceite e prova: (a) para cada item 1–5, teste que cobre e linha do código; (b) `python -m unittest discover -s skills/maestro-equipe/tests` → OK (cole resumo); (c) `python skills/maestro-equipe/scripts/maestri_batch.py --mostrar .maestri/despachos/AUD-R9.md` → sem retenção (cole linhas de trava/custo). Se a suíte falhar por ambiente, conclua (a) e (c) com STATUS parcial.
```

## 1. Gemini (Antigravity: Neon, Hydrogen, Orchestrator, Argon, Gemini 3.8 Flash)

**O que difere no PACIF:** coloque **limites e formato no início** (`Papel e limites` + `Formato`) e a **ação/pergunta específica + aceite e prova depois do contexto longo**, com frase de ancoragem. Use XML ou Markdown (um só), listas curtas, lotes pequenos e caminhos absolutos. **Não** peça "pense passo a passo" (o thinking é nativo; avalie o par `modelo × effort` antes de subir). Como o Gemini tende a ser conciso, nomeie exatamente quais provas colar no relatório. Modos de falha a prevenir: perder escopo em tarefa vaga, editar vizinhos, inventar caminhos/pacotes, entrar em loop de erro.

```text
Tamanho: <P|M>
Roteamento: Hydrogen medium | custo <30|90> | <mínimo apto | descartado: Hydrogen low porque exige edição com contrato N2>

<papel_e_limites>
Perfil: <perfil>, N<n>, EDIÇÃO. Raiz: <RAIZ> (branch <b>; não troque).
Leitura (apenas estes arquivos):
- <RAIZ>\<arquivo de referência>
- <RAIZ>\.maestri\contexto\<ID>.md
Escrita (apenas estes arquivos):
- <RAIZ>\<arquivo alvo>
Permissões: git proibido (ou: git só diff); rodar <comando exato>; não instalar pacotes; não criar arquivos extras; não explorar além das pastas listadas. Mesmo erro 2x: pare e reporte bloqueado.
</papel_e_limites>

<formato>
Relatório curto (até 25 linhas) com comandos e saídas literais de validação.
</formato>

<contexto>
Fatos confirmados: <...>.
Intenção: <quem usará a entrega e qual decisão tomará>.
</contexto>

Com base apenas nos arquivos de leitura acima, <ação específica em 1–2 frases>.

<aceite_e_prova>
- <critério 1>: <comando/entrada> → <resultado esperado> → <prova no relatório>.
- <critério 2>: <comando/entrada> → <resultado esperado> → <prova no relatório>.
- Plano B: se faltar <insumo>, <alternativa ou STATUS parcial/bloqueado>.
</aceite_e_prova>
```

Multi-arquivo no Antigravity: prefira o Orchestrator (planeja e executa) ou peça `/plan` antes de editar.

Despacho Gemini só com **caminhos legíveis** via `read_file`: texto ou imagem. Use Gemini 3.8 Flash apenas para triagem e classificação N0 de texto já convertido. Para PDF, Office ou zip, encaminhe a conversão conforme a matriz de `roteamento.md` e cite no despacho Gemini o arquivo convertido. Comandos de shell (`curl`, `python`, PowerShell), abertura de URL e ferramentas MCP funcionam no Antigravity com aprovação do Maestro (`comunicacao.md` §6); para verificação de fonte ou fato, exija prova bruta (comando, código HTTP e trecho literal) conforme a matriz.

## 2. Claude (Claude Code e Claude no Antigravity: Haiku, Sonnet, Opus, Fable)

Siga a árvore de decisão única (`SKILL.md` passo 5 e `roteamento.md`), sem família favorita. Se a trava de equilíbrio disparar, inclua `Motivo pool:` na seção.

**O que difere no PACIF:** destaque **contexto e motivo** (`Contexto` + `Intenção` claros — "funcionário brilhante, mas novo"). Em documento longo, ponha a pergunta específica no fim. Peça **conferência contra os critérios antes de terminar**. Em classificação ambígua, dê um exemplo válido e um caso recusado/limítrofe separados do material. Haiku: passos numerados e escopo fechado (em `low` pula checagens). Sonnet/Opus: objetivo e critérios, caminho livre dentro do escopo. Fable: menos prescrição.

```text
Tamanho: <P|M>
Roteamento: Sonnet 5.5 medium | custo <40|120> | <mínimo apto | descartado: <par> porque <motivo>>

Papel e limites: <perfil>, N<n>, EDIÇÃO. Raiz: <RAIZ> (branch <b>; não troque). Leitura: <arquivos exatos>. Escrita: <arquivos autorizados>. Permissões: <por operação, ex.: rodar testes; git proibido; sem instalar pacotes>. Não explore além das pastas listadas; mesmo erro 2x: pare e reporte bloqueado.
Ação: <o que entregar em 1–2 frases>.
Contexto: fatos confirmados: <...>. <erro ou comportamento atual, se houver>.
Intenção: <por que esta mudança existe e qual decisão destrava>.
Formato: relatório curto (até 25 linhas) com provas de validação.
Aceite e prova: <critérios verificáveis + comando exato>; confira cada critério antes de terminar. Se faltar <insumo>, <alternativa ou STATUS parcial/bloqueado>.
```

## 3. GPT (Codex: Luna, Terra, Sol, Astra)

**O que difere no PACIF:** **objetivo curto e critérios** numerados (`critério → sim/não → evidência`). Peça conclusão e prova observável, dispensando narração do raciocínio interno. Comece sem exemplos em tarefas claras; acrescente entrada→saída (1 caso que passa, 1 que deve ser recusado) quando o aceite for ambíguo. Registre decisões tomadas, trechos a preservar e o padrão conservador na dúvida (pedindo que registre a suposição). Proíba explorar o repositório inteiro para preservar a janela de 5 h.

| Degrau | Modelo no Codex | O que muda no despacho |
|---|---|---|
| Luna | `gpt-6-luna` | Passos numerados, esquema rígido da saída e comando de teste automático obrigatório. Tarefa fechada N0–N1 |
| Terra | `gpt-6.1-terra` | Texto-alvo, tamanho, registro e exemplo curto. Dê o formato de saída se a tarefa for conversão |
| Sol | `gpt-6.2-sol` | Especificação, critérios de aceite numerados e comando exato de validação. Para verificar fonte ou fato, exija prova bruta |
| Astra | `gpt-6.2-astra` | Conselho, N3 de risco ou escalada com avaliação. Objetivo, restrições e testes; execução dentro do escopo |

```text
Tamanho: <P|M>
Roteamento: <modelo> <effort> | custo <n> | <mínimo apto | descartado: <par mais barato> porque <motivo>>

Papel e limites: <perfil>, N<n>, <EDIÇÃO | SOMENTE LEITURA>. Raiz: <RAIZ> (branch <b>; não troque). Leitura: <arquivos exatos>. Escrita: <arquivos autorizados e trechos a preservar | só o relatório>. Permissões: <por operação; sem mutações git, sem instalar pacotes, sem controle do computador, sem /model>. Não explore além das pastas listadas; mesmo erro 2x: pare e reporte bloqueado.
Ação: <objetivo em uma frase>.
Contexto: fatos confirmados e decisões tomadas: <...>. Na dúvida, use <padrão conservador> e registre a suposição.
Intenção: <quem usa a entrega e decisão esperada>.
Formato: <arquivo/esquema>; relatório curto (até 25 linhas) no formato critério → sim/não → evidência.
Aceite e prova:
1. <critério verificável> → <evidência>
2. <critério verificável> → <evidência>
Valide com: <comando exato>. Se faltar <insumo>, <alternativa ou STATUS parcial/bloqueado>.
```

O relatório inclui comando e saída relevantes e, para fontes, código HTTP e trecho literal. Sem prova bruta, marque o critério como pendente. Antes de despachar um lote grande, ensaie um item representativo e confira o resultado contra os critérios antes de liberar o restante.

## 4. Modelos abertos (OpenCode grátis ou pagos)

**O que difere no PACIF:** **passos fechados** (numerados e comandos exatos), tarefa pequena, saída curta e nenhuma decisão de arquitetura. Bom para ler e resumir, rodar testes e relatar, gerar docs de código lido ou checar uma lista. Nunca mande código sensível para modelos grátis que treinam com os dados.

```text
Tamanho: <P|M>
Roteamento: OpenCode grátis | custo 0 | mínimo apto (tarefa N0 não sensível)

Papel e limites: Batedor, N<0|1>, SOMENTE LEITURA. Raiz: <RAIZ>. Leitura: <arquivo 1>, <arquivo 2>. Escrita: só o relatório do rodapé. Permissões: rodar <comando exato>; git proibido; não edite nenhum arquivo; não explore além das pastas listadas. Mesmo erro 2x: pare e reporte bloqueado.
Ação: execute os passos fechados abaixo:
1. Leia <arquivo 1> e <arquivo 2>.
2. Rode <comando exato> e anote a saída.
3. Grave o resumo pedido no relatório.
Contexto: <1 frase do que está sendo conferido>.
Intenção: <decisão ou insumo para a próxima tarefa>.
Formato: relatório curto (até <N> linhas) com comando e saída literal.
Aceite e prova: cada passo 1–3 com evidência no relatório. Se faltar <insumo essencial> ou o comando falhar 2x, pare e reporte STATUS bloqueado identificando o que faltou. SOMENTE LEITURA.
```

## 5. Consulta (Conselho, crítica, pesquisa)

```text
Tamanho: <P|M|G> (G só com linha `Indivisível: <motivo>` em consulta/auditoria indivisível; G de implementação: quebrar)
Roteamento: <modelo> <effort> | custo <n> | <mínimo apto | descartado: <par mais barato> porque <motivo>>

Papel e limites: Arquiteto/Crítico, N4, SOMENTE LEITURA. Raiz: <RAIZ>. Leitura: <arquivos exatos>. Escrita: só o relatório do rodapé. Permissões: <por operação, ex.: git só log/diff; web se autorizado>. Não explore além das pastas listadas; mesmo erro 2x: pare e reporte bloqueado.
Ação: responder à pergunta <...> sob o ângulo <arquitetura | riscos técnicos | alternativa simples e custo | segurança e regras do domínio>.
Contexto: <fatos confirmados e restrições do projeto>.
Intenção: <decisão de produto/arquitetura que o Maestro/usuário vai tomar>.
Formato: relatório curto (até <N> linhas) com recomendação, 2–3 alternativas com trade-offs, riscos e o que mudaria sua opinião.
Aceite e prova: cada afirmação ligada a arquivo:linha ou fonte verificada. Se faltar dado essencial, marque [incerto] e registre em PENDÊNCIAS. SOMENTE LEITURA.
```

Pesquisa: diga as fontes esperadas (oficiais primeiro, um benchmark independente), peça URL ao lado de cada fato e `[incerto]` no que não confirmou. Para declarar uma fonte verificada, encaminhe a um terminal da linha “Verificação de fonte/fato” da matriz e peça a prova bruta.

## 6. Revisão

Checklist em itens verificáveis (a), (b), (c), nunca "revise tudo". Passe o **caminho do relatório do autor** e o que o Maestro já viu no `git diff --stat`. O **orçamento de achados** (ex.: até 5 apontamentos) vai **só no despacho** — nunca no papel permanente. Todo despacho de revisão exige `VEREDITO: aprovado | aprovado com ajustes | reprovado` e indica a decisão que cada veredito dispara.

```text
Tamanho: <P|M>
Roteamento: <modelo> <effort> | custo <n> | <mínimo apto | descartado: <par mais barato> porque <motivo>>

Papel e limites: Revisor (família ≠ autor <nome>), N<n>, SOMENTE LEITURA. Raiz: <RAIZ>. Leitura: .maestri/despachos/<rodada>.md (seção <ID>), .maestri/relatorios/<ID>.md e diff de <arquivos>. Escrita: só o relatório do rodapé. Permissões: git só diff dos arquivos listados; rodar <teste/build exato>; não editar nem criar arquivos. Não explore além das pastas listadas; mesmo erro 2x: pare e reporte bloqueado.
Ação: revisar o diff de <arquivos> contra o despacho original e procurar regressões.
Contexto: fatos já confirmados (não redescubra): git diff --stat mostra só <arquivos>; <...>.
Intenção: o Maestro integra se aprovado, abre correção (-C1) se aprovado com ajustes ou devolve se reprovado.
Formato: até 20 linhas; VEREDITO aprovado | aprovado com ajustes | reprovado; até 5 apontamentos (arquivo:linha, problema, correção sugerida).
Aceite e prova:
(a) <item verificável, ex.: o formulário valida e-mail e mostra erro> → evidência arquivo:linha;
(b) <item, ex.: nenhum dado inventado nem segredo no diff> → conferência no diff;
(c) <comando de build/teste> → passa (cole resumo da saída).
Se faltar <insumo/ambiente>, conclua os itens possíveis, registre STATUS parcial e o critério pendente. SOMENTE LEITURA.
```

**Rodada de correção** (volta ao autor, mantendo o ID do defeito: `<ID>-C1`, e `-C2` só com decisão explícita após verificação): os apontamentos aceitos, numerados; `Leitura`/`Escrita` e permissões repetidos; mesmo `Aceite e prova`.

**Verificação curta** (N2+ de risco alto, ao revisor original, ID `<ID>-V1`, SOMENTE LEITURA): `Leitura:` relatório do `-C1` e `git diff` dos arquivos tocados; `Escrita:` só o relatório; `Permissões:` git só diff dos arquivos tocados; `Ação:` conferir cada apontamento aceito ("foi resolvido? sobrou ou nasceu algo?"); `Formato:` até 10 linhas, `VEREDITO: aprovado | aprovado com ajustes | reprovado` e só o que restou (`arquivo:linha`, problema).
