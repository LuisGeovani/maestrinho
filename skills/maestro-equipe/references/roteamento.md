# Roteamento: tarefa → perfil → terminal, modelo e effort → cota

Objetivo: cada tarefa no modelo **mais barato que resolve**, com o effort certo, no pool com folga, e com famílias diferentes se conferindo. Catálogo dos modelos: `modelos.md`. Fluxos por tipo de pedido: `fluxos.md`.

## 1. Classifique a tarefa (4 perguntas)

1. **Tipo:** código back · front/UI · infra/config · testes · docs · pesquisa · revisão · QA visual · decisão.
2. **Nível:**

| Nível | Exemplos | Revisão |
|---|---|---|
| N0 trivial | typo, renomear, config de uma linha, rodar um comando | validação por comando no próprio despacho (grep, build); sem revisor |
| N1 simples | README, fixture, script pequeno, componente simples | validação por comando; revisor de outra família só se tocar lógica ou UI |
| N2 médio | tela, endpoint CRUD, migração simples, refatoração local | revisor de outra família (+ QA visual se for UI) |
| N3 complexo | concorrência, idempotência, segurança, dinheiro, dados pessoais, consulta pesada, refatoração ampla | especificação executável + testes por uma família, implementação por outra, revisão (+ red team se houver risco) |
| N4 crítico | stack, modelo de dados, arquitetura, custo | Conselho (uma voz por família, só leitura) → o usuário decide → ADR |

3. **Risco:** segurança, dinheiro, dado pessoal → sobe um nível e pede red team em N3.
4. **Tamanho e dependência:** quantos arquivos? Depende de outra tarefa? **Cadeia dependente fica no mesmo terminal**; só tarefas independentes vão em paralelo para terminais diferentes (multi-agente custa ~15x os tokens de um chat e só compensa em trabalho independente).

## 2. Escolha o perfil e o modelo

A equipe é montada com o que o inventário achar (`scripts/inventario.py`). Cada terminal cobre um ou mais perfis. Use a 1ª opção disponível; desça para a próxima se ela não existir ou se a cota dela estiver acima de 80%.

| Perfil | Para quê | 1ª escolha → alternativas |
|---|---|---|
| **Batedor** | mapear arquivos e estado, resumir código para o Maestro, busca, inventário, rodar testes/lint/build, docs curtas, N0, consolidar pesquisas | Haiku 5.5 medium → OpenCode grátis (`deepseek-v4.1-flash-free`) → GPT Luna high → Hydrogen low |
| **Volume** | código N1–N2 bem especificado, UI em lotes por página ou fluxo, escrever testes, pesquisa web | Hydrogen high → Sonnet 5.5 medium no Antigravity → Sonnet 5.5 medium no Claude Code → GPT 6.2 Sol medium |
| **Volume de cuidado** | tarefa longa, redação ou engenharia que pede mais cuidado que o Hydrogen; segunda voz Gemini quando o Neon está ocupado ou o pool Gemini principal está apertado (Argon tem teto semanal próprio) | Argon medium (high se difícil) → Sonnet 5.5 medium no Antigravity → Neon medium → Hydrogen xhigh |
| **Crítico** | N3: concorrência, banco, segurança, lógica de dinheiro, refatoração grande | Neon high (Orchestrator Neon se for multi-arquivo) → Argon high `[incerto]` → Opus 5.5 high no Antigravity → Sonnet 5.5 high no Antigravity → Sonnet 5.5 high no Claude Code → GPT 6.2 Astra high |
| **Arquiteto** | N4, especificação executável, contratos, ADR, desempate | Conselho com uma voz por família: Neon xhigh + Opus 5.5 high (Antigravity) + GPT 6.2 Astra high (se houver) + Fable 5.2 high (se o plano tiver) |
| **Revisor** | revisão de diff N2+, sempre de família **diferente** do autor | autor Gemini → Sonnet 5.5 (medium; high em N3) ou Opus no Antigravity → os mesmos no Claude Code → GPT 6.2 Sol; autor Claude → Neon high → Argon high `[incerto]`; autor GPT ou aberto → Neon ou Sonnet (Antigravity) |
| **QA visual** | conferir UI pelo portal (390×844 e 1280), prints, PDFs, gráficos | Neon high → Sonnet 5.5 medium no Antigravity (olho de design) → Sonnet 5.5 medium no Claude Code |

Regras de ouro do roteamento:
- **Nível alto nunca em modelo leve.** Batedor não faz lógica N2+.
- **Famílias diferentes se conferem:** autor ≠ revisor em N2+; em N3, testes por uma terceira família quando houver. Dois terminais do mesmo modelo são dois votos iguais, não duas visões.
- **Tríplices por família** (`modelos.md`): Claude Haiku → Sonnet → Opus; Gemini Hydrogen → Argon → Neon. Cada degrau tem seu custo e sua cota: leve para volume e checagem, médio para produção cuidadosa, forte para N3/N4 e revisão.
- **Volume vai para o pool abundante:** Hydrogen e OpenCode grátis antes de gastar Claude Pro ou Codex.
- **Claude nos produtores: PRIMEIRO o Antigravity, SÓ DEPOIS o Claude Code.** Sonnet e Opus rodam nos presets Agy Sonnet / Agy Opus (pool "Claude and GPT"); o Claude Code (cota Pro dividida com o Maestro) é reserva. Exceções: pool Claude do Antigravity esgotado (`cotas.py` com 5h ou semanal ≥ 100%) ou tarefa que precisa de algo que só o Claude Code faz fora do sandbox do Antigravity (rede local/SSH sem autorização, git/gh, escrita fora do workspace); nesses casos use Claude Code e volte ao Antigravity quando a cota voltar. Haiku segue como está.
- **GPT entra quando há cota.** No plano Free, só Luna para checagens curtas; com Plus, Sol revisa e Astra opina em N4.
- **Dado sensível** (código fechado de cliente, segredos, dados pessoais) nunca vai para modelo grátis que treina com os dados (Big Pickle, Iceman, Flint, Inkling).

## 3. Escolha o effort

| Nível | Claude | Gemini | GPT | OpenCode |
|---|---|---|---|---|
| N0 | Haiku low | Hydrogen low | Luna medium | grátis |
| N1 | Haiku medium; Sonnet low | Hydrogen medium | Luna high; Sol low | grátis |
| N2 | Sonnet medium | Hydrogen high; Argon medium; Neon medium | Sol medium | pago, se houver |
| N3 | Sonnet high; Opus high | Neon high; Argon high `[incerto]` | Sol high; Astra high | — |
| N4 | Opus high; Fable high | Neon xhigh | Astra high/xhigh | — |

- Escreva **sempre** o modelo e o effort esperados no cartão e na 1ª linha do despacho: os padrões divergem entre ferramentas.
- `max`/`ultra` quase nunca: pensam demais e gastam mais. xhigh só com ganho real.
- Mude effort ou modelo **só entre tarefas** (no meio quebra o cache e o agente relê tudo). Se um perfil precisa de dois efforts com frequência, tenha dois terminais em vez de trocar toda hora.

## 4. Consulte a cota antes de decidir

`python <skill>/scripts/cotas.py` lê a cota ao vivo que o Maestri guarda. Rode no início da sessão, no início de cada rodada e antes de um lote grande.

- **Gaste primeiro** o pool com mais folga e reset mais próximo: cota que renova logo e sobra é cota perdida.
- **≥ 80%** num pool: só tarefas que só aquele modelo faz bem; o resto vai para a alternativa da tabela.
- **Claude Pro ≥ 70% na janela de 5 h:** pare de mandar trabalho para terminais Claude Code; use Opus/Sonnet no Antigravity (que já é a 1ª escolha para Claude). O Maestro precisa da folga para coordenar.
- **Pool "Claude and GPT" do Antigravity ≥ 100% (5 h ou semanal):** é a exceção que libera o Claude Code para Sonnet/Opus; volte ao Antigravity quando a cota voltar.
- Cota é recurso de equipe: nunca mova uma tarefa para um modelo **mais fraco** do que ela exige só para poupar cota; mova para outro pool equivalente.

## 5. Escalada quando falha

Falhou 2x (o produtor reportou bloqueado ou a revisão reprovou duas vezes):
1. Suba o **effort** no mesmo modelo (Haiku medium → high; Hydrogen high → xhigh).
2. Suba o **modelo** dentro da tríplice da mesma família, antes de trocar de família (Haiku → Sonnet → Opus no Antigravity; Hydrogen → Argon → Neon). Autor e revisor continuam de famílias diferentes.
3. Suba o **nível** da tarefa e reavalie o escopo (talvez falte especificação: despache ao Arquiteto).

## 6. Economia de tokens (custo por tarefa concluída, não por chamada)

- **Contexto do Maestro é o mais caro:** leia só o veredito e o `head` das saídas; nada de código ou diff; peça resumos curtos ao Batedor.
- **Passe caminhos, não conteúdo:** o produtor lê os arquivos; resultados voltam por arquivo em `.maestri/relatorios/`.
- **Afinidade de cache:** tarefas relacionadas no mesmo terminal, em sequência; `/clear` só ao mudar de assunto; nunca troque modelo ou effort no meio de uma tarefa.
- **Lote coeso:** várias tarefas pequenas do mesmo assunto num despacho só, para o mesmo terminal.
- **Fatos confirmados no despacho** ("o endpoint X existe e foi testado"), para ninguém redescobrir.
- **Ninguém é chamado por chamar:** toda tarefa tem entregável verificável; se uma etapa não muda a decisão, ela não existe.
- **Barato não é economia se refaz:** tarefa difícil em modelo leve que falha 3x custa mais que acertar de primeira no modelo certo.
