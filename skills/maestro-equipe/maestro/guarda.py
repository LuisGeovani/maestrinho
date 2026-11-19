"""Hook PreToolUse do Claude Code que impede o Maestro de executar trabalho.

O Maestro coordena: comandos `maestri`, git de integração, scripts desta skill,
leitura de relatórios e escrita só em .maestri/ (despachos, quadro, contexto).
Todo o resto (editar o projeto, ler código, pesquisar, buildar, subagentes) é
trabalho e deve ser despachado a um terminal do Maestri.

Instalação: `python instalar.py` gera settings.gerado.json com o caminho deste
arquivo e imprime o comando do preset do Maestro.
Desligar numa emergência: abrir o terminal do Maestro com MAESTRO_GUARDA=off.
Teste: python guarda.py --teste

Protocolo do hook: lê o JSON da chamada no stdin; sai 0 para liberar e 2 para
bloquear (a mensagem no stderr volta para o modelo).
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"

MSG = (
    "BLOQUEADO pelo kit do Maestro: {motivo}. Você coordena e não executa: "
    "despache isto a um terminal (scripts/maestri_batch.py) ou peça um resumo a um Batedor. "
    "Se o usuário quer mesmo que você faça, explique e peça que ele rode o comando ou desligue o kit."
)

FERRAMENTAS_TRABALHO = {
    "Grep": "busca no código",
    "Glob": "exploração de arquivos",
    "WebSearch": "pesquisa na web",
    "WebFetch": "leitura de página web",
    "Agent": "subagente interno (trabalho feito por você)",
    "Task": "subagente interno (trabalho feito por você)",
    "NotebookEdit": "edição de notebook",
}
ARQUIVOS_DE_AGENTE = {"agents.md", "claude.md", "gemini.md", "equipe.md", "maestro.md", "projeto.md", "status.md"}
LEITORES = {"cat", "head", "tail", "type", "get-content", "gc", "ls", "dir", "wc", "get-childitem", "less", "more", "sed-leitura"}
PALAVRAS_SHELL = {"do", "done", "then", "else", "elif", "fi", "if", "while", "until", "esac", "{", "}", "!", "in"}
FILTROS = {"grep", "cut", "sort", "uniq", "select-string", "select-object", "findstr", "tr", "column",
           "out-string", "format-table", "measure-object", "jq"}
NEUTROS = {"cd", "pwd", "echo", "printf", "true", "set-location", "write-output", "write-host", "date", "test", "["}
OPCOES_COM_VALOR = {"-n", "-c", "-m", "-A", "-B", "-C", "-e", "-f", "-d", "-k", "-t",
                    "-Pattern", "-TotalCount", "-Tail", "-First", "-Last", "-Head"}
GIT_CONTEUDO = {"grep", "blame", "apply", "am"}
GIT_SO_COM_RESUMO = {"diff", "show"}
GIT_FLAGS_RESUMO = {"--stat", "--shortstat", "--numstat", "--name-only", "--name-status", "--check", "--summary"}
REDIR_LIVRE = {"/dev/null", "$null", "nul"}


def _norm(caminho, cwd):
    if not caminho:
        return None
    c = os.path.expandvars(os.path.expanduser(str(caminho).strip().strip('"').strip("'")))
    if re.match(r"^/[a-zA-Z]/", c):  # /c/Users -> C:/Users (Git Bash)
        c = c[1] + ":" + c[2:]
    p = Path(c)
    if not p.is_absolute():
        p = Path(cwd or os.getcwd()) / p
    try:
        return p.resolve()
    except OSError:
        return p


def _dentro(p, base):
    try:
        p.relative_to(base)
        return True
    except ValueError:
        return False


def _temporarios():
    bases = [os.environ.get(v) for v in ("TEMP", "TMP", "TMPDIR")] + ["/tmp"]
    return [Path(b).resolve() for b in bases if b and Path(b).exists()]


def _area_do_claude(p, partes):
    casa = Path.home() / ".claude"
    return _dentro(p, casa / "plans") or ("memory" in partes and _dentro(p, casa / "projects"))


def leitura_permitida(caminho, cwd):
    p = _norm(caminho, cwd)
    if p is None:
        return False
    partes = [x.lower() for x in p.parts]
    if ".maestri" in partes or p.name.lower() in ARQUIVOS_DE_AGENTE:
        return True
    if _dentro(p, SKILL) or any(_dentro(p, t) for t in _temporarios()) or _area_do_claude(p, partes):
        return True
    return "docs" in partes and bool({"agentes", "rodadas", "adr"} & set(partes))


def escrita_permitida(caminho, cwd):
    p = _norm(caminho, cwd)
    if p is None:
        return False
    partes = [x.lower() for x in p.parts]
    if ".maestri" in partes or any(_dentro(p, t) for t in _temporarios()):
        return True
    return _area_do_claude(p, partes)


def sem_heredoc(cmd):
    """Remove corpos de heredoc e here-strings (o texto do despacho pode citar npm, sed etc.)."""
    cmd = re.sub(r"@'.*?'@", " ", cmd, flags=re.S)
    cmd = re.sub(r'@".*?"@', " ", cmd, flags=re.S)
    saida, fim = [], None
    for linha in cmd.split("\n"):
        if fim is not None:
            if linha.strip() == fim:
                fim = None
            continue
        m = re.search(r"<<-?\s*['\"]?([A-Za-z_]\w*)['\"]?", linha)
        if m:
            fim = m.group(1)
            linha = linha[: m.start()]
        saida.append(linha)
    return "\n".join(saida)


def tokens(cmd):
    # barra invertida de caminho do Windows vira /, sem mexer em \" e \\
    cmd = re.sub(r"\\(?=[\w .:\-])", "/", cmd)
    lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=";&|<>()")
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        return list(lex)
    except ValueError:  # aspas desbalanceadas
        return None


def programa(tok):
    t = tok.strip().strip("\"'")
    if t in ("$MAESTRI_CLI", "${MAESTRI_CLI}", "$env:MAESTRI_CLI"):
        return "maestri"
    nome = re.split(r"[\\/]", t)[-1].lower()
    return re.sub(r"\.(exe|cmd|bat|ps1)$", "", nome)


def _arquivos_lidos(prog, args):
    arquivos, pular = [], False
    falta_padrao = prog in ("grep", "select-string", "findstr")
    for a in args:
        if pular:
            pular = False
            continue
        if a in OPCOES_COM_VALOR:
            pular = True
            continue
        if a.startswith("-") or re.fullmatch(r"\d+", a):
            continue
        if falta_padrao:
            falta_padrao = False
            continue
        arquivos.append(a)
    return arquivos


def checar_segmento(seg, cwd):
    """Devolve None se liberado, ou o motivo do bloqueio."""
    while seg and (re.match(r"^[A-Za-z_]\w*=", seg[0]) or seg[0] in ("&", "") or seg[0] in PALAVRAS_SHELL):
        seg = seg[1:]
    if not seg:
        return None
    if seg[0] in ("for", "select", "case", "foreach"):  # for n in A B C: só a lista de valores
        return None
    prog, args = programa(seg[0]), seg[1:]
    if prog == "sed" and not any(a.startswith("-i") or a == "--in-place" for a in args):
        prog = "sed-leitura"
    if prog == "maestri":
        return None
    if prog == "git":
        sub = next((a for a in args if not a.startswith("-")), "")
        if sub in GIT_CONTEUDO:
            return f"git {sub} (ler ou aplicar conteúdo de código)"
        if sub in GIT_SO_COM_RESUMO and not (set(args) & GIT_FLAGS_RESUMO):
            return f"git {sub} sem --stat/--name-only (ler o diff é revisão, trabalho de outra família)"
        if sub == "log" and {"-p", "--patch"} & set(args):
            return "git log -p (ler diff)"
        return None
    if prog in ("python", "python3", "py"):
        if {"-c", "-m"} & set(args):
            return "python -c/-m (código solto)"
        script = next((a for a in args if not a.startswith("-")), None)
        sp = _norm(script, cwd) if script else None
        ok = sp is not None and sp.suffix == ".py" and _dentro(sp, SKILL)
        return None if ok else "python fora dos scripts da skill"
    if prog in NEUTROS:
        return None
    if prog == "mkdir":
        alvos = [a for a in args if not a.startswith("-")]
        return None if alvos and all(escrita_permitida(a, cwd) for a in alvos) else "mkdir fora de .maestri/"
    if prog in LEITORES or prog in FILTROS:
        ruins = [a for a in _arquivos_lidos(prog, args) if not leitura_permitida(a, cwd)]
        return f"{prog} em arquivo do projeto ({ruins[0]})" if ruins else None
    return f"comando de trabalho '{prog}'"


def checar_comando(cmd, cwd, shell="Bash"):
    cmd = sem_heredoc(cmd)
    internos = re.findall(r"\$\(([^()]*)\)", cmd)
    if shell == "Bash":
        internos += re.findall(r"`([^`]*)`", cmd)
    for interno in internos:
        if interno.strip():
            motivo = checar_comando(interno, cwd, shell)
            if motivo:
                return motivo
    toks = tokens(cmd)
    if toks is None:
        return "comando que não consegui analisar (aspas desbalanceadas)"
    segmento, i = [], 0
    while i < len(toks):
        t = toks[i]
        if re.fullmatch(r"[<>&]+", t) and ">" in t:  # >, >>, >&, &>
            alvo = toks[i + 1] if i + 1 < len(toks) else ""
            livre = t.endswith("&") or re.fullmatch(r"\d", alvo) or alvo.lower() in REDIR_LIVRE
            if not livre and not escrita_permitida(alvo, cwd):
                return f"redirecionamento para arquivo do projeto ({alvo})"
            i += 2
            continue
        if t in ("<", "<<", "<<<"):
            i += 2
            continue
        if t in (";", "&&", "||", "|", "&", "(", ")"):
            motivo = checar_segmento(segmento, cwd)
            if motivo:
                return motivo
            segmento = []
            i += 1
            continue
        if re.fullmatch(r"\d", t) and i + 1 < len(toks) and toks[i + 1].startswith(">"):
            i += 1  # o 2 de 2>&1
            continue
        segmento.append(t)
        i += 1
    return checar_segmento(segmento, cwd)


def decidir(chamada):
    nome = chamada.get("tool_name", "")
    entrada = chamada.get("tool_input") or {}
    cwd = chamada.get("cwd") or os.getcwd()
    if nome in FERRAMENTAS_TRABALHO:
        return FERRAMENTAS_TRABALHO[nome]
    if nome.startswith("mcp__"):
        return "ferramenta MCP (trabalho externo)"
    if nome == "Read":
        alvo = entrada.get("file_path")
        return None if leitura_permitida(alvo, cwd) else f"leitura de arquivo do projeto ({alvo}); peça um resumo ao Batedor"
    if nome in ("Write", "Edit", "MultiEdit"):
        alvo = entrada.get("file_path")
        return None if escrita_permitida(alvo, cwd) else f"edição de arquivo do projeto ({alvo})"
    if nome in ("Bash", "PowerShell"):
        return checar_comando(entrada.get("command", ""), cwd, nome)
    return None


CASOS = [
    ("Bash", "maestri list", True),
    ("Bash", 'maestri check "Prisma" 2>&1 | tail -20', True),
    ("Bash", 'maestri ask "Prisma" --raw "\\r"', True),
    ("Bash", 'maestri ask "Prisma" "texto com \\"aspas\\" e C:\\Users\\x"', True),
    ("Bash", "git status --short && git diff --stat", True),
    ("Bash", "git diff src/app.ts", False),
    ("Bash", 'git commit -qm "feat: x"', True),
    ("Bash", "git log --oneline -5", True),
    ("Bash", "git log -p -3", False),
    ("Bash", f'python "{SCRIPTS / "maestri_batch.py"}" - <<\'EOF\'\n### Prisma | T1\nrode npm run build; sed -i x\nEOF', True),
    ("Bash", f'python "{SCRIPTS / "cotas.py"}"', True),
    ("Bash", "python -c \"open('x','w')\"", False),
    ("Bash", "npm run build", False),
    ("Bash", "cd app && npx vite build", False),
    ("Bash", "cat src/main.ts", False),
    ("Bash", "head -40 .maestri/relatorios/PJ-T1.md 2>&1", True),
    ("Bash", "echo oi > src/x.ts", False),
    ("Bash", "echo oi > .maestri/quadro.md", True),
    ("Bash", "sed -i 's/a/b/' src/x.ts", False),
    ("Bash", 'maestri role write "Papel" "$(cat .maestri/papeis/x.md)"', True),
    ("Bash", 'maestri role write "Papel" "$(cat src/x.md)"', False),
    ("Bash", "grep -rn TODO src", False),
    ("Bash", 'for n in Brasa Neblina; do maestri check "$n" 2>&1 | head -15; done', True),
    ("Bash", "for f in src/*.ts; do cat $f; done", False),
    ("Bash", "sed -n 1,60p \"" + str(SKILL / "references" / "comunicacao.md") + "\"", True),
    ("Bash", "sed -n 1,60p src/app.ts", False),
    ("Bash", "if true; then npm test; fi", False),
    ("Bash", 'maestri check "Lente" | grep -i permission', True),
    ("PowerShell", "maestri list; git status --short", True),
    ("PowerShell", "Get-Content src\\app.ts", False),
    ("PowerShell", "Get-Content .maestri\\relatorios\\PJ-T1.md -TotalCount 30", True),
    ("PowerShell", '& "$env:MAESTRI_CLI" list', True),
    ("PowerShell", f"@'\n### Prisma | T1\nnpm run build\n'@ | python \"{SCRIPTS / 'maestri_batch.py'}\" -", True),
    ("Read", "src/app.ts", False),
    ("Read", ".maestri/relatorios/PJ-T1.md", True),
    ("Read", "AGENTS.md", True),
    ("Read", str(SKILL / "SKILL.md"), True),
    ("Write", ".maestri/despachos/R1.md", True),
    ("Write", "src/app.ts", False),
    ("Edit", "README.md", False),
    ("Grep", "", False),
    ("WebSearch", "", False),
    ("Agent", "", False),
    ("mcp__claude_ai_Figma__get_screenshot", "", False),
    ("Skill", "", True),
    ("AskUserQuestion", "", True),
]


def teste():
    sys.stdout.reconfigure(encoding="utf-8")
    cwd = str(SKILL.parent.parent)  # finge ser a raiz de um projeto
    erros = 0
    for nome, alvo, liberar in CASOS:
        chave = "command" if nome in ("Bash", "PowerShell") else "file_path"
        motivo = decidir({"tool_name": nome, "tool_input": {chave: alvo} if alvo else {}, "cwd": cwd})
        ok = (motivo is None) == liberar
        erros += not ok
        primeira = alvo.splitlines()[0][:70] if alvo else ""
        extra = "" if ok else f"  <- esperado {'libera' if liberar else 'bloqueia'} ({motivo})"
        print(f"{'ok ' if ok else 'ERR'} {'libera' if motivo is None else 'bloqueia':8} {nome}: {primeira}{extra}")
    print(f"{len(CASOS) - erros}/{len(CASOS)} casos ok")
    return 1 if erros else 0


def main():
    if "--teste" in sys.argv:
        return teste()
    if os.environ.get("MAESTRO_GUARDA", "").lower() in ("off", "desligado", "0"):
        return 0
    try:
        chamada = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except json.JSONDecodeError:
        return 0
    motivo = decidir(chamada)
    if motivo:
        sys.stderr.buffer.write(MSG.format(motivo=motivo).encode("utf-8"))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
