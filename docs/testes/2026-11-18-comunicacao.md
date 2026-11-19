# Testes de comunicação e roteamento no Maestri (2026-11-18)

Ambiente: Windows 11; Maestri e80f02c7; Maestro = Claude Code 2.1.328 (Opus 5.5) no terminal "Claude Code"; produtores de teste no workspace do maestrinho, papel "Teste Produtor" (só leitura, exceto `.maestri/teste` e `.maestri/relatorios`). Cota antes: Claude Pro 5 h 33%, Antigravity 0–11%, Codex Free 92% do mês.

| Terminal | Ferramenta · modelo · effort | Comando de recrutamento |
|---|---|---|
| Brasa | Claude Code · Haiku 5.5 · low | `--preset "Claude Code" --command "claude --model haiku --effort low --add-dir ../../.." --role "Teste Produtor"` |
| Neblina | Antigravity 1.5.12 · Gemini 4 Hydrogen · low | `--preset "Antigravity" --command "agy --model gemini-4-hydrogen-low --add-dir ../../.."` |
| Musgo | OpenCode 2.3.2 · deepseek-v4.1-flash-free | `--preset "OpenCode" --command '$env:OPENCODE_CONFIG="<...>/opencode.json"; opencode --standalone'` |
| Agulha | Codex 0.170.0 · GPT-6 Luna · low | `--preset "Codex" --command "codex -m gpt-6-luna -c model_reasoning_effort=low <variáveis MAESTRI_*>"` |

## Resultados

| # | Teste | Resultado | Evidência e correção aplicada |
|---|---|---|---|
| E1 | `inventario.py` e `cotas.py` | **passou** | inventário em ~3 s com CLIs, modelos (`agy models`, cache do Codex, `opencode models`), nome do Maestro e cotas |
| E2 | preset por modelo + `--add-dir ../../..` com papel | **passou** | os 4 leram o projeto sem pedir permissão (campo PENDENCIAS dos relatórios TS-T1..T4). Dois terminais com o mesmo papel compartilham a pasta de papel |
| E2b | confiança de pasta | Antigravity e Codex perguntam na 1ª vez em cada pasta de papel; Claude Code não | aprovado com `maestri ask "Nome" --raw "\r"`; o retorno do `--raw` mostra a tela antiga, conferir com `check` |
| E3 | despacho em lote em background, nome real do Maestro | **passou** | 4 famílias em 45 s; avisos chegaram como mensagens curtas e inteiras |
| E4 | relatório em arquivo com acentos, aspas, crase, `C:\…`, `\n` literal, `$(…)` | **passou** | os 4 arquivos idênticos ao original (conferido por revisão cruzada em E7) |
| E4b | status no resumo do script | falhou na 1ª versão ("?") | a saída do `--batch` é a tela do produtor, não o aviso → o script lê STATUS do arquivo e confere se o arquivo é novo |
| E4c | aviso com "STATUS" literal | Haiku low mandou `TS-T1 STATUS: pronto` | rodapé passou a dar o comando literal com "pronto" |
| E5 | regra genérica do Antigravity | **passou** | `command(regex:^maestri ask "[^"]+" "[^"$`;&|<>]*"$)` aceita qualquer nome e só o aviso curto; a regra antiga (`(?s)…(\s+.*)?$`) aceitava encadear comandos (`"x"; rm …`). Aviso do Antigravity chegou sem confirmação |
| E6 | despacho logo após reiniciar o terminal | **falhou 2x, passou na 3ª** | 1ª: o texto ficou parado na caixa de entrada (Enter perdido) e o lote voltou como ocioso; 2ª: o começo do texto se perdeu e o produtor recebeu um despacho cortado (reportou bloqueado, corretamente). Correção: o script espera a tela estabilizar com o campo de prompt visível antes de enviar e, se mesmo assim o texto ficar na caixa, manda Enter e espera o arquivo |
| E7 | passagem de bastão: revisor lê o relatório do autor pelo caminho | **passou** | Claude revisou Gemini (TS-T5) e Gemini revisou Claude (TS-T6) sem o Maestro repassar conteúdo; a revisão apontou STATUS na mesma linha da TAREFA → rodapé com um campo por linha e VEREDITO separado |
| E8 | kit do Maestro num terminal do Maestri | **passou** | pedido "rapidinho, sem despachar": leitura/edição do README e `npm` bloqueados com a mensagem; leitura de script da skill e `maestri list` liberados; o modelo não tentou contornar e ofereceu despachar. Antes, em `claude -p`: `npm` bloqueado, `maestri list` liberado. `guarda.py --teste`: 41/41 |
| E9 | Codex: ida e volta | **passou** | preset com as variáveis MAESTRI_*; aviso chegou; banner mostra "monthly limit: 8% left" |
| E10 | OpenCode | **passou com ajustes** | v1 (`opencode-ai`) falha: "Database is not empty and has no session table" (banco do app desktop) → v2 (`@opencode/cli`). Sem `--standalone` abriu em outro modelo (o serviço em segundo plano ignora `OPENCODE_CONFIG`) → `--standalone`. `permissions` com `git *` negado: confirmado ("Permission denied: shell"). `OPENAI_API_KEY` no ambiente faz aparecer 98 modelos `openai/*` pagos |
| — | "This terminal is not the Maestro" logo após ligar o modo | ocorreu | a opção levou alguns segundos para valer; documentado em `setup.md` |

## Ensaio ponta a ponta

Maestro de teste "Regente": Claude Code **Sonnet 5.5 medium** com o kit (`--append-system-prompt-file sistema.md --settings settings.gerado.json`). Sonnet em vez de Opus porque o Claude Pro estava em 64% da janela de 5 h e a própria regra da skill manda poupar a partir de 70%. Produtores já conectados: Brasa (Haiku), Neblina (Hydrogen), Musgo (OpenCode grátis). Pedido: "script csv_para_json.py com testes unittest e README curto em `.maestri/teste/proj`".

| Etapa | O que o Regente fez | Confere com a skill? |
|---|---|---|
| Início | carregou a skill, inventariou com `maestri check` | sim |
| Roteamento | implementação + testes → Neblina (Gemini, prompt em XML); README → Musgo (aberto, grátis); revisão → Brasa (Claude, outra família) | sim: 3 famílias, cada uma com entregável |
| Despacho | `maestri_batch.py` em background, IDs CJ1-T1/T2, encerrou o turno | sim |
| Revisão | despacho CJ1-REV com checklist (a)/(b)/(c), fatos confirmados e os caminhos dos relatórios dos autores | sim (passagem de bastão por arquivo) |
| Resultado | revisora rodou os 6 testes (OK), executou o script no CSV, conferiu o README; VISÃO: risco baixo de BOM do Excel | sim |
| Escopo | `git diff --stat` achou o `README.md` da raiz modificado (era a reescrita feita pelo Maestro real nesta sessão); não reverteu sem prova de autoria e perguntou ao usuário | sim |
| Reporte | tabela quem fez o quê, "Eu não rodei nada", pendência do BOM, sem commit | sim |
| Execução própria | nenhuma; uma tentativa de laço `for … maestri check` foi bloqueada pelo kit | o bloqueio era falso positivo → `guarda.py` passou a liberar laços e `sed -n` em arquivos permitidos (46/46 casos) |

Falha encontrada: o Regente não soube o modelo da Brasa ("modelo não confirmado"), porque o Claude Code só mostra o modelo no banner do topo, que some com o uso, e o `maestri list` não mostra modelo. Correção: formação anotada em `.maestri/equipe.md` ao recrutar (SKILL.md, setup.md, documentos.md; o `inventario.py` mostra a tabela).

Lição do lado do Maestro real: esperar texto na tela de um terminal falha (a tela rola). Espere pelo **arquivo de relatório** (o `maestri_batch.py` já faz isso) ou pela notificação do background.

Cota depois do ensaio e de todos os testes: ver `cotas.py` no fim da sessão (Claude Pro 5 h subiu principalmente pelo Maestro real em Opus xhigh, que construiu a skill).
