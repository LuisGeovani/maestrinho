# Fluxos: quem faz cada etapa

Todos participam, mas **ninguém é chamado por chamar**: uma etapa só existe se entrega algo verificável que muda a decisão. Perfis e modelos: `roteamento.md`. Formato dos despachos: `prompts.md`.

## Etapas padrão

| Etapa | Perfil | Entregável | Quando pular |
|---|---|---|---|
| Mapear | Batedor | `.maestri/contexto/<ID>.md`: arquivos envolvidos, contratos, comandos de build/teste, fatos confirmados (até ~40 linhas) | N0; ou quando o despacho já tem os caminhos certos |
| Especificar | Arquiteto | contrato + tabela de casos (entrada → resultado esperado) em `docs/contratos/` ou no contexto | N0–N2 |
| Implementar | Volume ou Crítico | código + validação rodada | — |
| Testar | outra família que o autor | testes que falham antes e passam depois | N0–N2 (o autor valida com comando) |
| Revisar | Revisor (família ≠ autor) | "aprovado" ou até 5 apontamentos com arquivo, trecho e correção | N0; N1 sem lógica nem UI |
| QA visual | QA visual | prints no portal (390×844 e 1280) + lista de problemas | sem UI |
| Consolidar | Batedor | 1 arquivo com o resultado de várias fontes ou terminais | quando há 1 fonte só |
| Integrar | Maestro | conferência de escopo + commit | nunca |

**Passagem de bastão por arquivo:** o Batedor grava o contexto; o autor lê o contexto; o autor grava o relatório; o revisor lê o relatório do autor **pelo caminho** (o Maestro não repassa conteúdo); o Maestro lê só o veredito do revisor.

## Pipelines por tipo de pedido

| Pedido | Etapas (perfil · exemplo de modelo) |
|---|---|
| **Feature N2** | Mapear (Batedor · Haiku) → Implementar (Volume · Hydrogen high) → Revisar (Sonnet medium) → 1 rodada de correção → Integrar |
| **Bug** | Mapear + reproduzir (Batedor) → Corrigir + teste de regressão (Volume, ou Crítico se N3) → Revisar (outra família) |
| **N3 crítico** | Especificar (Arquiteto · Opus no Antigravity) → Testes (família A · Sonnet) → Implementar (família B · Neon high) → Red team se houver risco (família C · GPT, ou outro modelo Claude/Gemini) → Revisar |
| **UI** | Implementar por página ou fluxo (Volume · Hydrogen) → QA visual (Neon) → Revisar código (Claude · Sonnet) |
| **Refatoração ampla** | Mapear → Orchestrator Neon (planeja e executa) ou Crítico → testes existentes rodados pelo Batedor → Revisar (Claude) |
| **Pesquisa** | 2–3 famílias em paralelo, cada uma com fontes ou ângulo próprio, só leitura → Consolidar (Batedor) → o Maestro lê só o consolidado |
| **Decisão N4** | Conselho em paralelo, só leitura (uma voz por família, ângulos diferentes: arquitetura, riscos, alternativa simples/custo) → o Maestro sintetiza consensos, divergências e recomendação → o usuário decide → Batedor registra o ADR com as visões vencidas |
| **Docs ou config N0–N1** | Batedor faz + grep de validação no próprio despacho; sem revisor |
| **Entender o projeto** (sessão nova, código desconhecido) | Batedor gera um resumo de até 40 linhas em `.maestri/contexto/projeto.md`; o Maestro lê só isso |

## Paralelo, dependência e arquivos compartilhados

- **Independente → paralelo**, no mesmo lote. **Dependente → em sequência**, de preferência no mesmo terminal (reaproveita o contexto).
- Antes de frentes paralelas que se tocam (front + back), fixe o contrato (API, tipos, mocks) num arquivo que ninguém muda sem passar pelo dono.
- **Um dono por rodada** para arquivos compartilhados (`package.json`, rotas, tema, configs, migrações). Reserve o número das migrações no cartão.
- Dois produtores precisam editar os mesmos arquivos ao mesmo tempo → use **floors** do Maestri (cada um num worktree): `maestri floor create "Nome" --branch <b>` e `recruit --floor`; o Maestro faz o `floor land` do Ground. No Windows o floor é um checkout simples: peça ao produtor para instalar dependências antes.

## Padrões de colaboração

- **Par autor + revisor (N2+):** o despacho do autor já diz quem revisa; o revisor recebe o caminho do relatório do autor e um checklist (a), (b), (c). No máximo **uma** rodada de correção; depois o Maestro decide.
- **Teste por terceiro (N3):** só com especificação executável. Ordem: interfaces e stubs → testes (falham) → implementação.
- **Red team:** só quando o cartão marca risco (segurança, dinheiro, dado pessoal). Ataca quem não escreveu o código.
- **Conselho (N4):** mesma pergunta para todos, cada um com um ângulo, sem ver as respostas dos outros. Visões próximas (mesma família) pesam como uma.
- **Brief compartilhado:** para uma rodada grande, um Batedor escreve o brief numa nota do Maestri (`maestri note create --name "Brief RNN"`), o usuário pode travá-la (Lock Contents), e os produtores recebem o nome da nota no despacho.
