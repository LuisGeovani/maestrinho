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
| **Feature N2** | Mapear (Batedor · degrau básico pela folga) → Implementar (Volume · Hydrogen high, Sol medium ou Sonnet pela folga) → Revisar (outra família, pela folga entre candidatos que cumprem o mesmo checklist) → 1 rodada de correção → Integrar |
| **Bug** | Mapear + reproduzir (Batedor) → Corrigir + teste de regressão (Volume, ou Crítico se N3) → Revisar (outra família) |
| **N3 crítico** | Especificar (Arquiteto · Neon high/xhigh, Astra high ou Opus pela folga) → Testes (família A com shell · Sol medium/Astra high, ou Sonnet/Haiku se Pro elegível) → Implementar (família B ≠ A · quando os testes forem GPT, implementa outra família como Neon high ou Opus; Astra high só implementa se os testes estiverem com outra família apta e com shell) → Red team se houver risco (terceira família elegível quando possível sem disparar a trava; se estiver retida ou vetada, use a família dos testes ou da especificação, diferente da implementadora; OpenCode grátis não entra em N3) → Revisar |
| **UI** | Implementar por página ou fluxo (Volume de código, pela folga) → QA visual (pela matriz) → Revisar código (outra família, pela matriz) |
| **Refatoração ampla** | Mapear → Orchestrator Neon (planeja e executa) ou Crítico → testes existentes rodados pelo Batedor → Revisar (outra família, pela matriz) |
| **Pergunta de fonte única** | Um terminal elegível com shell (Sol medium, Haiku 5.5 medium ou Sonnet 5.5 medium, conforme a folga). Na mesma tarefa, abre a fonte e entrega a resposta com prova bruta (comando e saída, código HTTP e trecho literal) |
| **Pesquisa ampla** | 2–3 famílias em paralelo, cada uma com fontes ou ângulo próprio, só leitura → Verificar fonte/fato com Sol, Sonnet 5.5 ou Haiku 5.5 em terminal com shell e prova bruta → Consolidar (Batedor) → o Maestro lê só o consolidado |
| **Decisão N4** | Conselho em paralelo, só leitura (Neon xhigh, Astra high e Opus pela ordem Claude da matriz, uma voz por família) → o Maestro sintetiza consensos, divergências e recomendação → o usuário decide → Batedor registra o ADR com as visões vencidas |
| **Docs ou config N0–N1** | Batedor faz + grep de validação no próprio despacho. Doc N1 curto e especificado (README, nota, ajuste de frase) vai ao Batedor de escrita (Terra) ou ao Batedor básico; Volume: texto é para redação longa ou aberta. Em N1 com lógica ou UI, também há revisão cruzada |
| **Entender o projeto** (sessão nova, código desconhecido) | Batedor gera um resumo de até 40 linhas em `.maestri/contexto/projeto.md`; o Maestro lê só isso |

Aplique a matriz de `roteamento.md` para escolher o terminal e a família de cada etapa. Reserve o fluxo com 2–3 famílias para pesquisa ampla ou decisão. Na pesquisa ampla, encaminhe a verificação de fonte/fato conforme a matriz. Prepare binários e execute scripts que o sandbox bloqueia em terminais elegíveis com shell antes de repassar os resultados ao Antigravity. Em tarefas de navegador ou site, siga a ordem CLI/API com shell (`gh`, CLI de deploy) → Portal do Maestri (Gemini ou GPT) → Claude Code `--chrome` apenas para sessão exclusiva no Chrome do usuário.

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
