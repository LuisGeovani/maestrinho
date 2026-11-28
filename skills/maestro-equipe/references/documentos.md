# Modelos de documentos e notas

## Formação (`.maestri/equipe.md`; o Maestro escreve ao recrutar e relê em toda sessão)

O `maestri list` não mostra o modelo, e no Claude Code o modelo só aparece no banner do topo, que some depois que o terminal trabalha. Por isso a formação fica anotada:

```
| Terminal | Ferramenta | Modelo · effort | Peso do par | Família | Perfis | Comando/preset |
|---|---|---|---|---|---|---|
| Brasa | Claude Code | Haiku 5.5 · medium | 2 | Claude | Batedor | preset "Haiku" |
| Faísca | Antigravity | Gemini 4 Hydrogen · low | 15 | Gemini | Batedor | preset "Agy Hydrogen Low" |
| Neblina | Antigravity | Gemini 4 Hydrogen · medium | 30 | Gemini | Volume / Fatias / UI | preset "Agy Hydrogen" |
| Prisma | Antigravity | Gemini 4 Neon · medium | 60 | Gemini | Spec / Julgamento / MCP | preset "Agy Neon" |
| Musgo | OpenCode | deepseek-v4.1-flash-free | 0 | aberto | Batedor (não sensível) | preset "OpenCode Gratis" |
```

`Peso do par` = `peso do modelo × multiplicador de effort` (valores `[incerto]` em `modelos.md`; **pesado** = Neon, Opus, Astra, Fable; **leve** = Hydrogen, Argon, Sol, Sonnet, Terra, Luna, Haiku, Flash, OpenCode). Atualize a linha a cada `recruit --replace` ou troca de modelo; `Hydrogen high` (leve, barato) e terminais pesados em `high` entram sob demanda e voltam ao par base ao terminar.

## Quadro da rodada (nota do Maestri, fichário "Rodadas"; só o Maestro escreve)

```
QUADRO Rodada NN (só o Maestro escreve aqui)
Legenda: N0-N4 | status: a fazer > fazendo > revisão > aprovado | revisor sempre de outra família
Cota no início: <saída curta do cotas.py>

[RNN-T1] N? · <título>
  Autor: <terminal> (<modelo, effort>) · Tamanho: <P|M> (G = quebrar) · Custo: <n> · Revisor: <terminal> (<família>) · Testes: <terminal ou —>
  Pastas: <pastas> · Migração reservada: <V? ou —> · Risco: <segurança/dinheiro/dado pessoal ou —>
  Status: a fazer · Relatório: .maestri/relatorios/RNN-T1.md
  Pronto quando: <critério verificável>
```

## Despacho (`.maestri/despachos/<rodada>.md`, molde PACIF — `prompts.md` §0)

```markdown
### <Terminal> | <ID>
Tamanho: <P|M|G> (G só com linha `Indivisível: <motivo>` em consulta/auditoria indivisível; G de implementação: quebrar)
Leitura ampla: <opcional — quando lê muito mas altera pouco>
Roteamento: <modelo> <effort> | custo <n> | <mínimo apto | descartado: <par mais barato> porque <motivo>>

Papel e limites: <perfil>, N<0-4>, <EDIÇÃO | SOMENTE LEITURA>. Raiz: <RAIZ> (branch <b>). Leitura: <arquivos/pastas>. Escrita: <arquivos/pastas | só o relatório>. Permissões: <por operação, ex.: git só diff; rodar suíte>.
Ação: <verbo + entrega concreta>.
Contexto: <insumos acessíveis, fatos confirmados, decisões anteriores>.
Intenção: <quem usa a entrega e qual decisão toma>.
Formato: <esquema, limite de linhas; em revisão: VEREDITO e orçamento de achados>.
Aceite e prova: <critério → resultado esperado → prova bruta>. Se faltar <insumo>, <plano B>.
```

## Rodada (`docs/rodadas/RNN.md`, escrita por um Batedor a mando do Maestro)

```markdown
# Rodada NN — <objetivo em uma linha>

**Cota no início:** <cotas.py resumido>
**Donos de arquivos compartilhados:** `package.json` → <terminal> · rotas → <terminal> · tema → <terminal> · `docs/contratos/` → <terminal>
**Migrações reservadas:** V<n> → RNN-T<x>

## Tarefas

### RNN-T1 · N<0-4> · <título>
- **Autor:** <terminal> · **Tamanho:** <P|M|G> (G só com linha `Indivisível: <motivo>` em consulta/auditoria indivisível; G de implementação: quebrar; leitura ampla à parte) · **Roteamento:** `<modelo> <effort> | custo <n> | <mínimo apto | descartado: <par mais barato> porque <motivo>>` · **Revisor:** <outra família> · **Testes:** <terminal ou —>
- **Leitura:** <arquivos/pastas> · **Escrita:** <arquivos/pastas> · **Permissões:** <por operação> · **Floor:** <nome ou —> · **Risco:** <—>
- **Ação e intenção:** <entrega concreta e decisão que destrava>
- **Aceite e prova:** <critério verificável + evidência; UI inclui portal em 390x844 e 1280>

## Conselho (só em N4)
Pergunta, visões por família, síntese do Maestro, decisão do usuário (vira ADR).

## Resultado
Status de cada tarefa, ajustes, VISÃO registrada, commits.
- **Aceite de primeira (por nível N0–N4):** `Aceite de primeira: X/Y tarefas aprovadas na 1ª revisão; custo estimado total (inclui correções) por tarefa aceita` (separado por nível; listar pendentes à parte).
```

## Relatório do produtor (`.maestri/relatorios/<ID>.md`)

```
TAREFA: <ID>
STATUS: pronto | parcial | bloqueado
VEREDITO: aprovado | aprovado com ajustes | reprovado (só em revisão)
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

## Pacote de retomada (`.maestri/contexto/<ID>-retomada.md`, ≤ 15 linhas)

Regra: o Maestro gera o pacote ao trocar/reiniciar terminal ou ao continuar um parcial; o produtor novo lê só o pacote e os arquivos citados.

```
RETOMADA <ID>
Despacho de origem: .maestri/despachos/<rodada>.md (<ID>)
Última etapa confirmada: <etapa> · Evidência: <comando/saída ou relatório>
Arquivos tocados: <caminho: alteração em 1 linha>
Pendência: <o que falta>
Próximo passo autorizado: <ação/comando permitido e escopo>
```

## Lições por recorrência (`.maestri/contexto/licoes.md`)

Quando o mesmo erro aparecer em 2 tarefas, registre em 1 linha cada (gatilho, correção e IDs); o despacho cita **só a lição aplicável**.

```markdown
- [Gatilho: papel exige leitura obrigatória de AGENTS.md] → Correção: marcar AGENTS.md/CLAUDE.md/GEMINI.md como opcionais no papel para não bloquear produtores (IDs: sessão atual).
- [Gatilho: rodapé do despacho contradiz o corpo sobre escrita/entrega] → Correção: validar coerência entre corpo e rodapé antes do envio (IDs: MKT-T3).
- [Gatilho: despacho pede ao revisor prova que só o Maestro pode coletar] → Correção: o Maestro coleta e fornece o insumo no despacho antes da revisão (IDs: sessão atual).
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
