# Prompts de despacho por família

O Maestro escolhe o formato pelo **destinatário**, não pelo autor. Em todo despacho: tarefa e nível, **modelo e raciocínio esperados**, caminho absoluto do projeto (`<RAIZ>`), escopo, critério de pronto e relatório. Consulta (Conselho, crítica) diz **SOMENTE LEITURA**.

Relatório: peça curto (até 10–12 linhas) e **sem aspas dentro do texto**; relatório longo ou com aspas pode chegar cortado. Se cortar, peça só o restante.

## 0. O que funcionou nos despachos (vale para qualquer família)

- **Primeira linha:** ID, nível, modo (EDIÇÃO ou SOMENTE LEITURA), **modelo e raciocínio** esperados; depois o caminho absoluto de `<RAIZ>` e a branch ("não troque de branch").
- **Contexto com os arquivos exatos** a ler e os **fatos já confirmados**, para o autor não redescobrir. Ex.: "os endpoints X e Y foram testados pela Forja; GET /itens não existe". O Maestro só repassa fatos que vieram de relatório de produtor, nunca palpite.
- **Escopo** permitido **e** proibido, com caminhos. Proibições comuns: "não rode git", "não derrube os containers", "não invente dados", "não mude estrutura, versões nem configs de terceiros".
- **Validação com comandos exatos** (build, lint, curl, `docker compose config`) e o plano B: "se o Docker estiver desligado, diga no relatório".
- **Relatório:** formato fixo (TAREFA, STATUS, ARQUIVOS, VALIDAÇÃO, PENDÊNCIAS, VISÃO opcional), **máximo de linhas** e **sem aspas no texto** (aspas cortam a mensagem).
- **Antigravity:** prompt em XML, com as restrições no fim (seção 1). **Claude:** texto direto, com checklist e "confira antes de terminar" (seção 2).
- Quando o escopo é verificável por grep, peça o grep no próprio despacho ("rode grep -rn <padrão> <pasta> e cole a contagem"). É o que substitui o revisor em N0/N1.

## 1. Gemini (Prisma, Lente, Flash)

Fontes: https://ai.google.dev/gemini-api/docs/prompting-strategies · https://ai.google.dev/gemini-api/docs/long-context · https://ai.google.dev/gemini-api/docs/thinking · https://ai.google.dev/gemini-api/docs/function-calling · https://antigravity.google/docs · https://antigravity.google/docs/cli/best-practices · https://antigravity.google/docs/rules-workflows · https://antigravity.google/docs/skills

Regras:
- Contexto e arquivos **no começo**; `<proibido>`, `<criterio_de_pronto>` e `<saida>` **no fim**, com frase de ancoragem ("Com base apenas nos arquivos acima…").
- Delimitadores XML (ou `##` Markdown). Listas curtas.
- Ciclo Ler → Executar → Validar com ferramenta → Reportar.
- Lotes curtos: 1 página ou 1 fluxo por despacho. Caminhos absolutos.
- Disjuntor: "erro repetido 2x → pare e reporte".
- **Não** peça "pense passo a passo": o raciocínio é nativo (`/effort`). Temperatura padrão 1.0.
- Multi-arquivo: peça `/plan` (Planning Mode, com Artifact); pontual: Fast Mode.
- Regras duradouras em `AGENTS.md`/`GEMINI.md` (teto de 24 KB por arquivo, 20.000 tokens agregados); fluxos repetitivos como skills em `.agents/skills/<nome>/SKILL.md`.
- Consulta: "SOMENTE LEITURA" no topo **e** no fim.

Modelo:

```
TAREFA: <ID> · Nivel <N1-N4> · Modo: <EDICAO | SOMENTE LEITURA>
MODELO: <ex.: Gemini 4 Hydrogen, XHigh>
PROJETO: <RAIZ, caminho absoluto>

<objetivo>
<1 a 2 frases dizendo O QUE entregar>
</objetivo>

<contexto_obrigatorio>
Leia APENAS estes arquivos antes de agir (nao explore outras pastas):
- <caminho/arquivo_referencia>
- <caminho/contrato_ou_spec>
</contexto_obrigatorio>

Com base apenas nos arquivos acima, <repita a acao pedida em uma frase>.

<escopo_permitido>
Voce so pode criar ou editar:
- <caminho/arquivo_alvo>
</escopo_permitido>

<passos>
1. Leia os arquivos de <contexto_obrigatorio>.
2. Aplique a mudanca estritamente em <escopo_permitido>.
3. Valide executando: <comando exato>.
</passos>

<proibido>
- NAO leia nem edite arquivos fora de <escopo_permitido>.
- NAO crie arquivos extras, NAO instale pacotes e NAO rode git.
- Se qualquer comando ou build falhar 2x com o mesmo erro, PARE imediatamente.
</proibido>

<criterio_de_pronto>
- <condicao verificavel 1>
- <condicao verificavel 2>
</criterio_de_pronto>

<saida>
Ao atingir <criterio_de_pronto> (ou se bloquear), PARE e envie APENAS o relatorio em ate 10 linhas, sem aspas no texto (TAREFA, STATUS, ARQUIVOS, VALIDACAO, PENDENCIAS, VISAO opcional) com:
maestri ask "Maestro" "<relatorio>" (se der access denied, rode so o maestri fora do sandbox).
Lembrete final: SOMENTE o escopo permitido; nada fora dele.
</saida>
```

### Modos de falha do Gemini e prevenção

| Falha | Prevenção no prompt |
|---|---|
| Perde o escopo em tarefa longa ou vaga | Lotes curtos (1 página ou fluxo), caminhos exatos, leitura limitada à lista |
| Over-editing (refatora vizinhos, imports, estilos globais) | `<escopo_permitido>` (lista branca) + `<proibido>` (lista negra) com caminhos absolutos; em consulta, SOMENTE LEITURA no topo e no fim |
| Inventa arquivos, rotas ou pacotes | Passo 1 obrigatório: ler os arquivos e contratos reais; proibir criar fora da lista e instalar pacotes |
| Esquece restrições e formato depois de muitas chamadas de ferramenta (diluição de atenção) | Listas curtas em XML; `<proibido>`, `<criterio_de_pronto>` e `<saida>` no **fim**, com lembrete final |
| Entra em loop de erro | Disjuntor "mesmo erro 2x → pare e reporte"; documente o contorno do sandbox (só o comando `maestri` roda fora dele) |

## 2. Claude (Faísca, Forja, Farol, Bigorna)

Fontes: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices · https://code.claude.com/docs/en/sub-agents · https://platform.claude.com/docs/en/build-with-claude/effort

Regras:
- **"Funcionário brilhante mas novo":** o agente só tem o prompt. Dê caminhos, objetivo, erros ou repro, critério de pronto e formato do relatório. Teste: um colega sem contexto entenderia?
- Documento longo: ponha a pergunta **no fim** (ganho de até 30% nos testes da Anthropic).
- Peça **verificação contra os critérios antes de terminar**.
- Restrinja pastas e comandos; peça parada ao falhar 2x.
- **Haiku:** escopo bem fechado e explícito, passos numerados. Em `low` ele tende a pular checagens: para instrução rígida e longa, use `high`.
- **Sonnet/Opus:** diga o objetivo e os critérios; deixe o caminho aberto, mas com os limites de escopo.
- Delegue só o que é isolado ou paralelizável; não multiplique agentes à toa.

Modelo:

```
Tarefa <ID>, nivel <N>. Modelo/raciocinio esperados: <ex.: Sonnet 5.5, medium>.
O projeto fica em <RAIZ> (trabalhe la, nao na pasta .maestri). Pastas permitidas: <pastas>.

Objetivo: <o que entregar e por que>.
Contexto: leia <arquivos ou secao da rodada>. <erro ou comportamento atual, se houver>.
Pronto quando: <criterios verificaveis>. Valide com <comando> e confira contra estes criterios antes de terminar.
Nao faca: git, instalar pacotes, editar fora das pastas permitidas. Erro repetido 2x: pare e reporte.
Relatorio ate 10 linhas, sem aspas no texto, com maestri ask "Maestro" "<relatorio>" no formato de <DOCS>EQUIPE.md.
<Se o documento for longo: a pergunta final fica por ultimo.>
```

## 3. Codex / GPT (Agulha, quando ativa)

Fontes: https://developers.openai.com/codex/learn/best-practices · https://developers.openai.com/codex/prompting · https://developers.openai.com/blog/run-long-horizon-tasks-with-codex · https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide

Regras:
- Objetivo, contexto, restrições, critério de pronto e **como validar** (build e teste).
- Nomeie o comportamento e aponte o código ou o repro.
- Regras duradouras no `AGENTS.md`. Tarefa longa: arquivo de spec e plano como fonte da verdade, validação por marco, diffs pequenos.
- Raciocínio `medium` é o padrão interativo.
- **Proíba o controle do computador.** A Agulha tentou usar computer use para abrir o próprio `/model`. Quem lê modelo e cota é o Maestro, pelo rodapé (`maestri check`).

Modelo:

```
Tarefa <ID>, nivel <N>. Modelo/raciocinio esperados: <ex.: GPT Sol, medium>.
Projeto: <RAIZ>. Objetivo: <o que entregar>.
Contexto: <arquivos, erro ou diff a revisar>.
Restricoes: so as pastas <pastas>; sem git; sem instalar pacotes; NAO use computer use nem controle do computador; NAO rode /model.
Pronto quando: <criterios>. Valide com: <build e teste exatos>.
Relatorio ate 10 linhas, sem aspas no texto, com maestri ask "Maestro" "<relatorio>".
```

## 4. Consulta somente leitura (Conselho ou crítica)

```
Consulta, SOMENTE LEITURA (nao crie nem altere arquivos). Projeto: <RAIZ>.
MODELO/RACIOCINIO esperados: <ex.: Gemini 4 Hydrogen, High>.
<contexto curto>. <pergunta e angulo esperado>.
Se qualquer comando falhar 2x com o mesmo erro, PARE e reporte.
Maximo <N> linhas, sem aspas no texto. Responda com maestri ask "Maestro" "<resposta>" (so o maestri fora do sandbox se der access denied).
SOMENTE LEITURA: nada de editar arquivos.
```

## 5. Revisão

Checklist em **itens (a), (b), (c)**: cada um é uma coisa verificável, não "revise tudo". Passe também os **fatos já confirmados** (o que o autor relatou, o que o Maestro viu no `git diff --stat`) para o revisor não refazer a descoberta.

```
Revisao de <ID> (autor: <nome, outra familia>). Modo: SOMENTE LEITURA. Projeto: <RAIZ>.
MODELO/RACIOCINIO esperados: <ex.: Gemini 4 Argon, High>.
Fatos ja confirmados (nao redescubra): <ex.: o autor reportou build ok; git diff --stat mostra so <arquivos>>.
Revise o diff dos arquivos <lista> conferindo:
(a) <item verificavel 1, ex.: o formulario valida e-mail e mostra erro>
(b) <item 2, ex.: nenhum dado inventado nem segredo no diff>
(c) <item 3, ex.: <comando de build/teste> passa>
Se qualquer comando falhar 2x com o mesmo erro, PARE e reporte.
Devolva "aprovado" ou ate 5 apontamentos (arquivo, trecho, problema, correcao sugerida), um por item. Sem aspas no texto.
Envie com maestri ask "Maestro" "<relatorio>" (se der access denied, rode so o maestri fora do sandbox).
SOMENTE LEITURA: nao edite nem crie arquivos.
```

Rodada de correção (volta ao **autor**, uma vez só): liste os apontamentos aceitos **numerados**, repita o escopo permitido e peça o relatório no mesmo formato.
