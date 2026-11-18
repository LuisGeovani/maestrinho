# Modelos de documentos e notas

## Quadro (nota do Maestri, fichário "Rodadas"; só o Maestro escreve)

```
QUADRO Rodada NN (só o Maestro escreve aqui)
Legenda: nível N0-N4 | status: a fazer > fazendo > revisão > aprovado | revisor sempre de outra família

[RNN-T1] N? · <título>
  Autor: <produtor> · Modelo/raciocínio: <ex.: Sonnet 5.5 medium> · Revisor: <produtor> · Testes: <produtor ou —>
  Pastas: <pastas> · Migração reservada: <V? ou —> · Risco: <segurança/dinheiro/dado pessoal ou —>
  Status: a fazer
  Pronto quando: <critério verificável>
  Notas: <decisões, VISÃO dos produtores>
```

## Rodada (`docs/rodadas/RNN.md`)

```markdown
# Rodada NN — <objetivo em uma linha>

**Cota no início:** Claude Pro <x%> · Gemini <x%> · Claude/GPT (Antigravity) <x%> · Codex <x%>
**Donos de arquivos compartilhados nesta rodada:** `pom.xml` → <produtor> · `application.yml` → <produtor> · `package.json` → <produtor> · rotas → <produtor> · tema → <produtor> · `docs/contratos/` → <produtor>
**Migrações reservadas:** V<n> → RNN-T<x>

## Tarefas

### RNN-T1 · N<0-4> · <título>
- **Autor:** <produtor> · **Modelo e raciocínio:** <ex.: Haiku 5.5 medium> · **Revisor:** <outra família> · **Testes:** <produtor ou —>
- **Pastas permitidas:** <pastas> · **Worktree:** <.worktrees/rNN-t1 ou —>
- **Risco:** <segurança / dinheiro / dado pessoal / —>
- **Fazer:** <descrição>
- **Pronto quando:** <critério verificável; front inclui portal em 390x844 e 1280>

## Conselho (só em N4)
Pergunta, visões, síntese do Maestro, decisão do usuário (vira ADR).

## Resultado
_(Faísca preenche a mando do Maestro: status de cada tarefa, ajustes, VISÃO registrada, commits.)_
```

## Despacho de tarefa e consulta

Os modelos de prompt por família (Gemini em XML, Claude, Codex/GPT), de consulta somente leitura e de revisão estão em `prompts.md`. Todo despacho traz o modelo e o raciocínio esperados.

## Relatório do produtor

```
TAREFA: <id>
STATUS: pronto | parcial | bloqueado
ARQUIVOS: <lista curta>
VALIDAÇÃO: <comando rodado e resultado em 1 linha>
PENDÊNCIAS: <o que ficou de fora ou precisa de decisão>
VISÃO: <opcional: discordância ou risco real>
```

## `docs/contratos/README.md`

```markdown
# Contratos
Fixados antes de trabalho em paralelo; ninguém muda sem passar pelo dono da rodada.
- API: rotas, métodos, DTOs, códigos de erro (`<recurso>.md` ou `openapi.yaml`).
- TypeScript: interfaces do front (`*.ts`).
- Mocks: respostas de exemplo (`*.mock.json`).
- Tabela de casos (N3): entrada → resultado esperado, base para os testes de terceiro.
```

## Linhas para `AGENTS.md` e `CLAUDE.md` do projeto

AGENTS.md:
```
- Não faça commit, push nem troca de branch; o git é do Maestro.
- Cada tarefa vem com nível (N0–N4), autor e revisor. Quem revisa é sempre de outra família de modelo. Arquivos compartilhados têm um dono por rodada: não edite os que não são seus.
```

CLAUDE.md:
```
- O Maestro só coordena: não edita arquivos, não lê código, não pesquisa, não roda build ou teste e não usa subagentes internos; todo trabalho vai para os terminais do Maestri.
- O Maestro segue a skill maestro-equipe e o MAESTRO.md do projeto: ele comanda (planeja, roteia, despacha, decide, git) e não executa as tarefas. Escolhe o modelo e o raciocínio mais baratos que resolvem e os escreve em cada despacho. Só o Maestro usa Opus no Claude Code; os outros terminais usam Sonnet 5.5 e Haiku 5.5.
- Commits só no nome do usuário: sem Co-Authored-By e sem rodapé de PR.
- Tarefas têm nível N0–N4 e o revisor é sempre de outra família de modelo.
```
