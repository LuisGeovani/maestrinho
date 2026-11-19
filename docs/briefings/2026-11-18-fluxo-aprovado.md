> **Histórico.** Este documento descreve a versão anterior da skill. A versão atual (reescrita em 2026-11-18) está em `skills/maestro-equipe/`, com fontes em `docs/pesquisa/2026-11-18b/` e testes em `docs/testes/`.

# Briefing do Maestro: o fluxo aprovado pelo usuário (2026-11-18)

O usuário disse: "teu fluxo de trabalho tá perfeito... esse é o fluxo que eu queria". Medo dele: uma sessão nova, começada do zero, não repetir isso e o Maestro voltar a trabalhar sozinho. Este briefing descreve **exatamente** o ciclo usado nas sessões de 18/11/2026 (projetos Dra e regex), para virar o roteiro operacional da skill.

## 1. Início de sessão do zero (checklist obrigatório, antes de qualquer pedido)

1. Carregar a skill `maestro-equipe` e ler a REGRA DE OURO.
2. `maestri list`, `maestri role list`, `maestri preset list`.
3. `maestri check` em cada terminal e ler o **rodapé**: modelo, raciocínio, pasta (`.maestri/roles/<id>` do projeto certo?), avisos no banner (ex.: regra inválida no settings.json), pedidos pendentes (confiança de pasta, permissão).
4. **Conferir se papéis e presets são deste projeto.** Caso real: o workspace "Regex" era cópia do da Dra: papéis diziam "projeto Dra" e os terminais abriam com `--add-dir` da Dra. Correção: reabrir a Faísca com o preset do projeto; ela reescreve os papéis a partir de `references/papeis.md` + docs do projeto (em arquivos no scratchpad); o Maestro aplica com `maestri role write` e reabre todos com `maestri recruit "Nome" --preset "<preset do projeto>" --replace "Nome"`; aprovar "trust this folder" no Antigravity (`--raw "\r"`).
5. Ler só os docs de agentes do projeto (AGENTS.md, CLAUDE.md) e a memória. Nada de código.

## 2. O ciclo de cada pedido

1. **Entender e checar estado só com git/maestri** (`git status --short`, `git log`, `git diff --stat`, `maestri check`). Não ler código: se precisar entender código, pedir resumo a um produtor leve.
2. **Quebrar em tarefas com ID** (`<PREFIXO>-T<n>`, ex.: `RX-T2`), nível, autor, revisor de outra família, modelo e raciocínio. Tarefas dependentes vão em sequência (ex.: Forja sobe a stack e salva o contrato → Prisma integra → Forja revisa); independentes, no mesmo lote.
3. **Escrever o despacho num JSON no scratchpad** e enviar com `python <skill>/scripts/maestri_batch.py <arquivo> --linhas N` usando **`run_in_background: true`**. Nunca montar JSON na linha de comando.
4. **Responder ao usuário em poucas linhas e encerrar o turno.** Não fazer polling: a notificação do background chega sozinha e o relatório chega como mensagem nova (`maestri ask "Maestro"`).
5. **Na notificação, ler só o começo da saída** (`head`). Casos:
   - "responded by messaging you directly" → aguardar o relatório (ou ele já chegou).
   - tela com pedido de permissão → `maestri check` para ver o comando; se estiver dentro do escopo, aprovar uma vez (`maestri ask "Nome" --raw "\r"`); senão negar ou perguntar ao usuário.
   - tarefa ainda rodando em segundo plano no Antigravity (`1 task(s)`) → aguardar.
   - tela mostra outra coisa (ex.: o usuário rodou um comando no terminal, como `/auto-mode-setup`) → o despacho se perdeu: conferir com `git status` que nada mudou e **reenviar**.
6. **Ao receber o relatório: conferir o escopo** com `git status --short` e `git diff --stat` (sem ler o diff linha a linha). Arquivo fora da lista = devolver.
7. **Despachar a revisão para outra família** com checklist explícito (itens a, b, c… do que conferir), "aprovado ou até 5 apontamentos com arquivo, trecho e correção", somente leitura. Pares usados: Prisma (Gemini) → Forja (Claude); Forja (Claude) → Lente (Gemini); Faísca em N0/N1 → conferência de escopo pelo Maestro + grep pedido no próprio despacho.
8. **Decidir os apontamentos**: aceitar, ajustar (ex.: a Lente sugeriu tirar o manifesto do mobile, o Maestro corrigiu para manter o manifesto e tirar só o código) ou rejeitar com motivo. **Uma única rodada de correção** volta ao autor, com os itens numerados.
9. **Integrar com git**: commit só no nome do usuário (sem Co-Authored-By); **push só com autorização explícita para aquele push** (autorização anterior não vale; o classificador do Claude Code bloqueia). Se o usuário disser "não commite", apenas integrar na working tree.
10. **Reportar ao usuário**: curto, com tabela "quem fez o quê", o que está pendente e o que depende dele. Nunca dizer que algo foi testado se não foi (ex.: "build real não testado: Docker desligado").

## 3. Decisões com o usuário

- Usar AskUserQuestion quando há escolha que é dele (commit/branch, descartar stash, consertar algo que é de outra pessoa da turma), com a opção recomendada primeiro.
- Seguir a resposta mesmo quando ela difere da recomendação (ex.: "commita na frontendInicial", "descartar os três stashes").
- Problemas encontrados que não são do pedido (ex.: Docker do front quebrado pela reorganização de uma colega; Lombok no JDK 25; e-mail inválido no .env.example) viram **lista de pendências para o usuário decidir**, não correção por conta própria. Contorno local para destravar a tarefa é ok, desde que avisado e sem commit.

## 4. Git seguro em repositório compartilhado

- Antes de descartar algo: olhar (`git diff --stat`), salvar o que importa (patch no scratchpad) e usar **stash** como backup em vez de apagar; descartar de vez só com ok do usuário.
- `git pull --ff-only`; trocar de branch levando mudanças com stash push/pop; conferir conflito.
- Trazer arquivos de outra branch sem commit: `git restore --source=<ref> --worktree -- <pasta>`.
- Antes de levar mudanças para outra branch, conferir com `git merge-base --is-ancestor` e `git diff --stat` o que difere.
- O trabalho de outra pessoa (ex.: a reorganização da colega) é a **referência**: o despacho proíbe mudar estrutura, versões e configs dela; o trabalho do usuário entra como acréscimo.

## 5. Economia do próprio Maestro (Opus)

- Respostas curtas ao usuário; tabela em vez de parágrafos.
- Ler só `head` das saídas; não reler arquivos; não checar terminais sem motivo.
- Não ler código nem diff de conteúdo: pedir a um produtor.
- Erros cometidos nesta sessão, a evitar: editar settings.json do Antigravity pessoalmente (devia ter despachado); ler trechos do diff do mapa para classificar (devia ter pedido à Faísca); checagens repetidas de terminais; mensagens longas.

## 6. Detalhes que funcionaram nos despachos

- Primeira linha: ID, nível, modo (EDIÇÃO/SOMENTE LEITURA), MODELO e raciocínio; caminho absoluto do projeto e branch ("não troque de branch").
- Contexto com os arquivos exatos a ler e fatos já confirmados (ex.: endpoints testados pela Forja, "GET /pois não existe") para o autor não redescobrir.
- Escopo permitido e proibido com caminhos; "não rode git"; "não derrube os containers"; "não invente dados".
- Validação com comandos exatos (build, lint, curl, docker compose config) e o que fazer se a ferramenta faltar ("se o Docker estiver desligado, diga no relatório").
- Relatório: formato fixo, máximo de linhas, **sem aspas no texto** (aspas cortam a mensagem).
- Antigravity: prompts em XML com restrições no fim (references/prompts.md). Claude: texto direto com checklist e "confira antes de terminar".
