"""Monta o papel de um produtor a partir dos blocos de references/papeis.md.

Uso:
    python criar_papel.py "<Nome>" --projeto "<Projeto>" --raiz "<RAIZ>" --modelo "<Modelo>"
        --effort <e> --familia <Claude|Gemini|GPT|aberto> --perfis "<Batedor,Volume,...>"
        [--pastas "..."] [--entrega "<pasta>"] [--ferramenta agy|codex|opencode] [--aplicar]

Lê o próprio papeis.md (modelo de papel, linhas de perfil, bloco comum e bloco da ferramenta):
o texto não é copiado para este script. Grava <RAIZ>/.maestri/papeis/<Nome>.md (UTF-8 sem BOM).
Com --aplicar, roda `maestri role create` (ou `maestri role write`, se `role show` achar o papel)
e confere com `role show` se o texto não ficou truncado; isso só funciona no terminal Maestro.
Nos campos de caminho (<RAIZ>, --pastas, --entrega) vão barras normais: o CLI do Maestri decodifica \\n e \\t
nos argumentos, e o Windows aceita as duas barras.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

PAPEIS = Path(__file__).resolve().parent.parent / "references" / "papeis.md"
FAMILIAS = {"claude": "Claude", "gemini": "Gemini", "gpt": "GPT", "aberto": "aberto"}
FERRAMENTAS = {"agy": "Bloco do Antigravity", "codex": "Bloco do Codex", "opencode": "Bloco do OpenCode"}
PADRAO_PASTAS = "as indicadas em cada despacho"
PADRAO_ENTREGA = "nenhuma (o resultado fica em .maestri/ e no relatório)"


# Campo do modelo: <NOME>, <FAMILIA>, <PASTA_ENTREGA>, <FAMÍLIA>... (3+ letras maiúsculas, com acento e _)
CAMPO = re.compile(r"<([A-ZÀ-ÖØ-Þ_]{3,})>")


class Erro(Exception):
    pass


def barras_normais(caminho):
    """Só nos campos de caminho: o CLI do Maestri decodifica \\n e \\t nos argumentos."""
    return caminho.replace("\\", "/")


def sem_acento(texto):
    base = unicodedata.normalize("NFD", texto)
    return "".join(c for c in base if unicodedata.category(c) != "Mn").casefold().strip()


def ler_papeis():
    """Devolve (seções {título: [linhas]}, na ordem do arquivo)."""
    if not PAPEIS.exists():
        raise Erro(f"não achei {PAPEIS}")
    secoes, atual = {}, None
    for linha in PAPEIS.read_text(encoding="utf-8-sig").splitlines():
        if linha.startswith("## "):
            atual = linha[3:].strip()
            secoes[atual] = []
        elif atual is not None:
            secoes[atual].append(linha)
    return secoes


def secao(secoes, prefixo):
    for titulo, linhas in secoes.items():
        if titulo.startswith(prefixo):
            return linhas
    raise Erro(f'papeis.md sem a seção "{prefixo}..."')


def bloco_de_codigo(linhas):
    """Texto do 1º bloco ``` ... ``` da seção."""
    dentro, saida = False, []
    for l in linhas:
        if l.strip().startswith("```"):
            if dentro:
                return "\n".join(saida).strip()
            dentro = True
        elif dentro:
            saida.append(l)
    raise Erro("bloco ``` não encontrado ou não fechado em papeis.md")


def linhas_de_perfil(secoes):
    """{nome do perfil: texto} das linhas '- **Nome:** texto' da seção do modelo de papel."""
    perfis = {}
    for l in secao(secoes, "Modelo de papel"):
        m = re.match(r"^- \*\*(.+?):\*\*\s*(.+)$", l.strip())
        if m:
            perfis[m.group(1).strip()] = m.group(2).strip()
    if not perfis:
        raise Erro("papeis.md sem linhas de perfil")
    return perfis


def escolher_perfis(pedidos, perfis):
    por_nome = {sem_acento(n): n for n in perfis}
    escolhidos = []
    for p in [x for x in pedidos.split(",") if x.strip()]:
        nome = por_nome.get(sem_acento(p))
        if nome is None:
            raise Erro(f'perfil "{p.strip()}" não existe; use: {", ".join(perfis)}')
        if nome not in escolhidos:
            escolhidos.append(nome)
    if not escolhidos:
        raise Erro("--perfis vazio")
    return escolhidos


def montar(args, raiz_texto):
    secoes = ler_papeis()
    perfis = linhas_de_perfil(secoes)
    escolhidos = escolher_perfis(args.perfis, perfis)

    modelo = bloco_de_codigo(secao(secoes, "Modelo de papel"))
    cabecalho = []
    for l in modelo.splitlines():
        if l.startswith("+"):
            break
        cabecalho.append(l)
    cabecalho = " ".join(cabecalho).strip()

    texto_perfis = " ".join(f"{n}: {perfis[n]}" for n in escolhidos)
    valores = {
        "NOME": args.nome,
        "PROJETO": args.projeto,
        "RAIZ": raiz_texto,
        "MODELO": args.modelo,
        "EFFORT": args.effort,
        "FAMILIA": FAMILIAS[args.familia.casefold()],
        "PERFIS": texto_perfis.rstrip("."),
        "PASTAS": barras_normais(args.pastas or PADRAO_PASTAS).rstrip("."),
        "ENTREGA": barras_normais(args.entrega or PADRAO_ENTREGA).rstrip("."),
    }

    def trocar(m):
        if m.group(1) not in valores:
            raise Erro(f"papeis.md tem o campo <{m.group(1)}> que o script não conhece")
        return valores[m.group(1)]

    partes = [cabecalho, bloco_de_codigo(secao(secoes, "Bloco comum"))]
    if args.ferramenta:
        partes.append(bloco_de_codigo(secao(secoes, FERRAMENTAS[args.ferramenta])))
    texto = "\n".join(partes)
    # Troca única: o que o usuário digitou não é reprocessado (um "<APP>" num valor fica como está).
    # Campo desconhecido no papeis.md levanta Erro em trocar(). <ID> (2 letras) não é campo.
    return CAMPO.sub(trocar, texto)


def nome_de_arquivo(nome):
    return re.sub(r'[\\/:*?"<>|]', "_", nome).strip() or "papel"


def gravar(raiz, nome, texto):
    pasta = raiz / ".maestri" / "papeis"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{nome_de_arquivo(nome)}.md"
    destino.write_bytes((texto + "\n").encode("utf-8"))  # UTF-8 sem BOM, LF
    return destino


def achar_maestri():
    exe = shutil.which("maestri") or os.environ.get("MAESTRI_CLI")
    if not exe:
        raise Erro("maestri não está no PATH (nem em $MAESTRI_CLI)")
    return exe


def rodar(args):
    p = subprocess.run(args, capture_output=True, timeout=60)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def papel_existe(exe, nome):
    """Pergunta ao próprio Maestri (role show): nome parecido não conta, só o papel exato."""
    rc, saida, erro = rodar([exe, "role", "show", nome])
    junto = saida + erro
    if "not the Maestro" in junto:
        raise Erro("o terminal não é o Maestro: só ele cria ou grava papéis")
    if re.search(r"not found|no such|does not exist|unknown role|n[ãa]o encontr", junto, re.I):
        return False
    return rc == 0 and bool(saida.strip())


def compacto(texto):
    return " ".join(texto.split())


def conferir(exe, nome, texto):
    """Depois do create/write: o role show traz o começo e o fim do texto? Devolve um aviso ou None."""
    rc, saida, erro = rodar([exe, "role", "show", nome])
    if rc != 0:
        return f"não consegui conferir com role show: {(erro or saida).strip()[:120]}"
    lido, esperado = compacto(saida), compacto(texto)
    if esperado[:80] not in lido or esperado[-80:] not in lido:
        return "o papel gravado parece truncado (o role show não traz o começo e o fim do texto); confira com maestri role show"
    return None


def aplicar(nome, texto):
    """Devolve (verbo, aviso). O texto vai como está; só os campos de caminho já vieram com barras normais."""
    exe = achar_maestri()
    verbo = "write" if papel_existe(exe, nome) else "create"
    rc, saida, erro = rodar([exe, "role", verbo, nome, texto])
    if rc != 0:
        raise Erro(f"maestri role {verbo} falhou: {(erro or saida).strip()[:200]}")
    return verbo, conferir(exe, nome, texto)


def principal():
    ap = argparse.ArgumentParser(description="Monta e grava o papel de um produtor a partir de papeis.md")
    ap.add_argument("nome", help="codinome do produtor (nome do papel)")
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--raiz", required=True, help="caminho absoluto do projeto")
    ap.add_argument("--modelo", required=True, help='ex.: "Gemini 4 Hydrogen"')
    ap.add_argument("--effort", required=True)
    ap.add_argument("--familia", required=True, help="Claude, Gemini, GPT ou aberto")
    ap.add_argument("--perfis", required=True, help='ex.: "Batedor,Volume" (nomes das linhas de perfil de papeis.md)')
    ap.add_argument("--pastas", help="pastas em que costuma trabalhar")
    ap.add_argument("--entrega", help="pasta de entrega (fora de .maestri/)")
    ap.add_argument("--ferramenta", choices=list(FERRAMENTAS))
    ap.add_argument("--aplicar", action="store_true", help="roda maestri role create/write")
    args = ap.parse_args()
    args.familia = args.familia.strip().casefold()
    if args.familia not in FAMILIAS:
        raise Erro("--familia deve ser Claude, Gemini, GPT ou aberto")

    sys.stdout.reconfigure(encoding="utf-8")
    raiz = Path(args.raiz).expanduser().resolve()
    if not raiz.is_dir():
        raise Erro(f"--raiz não é uma pasta: {raiz}")
    texto = montar(args, raiz.as_posix())
    destino = gravar(raiz, args.nome, texto)
    print(f"Papel gravado: {destino} ({len(texto)} caracteres, perfis: {args.perfis})")
    if "\\" in texto:
        print("AVISO: o texto tem barra invertida; o CLI do Maestri decodifica \\n e \\t nos argumentos.")
    if not args.aplicar:
        print("Não aplicado (use --aplicar no terminal Maestro).")
        return 0
    verbo, aviso = aplicar(args.nome, texto)
    print(f'Aplicado: maestri role {verbo} "{args.nome}"')
    if aviso:
        print(f"AVISO: {aviso}")
        return 3
    print("Conferido com maestri role show.")
    return 0


def main():
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        return principal()
    except Erro as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
