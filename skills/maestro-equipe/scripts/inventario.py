"""Inventário do ambiente para montar a equipe: CLIs, modelos disponíveis e cotas.

Uso:
    python inventario.py [--rapido]

--rapido pula as consultas lentas (agy models, opencode models).
Saída curta (cerca de 20 linhas), pensada para o contexto do Maestro.
Só leitura: roda comandos de listagem e lê caches locais.
Também avisa, uma linha por preset, dos presets com --add-dir/--dir de caminho absoluto
(precisa do terminal Maestro: usa `maestri preset list` e `maestri preset show`).
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cotas import ler_cotas, modelos_codex_cache, resumo_linhas  # noqa: E402

CLIS = {
    "claude": "Claude Code",
    "agy": "Antigravity",
    "codex": "Codex",
    "opencode": "OpenCode",
    "maestri": "Maestri",
}
PRESETS_CODEX = {
    "Codex Luna": ("gpt-6-luna", "high"),
    "Codex Terra": ("gpt-6.1-terra", "medium"),
    "Codex Sol": ("gpt-6.2-sol", "medium"),
    "Codex Astra": ("gpt-6.2-astra", "high"),
}
PRESETS_SUGERIDOS = {**PRESETS_CODEX, "Agy Flash": ("gemini-3.8-flash-low", None)}
ENV_MAESTRI_CODEX = {"MAESTRI_CLI", "MAESTRI_DATA_DIR", "MAESTRI_PIPE", "MAESTRI_TERMINAL_ID", "MAESTRI_WORKSPACE_ID"}
MEDIDORES_GEMINI_CONFIRMADOS = {
    "gemini-4-hydrogen": "gemini-models",
    "gemini-4-neon": "gemini-models",
    "gemini-pro-orchestrator-neon": "gemini-models",
    "gemini-pro-orchestrator-g1-pro": "gemini-4-argon",
}
MEDIDORES_GEMINI_CONHECIDOS = ("Gemini Models", "Gemini 4 Argon")


def rodar(args, timeout=30):
    try:
        p = subprocess.run(args, capture_output=True, stdin=subprocess.DEVNULL, timeout=timeout)
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


def modelos_codex(modelos=None):
    casa = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    cache = casa / "models_cache.json"
    if not cache.exists():
        return "sem cache (abra o codex uma vez)"
    if modelos is None:
        modelos = modelos_codex_cache()
    partes = []
    for m in modelos:
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
    return (", ".join(partes) or "cache vazio ou ilegível") + padrao


def degraus_codex(modelos):
    por_id = {m.get("slug"): m for m in modelos}
    partes = []
    for nome, (modelo, _) in PRESETS_CODEX.items():
        m = por_id.get(modelo)
        if m is None or m.get("visibility") == "hide":
            estado = "não listado no cache"
        else:
            niveis = [n["effort"] for n in m.get("supported_reasoning_levels", []) if n.get("effort")]
            estado = f"listado no cache{', effort ' + '/'.join(niveis) if niveis else ''}"
        partes.append(f"{nome.removeprefix('Codex ')} ({modelo}, {estado})")
    return "GPT no Codex: " + " · ".join(partes)


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
COMANDO_PRESET = re.compile(r"^[ \t]*(?:command|comando)[ \t]*:[ \t]*(.*)$", re.I | re.M)
CLI_PRESET = re.compile(r"""(?<![\w.-])(codex|claude|agy|opencode)(?:\.(?:exe|cmd|bat|ps1))?(?=[\s"';&]|$)""", re.I)
MODELO_PRESET = re.compile(r"""(?:^|\s)(?:--model|-m)(?:\s+|=)["']?([^\s"';]+)""", re.I)
TITULO_PRESETS = re.compile(
    r"^(?:available|no)\s|^(?:(?:agent|recruit|saved|configured|quick[- ]start|maestri)\s+)*presets\b"
    r"|^(?:available\s+)?(?:cli\s+)?accounts?\b",
    re.I,
)


def nomes_de_presets(texto):
    """Nome de cada linha de `maestri preset list`: o 1º trecho entre aspas ou o texto antes de ':'/' - '."""
    nomes = []
    for linha in texto.splitlines():
        l = linha.strip().lstrip("-*•> ").strip()
        if not l or l.endswith(":") or TITULO_PRESETS.match(l):
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


def medidor_gemini(modelo, medidores_agy):
    """Prioriza o medidor dedicado e usa vínculos confirmados quando disponíveis."""
    base = re.sub(r"-(?:low|medium|high|xhigh|max)$", "", modelo)
    por_nome = {"-".join(nome.casefold().split()): nome for nome in medidores_agy}
    if base != "gemini-models" and base in por_nome:
        return por_nome[base]
    return por_nome.get(MEDIDORES_GEMINI_CONFIRMADOS.get(base), "medidor desconhecido")


def ferramenta_e_pool(comando, plano_claude, medidores_agy=()):
    achado = CLI_PRESET.search(comando)
    if not achado:
        return "ferramenta não identificada", "pool não identificado"
    cli = achado.group(1).lower()
    modelo = MODELO_PRESET.search(comando, achado.end())
    modelo = modelo.group(1).lower() if modelo else ""
    if cli == "codex":
        pool = "Codex"
    elif cli == "claude":
        pool = f"Claude {plano_claude}" if plano_claude else "Claude Code (plano não identificado)"
    elif cli == "opencode":
        gratis = modelo.endswith("-free") or "big-pickle" in modelo or "opencode-gratis" in comando.casefold()
        pool = "grátis" if gratis else "pool não identificado"
    elif modelo.startswith("gemini-"):
        pool = medidor_gemini(modelo, medidores_agy)
    elif modelo.startswith(("claude-", "gpt-")):
        pool = "Claude and GPT models"
    else:
        pool = "pool não identificado"
    return CLIS[cli], pool


def comando_da_formacao(ferramenta, modelo, preset):
    """Representa os metadados da equipe quando o CLI não expõe o preset."""
    cli = next((cli for cli, nome in CLIS.items() if nome.casefold() == ferramenta.casefold()), "")
    if not cli:
        return ""
    modelo = re.sub(r"[^\w]+", "-", modelo.casefold()).strip("-")
    if cli == "opencode" and re.search(r"\bgr[aá]tis\b", preset, re.I):
        modelo = "opencode-gratis"
    return f"{cli} --model {modelo}" if modelo else cli


def comando_preset(detalhes):
    if not detalhes:
        return ""
    m = COMANDO_PRESET.search(detalhes)
    if m:
        return m.group(1)
    return detalhes.strip() if len(detalhes.strip().splitlines()) == 1 else ""


def presets_com_caminho_fixo(exe, plano_claude="", medidores_agy=()):
    """Relata caminhos fixos e os vínculos entre presets, CLIs e medidores."""
    saida, erro = rodar([exe, "preset", "list"], timeout=20)
    texto = saida or ""
    if not texto.strip() or "not the Maestro" in texto or "not the Maestro" in (erro or ""):
        return ["Presets: não verificado (só o terminal Maestro lê os presets)"]
    suspeitos, vinculos = [], []
    nomes = list(dict.fromkeys(nomes_de_presets(texto)))
    for nome in nomes:
        detalhes, _ = rodar([exe, "preset", "show", nome], timeout=20)
        if detalhes is None:
            continue
        comando = comando_preset(detalhes)
        for flag, valor in caminhos_fixos(detalhes):
            suspeitos.append(f'  "{nome}": {flag} {valor}')
        ferramenta, pool = ferramenta_e_pool(comando, plano_claude, medidores_agy)
        linha = f'  "{nome}" → {ferramenta} → {pool}'
        if ferramenta == "Codex":
            citadas = set(re.findall(r"\bMAESTRI_[A-Z0-9_]+\b", comando.upper()))
            faltam = sorted(ENV_MAESTRI_CODEX - citadas)
            linha += f" | aviso: faltam {', '.join(faltam)}" if faltam else " | MAESTRI_* presentes"
        vinculos.append(linha)
    linhas = (["Presets com caminho fixo (use o genérico: references/setup.md §2):"] + suspeitos
              if suspeitos else ["Presets: nenhum com caminho fixo"])
    if vinculos:
        linhas += ["Preset → ferramenta → pool"] + vinculos
    presentes = {nome.casefold() for nome in nomes}
    for nome, (modelo, effort) in PRESETS_SUGERIDOS.items():
        if nome.casefold() not in presentes:
            ferramenta, pool = ferramenta_e_pool(f"{'codex' if effort else 'agy'} --model {modelo}", plano_claude, medidores_agy)
            linhas.append(f"Preset sugerido: {nome} → {ferramenta} → {pool} ({modelo}{', ' + effort if effort else ''})")
    return linhas


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    rapido = "--rapido" in sys.argv
    pools, avisos = ler_cotas()
    medidores_agy = {p["medidor"] for p in pools if p["provedor"].casefold() == "antigravity"}
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
        flash = medidor_gemini("gemini-3.8-flash", medidores_agy)
        consulta = " · consulta de disponibilidade pulada (--rapido)" if rapido else ""
        linhas.append(f"Gemini 3.8 Flash (gemini-3.8-flash): {flash}{consulta}")
        from configurar_antigravity import resumo as config_agy
        linhas.append(config_agy())
    if achados["codex"]:
        cache = modelos_codex_cache()
        linhas.append("Codex: " + modelos_codex(cache))
        linhas.append(degraus_codex(cache))
    if achados["opencode"]:
        linhas.append("OpenCode: " + ("(pulado)" if rapido else modelos_opencode(achados["opencode"])))
    if achados["maestri"]:
        nome, agentes = nome_do_maestro(achados["maestri"])
        linhas.append("== Maestri")
        linhas.append(f"Você (nome para o ask back): {nome or '?'}")
        linhas.append("Conectados: " + (", ".join(agentes) if agentes else "nenhum"))
        plano_claude = next((p["plano"].title() for p in pools if p["provedor"] == "Claude Code" and p["plano"]), "")
        linhas += presets_com_caminho_fixo(achados["maestri"], plano_claude, medidores_agy)
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
    linhas += resumo_linhas(pools, avisos)
    print("\n".join(linhas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
