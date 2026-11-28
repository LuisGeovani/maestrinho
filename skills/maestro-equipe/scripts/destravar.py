"""Reconhece pedidos de shell e banners de abertura nas telas do Maestri."""

import re
from dataclasses import dataclass

from configurar_antigravity import REGRAS_ALLOW, REGRAS_DENY, SEG


# Os textos literais dos menus de shell ainda não foram capturados ao vivo.
# Cada layout exige opções de execução única e de recusa, com teclas explícitas.
MENUS = {
    "agy": (
        r"(?:allow (?:this (?:shell )?command|running (?:this|the) command)|run (?:this command )?outside (?:the )?sandbox"
        r"|(?:this )?command requires approval)",
        r"allow(?: once| for this command| this time)?|yes,? once",
        r"deny|reject|cancel|don't allow|no",
    ),
    "codex": (
        r"(?:would you like to run (?:the following|this) command|allow (?:this|the) command"
        r"|approve (?:this|the) command|run this command)",
        r"yes,? proceed|allow once|approve once",
        r"no(?:, and tell Codex what to do differently)?|deny|reject|cancel",
    ),
    "claude": (
        r"do you want to proceed",
        r"yes|allow once",
        r"no(?:, and tell Claude what to do differently)?|deny|reject|cancel",
    ),
}
ABERTURA = {
    "codex": r"(?:_\s*)?(?:OpenAI )?Codex\s+\(v?\d+\.\d+(?:\.\d+)?[^)]*\)",
    "claude": r"Claude Code\s+v?\d+\.\d+(?:\.\d+)?(?:[-+][\w.-]+)?",
    "agy": r"(?:Antigravity CLI|agy)\s+v?\d+\.\d+(?:\.\d+)?(?:[-+][\w.-]+)?",
}
RE_PROMPT_VAZIO = re.compile(r"^[\s│┃║╎]*[>›❯]\s*(?:Ask (?:Codex|anything).*|Try [\"“].*)?$", re.I)
RE_LINHA = re.compile(r"^[ \t│┃║╎╭╰┌└─━═ >›❯]+")
RE_OPCAO = re.compile(r"(?:(\d+)\. +)?(.+?)(?: +\((y|n|esc|escape)\))?", re.I)
RE_COMANDO_ROTULADO = re.compile(r"(?:shell )?command(?: to run)? *: *(\S.*)", re.I)
RE_COMANDO = re.compile(r"(?:(?:shell |bash |run )?command(?: to run)? *: *|\$ +)(\S.*)", re.I)
RE_BLOCO_SHELL = re.compile(r"(?:Bash(?: command)?|Run command):?", re.I)
RE_COMANDO_CLAUDE = re.compile(r"(?:Bash|Run) command *: *(\S.*)", re.I)
RE_ATIVIDADE = re.compile(
    r"\[pasted text\b|esc to interrupt|"
    r"^\s*[•●⏺✻✽⏳]|^\s*(?:working|thinking|running|executing|worked for|tool call"
    r"|ran|searched|edited|executando|trabalhando)\b", re.I,
)
RE_RAIZ_GIT = re.compile(r"^git -C (?:\.\./\.\./\.\.|\.\.\\\.\.\\\.\.) ")
RE_CONTROLE = re.compile(r"[\x00-\x1f\x7f-\x9f]")
RE_EXPRESSAO_SHELL = re.compile(r"[(){}]")
RE_PENDENTE = re.compile(
    r"(?:\ballow\b.*\?|\bapprove\b.*\?|permission (?:required|needed)|needs? (?:your )?permission"
    r"|waiting for (?:your )?(?:approval|confirmation)|requires approval|approval (?:needed|required)|allow once|approve once"
    r"|trust (?:this|the) (?:folder|files|contents)|do you want to proceed|would you like to run .*command"
    r"|run (?:this command )?outside (?:the )?sandbox|permitir|\(y/n\))",
    re.I,
)

ALLOW = tuple(re.compile(regra[len("command(regex:"):-1]) for regra in REGRAS_ALLOW)
DENY = tuple(re.compile(regra[len("command(regex:"):-1]) for regra in REGRAS_DENY)
RE_SEGURO = re.compile(SEG + "+")


@dataclass(frozen=True)
class Pedido:
    comando: str
    titulo: str
    aprovar: str | None = None
    negar: str | None = None

    @property
    def chave(self):
        if self.aprovar and self.negar:
            return self.comando, self.aprovar, self.negar
        return self.comando, self.titulo


def _linha(texto):
    if texto.lstrip().startswith(("│", "┃", "║", "╎", "╭", "╰", "┌", "└")):
        texto = texto.rstrip(" \t│┃║╎╮╯┐┘")
    return RE_LINHA.sub("", texto).rstrip(" ")


def _tecla(linha, rotulo, cli):
    opcao = RE_OPCAO.fullmatch(linha)
    if not opcao or not re.fullmatch(rotulo, opcao[2], re.I):
        return None
    numero, atalho = opcao[1], opcao[3]
    if cli == "codex":
        chave = (atalho or "").lower()
        return "\\e" if chave in ("esc", "escape") else chave or None
    if cli == "agy" and opcao[2].casefold() == "allow" and numero != "1":
        return None
    return numero if numero and len(numero) == 1 else None


def _cli(cli):
    return {"antigravity": "agy", "claude code": "claude"}.get(cli, cli)


def pedido_permissao(texto, cli):
    brutas = [linha for linha in texto.splitlines() if linha.strip()][-25:]
    # Um compositor vazio ao fim da tela indica que o menu antigo já fechou.
    inicio = max((i + 1 for i, linha in enumerate(brutas) if RE_PROMPT_VAZIO.fullmatch(linha)), default=0)
    linhas = [limpa for linha in brutas[inicio:] if (limpa := _linha(linha))]
    cli = _cli(cli)
    titulo, sim, nao = MENUS.get(cli, (r"(?!)", None, None))
    for i in range(len(linhas) - 1, -1, -1):
        linha = linhas[i]
        conhecido = re.fullmatch(titulo + r"[?:]?", linha, re.I)
        if not conhecido and not RE_PENDENTE.search(linha):
            continue
        # A opção pode casar o detector genérico; prefira o título imediatamente acima.
        if _tecla(linha, sim or r"(?!)", cli) or re.match(r"^\d+\. ", linha):
            continue
        depois = linhas[i + 1:i + 7]
        teclas = [(_tecla(item, sim or r"(?!)", cli), _tecla(item, nao or r"(?!)", cli)) for item in depois]
        menus = [(k, a, n) for k, (a, n) in enumerate(teclas) if a or n]
        antes = linhas[i - 1:i] if i else []
        trecho = depois[:menus[0][0]] if menus else depois[:1]
        candidatos = [m[1] for item in antes + trecho if (m := RE_COMANDO.fullmatch(item))]
        bloco_claude = cli == "claude" and i >= 2 and RE_BLOCO_SHELL.fullmatch(linhas[i - 2])
        if bloco_claude and not candidatos:
            candidatos = antes
        comando = candidatos[0] if len(candidatos) == 1 else "[comando não identificado]"
        if cli == "claude":
            shell = not trecho and (bloco_claude or antes and RE_COMANDO_CLAUDE.fullmatch(antes[0]))
        else:
            shell = bool(not trecho and antes and RE_COMANDO_ROTULADO.fullmatch(antes[0])
                         or len(trecho) == 1 and RE_COMANDO.fullmatch(trecho[0]))
        if conhecido and shell and len(candidatos) == 1 and len(menus) == 2:
            _, aprovar, _ = menus[0]
            _, _, negar = menus[1]
            if aprovar and negar and aprovar != negar:
                return Pedido(comando, linha, aprovar, negar)
        return Pedido(comando, linha)
    return None


def classificar_comando(comando):
    if comando.rstrip().endswith(("…", "...")):
        return "pendente"
    # O shell dos papéis parte de .maestri/roles/<id>. Só esta variante de -C
    # equivale ao git na raiz, sem liberar opções globais nem caminhos arbitrários.
    normalizado = RE_RAIZ_GIT.sub("git ", comando, count=1)
    if RE_CONTROLE.search(comando):
        return "pendente"
    if any(regra.fullmatch(normalizado) for regra in DENY):
        return "negado"
    # O PowerShell também avalia agrupamentos sem o cifrão coberto por SEG.
    if (RE_SEGURO.fullmatch(comando) and not RE_EXPRESSAO_SHELL.search(comando)
            and any(regra.fullmatch(normalizado) for regra in ALLOW)):
        return "aprovado"
    return "pendente"


def assinatura_banner(texto, cli):
    padrao = ABERTURA.get(_cli(cli))
    if not padrao:
        return None
    return next((limpa for linha in texto.splitlines()[:12]
                 if re.fullmatch(padrao, limpa := _linha(linha).rstrip(" ─━═"), re.I)), None)


def banner_abertura(texto, cli):
    linhas = texto.splitlines()
    if any(RE_ATIVIDADE.search(_linha(linha)) for linha in linhas):
        return None
    if any(re.match(r"^\s*[│┃║╎]*\s*[›❯]\s*\S", linha)
           and not RE_PROMPT_VAZIO.fullmatch(linha) for linha in linhas):
        return None
    if any(RE_PROMPT_VAZIO.fullmatch(linha) for linha in linhas[-8:]):
        return assinatura_banner(texto, cli)
    return None
