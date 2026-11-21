# Prompts de despacho por família

O formato é escolhido pelo **destinatário**, não pelo autor da tarefa. O rodapé do relatório (arquivo + aviso curto) é acrescentado pelo `maestri_batch.py`: não o escreva à mão.

## 0. O que todo despacho tem (qualquer família)

1. **1ª linha:** `TAREFA <ID> · N<nível> · <EDIÇÃO | SOMENTE LEITURA> · <modelo e effort esperados>`.
2. **Projeto:** caminho absoluto de `<RAIZ>` e a branch ("não troque de branch"). Os produtores abrem numa pasta de papel; trabalham sempre em `<RAIZ>`.
3. **Objetivo** em 1–2 frases: o que entregar e por quê.
4. **Contexto:** arquivos exatos a ler (ou o `.maestri/contexto/<ID>.md` do Batedor) e **fatos já confirmados** (vindos de relatório, nunca palpite), para ninguém redescobrir.
5. **Escopo permitido e proibido**, com caminhos. Proibições padrão: git; instalar pacotes; editar fora da lista; inventar dados; mudar estrutura, versões ou configs de terceiros.
6. **Pronto quando:** critérios verificáveis + **comandos exatos de validação** e o plano B ("se o Docker estiver desligado, diga no relatório").
7. **Disjuntor:** "mesmo erro 2x: pare e reporte bloqueado".
8. Em consulta, **SOMENTE LEITURA** no topo e no fim (o arquivo de relatório é a única escrita permitida).

Teste do bom despacho (Anthropic): um colega competente, sem nenhum contexto, faria a tarefa só com esse texto?

## 1. Gemini (Antigravity: Neon, Hydrogen, Orchestrator, Argon, Flash)

Regras: XML ou Markdown (um só); contexto e arquivos no começo; ação, restrições, critério de pronto e saída **no fim**, com frase de ancoragem; listas curtas; lotes pequenos (1 página ou 1 fluxo); caminhos absolutos; **não** peça "pense passo a passo" (o thinking é nativo; suba o effort se precisar); o Gemini responde curto por padrão, então peça detalhe quando precisar. Modos de falha a prevenir: perde escopo em tarefa vaga, edita vizinhos (imports, estilos globais), inventa arquivos/rotas/pacotes, esquece restrições depois de muitas chamadas de ferramenta, entra em loop de erro.

```
TAREFA <ID> · N<n> · EDICAO · Gemini 4 Hydrogen, high
PROJETO: <RAIZ> (branch <b>; nao troque de branch)

<objetivo>
<1 a 2 frases: o que entregar>
</objetivo>

<contexto_obrigatorio>
Leia APENAS estes arquivos antes de agir (nao explore outras pastas):
- <RAIZ>\<arquivo de referencia>
- <RAIZ>\.maestri\contexto\<ID>.md
Fatos confirmados: <...>
</contexto_obrigatorio>

<escopo_permitido>
Voce so pode criar ou editar:
- <RAIZ>\<arquivo alvo>
</escopo_permitido>

<passos>
1. Leia os arquivos de contexto_obrigatorio.
2. Faca a mudanca estritamente no escopo_permitido.
3. Valide executando: <comando exato>.
</passos>

Com base apenas nos arquivos acima, <repita a acao em uma frase>.

<proibido>
- NAO leia nem edite fora do escopo_permitido; NAO crie arquivos extras; NAO instale pacotes; NAO rode git.
- Se faltar arquivo ou o mesmo erro se repetir 2x, PARE e reporte bloqueado.
</proibido>

<criterio_de_pronto>
- <condicao verificavel 1>
- <condicao verificavel 2>
</criterio_de_pronto>
```

Multi-arquivo no Antigravity: prefira o Orchestrator (planeja e executa) ou peça `/plan` antes de editar.

Despacho Gemini só com **caminhos legíveis**: texto ou imagem. Binário (PDF, Office, zip...) vira texto antes, por um terminal Claude Code (`roteamento.md`), e o despacho cita o arquivo convertido. Script de verificação e listagem de pastas fora da pasta de papel: o sandbox pode bloquear; no "Valide" do despacho Gemini ponha só comando simples e despache a checagem por script a outro terminal.

## 2. Claude (Claude Code e Claude no Antigravity: Haiku, Sonnet, Opus, Fable)

Regras: texto direto; "funcionário brilhante, mas novo": o agente só tem o prompt. Documento longo: a pergunta vai no fim. Peça **conferência contra os critérios antes de terminar**. Haiku: passos numerados e escopo bem fechado (em low ele pula checagens). Sonnet/Opus: objetivo e critérios, caminho livre dentro do escopo. Fable: menos prescrição (prompt prescritivo demais piora).

```
TAREFA <ID> · N<n> · EDICAO · Sonnet 5.5, medium
Projeto: <RAIZ> (branch <b>; nao troque). Trabalhe so em: <pastas>.

Objetivo: <o que entregar e por que>.
Contexto: leia <arquivos | .maestri/contexto/<ID>.md>. Fatos confirmados: <...>. <erro ou comportamento atual, se houver>.
Pronto quando: <criterios verificaveis>. Valide com <comando> e confira cada criterio antes de terminar.
Nao faca: git, instalar pacotes, editar fora das pastas. Mesmo erro 2x: pare e reporte bloqueado.
```

## 3. GPT (Codex)

Regras: as quatro partes da OpenAI (objetivo, contexto, restrições, pronto quando) + **como validar**; siga no escopo, registre suposições, pare só em bloqueio ou decisão do usuário; confira cada parte do pedido antes de terminar; reaproveite a lógica existente. **Proíba computer use e `/model`** (o Codex já tentou controlar o computador para ver o próprio modelo).

```
TAREFA <ID> · N<n> · EDICAO · GPT 6.2 Sol, medium
Projeto: <RAIZ>. Objetivo: <o que entregar>.
Contexto: <arquivos, erro ou diff a revisar>. Fatos confirmados: <...>.
Restricoes: so as pastas <pastas>; sem git; sem instalar pacotes; NAO use computer use nem controle do computador; NAO rode /model.
Pronto quando: <criterios>. Valide com: <build e teste exatos>. Mesmo erro 2x: pare e reporte bloqueado.
```

## 4. Modelos abertos (OpenCode grátis ou pagos)

Regras: são os mais fracos em agente longo. Tarefa **pequena e fechada**, passos numerados, comandos exatos, nada de decisão de arquitetura. Bom para: ler e resumir, rodar testes e relatar, gerar docs a partir de código lido, checar uma lista. Nunca mande código sensível para os modelos que treinam com os dados.

```
TAREFA <ID> · N<n> · SOMENTE LEITURA · OpenCode deepseek-v4.1-flash-free
Projeto: <RAIZ>.
Passos:
1. Leia <arquivo 1> e <arquivo 2>.
2. <acao exata>, por exemplo: rode <comando> e anote o resultado.
3. Escreva o resumo pedido (ate <N> linhas) no relatorio.
Nao edite nenhum arquivo. Nao rode git. Se algo falhar 2x, pare e reporte bloqueado.
SOMENTE LEITURA.
```

## 5. Consulta (Conselho, crítica, pesquisa)

```
TAREFA <ID> · N4 · SOMENTE LEITURA · <modelo e effort>
Projeto: <RAIZ>. <contexto curto e fatos confirmados>.
Pergunta: <...>. Seu angulo: <arquitetura | riscos tecnicos | alternativa simples e custo | seguranca e regras do dominio>.
Responda com: recomendacao, 2-3 alternativas com trade-offs, riscos, e o que mudaria sua opiniao. Ate <N> linhas.
Mesmo erro 2x: pare e reporte. SOMENTE LEITURA: nao edite nem crie arquivos (so o relatorio).
```

Pesquisa: diga as fontes esperadas (oficiais primeiro, um benchmark independente), peça URL ao lado de cada fato e `[incerto]` no que não confirmou.

## 6. Revisão

Checklist em itens verificáveis (a), (b), (c), nunca "revise tudo". Passe o **caminho do relatório do autor** e o que o Maestro já viu no `git diff --stat`.

```
TAREFA <ID>-REV · N<n> · SOMENTE LEITURA · <modelo e effort> · autor: <nome> (<familia diferente>)
Projeto: <RAIZ>. Leia o relatorio do autor em .maestri/relatorios/<ID>.md.
Fatos ja confirmados (nao redescubra): git diff --stat mostra so <arquivos>; <...>.
Revise o diff de <arquivos> conferindo:
(a) <item verificavel, ex.: o formulario valida e-mail e mostra erro>
(b) <item, ex.: nenhum dado inventado nem segredo no diff>
(c) <item, ex.: <build/teste> passa>
Devolva aprovado ou ate 5 apontamentos (arquivo, trecho, problema, correcao sugerida).
Mesmo erro 2x: pare e reporte. SOMENTE LEITURA: nao edite nem crie arquivos (so o relatorio).
```

**Rodada de correção** (volta ao autor, uma vez só, com ID novo `<ID>-C1`): os apontamentos aceitos, numerados; o escopo permitido repetido; mesmo critério de pronto.

**Verificação curta** (N2+ de risco alto, ao revisor original, ID `<ID>-V1`, SOMENTE LEITURA): caminho do relatório do `-C1` e os apontamentos aceitos, numerados. Pergunta: "cada um foi resolvido? sobrou ou nasceu algo?". Resposta: aprovado, ou só o que restou (arquivo, trecho, problema). Até 10 linhas.
