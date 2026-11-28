# Fluxos: quem faz cada etapa

Todos participam, mas **ninguém é chamado por chamar**: uma etapa só existe se entrega algo verificável que muda a decisão. Árvore de decisão no `SKILL.md`; perfis e modelos em `roteamento.md`. Formato dos despachos: `prompts.md`.

## Etapas padrão

| Etapa | Perfil | Entregável | Quando pular |
|---|---|---|---|
| Mapear | Batedor barato | `.maestri/contexto/<ID>.md`: arquivos envolvidos, contratos, comandos de build/teste, fatos confirmados (até ~40 linhas) | N0; ou quando o despacho já tem os caminhos e fatos confirmados |
| Especificar | Arquiteto (`Neon` / `Sol` / `Sonnet medium`; `high` só sob demanda com raciocínio + contexto amplo) | contrato curto + tabela de casos + quebra em fatias `P`/`M` em `docs/contratos/` ou no contexto | N0–N1; ou quando já há contrato claro (≤ 3 arquivos e ≤ 200 linhas de alteração) |
| Implementar | Volume ou Crítico (em fatias `P`/`M`) | código + validação rodada | — |
| Testar | outra família que o autor | testes que falham antes e passam depois | N0–N2 (o autor valida com comando) |
| Revisar | Revisor (família ≠ autor, em `medium`) | "aprovado" ou até 5 apontamentos com arquivo, trecho, correção e passagem (1ª escopo / 2ª qualidade) | N0; N1 sem lógica nem UI |
| QA visual | QA visual (`Terra` / `Hydrogen` / `Argon` / `Sonnet` / `Neon`, menor par apto) | prints no portal (390×844 e 1280) + lista de problemas | sem UI |
| Consolidar | Batedor | 1 arquivo com o resultado de várias fontes ou terminais | quando há 1 fonte só |
| Integrar | Maestro | conferência de escopo + commit | nunca |

**Teto de tamanho (`roteamento.md` §1):** `Tamanho: P|M|G` mede **o que será alterado** (leitura ampla vai declarada à parte). Qualquer **implementação `G`** (> 3 arquivos ou > ~200 linhas alteradas, ou "implemente a feature X" inteira) **deve ser quebrada** em fatias `P`/`M` com aceite independente: Batedor barato se falta informação → especificação curta se falta contrato → fatias nos pares aptos (`Hydrogen` / `Sol` / `Sonnet medium` / `Luna`) → revisão em `medium`. Proibido mandar implementação grande inteira a um modelo "porque ele dá conta". **`G` de consulta indivisível** (auditoria ou análise que exige visão de conjunto) só é permitido com motivo explícito no despacho.

**Passagem de bastão por arquivo:** o Batedor grava o contexto; o autor lê o contexto; o autor grava o relatório; o revisor lê o relatório do autor **pelo caminho** (o Maestro não repassa conteúdo); o Maestro lê só o veredito do revisor.

## Pipelines por tipo de pedido

| Pedido | Etapas (perfil · candidatos por mérito técnico e escalada sob demanda) |
|---|---|
| **Feature N2** | Levantar/mapear se faltar informação (Batedor barato · `OpenCode grátis` / `Hydrogen low` / `Haiku`) → Especificação curta se faltar contrato ou passar do teto (`Neon`/`Sol`/`Sonnet medium`) → Implementar em fatias `P`/`M` (`Hydrogen medium` / `Sol medium` / `Sonnet 5.5 medium` / `Luna`; lógica difícil sobe no leve em `high`; N2 de risco sobe com avaliação) → Revisar em `medium` (família ≠ autor) → Correção (`<ID>-C1`) → Integrar |
| **Bug** | Mapear + reproduzir (Batedor barato) → Corrigir + teste de regressão (`Hydrogen medium` / `Sol medium` / `Sonnet 5.5 medium`; lógica/depuração difícil sobe para `Hydrogen high` ou `Sol high` antes de subir degrau) → Revisar em `medium` (família ≠ autor) |
| **N3 crítico** | Levantar (Batedor barato) → Especificar (Arquiteto em `medium`; `high`/`xhigh` sob demanda só se exigir raciocínio difícil + contexto amplo) → Testes em fatias (família A com shell) → Implementar em fatias (família B ≠ A · `Hydrogen high` em lógica fechada ou `Neon high` / `Astra` / `Opus` sob demanda justificado) → Red team se houver risco (3ª família elegível em `medium`/`high`; OpenCode grátis não entra em N3) → Revisar (`medium`, ou `high` sob demanda só se risco alto justificar) |
| **UI** | Levantar (Batedor) → Especificação curta se > 3 arquivos alterados ou sem contrato → Implementar em fatias por página/fluxo (`Hydrogen medium` ↔ `Sol medium` ↔ `Sonnet 5.5 medium`; `high` só se lógica de estado difícil) → QA visual (menor par apto; `Neon`/`Sonnet` em QA crítico) → Revisar código em `medium` (família ≠ autor) |
| **Refatoração ampla** | Quebra obrigatória em fatias `P`/`M`: Mapear (Batedor barato) → Especificação curta → Executar fatias (`Orchestrator Neon` em multi-arquivo, ou `Hydrogen`/`Sol`/`Sonnet medium` em fatias — `high` só em fatia de lógica difícil) → testes existentes rodados pelo Batedor → Revisar em `medium` (família ≠ autor) |
| **Pergunta de fonte única** | Menor par apto com shell (`Haiku 5.5 medium`, `Hydrogen medium`, `Sol medium`, `Sonnet 5.5 medium` ou `Neon medium`, pela árvore de decisão). Na mesma tarefa, abre a fonte e entrega a resposta com prova bruta (comando e saída, código HTTP e trecho literal) |
| **Pesquisa ampla** | 2–3 famílias em paralelo, cada uma com fontes ou ângulo próprio, só leitura → Verificar fonte/fato com terminal com shell e prova bruta → Consolidar (Batedor) → o Maestro lê só o consolidado |
| **Decisão N4** | Conselho em paralelo, só leitura (uma voz por família: `Neon`, `Astra` e `Opus 5.5` pela ordem Claude da matriz, em `medium` ou `high` sob demanda conforme avaliação do par em `roteamento.md`; `xhigh` só com ganho real; `Fable` só em escalada extrema) → o Maestro sintetiza consensos, divergências e recomendação → o usuário decide → Batedor registra o ADR com as visões vencidas |
| **Docs ou config N0–N1** | Batedor faz + grep de validação no próprio despacho. Doc N1 curto e especificado (README, nota, ajuste de frase) vai ao Batedor básico ou `Terra low/medium`; Volume: texto é para redação longa ou aberta (`Terra`/`Argon`/`Sol`/`Sonnet medium`). Em N1 com lógica ou UI, também há revisão cruzada em `medium` |
| **Entender o projeto** (sessão nova, código desconhecido) | Batedor gera um resumo de até 40 linhas em `.maestri/contexto/projeto.md`; o Maestro lê só isso |

Aplique a árvore de decisão do `SKILL.md` e a matriz de `roteamento.md` para escolher o terminal e a família de cada etapa (sem família favorita; respeite o teto de tamanho e a separação entre alteração e leitura). Reserve o fluxo com 2–3 famílias para pesquisa ampla ou decisão. Converta binários (`PDF`, `Office`, `zip`) para texto ou imagem antes de mandar ao `read_file` do Antigravity; comandos de shell (`curl`, `python`, PowerShell), URLs e ferramentas MCP funcionam no Antigravity com aprovação do Maestro (`comunicacao.md` §6). Em tarefas de navegador ou site, siga CLI/API com shell (`gh`, CLI de deploy) → Portal do Maestri → Claude Code `--chrome` apenas para sessão exclusiva no Chrome do usuário.

## Paralelo, dependência e arquivos compartilhados

- **Independente → paralelo**, no mesmo lote. **Dependente → em sequência**, de preferência no mesmo terminal (reaproveita o contexto).
- Antes de frentes paralelas que se tocam (front + back), fixe o contrato (API, tipos, mocks) num arquivo que ninguém muda sem passar pelo dono.
- **Um dono por rodada** para arquivos compartilhados (`package.json`, rotas, tema, configs, migrações). Reserve o número das migrações no cartão.
- Dois produtores precisam editar os mesmos arquivos ao mesmo tempo → use **floors** do Maestri (cada um num worktree): `maestri floor create "Nome" --branch <b>` e `recruit --floor`; o Maestro faz o `floor land` do Ground. No Windows o floor é um checkout simples: peça ao produtor para instalar dependências antes.

## Padrões de colaboração

- **Par autor + revisor (N2+):** o despacho do autor já diz quem revisa; o revisor recebe o caminho do relatório do autor e um checklist em **2 passagens** pelo mesmo revisor: **1ª passagem — aderência à especificação** (cada requisito → evidência; faltou ou inventou algo?), **2ª passagem — qualidade do código** (só depois da 1ª). O relatório diz qual passagem (`[P1]` ou `[P2]`) achou cada problema. O mesmo defeito **mantém o ID** nas correções (`<ID>-C1`, `-C2` — nunca troque o ID para reiniciar a contagem).
- **Verificação pós-correção (N2+ de risco alto):** depois do `<ID>-C1`, o revisor original faz uma verificação curta (`<ID>-V1`, só leitura): "cada apontamento aceito foi resolvido? sobrou ou nasceu algo?". Devolve aprovado ou só o que restou. É nessa verificação que o Maestro decide entre aceitar, adiar como pendência para o usuário ou abrir nova correção (`<ID>-C2`) com motivo de risco explícito. Em risco baixo, a conferência do Maestro por `git diff --stat` basta.
- **Teste por terceiro (N3):** só com especificação executável. Ordem: interfaces e stubs → testes (falham) → implementação.
- **Red team:** só quando o cartão marca risco (segurança, dinheiro, dado pessoal). Ataca quem não escreveu o código.
- **Conselho (N4):** mesma pergunta para todos, cada um com um ângulo, sem ver as respostas dos outros. Visões próximas (mesma família) pesam como uma.
- **Brief compartilhado:** para uma rodada grande, um Batedor escreve o brief numa nota do Maestri (`maestri note create --name "Brief RNN"`), o usuário pode travá-la (Lock Contents), e os produtores recebem o nome da nota no despacho.
