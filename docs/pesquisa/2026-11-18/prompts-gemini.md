# Pesquisa: prompts para Gemini no Antigravity (Lente, Gemini 4 Argon High, 2026-11-18)

## 1. Estrutura (oficial Google)
- Contexto, arquivos e dados ANTES; ação + restrições no FINAL, com frase de ancoragem ("Com base apenas nos arquivos acima..."). https://ai.google.dev/gemini-api/docs/prompting-strategies ; https://ai.google.dev/gemini-api/docs/long-context
- Delimitadores XML (<objetivo>, <escopo_permitido>, <proibido>, <passos>, <criterio_de_pronto>, <saida>) ou ## Markdown.
- Ciclo Ler -> Executar -> Validar com ferramenta -> Reportar. Planning Mode (/plan) com Artifact para multi-arquivo; Fast Mode para pontual. https://antigravity.google/docs ; https://antigravity.google/docs/cli/best-practices
- Stop conditions: "falhou 2x ou faltou arquivo: PARE e reporte". https://ai.google.dev/gemini-api/docs/function-calling
- Thinking nativo (low/medium/high/xhigh via /effort). NÃO pedir "pense passo a passo". Temperatura padrão 1.0. https://ai.google.dev/gemini-api/docs/thinking ; https://ai.google.dev/gemini-api/docs/gemini-3
- Regras em AGENTS.md / GEMINI.md (teto 24 KB por arquivo, 20.000 tokens agregados; acima viram ponteiros). Fluxos repetitivos como Skills (.agents/skills/<nome>/SKILL.md). https://antigravity.google/docs/rules-workflows ; https://antigravity.google/docs/skills

## 2. Modos de falha e prevenção
1) Perda de escopo em tarefa longa/vaga: lotes curtos (1 página/fluxo), caminhos exatos, leitura limitada aos arquivos listados.
2) Over-editing (refatorar vizinhos, imports, estilos globais): whitelist <escopo_permitido> + blacklist <proibido> com caminhos absolutos; em consulta, "SOMENTE LEITURA" no topo E no fim.
3) Inventar arquivos/rotas/pacotes: passo 1 obrigatório de ler arquivos/contratos reais; proibir criar fora da lista e instalar pacotes.
4) Esquecer restrições/formato (diluição de atenção após muitos tool calls): listas curtas em XML; <proibido>, <criterio_de_pronto> e <saida> no FINAL.
5) Loops de erro: disjuntor "erro repetido 2x -> pare e reporte"; documentar contorno do sandbox (maestri fora do sandbox).

## 3. Modelo de despacho para Gemini
```
TAREFA: <ID> · Nivel <N1-N4> · Modo: <EDICAO | SOMENTE LEITURA>
PROJETO: <caminho absoluto da raiz>

<objetivo>
<1 a 2 frases diretas dizendo O QUE entregar>
</objetivo>

<contexto_obrigatorio>
Leia APENAS estes arquivos antes de agir (nao explore outras pastas):
- <caminho/arquivo_referencia_1>
- <caminho/contrato_ou_spec>
</contexto_obrigatorio>

<escopo_permitido>
Voce so pode criar ou editar:
- <caminho/arquivo_alvo_1>
</escopo_permitido>

<proibido>
- NAO leia nem edite arquivos fora de <escopo_permitido>.
- NAO crie arquivos extras, NAO instale pacotes e NAO rode git.
- Se qualquer comando/build falhar 2x com o mesmo erro, PARE imediatamente.
</proibido>

<passos>
1. Leia os arquivos em <contexto_obrigatorio>.
2. Aplique a mudanca estritamente em <escopo_permitido>.
3. Valide executando: <comando exato>.
</passos>

<criterio_de_pronto>
- <condicao verificavel 1>
- <condicao verificavel 2>
</criterio_de_pronto>

<saida>
Ao atingir <criterio_de_pronto> (ou se bloquear), PARE e envie APENAS o relatorio em ate 10 linhas (TAREFA, STATUS, ARQUIVOS, VALIDACAO, PENDENCIAS, VISAO opcional) com:
maestri ask "Maestro" "<relatorio>" (rode fora do sandbox se der access denied).
</saida>
```
