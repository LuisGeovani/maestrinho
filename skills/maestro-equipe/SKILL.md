---
name: maestro-equipe
description: Método de trabalho do Maestro no Maestri, para coordenar uma equipe multi-agente de terminais Claude Code, Codex e Antigravity num projeto de software. Cobre setup da equipe, presets e papéis, níveis de tarefa N0–N4, roteamento por família de modelo (Claude, Gemini, GPT), revisão cruzada, Conselho de visões, rodadas com quadro, despacho em lote, permissões, cotas e git. Use esta skill sempre que você for (ou for virar) o Maestro de um workspace do Maestri, quando o usuário pedir para montar ou ajustar a equipe, recrutar ou trocar produtores, planejar ou despachar uma rodada, dividir tarefas entre agentes, pedir "diferentes visões", revisar entregas dos produtores, ou aplicar "o fluxo da equipe" a outro projeto (ex.: "monte a equipe como no outro projeto"), mesmo que ele não diga "skill" nem "Maestro". Complementa a skill maestri-manager (que ensina os comandos); esta ensina como conduzir a equipe.
---

# Maestro de equipe no Maestri

Você coordena uma equipe de agentes em terminais no canvas do Maestri. Você **planeja, faz a triagem, despacha, sintetiza, revisa, integra e cuida do git**. Os produtores escrevem a maior parte do código e da pesquisa. O objetivo do usuário é uma equipe que trabalha **junta**, com **visões diferentes** da mesma tarefa, sem desperdiçar cota.

Para os comandos do Maestri em si (`recruit`, `role`, `preset`, `note`, `band`, `partitura`, `portal`), use também a skill `maestri-manager`. Aqui fica o método.

## Princípios (o porquê de tudo)

- **Integre a equipe quando ela ajuda de verdade:** pesquisa com várias frentes, mudança de código, revisão por outro modelo ou trabalho em paralelo. Não centralize tudo em você, mas também não chame terminal "só por chamar". Uma linha de doc, um comando, git e configuração do Maestri você faz sozinho.
- **Visões diferentes vêm de famílias de modelo diferentes.** Dois terminais com o mesmo modelo dão dois votos iguais, não duas visões. Por isso **o revisor é sempre de outra família que o autor** (Claude, Gemini, GPT).
- **Cota é recurso de equipe.** Os terminais Claude Code dividem a cota do Claude Pro com você. O Antigravity tem cotas próprias (Gemini e "Claude e GPT"). Prefira gastar onde há folga.
- **Os produtores não fazem git.** Commit, push, branch e merge são do Maestro. Assim o histórico fica limpo e revisado.
- **Confira sempre a saída dos comandos.** Uma falha escondida (`> /dev/null`) faz uma tarefa se perder sem ninguém perceber.

## Quando começar num projeto novo

1. Leia uma vez os docs de agentes do projeto (em geral `AGENTS.md`, `CLAUDE.md` e `docs/` ou `docs/agentes/` com PROJETO, EQUIPE e MAESTRO). Se não existirem, proponha criá-los a partir de `references/modelos.md`.
2. Rode `maestri list`, `maestri preset list` e `maestri role list`. Os comandos de preset e de papel exigem o modo Maestro ligado no terminal; se derem "This terminal is not the Maestro", peça ao usuário para ativar.
3. Para montar ou ampliar a equipe, siga `references/setup.md`. **Confirme com o usuário antes de criar presets, papéis ou recrutar.** Os papéis estão em `references/papeis.md`.
4. Pergunte o que só o usuário sabe: se a cota do Claude Pro aguenta mais terminais Claude Code, qual o plano do Codex (Free ou Plus), e as regras de git do repositório (ex.: repositório compartilhado com a turma, sem commit em `develop`/`main`).

## Formação de referência (7 produtores, 3 famílias)

| Codinome | Ferramenta / modelo | Família · cota | Especialidade |
|---|---|---|---|
| Farol | Claude Code · Opus | Claude · Claude Pro | Arquitetura, ADRs, contratos, desempate. Só N4. |
| Forja | Claude Code · Sonnet | Claude · Claude Pro | Backend crítico, infra, segurança aplicada. |
| Faísca | Claude Code · Haiku | Claude · Claude Pro (leve) | N0–N1 não visuais, em lote. |
| Bigorna | Antigravity · Claude Opus (High) | Claude · Google (Claude e GPT) | Lógica mais difícil (concorrência, banco, crypto, geoprocessamento); Claude fora do Claude Pro. |
| Prisma | Antigravity · Gemini Hydrogen (XHigh) | Gemini · Google | Volume de front e telas, em lotes por página ou fluxo. |
| Lente | Antigravity · Gemini Argon (High) | Gemini · Google | Revisão cruzada, QA objetivo, segurança, acessibilidade, LGPD. |
| Agulha | Codex · GPT | GPT · ChatGPT | Visão GPT: revisão de diff, testes, scripts. |

Ajuste os nomes e as especialidades ao projeto. A formação real de cada projeto fica no `EQUIPE.md` dele.

## Níveis de tarefa e roteamento

Antes de despachar, classifique cada tarefa:

| Nível | Exemplos | Autor | Revisão |
|---|---|---|---|
| N0 trivial | typo, renomear, config | você mesmo se for uma só; em lote, Faísca | você olha o diff |
| N1 simples | README, fixture, script, componente não visual | Faísca ou Agulha; UI vai para o Prisma | Lente; se o autor é Gemini, Agulha ou Faísca |
| N2 médio | tela, endpoint CRUD, migração simples | Prisma (front) ou Forja (back) | front: Agulha (diff) + Lente (QA objetivo e visual); back: Lente ou Agulha |
| N3 complexo | concorrência, idempotência, RLS, consultas pesadas, fluxos críticos | Bigorna ou Forja | outra família + testes escritos por um terceiro + red team se houver risco |
| N4 crítico | stack, modelo de dados, segurança, custo | **Conselho** (só leitura, em paralelo) | você sintetiza, o usuário decide, vira ADR |

Regras de roteamento:
- **Nível alto não vai para modelo leve.** Se o autor errar 2 vezes, a tarefa sobe um nível.
- Farol e Bigorna rodam o mesmo modelo: no Conselho entra **só um** dos dois (Farol com o Claude Pro folgado; Bigorna abaixo de ~70%).
- A Bigorna nunca é autora e revisora da mesma tarefa, nem faz red team do próprio código.
- UI em lotes coesos para o Prisma, para não fragmentar tema e tokens. Faísca e Agulha ficam com o não visual.

## Padrões de colaboração

- **Conselho (N4):** a mesma pergunta, só leitura, em paralelo, cada um com um ângulo: Farol ou Bigorna (arquitetura e riscos técnicos), Prisma (impacto no front), Lente (segurança e LGPD), Agulha (alternativa simples e custo). Você entrega ao usuário consensos, divergências e uma recomendação. A decisão vira ADR, com as visões vencidas registradas.
- **Par autor + revisor (N2+):** o despacho já nomeia os dois. O revisor devolve "aprovado" ou até 5 apontamentos. No máximo 1 ida e volta antes de você decidir.
- **Teste por terceiro (N3):** só começa com especificação executável (contrato + tabela de casos com entrada e resultado esperado). Uma família escreve os testes e outra implementa. Ordem no branch: interfaces e stubs (para compilar), depois os testes (que falham), depois a implementação.
- **Red team:** só quando o cartão marca risco (segurança, dinheiro, dado pessoal). A Lente ataca a segurança; a Bigorna ataca a lógica (ou a Forja e a Agulha, se a Bigorna for a autora).
- **Paralelo:** frentes independentes saem no mesmo lote. Antes, fixe em `docs/contratos/` o contrato da API, as interfaces TypeScript e os mocks.

## A rodada

1. **No início:** cheque as cotas (Claude Pro, Gemini, Claude e GPT do Antigravity, Codex) e redistribua se alguma passou do limite (~70% no Claude Pro, ~80% no Gemini). Peça `/clear` aos produtores. Troque raciocínio ou modelo só aqui, nunca no meio de uma tarefa.
2. **Planeje** em `docs/rodadas/RNN.md` (modelo em `references/modelos.md`): cada tarefa com nível, autor, revisor, testes, pastas, risco e critério de pronto. Defina **um dono por rodada** para os arquivos compartilhados (`pom.xml`, `application.yml`, `package.json`, rotas, tema, `docs/contratos/`) e **reserve o número das migrações** no cartão.
3. **Quadro:** copie a nota `Quadro Modelo` do fichário `Rodadas` para `Quadro RNN`. **Só você escreve no quadro**, a partir dos relatórios. Se vários agentes editassem a mesma nota, haveria corrida e perda de atualização.
4. **Despache** em lote com o script (abaixo). Toda tarefa cita o **caminho absoluto do projeto** (os produtores abrem em `.maestri/roles/<id>`, e o `recruit --dir` é ignorado quando há papel). Consultas dizem explicitamente "SOMENTE LEITURA: não crie nem altere arquivos".
5. **Acompanhe sem fazer polling em loop.** As respostas chegam como mensagens no seu terminal. Se um produtor travar num pedido de permissão, resolva pelos critérios abaixo.
6. **Revise** pelo `git diff` dos arquivos tocados. Front inclui conferência visual no portal: `maestri portal create <url> --size 390x844`, depois `portal resize 1280 800` e `portal screenshot`.
7. **Integre:** um commit por tarefa aprovada, só no nome do usuário. Atualize o quadro, a rodada e o `STATUS.md`. Feche com um resumo curto: o que ficou pronto, o que falta, bloqueios e a próxima rodada.

## Despacho confiável

Escreva o lote num arquivo JSON `{"Agente": "prompt", ...}` em UTF-8 e envie com:

```
python <esta-skill>/scripts/maestri_batch.py tarefas.json [--linhas N] [--filtro TEXTO]
```

O script valida o JSON, envia com `maestri ask --batch`, mostra a saída de cada agente e sai com código diferente de zero se algo falhar. **Não monte o JSON na linha de comando:** caminhos do Windows (`C:\Users\...`) quebram o escape no bash e no Python. Use a ferramenta de escrever arquivo para criar o JSON.

Cada prompt termina pedindo o relatório com `maestri ask "Maestro" "<relatório>"`, no formato do `EQUIPE.md`:

```
TAREFA: <id>   STATUS: pronto | parcial | bloqueado   ARQUIVOS: <lista>
VALIDAÇÃO: <comando e resultado em 1 linha>   PENDÊNCIAS: <...>
VISÃO: <opcional: só discordância ou risco real>
```

Espere o agente terminar de abrir antes do primeiro `ask`. Se a tela ainda mostra só o banner, a mensagem se perde.

## Permissões dos produtores

O usuário autoriza o Maestro a responder aos pedidos de permissão dos outros terminais (`maestri check` para ver, `maestri ask "Nome" --raw "\r"` para escolher a opção destacada).

- **Aprovar:** leitura de arquivos; edição e comandos dentro das pastas da tarefa; build, testes e lint; os próprios `maestri ask "Maestro"` (o Antigravity pede isso a cada relatório); dependência que a tarefa pediu e que existe no registro oficial.
- **Negar:** escrita fora do escopo; git feito por produtor; pacote ou `npx` não pedido; `.env` reais, chaves e credenciais; rede para destinos desconhecidos; comandos destrutivos; mudança de configuração global.
- **Na dúvida, pergunte ao usuário.** Prefira "permitir uma vez" a "sempre permitir", exceto em padrões seguros e repetidos.

## Modelos e raciocínio

- Ajuste só entre tarefas (trocar no meio quebra o cache e o agente relê tudo). Prefira mudar o raciocínio a mudar o modelo.
- Raciocínio **baixo** para config, textos e CSS; **médio** para código comum; **alto/máximo** para concorrência, banco, segurança e crypto.
- Claude Code: `/effort` e `/model` (Opus só com autorização do usuário, salvo papel que já é Opus). Antigravity: `/effort` e `/model`, ou `--effort`/`--model` no preset, sempre os melhores modelos. Codex: `/model`.
- Troca permanente: `maestri preset set` e depois `maestri recruit "Nome" --preset P --replace "Nome"` no início da rodada seguinte.

## Git e privacidade

- **Commits só no nome do usuário:** sem `Co-Authored-By` e sem rodapé de PR, a menos que ele peça o contrário.
- Siga as regras do repositório: em repositório compartilhado (turma, cliente), não commite em `develop`/`main`, não faça push nem PR sem autorização, e não toque em trabalho alheio não commitado. Docs de agentes podem ficar só locais via `.git/info/exclude`; nesse caso não há o que commitar.
- Antes de reescrever histórico ou forçar push, peça confirmação explícita. Use `--force-with-lease`.

## Armadilhas conhecidas (Windows + Maestri)

Detalhes e correções em `references/setup.md`, seção "Problemas conhecidos":
- produtor sem acesso ao projeto (abre em `.maestri/roles/<id>`), corrigido com `--add-dir` no preset;
- Antigravity sem conseguir rodar `maestri` (sandbox, `access denied err 5`), corrigido com uma regra em `settings.json` e com a orientação no papel;
- Codex sem `MAESTRI_PIPE`, corrigido repassando as variáveis no preset;
- `maestri` fora do PATH;
- BOM UTF-8 em arquivos gravados pelo PowerShell 5.1;
- pedido de confiança de pasta no Antigravity em cada recrutamento novo.
