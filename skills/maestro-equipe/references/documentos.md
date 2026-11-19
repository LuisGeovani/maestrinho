# Modelos de documentos e notas

## Formação (`.maestri/equipe.md`; o Maestro escreve ao recrutar e relê em toda sessão)

O `maestri list` não mostra o modelo, e no Claude Code o modelo só aparece no banner do topo, que some depois que o terminal trabalha. Por isso a formação fica anotada:

```
| Terminal | Ferramenta | Modelo · effort | Família | Perfis | Comando/preset |
|---|---|---|---|---|---|
| Brasa | Claude Code | Haiku 5.5 · medium | Claude | Batedor | preset "Haiku" |
| Neblina | Antigravity | Gemini 4 Hydrogen · high | Gemini | Volume | preset "Agy Hydrogen" |
| Musgo | OpenCode | deepseek-v4.1-flash-free | aberto | Batedor (não sensível) | preset "OpenCode Gratis" |
```

Atualize a linha a cada `recruit --replace` ou troca de modelo.

## Quadro da rodada (nota do Maestri, fichário "Rodadas"; só o Maestro escreve)

```
QUADRO Rodada NN (só o Maestro escreve aqui)
Legenda: N0-N4 | status: a fazer > fazendo > revisão > aprovado | revisor sempre de outra família
Cota no início: <saída curta do cotas.py>

[RNN-T1] N? · <título>
  Autor: <terminal> (<modelo, effort>) · Revisor: <terminal> (<família>) · Testes: <terminal ou —>
  Pastas: <pastas> · Migração reservada: <V? ou —> · Risco: <segurança/dinheiro/dado pessoal ou —>
  Status: a fazer · Relatório: .maestri/relatorios/RNN-T1.md
  Pronto quando: <critério verificável>
```

## Rodada (`docs/rodadas/RNN.md`, escrita por um Batedor a mando do Maestro)

```markdown
# Rodada NN — <objetivo em uma linha>

**Cota no início:** <cotas.py resumido>
**Donos de arquivos compartilhados:** `package.json` → <terminal> · rotas → <terminal> · tema → <terminal> · `docs/contratos/` → <terminal>
**Migrações reservadas:** V<n> → RNN-T<x>

## Tarefas

### RNN-T1 · N<0-4> · <título>
- **Autor:** <terminal> · **Modelo e effort:** <ex.: Hydrogen high> · **Revisor:** <outra família> · **Testes:** <terminal ou —>
- **Pastas permitidas:** <pastas> · **Floor:** <nome ou —> · **Risco:** <—>
- **Fazer:** <descrição>
- **Pronto quando:** <critério verificável; UI inclui portal em 390x844 e 1280>

## Conselho (só em N4)
Pergunta, visões por família, síntese do Maestro, decisão do usuário (vira ADR).

## Resultado
Status de cada tarefa, ajustes, VISÃO registrada, commits.
```

## Relatório do produtor (`.maestri/relatorios/<ID>.md`)

```
TAREFA: <ID>
STATUS: pronto | parcial | bloqueado
ARQUIVOS: <criados ou alterados>
VALIDAÇÃO: <comandos rodados e resultado>
PENDÊNCIAS: <o que ficou de fora ou precisa de decisão>
VISÃO: <opcional: discordância ou risco real>
```

## Contexto do Batedor (`.maestri/contexto/<ID>.md`, até ~40 linhas)

```
CONTEXTO <ID>
Arquivos envolvidos: <caminho: papel em 1 linha>
Contratos e tipos: <onde estão>
Comandos: build <...> · teste <...> · lint <...>
Fatos confirmados: <...>
Riscos e dúvidas: <...>
```

## `docs/contratos/README.md`

```markdown
# Contratos
Fixados antes de trabalho em paralelo; ninguém muda sem passar pelo dono da rodada.
- API: rotas, métodos, DTOs, códigos de erro (`<recurso>.md` ou `openapi.yaml`).
- Tipos do front (`*.ts`) e mocks (`*.mock.json`).
- Tabela de casos (N3): entrada → resultado esperado, base dos testes de terceiro.
```

## Linhas para os docs de agentes do projeto

`AGENTS.md` (todos os produtores leem):
```
- Não faça commit, push nem troca de branch; o git é do Maestro.
- Cada tarefa vem com ID, nível (N0–N4) e escopo; quem revisa é de outra família de modelo.
- Ao terminar, grave o relatório em .maestri/relatorios/<ID>.md e avise o Maestro com o comando curto do despacho.
- Arquivos compartilhados têm um dono por rodada: não edite os que não são seus.
```

`CLAUDE.md` (lido pelo Maestro e pelos produtores Claude):
```
- O Maestro só coordena (skill maestro-equipe): não edita arquivos do projeto, não lê código, não pesquisa, não roda build ou teste e não usa subagentes internos; todo trabalho vai para os terminais do Maestri.
- Commits só no nome do usuário: sem Co-Authored-By e sem rodapé de PR.
```

`.gitignore`: inclua `.maestri/` (papéis gerados, despachos, relatórios, contexto).
