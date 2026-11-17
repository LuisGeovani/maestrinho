# Modelos de documentos e notas

## Quadro (nota do Maestri, fichário "Rodadas"; só o Maestro escreve)

```
QUADRO Rodada NN (só o Maestro escreve aqui)
Legenda: nível N0-N4 | status: a fazer > fazendo > revisão > aprovado | revisor sempre de outra família

[RNN-T1] N? · <título>
  Autor: <produtor> · Revisor: <produtor> · Testes: <produtor ou —>
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
- **Autor:** <produtor> · **Revisor:** <outra família> · **Testes:** <produtor ou —>
- **Pastas permitidas:** <pastas> · **Worktree:** <.worktrees/rNN-t1 ou —>
- **Risco:** <segurança / dinheiro / dado pessoal / —>
- **Fazer:** <descrição>
- **Pronto quando:** <critério verificável; front inclui portal em 390x844 e 1280>

## Conselho (só em N4)
Pergunta, visões, síntese do Maestro, decisão do usuário (vira ADR).

## Resultado
_(Maestro preenche: status de cada tarefa, ajustes, VISÃO registrada, commits.)_
```

## Despacho de tarefa (texto do prompt)

```
Rodada NN, tarefa RNN-Tx, nível N?. O projeto fica em <RAIZ> (trabalhe lá, não na pasta .maestri).
Leia <arquivo da rodada> (seção RNN-Tx) e execute só ela. Pastas permitidas: <pastas>.
Revisor: <nome>. Valide com <comando>. Ao terminar, reporte com maestri ask "Maestro" no formato de <DOCS>EQUIPE.md.
```

Consulta (Conselho ou crítica):

```
Consulta, SOMENTE LEITURA (não crie nem altere arquivos). <contexto curto>. <pergunta e ângulo esperado>.
Máximo N linhas. Responda com maestri ask "Maestro" "<resposta>" (fora do sandbox se der access denied).
```

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
- O Maestro segue a skill maestro-equipe e o MAESTRO.md do projeto. Integre os terminais do Maestri quando ajudam de verdade, sem chamar só por chamar.
- Commits só no nome do usuário: sem Co-Authored-By e sem rodapé de PR.
- Tarefas têm nível N0–N4 e o revisor é sempre de outra família de modelo.
```
