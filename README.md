# maestrinho

Skills para conduzir equipes de agentes de IA no [Maestri](https://www.themaestri.app/) (canvas com terminais Claude Code, Codex e Antigravity). Não dependem de nenhum projeto específico.

## Skills

| Skill | O que faz |
|---|---|
| [`maestro-equipe`](skills/maestro-equipe/SKILL.md) | Método do Maestro: setup da equipe (presets, papéis, recrutamento), níveis de tarefa N0–N4, roteamento por família de modelo (Claude, Gemini, GPT), revisão cruzada, Conselho de visões, rodadas com quadro, despacho em lote, permissões, cotas e git. |

Estrutura de uma skill:

```
skills/<nome>/
├── SKILL.md        # instruções principais (frontmatter com name e description)
├── references/     # detalhes lidos sob demanda (setup, papéis, modelos)
└── scripts/        # utilitários (ex.: maestri_batch.py)
```

## Instalação

Clone o repositório uma vez e **ligue** (junction ou symlink) a pasta da skill na pasta de skills de cada agente. Assim, um `git pull` atualiza a skill em todos os agentes.

```powershell
git clone https://github.com/LuisGeovani/maestrinho.git "$HOME\maestrinho"
```

### Claude Code

Skills de usuário ficam em `~/.claude/skills/`.

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\maestro-equipe" -Target "$HOME\maestrinho\skills\maestro-equipe"
```

macOS/Linux: `ln -s ~/maestrinho/skills/maestro-equipe ~/.claude/skills/maestro-equipe`

### Outros agentes (Codex, Antigravity)

Os dois também leem skills no formato `SKILL.md`. Crie a mesma ligação na pasta de skills de usuário de cada ferramenta (confira o caminho na documentação da versão instalada; por exemplo, `~/.codex/skills/` no Codex). Se a ferramenta não carregar skills, aponte o agente para o arquivo no prompt ou no papel: "siga `<caminho>/skills/maestro-equipe/SKILL.md`".

## Uso

Num terminal com o modo Maestro ligado no Maestri, peça algo como "monte a equipe para este projeto", "planeje a próxima rodada" ou "quero diferentes visões sobre esta decisão". A skill carrega sozinha pela descrição.

Despacho em lote, com validação e saída conferida:

```
python <maestrinho>/skills/maestro-equipe/scripts/maestri_batch.py tarefas.json
```

`tarefas.json` é um objeto `{"Agente": "prompt"}` em UTF-8.

## Atualizar

```powershell
git -C "$HOME\maestrinho" pull
```
