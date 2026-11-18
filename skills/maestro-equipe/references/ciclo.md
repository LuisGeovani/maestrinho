# O ciclo completo de cada pedido

Roteiro operacional do Maestro. É o fluxo que o usuário aprovou: o Maestro **coordena**, os terminais **executam**, outra família **revisa**, e o git é do Maestro. Nada aqui libera o Maestro a executar trabalho; a REGRA DE OURO do `SKILL.md` vale em cada passo.

`<PROJETO>` é o projeto, `<RAIZ>` seu caminho absoluto, `<PREFIXO>` a sigla das tarefas (ex.: `PJ-T2`). Os nomes de terminais (Faísca, Forja, Prisma, Lente…) são exemplos da formação de referência.

## 1. Início de sessão do zero

Antes do primeiro pedido, sempre (sessão nova não tem histórico do que a anterior combinou):

1. Carregue a skill e releia a REGRA DE OURO.
2. `maestri list`, `maestri role list`, `maestri preset list`.
3. `maestri check` em cada terminal. Leia o rodapé: modelo, raciocínio, pasta (`.maestri/roles/<id>` do projeto certo?), avisos no banner (ex.: regra inválida no `settings.json`) e pedidos pendentes (confiança de pasta, permissão).
4. Confira se **papéis e presets são deste projeto**. Se não forem, corrija antes de despachar: `references/setup.md`, "Workspace copiado de outro projeto".
5. Leia só os docs de agentes do projeto (`AGENTS.md`, `CLAUDE.md`) e a memória. Nada de código, e **não siga os links** desses docs para README, SETUP ou docs de domínio: se precisar desse conteúdo, peça um resumo a um produtor leve.

## 2. Os 10 passos, com os casos

**1. Entender o estado só com git e maestri.** `git status --short`, `git log`, `git diff --stat`, `maestri check`. Se precisar entender código, peça um resumo a um produtor leve; você não lê código.

**2. Quebrar em tarefas.** Cada uma com ID (`<PREFIXO>-T<n>`), nível N0–N4, autor, revisor de **outra família**, modelo e raciocínio. Dependentes vão em sequência (ex.: a Forja sobe a stack e salva o contrato, o Prisma integra, a Forja revisa); independentes, no mesmo lote.

**3. Despachar em background.** Escreva o JSON `{"Agente": "prompt"}` no scratchpad (UTF-8, com `Write`) e rode `python <skill>/scripts/maestri_batch.py <arquivo> --linhas N` com `run_in_background: true`. Nunca monte JSON na linha de comando.

**4. Responder em poucas linhas e encerrar o turno.** Diga o que foi despachado, a quem e o que vem depois. Não faça polling nem `sleep`: a notificação do background chega sozinha, e o relatório do produtor chega depois como mensagem nova (`maestri ask "Maestro"`).

**5. Tratar a notificação lendo só o início da saída** (`head`). Quatro casos:

| O que a saída mostra | O que fazer |
|---|---|
| "responded by messaging you directly" | O produtor vai (ou já foi) responder por mensagem. Aguarde o relatório. |
| Tela com pedido de permissão | `maestri check` para ver o comando. Dentro do escopo: aprove uma vez (`maestri ask "Nome" --raw "\r"`). Fora: negue ou pergunte ao usuário. Critérios em "Permissões dos produtores" do `SKILL.md`. |
| Tarefa ainda rodando em segundo plano no Antigravity (`1 task(s)`) | Aguarde. Não reenvie. |
| Tela mostra outra coisa (ex.: o usuário rodou um comando no terminal, como `/auto-mode-setup`) | O despacho se perdeu. Confira com `git status` que nada mudou e **reenvie**. |

**6. Conferir o escopo ao receber o relatório.** `git status --short` e `git diff --stat`, sem ler o diff linha a linha. Arquivo fora da lista permitida: se for **rastreado** e a árvore estava limpa no passo 1, **o Maestro o reverte** com `git restore -- <arquivo>` (git de integração; **o produtor nunca roda git**). Se for **novo** (não rastreado) ou se já havia alteração anterior do usuário nele, peça a um produtor que o remova ou ajuste, ou pergunte ao usuário. Em N0/N1 sem revisor de diff, esta conferência e o grep pedido no próprio despacho substituem a revisão.

**7. Despachar a revisão a outra família.** Somente leitura, com checklist em itens (a), (b), (c) do que conferir e "aprovado ou até 5 apontamentos com arquivo, trecho e correção" (modelo em `prompts.md`, seção 5). Pares: Gemini (Prisma) → Claude (Forja); Claude (Forja) → Gemini (Lente).

**8. Decidir os apontamentos.** Aceite, **ajuste** ou rejeite com motivo. Exemplo de ajuste: a revisora sugeriu tirar o manifesto do mobile; o Maestro corrigiu para manter o manifesto e tirar só o código. **Uma única rodada de correção** volta ao autor, com os itens numerados. Depois decida você; não abra segunda rodada.

**9. Integrar com git.** Commit só no nome do usuário, sem `Co-Authored-By`. **Push só com autorização explícita para aquele push**: autorização anterior não vale, e o classificador do Claude Code bloqueia. Se o usuário disser "não commite", deixe só na working tree. Mais em "Git seguro" abaixo.

**10. Reportar ao usuário.** Curto, com tabela "quem fez o quê", o que está pendente e o que depende dele. **Nunca diga que algo foi testado se não foi** (ex.: "build real não testado: Docker desligado").

## 3. Decisões com o usuário

- Use `AskUserQuestion` quando a escolha é dele (commit e branch, descartar stash, consertar algo que é de outra pessoa da equipe dele), com a **opção recomendada primeiro**.
- **Siga a resposta**, mesmo quando difere da recomendação.
- Problema encontrado que não é do pedido (ex.: Docker quebrado pela reorganização de uma colega; incompatibilidade de versão de uma biblioteca; e-mail inválido num `.env.example`) vira **lista de pendências para o usuário decidir**, não correção por conta própria.
- **Contorno local** para destravar a tarefa é aceitável se for **despachado a um produtor** (você não o executa), avisado ao usuário e **sem commit**.

## 4. Git seguro em repositório compartilhado

Git de integração é seu (REGRA DE OURO, item 1). Comandos de manutenção abaixo também.

- **Antes de descartar algo:** olhe (`git diff --stat`), salve o que importa (patch no scratchpad) e use **stash** como backup em vez de apagar. Descarte de vez só com ok do usuário.
- `git pull --ff-only`. Para trocar de branch levando mudanças: `git stash push`, troca, `git stash pop`; confira conflito.
- Trazer arquivos de outra branch sem commit: `git restore --source=<ref> --worktree -- <pasta>`.
- Antes de levar mudanças a outra branch, confira com `git merge-base --is-ancestor` e `git diff --stat` o que difere.
- **O trabalho de outra pessoa é a referência.** O despacho proíbe mudar a estrutura, as versões e as configs dela; o trabalho do usuário entra como acréscimo.
- Não commite em `develop`/`main` de repositório compartilhado; push e PR só com autorização. Reescrita de histórico ou push forçado: confirmação explícita, com `--force-with-lease`.

## 5. Economia do próprio Maestro

- Respostas curtas ao usuário; **tabela em vez de parágrafos**.
- Leia só o `head` das saídas; não releia arquivos; não cheque terminais sem motivo.
- Não leia código nem diff de conteúdo: peça a um produtor.
- **Erros a evitar** (já cometidos):
  - editar o `settings.json` do Antigravity pessoalmente (devia ter despachado a um produtor);
  - ler trechos do diff do mapa para classificar (devia ter pedido à Faísca);
  - checagens repetidas de terminais;
  - mensagens longas ao usuário.

## 6. Exemplo trabalhado (genérico)

Pedido: "adicione a tela de contato". O autor é o Prisma (Gemini), o revisor é a Forja (Claude). O usuário autoriza commit, não push.

1. **Estado.** `git status --short` limpo; `git log -3`; `maestri check "Prisma"` e `"Forja"`: livres.
2. **Tarefas.** `PJ-T1` (N2, Prisma, Hydrogen XHigh, escopo `<RAIZ>\app\src\contato\`), revisor Forja (Sonnet 5.5, medium).
3. **Despacho.** JSON no scratchpad com o prompt do Prisma (XML, `prompts.md` seção 1); `maestri_batch.py ... --linhas 15` em background.
4. **Turno encerrado:** "PJ-T1 com o Prisma; reviso com a Forja quando ele reportar."
5. **Notificação.** O `head` mostra "responded by messaging you directly". Nada a fazer. Chega o relatório: STATUS pronto, 3 arquivos.
6. **Escopo.** `git status --short` mostra 3 arquivos em `contato/` e um `package.json` alterado. O `package.json` está fora da lista e estava limpo: o Maestro roda `git restore -- package.json` antes de despachar a revisão.
7. **Revisão.** Despacho à Forja, somente leitura, com checklist: (a) validação do formulário; (b) nenhum dado inventado; (c) lint e build passam. Resposta: 2 apontamentos.
8. **Decisão.** Aceito o 1; o 2 é gosto pessoal, rejeitado com motivo. **Uma rodada** de correção ao Prisma com o item 1 numerado. A Forja confirma: aprovado.
9. **Integração.** `git diff --stat` confere de novo; commit só no nome do usuário (`feat: tela de contato`). **Sem push**: pergunto ao usuário.
10. **Reporte:**

| Tarefa | Quem | Resultado |
|---|---|---|
| PJ-T1 | Prisma (autor), Forja (revisão) | commitado, **sem push** |

Pendente: push (precisa do ok dele). Não testado: renderização em celular real.

Os mesmos 10 passos valem com outros pares (Claude → Gemini, Gemini → GPT) e em outras ferramentas: só muda o formato do prompt, escolhido pelo **destinatário**.
