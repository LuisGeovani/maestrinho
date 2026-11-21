"""Inventário do ambiente para montar a equipe: CLIs, modelos disponíveis e cotas.

Uso:
    python inventario.py [--rapido]

--rapido pula as consultas lentas (agy models, opencode models).
Saída curta (cerca de 20 linhas), pensada para o contexto do Maestro.
Só leitura: roda comandos de listagem e lê caches locais.
Também avisa, uma linha por preset, dos presets com --add-dir/--dir de caminho absoluto
(precisa do terminal Maestro: usa `maestri preset list` e `maestri preset show`).
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cotas import ler_cotas, resumo_linhas  # noqa: E402

CLIS = {
    "claude": "Claude Code",
    "agy": "Antigravity",
    "codex": "Codex",
    "opencode": "OpenCode",
    "maestri": "Maestri",
}


def rodar(args, timeout=30):
    try:
        p = subprocess.run(args, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)
    saida = p.stdout.decode("utf-8", "replace")
    erro = p.stderr.decode("utf-8", "replace")
    return (saida if p.returncode == 0 else None), erro


def versao(exe):
    saida, _ = rodar([exe, "--version"], timeout=20)
    if not saida:
        return "?"
    m = re.search(r"\d+\.\d+[\w.\-]*", saida)
    return m.group(0) if m else saida.strip().splitlines()[0][:30]


def agrupar_por_effort(ids):
    """gemini-4-neon-high, gemini-4-neon-low -> gemini-4-neon[low,high]"""
    grupos = {}
    for i in ids:
        m = re.match(r"(.+?)-(low|medium|high|xhigh|max)$", i)
        base, nivel = (m.group(1), m.group(2)) if m else (i, None)
        grupos.setdefault(base, [])
        if nivel:
            grupos[base].append(nivel)
    ordem = ["low", "medium", "high", "xhigh", "max"]
    partes = []
    for base, niveis in grupos.items():
        niveis = sorted(set(niveis), key=ordem.index)
        partes.append(f"{base}[{','.join(niveis)}]" if niveis else base)
    return partes


def modelos_agy(exe):
    saida, erro = rodar([exe, "models"], timeout=60)
    if not saida:
        return f"falhou ({(erro or '').strip()[:80]})"
    ids = [l.split("\t")[0].strip() for l in saida.splitlines() if "\t" in l]
    return ", ".join(agrupar_por_effort(ids)) or "nenhum"


def modelos_codex():
    casa = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    cache = casa / "models_cache.json"
    if not cache.exists():
        return "sem cache (abra o codex uma vez)"
    dados = json.loads(cache.read_text(encoding="utf-8"))
    partes = []
    for m in dados.get("models", []):
        niveis = [n.get("effort") for n in m.get("supported_reasoning_levels", []) if n.get("effort")]
        faixa = f"{niveis[0]}..{niveis[-1]}" if niveis else ""
        partes.append(f"{m.get('slug')}[{faixa}]")
    config = casa / "config.toml"
    padrao = ""
    if config.exists():
        texto = config.read_text(encoding="utf-8", errors="replace")
        mm = re.search(r'^model\s*=\s*"([^"]+)"', texto, re.M)
        me = re.search(r'^model_reasoning_effort\s*=\s*"([^"]+)"', texto, re.M)
        if mm:
            padrao = f" | padrão: {mm.group(1)} {me.group(1) if me else ''}".rstrip()
    return ", ".join(partes) + padrao


def modelos_opencode(exe):
    saida, erro = rodar([exe, "models"], timeout=90)
    if not saida:
        return f"falhou ({(erro or '').strip()[:80]})"
    ids = [l.strip() for l in saida.splitlines() if "/" in l and " " not in l.strip()]
    gratis = [i for i in ids if i.endswith("-free") or "big-pickle" in i]
    return f"{len(ids)} modelos; grátis: {', '.join(gratis) if gratis else 'nenhum'}"


def nome_do_maestro(exe):
    saida, _ = rodar([exe, "list"], timeout=20)
    if not saida:
        return None, []
    nome, agentes, secao = None, [], None
    for linha in saida.splitlines():
        if re.match(r"^\S.*:\s*$", linha):
            secao = linha.strip().rstrip(":").lower()
            continue
        m = re.search(r'name:\s*"([^"]+)"', linha)
        if not m:
            continue
        if secao == "you" and nome is None:
            nome = m.group(1)
        elif secao and secao != "you":
            agentes.append(m.group(1))
    return nome, agentes


FLAG_DIR = re.compile(r"(?<![\w-])--(add-dir|dir)(?:\s+|=)(\"[^\"]*\"|'[^']*'|\S+)")
CAMINHO_FIXO = re.compile(r"^(?:[A-Za-z]:[\\/]|[\\/]|~)")


def nomes_de_presets(texto):
    """Nome de cada linha de `maestri preset list`: o 1º trecho entre aspas ou o texto antes de ':'/' - '."""
    nomes = []
    for linha in texto.splitlines():
        l = linha.strip().lstrip("-*•> ").strip()
        if not l or l.endswith(":") and "\"" not in l:
            continue
        m = re.match(r'"([^"]+)"', l) or re.match(r"(.+?)(?:\s*[:—–]\s|\s+-\s|\s{2,}|$)", l)
        if m and m.group(1).strip():
            nomes.append(m.group(1).strip())
    return nomes


def caminhos_fixos(comando):
    """[(flag, valor)] dos --add-dir/--dir cujo valor é caminho absoluto ou do diretório pessoal."""
    achados = []
    for flag, valor in FLAG_DIR.findall(comando):
        valor = valor.strip("\"'")
        if CAMINHO_FIXO.match(valor):
            achados.append((f"--{flag}", valor))
    return achados


def presets_com_caminho_fixo(exe):
    """Linhas do relatório: um preset suspeito por linha, ou uma linha só dizendo que está tudo bem."""
    saida, erro = rodar([exe, "preset", "list"], timeout=20)
    texto = saida or ""
    if not texto.strip() or "not the Maestro" in texto or "not the Maestro" in (erro or ""):
        return ["Presets: não verificado (só o terminal Maestro lê os presets)"]
    suspeitos, vistos = [], set()
    for nome in nomes_de_presets(texto)[:40]:
        if nome in vistos:
            continue
        vistos.add(nome)
        comando, _ = rodar([exe, "preset", "show", nome], timeout=20)
        for flag, valor in caminhos_fixos(comando or ""):
            suspeitos.append(f'  "{nome}": {flag} {valor}')
    if not suspeitos:
        return ["Presets: nenhum com caminho fixo"]
    return ["Presets com caminho fixo (use o genérico: references/setup.md §2):"] + suspeitos


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    rapido = "--rapido" in sys.argv
    linhas = ["== CLIs"]
    achados = {}
    for cmd, rotulo in CLIS.items():
        exe = shutil.which(cmd)
        achados[cmd] = exe
        linhas.append(f"{rotulo}: {versao(exe) if exe else 'NÃO instalado'}")
    linhas.append("== Modelos")
    if achados["claude"]:
        linhas.append("Claude Code: aliases fable, opus, sonnet, haiku (versões em references/modelos.md)")
    if achados["agy"]:
        linhas.append("Antigravity: " + ("(pulado)" if rapido else modelos_agy(achados["agy"])))
        from configurar_antigravity import resumo as config_agy
        linhas.append(config_agy())
    if achados["codex"]:
        linhas.append("Codex: " + modelos_codex())
    if achados["opencode"]:
        linhas.append("OpenCode: " + ("(pulado)" if rapido else modelos_opencode(achados["opencode"])))
    if achados["maestri"]:
        nome, agentes = nome_do_maestro(achados["maestri"])
        linhas.append("== Maestri")
        linhas.append(f"Você (nome para o ask back): {nome or '?'}")
        linhas.append("Conectados: " + (", ".join(agentes) if agentes else "nenhum"))
        linhas += presets_com_caminho_fixo(achados["maestri"])
        p = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True)
        raiz = Path(p.stdout.decode("utf-8", "replace").strip()) if p.returncode == 0 else Path.cwd()
        equipe = raiz / ".maestri" / "equipe.md"
        if equipe.exists():
            tabela = [l for l in equipe.read_text(encoding="utf-8").splitlines() if l.startswith("|") and "---" not in l]
            linhas.append(f"Formação anotada ({equipe}):")
            linhas += ["  " + l for l in tabela[1:13]]
        else:
            linhas.append("Formação: sem .maestri/equipe.md (anote ao recrutar; o maestri list não mostra modelo)")
    linhas.append("== Cotas")
    pools, avisos = ler_cotas()
    linhas += resumo_linhas(pools, avisos)
    print("\n".join(linhas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
