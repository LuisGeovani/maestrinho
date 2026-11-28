# Fluxos: quem faz cada etapa

Todos participam, mas **ninguém é chamado por chamar**: uma etapa só existe se entrega algo verificável que muda a decisão. Perfis e modelos: `roteamento.md`. Formato dos despachos: `prompts.md`.

## Etapas padrão

| Etapa | Perfil | Entregável | Quando pular |
|---|---|---|---|
| Mapear | Batedor barato | `.maestri/contexto/<ID>.md`: arquivos envolvidos, contratos, comandos de build/teste, fatos confirmados (até ~40 linhas) | N0; ou quando o despacho já tem os caminhos certos |
| Especificar | Arquiteto (`Neon medium`; `high` só sob demanda com raciocínio + contexto amplo) | contrato curto + tabela de casos + quebra em fatias `P`/`M` em `docs/contratos/` ou no contexto | N0–N1; ou N2 pequeno (≤ 3 arquivos e ≤ 200 linhas) |
| Implementar | Volume ou Crítico (em fatias `P`/`M`) | código + validação rodada | — |
| Testar | outra família que o autor | testes que falham antes e passam depois | N0–N2 (o autor valida com comando) |
| Revisar | Revisor (família ≠ autor, `medium` por padrão) | "aprovado" ou até 5 apontamentos com arquivo, trecho e correção | N0; N1 sem lógica nem UI |
| QA visual | QA visual (`Hydrogen medium/high` — barato) | prints no portal (390×844 e 1280) + lista de problemas | sem UI |
| Consolidar | Batedor | 1 arquivo com o resultado de várias fontes ou terminais | quando há 1 fonte só |
| Integrar | Maestro | conferência de escopo + commit | nunca |

**Teto de tamanho (quebra obrigatória, `roteamento.md` §1):** qualquer pedido com **> ~3 arquivos**, **> ~200 linhas** ou **"implemente a feature X" inteira** (`Tamanho: G`) **deve** seguir a sequência: **(1) Batedor barato levanta/resume → (2) especificação curta (`Neon medium`) → (3) fatias `P`/`M` em `Hydrogen medium` / `Sol medium` / `Luna` → (4) revisão em `medium`**. Proibido mandar pedido grande inteiro a um modelo "porque ele dá conta".

**Passagem de bastão por arquivo:** o Batedor grava o contexto; o autor lê o contexto; o autor grava o relatório; o revisor lê o relatório do autor **pelo caminho** (o Maestro não repassa conteúdo); o Maestro lê só o veredito do revisor.

## Pipelines por tipo de pedido

| Pedido | Etapas (perfil · par inicial mais barato e escalada sob demanda) |
|---|---|
| **Feature N2** | Levantar/mapear (Batedor barato · `OpenCode grátis` / `Hydrogen low`) → Especificação curta se passar do teto (`Neon medium`) → Implementar em fatias `P`/`M` (`Hydrogen medium` / `Sol medium` / `Luna`; `Hydrogen high` sob demanda só se lógica difícil; `Neon medium/high` sob demanda só em N2 de risco com avaliação) → Revisar em `medium` (outra família, ou outro Gemini se outros pools apertarem) → 1 rodada de correção → Integrar |
| **Bug** | Mapear + reproduzir (Batedor barato) → Corrigir + teste de regressão (`Hydrogen medium` / `Sol medium`; lógica/depuração difícil sobe para `Hydrogen high` sob demanda ou `Sol medium/high` antes de `Neon medium/high` sob demanda com avaliação) → Revisar em `medium` (outra família) |
| **N3 crítico** | Levantar (Batedor barato) → Especificar (Arquiteto · `Neon medium`; `Neon high/xhigh` sob demanda só se exigir raciocínio difícil + contexto amplo) → Testes em fatias (família A com shell · `Sol medium`, ou `Haiku`/`Sonnet medium` se Pro elegível; `Astra medium/high` só sob demanda com avaliação) → Implementar em fatias (família B ≠ A · `Hydrogen high` em lógica fechada ou `Neon high` sob demanda justificado; `Astra`/`Opus` só sob demanda com avaliação se outra família apta cobrir testes) → Red team se houver risco (3ª família elegível em `medium`/`high` conforme avaliação; OpenCode grátis não entra em N3) → Revisar (`medium`, ou `high` sob demanda só se risco alto justificar) |
| **UI** | Levantar (Batedor) → Especificação curta se > ~3 arquivos (`Neon medium`) → Implementar em fatias por página/fluxo (`Hydrogen medium`; `Hydrogen high` só se lógica de estado difícil; `Sol`/`Sonnet medium` se Gemini apertar) → QA visual (`Hydrogen medium/high` — barato; `Neon medium/high` só em QA crítico com avaliação) → Revisar código em `medium` (outra família) |
| **Refatoração ampla** | Quebra obrigatória em fatias `P`/`M`: Mapear (Batedor barato) → Especificação curta (`Neon medium`) → Executar fatias (`Orchestrator Neon` em multi-arquivo, ou `Hydrogen medium` em fatias — `high` só em fatia de lógica difícil) → testes existentes rodados pelo Batedor → Revisar em `medium` (outra família) |
| **Pergunta de fonte única** | Um terminal elegível com shell no par mais barato (`Hydrogen medium`, `Haiku 5.5 medium` se Pro liberado, `Sol medium`, `Neon medium` ou `Sonnet 5.5 medium`; Gemini por padrão). Na mesma tarefa, abre a fonte e entrega a resposta com prova bruta (comando e saída, código HTTP e trecho literal) |
| **Pesquisa ampla** | 2–3 famílias em paralelo, cada uma com fontes ou ângulo próprio, só leitura → Verificar fonte/fato com Hydrogen, Haiku 5.5, Sol, Neon ou Sonnet 5.5 em terminal com shell e prova bruta → Consolidar (Batedor) → o Maestro lê só o consolidado |
| **Decisão N4** | Conselho em paralelo, só leitura (uma voz por família: `Neon`, `Astra` e `Opus 5.5` pela ordem Claude da matriz, em `medium` ou `high` sob demanda conforme avaliação do par em `roteamento.md`; `xhigh` só com ganho real; `Fable` só em escalada extrema) → o Maestro sintetiza consensos, divergências e recomendação → o usuário decide → Batedor registra o ADR com as visões vencidas |
| **Docs ou config N0–N1** | Batedor faz + grep de validação no próprio despacho. Doc N1 curto e especificado (README, nota, ajuste de frase) vai ao Batedor básico ou `Terra low/medium`; Volume: texto é para redação longa ou aberta (`Argon medium`). Em N1 com lógica ou UI, também há revisão cruzada em `medium` |
| **Entender o projeto** (sessão nova, código desconhecido) | Batedor gera um resumo de até 40 linhas em `.maestri/contexto/projeto.md`; o Maestro lê só isso |

Aplique a matriz e a avaliação do par modelo × effort de `roteamento.md` para escolher o terminal e a família de cada etapa (Gemini por padrão; comece pelo par mais barato provável e respeite o teto de tamanho). Reserve o fluxo com 2–3 famílias para pesquisa ampla ou decisão. Na pesquisa ampla, encaminhe a verificação de fonte/fato conforme a matriz. Converta binários (`PDF`, `Office`, `zip`) para texto ou imagem antes de mandar ao `read_file` do Antigravity; já comandos de shell (`curl`, `python`, PowerShell), URLs e ferramentas MCP funcionam no Antigravity com aprovação do Maestro (`comunicacao.md` §6). Em tarefas de navegador ou site, siga a ordem CLI/API com shell (`gh`, CLI de deploy) → Portal do Maestri (Gemini ou GPT) → Claude Code `--chrome` apenas para sessão exclusiva no Chrome do usuário.

## Paralelo, dependência e arquivos compartilhados

- **Independente → paralelo**, no mesmo lote. **Dependente → em sequência**, de preferência no mesmo terminal (reaproveita o contexto).
- Antes de frentes paralelas que se tocam (front + back), fixe o contrato (API, tipos, mocks) num arquivo que ninguém muda sem passar pelo dono.
- **Um dono por rodada** para arquivos compartilhados (`package.json`, rotas, tema, configs, migrações). Reserve o número das migrações no cartão.
- Dois produtores precisam editar os mesmos arquivos ao mesmo tempo → use **floors** do Maestri (cada um num worktree): `maestri floor create "Nome" --branch <b>` e `recruit --floor`; o Maestro faz o `floor land` do Ground. No Windows o floor é um checkout simples: peça ao produtor para instalar dependências antes.

## Padrões de colaboração

- **Par autor + revisor (N2+):** o despacho do autor já diz quem revisa; o revisor recebe o caminho do relatório do autor e um checklist (a), (b), (c). No máximo **uma** rodada de correção; depois o Maestro decide.
- **Verificação pós-correção (N2+ de risco alto):** depois do `<ID>-C1`, o revisor original faz uma verificação curta (`<ID>-V1`, só leitura): "cada apontamento aceito foi resolvido? sobrou ou nasceu algo?". Devolve aprovado ou só o que restou, e o Maestro decide. Não é segunda rodada de correção: se sobrar algo, o Maestro decide (aceita, ajusta ou pendência para o usuário). Em risco baixo, a conferência do Maestro por `git diff --stat` basta.
- **Teste por terceiro (N3):** só com especificação executável. Ordem: interfaces e stubs → testes (falham) → implementação.
- **Red team:** só quando o cartão marca risco (segurança, dinheiro, dado pessoal). Ataca quem não escreveu o código.
- **Conselho (N4):** mesma pergunta para todos, cada um com um ângulo, sem ver as respostas dos outros. Visões próximas (mesma família) pesam como uma.
- **Brief compartilhado:** para uma rodada grande, um Batedor escreve o brief numa nota do Maestri (`maestri note create --name "Brief RNN"`), o usuário pode travá-la (Lock Contents), e os produtores recebem o nome da nota no despacho.
