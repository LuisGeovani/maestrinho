# maestrinho

Skills para conduzir equipes de agentes de IA no [Maestri](https://www.themaestri.app/) (canvas com terminais Claude Code, Antigravity, Codex e OpenCode). Não dependem de nenhum projeto específico.

## Skills

| Skill | O que faz |
|---|---|
| [`maestro-equipe`](skills/maestro-equipe/SKILL.md) | Método do Maestro, que **comanda e não executa**. Quebra o pedido em tarefas, escolhe para cada uma o terminal, o modelo e o effort pelo catálogo de modelos e pela **cota ao vivo**, monta fluxos em que várias famílias participam (autor, testador e revisor diferentes), despacha com **relatório por arquivo**, revisa cruzado, decide e cuida do git. Inclui o **kit do Maestro**, um hook que impede o Maestro de executar trabalho. |

```
skills/maestro-equipe/
├── SKILL.md            regra de ouro, início de sessão, ciclo do pedido, roteamento rápido
├── maestro/            kit do Maestro: sistema.md, guarda.py (hook), instalar.py, opencode-gratis.json
├── references/         modelos (catálogo), roteamento, fluxos, comunicacao, prompts, setup, papeis, documentos
└── scripts/            maestri_batch.py (despacho), cotas.py (cota ao vivo), inventario.py (ambiente)
```

`docs/pesquisa/` guarda as fontes do catálogo de modelos e `docs/testes/`, os testes de comunicação feitos no Maestri.

## Instalação

Clone uma vez e **ligue** (junction ou symlink) a pasta da skill na pasta de skills de cada ferramenta. Um `git pull` atualiza todas.

```powershell
git clone https://github.com/LuisGeovani/maestrinho.git "$HOME\maestrinho"
New-Item -ItemType Junction -Path "$HOME\.claude\skills\maestro-equipe" -Target "$HOME\maestrinho\skills\maestro-equipe"
```

macOS/Linux: `ln -s ~/maestrinho/skills/maestro-equipe ~/.claude/skills/maestro-equipe`

| Ferramenta | Pasta de skills do usuário |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex e OpenCode | `~/.agents/skills/` (o OpenCode também lê `~/.claude/skills/`) |
| Antigravity | `~/.gemini/config/skills/` (também lê `~/.gemini/skills/`) |

O Maestro roda no Claude Code; os produtores não precisam da skill (recebem tudo pelo papel e pelo despacho).

### Kit do Maestro (recomendado)

```
python ~/maestrinho/skills/maestro-equipe/maestro/instalar.py
```

Imprime o comando do terminal do Maestro (`claude --model opus --effort medium --append-system-prompt-file … --settings …`) e a linha para cadastrar o preset no Maestri com o modo Maestro ligado. O hook bloqueia edição do projeto, leitura de código, pesquisa, build/testes e subagentes no terminal do Maestro, com a mensagem "despache isto". Teste: `python .../maestro/guarda.py --teste`. Rode o instalador de novo se mover a pasta.

### Requisitos

- Python 3 (só biblioteca padrão) para os scripts e o hook.
- Maestri com o CLI `maestri` no PATH.
- As CLIs que a pessoa tiver: `claude`, `agy` (Antigravity), `codex`, `opencode` (v2: `npm i -g @opencode/cli`). Detalhes e problemas conhecidos: `skills/maestro-equipe/references/setup.md`.

## Uso

**Primeira vez? Siga [`docs/primeira-conversa.md`](docs/primeira-conversa.md):** como abrir o Maestro pelo Quick Start, a primeira mensagem pronta para colar, o que esperar e o que fazer se algo der errado.

Depois do setup, num terminal aberto com o preset "Maestro", peça algo como "implemente X", "corrija o bug Y" ou "quero visões diferentes sobre esta decisão". A skill carrega pela descrição; numa sessão nova o Maestro roda o inventário (`scripts/inventario.py`), confere a equipe e segue o ciclo do `SKILL.md`.

```
python <skill>/scripts/inventario.py                 # o que o ambiente tem e quem é o Maestro
python <skill>/scripts/cotas.py                      # cota ao vivo e o que gastar primeiro
python <skill>/scripts/maestri_batch.py despacho.md  # despacho em lote (seções "### Terminal | ID")
```

## Atualizar

```powershell
git -C "$HOME\maestrinho" pull
```
