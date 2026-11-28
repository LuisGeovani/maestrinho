"""Despacha tarefas aos produtores do Maestri e resume o retorno de cada um.

Uso:
    python maestri_batch.py despacho.md [--raiz PASTA] [--maestro NOME] [--mostrar] [--espera MIN]
    python maestri_batch.py - < despacho.md          (lê do stdin)

Formato do despacho (texto puro, sem JSON e sem escapar nada):

    Texto opcional antes do primeiro ###: vai no início de TODOS os prompts.
    ### Prisma | PJ-T3
    prompt da tarefa, com qualquer caractere (aspas, C:\\caminhos, acentos)
    ### Lente | PJ-T3-REV
    outro prompt

Cada seção é "### <nome exato do agente> | <ID da tarefa>". Use um ID por relatório. O script:
- descobre o nome real do Maestro em `maestri list` (seção You:) e confere os destinos;
- avisa quando um despacho Codex não contém critério de pronto nem comando de validação;
- cria <raiz>/.maestri/relatorios/ e acrescenta a cada prompt o rodapé do relatório:
  o produtor grava o relatório completo em .maestri/relatorios/<ID>.md e avisa com
  um ping curto `maestri ask "<Maestro>" "<ID> <status>: .maestri/relatorios/<ID>.md"`;
- monta o JSON com o escape certo e envia com `maestri ask --batch` (em lotes de até
  ~24 mil caracteres por chamada, por causa do limite de linha de comando do Windows);
- confere terminal e relatório quando perde a confirmação e só repete um envio rejeitado;
- resume cada retorno: relatório recebido, pedido de permissão pendente, ou últimas linhas.

Rode em background (run_in_background) e encerre o turno: o retorno chega sozinho.
Saída 0 = todos responderam; 1 = algum falhou ou ficou pendente; 2 = erro no despacho.
"""
import argparse
import errno
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from cotas import LOG_DISTRIBUICAO, formatar_distribuicao, ler_cotas
from inventario import (
    CLI_PRESET, MEDIDORES_GEMINI_CONHECIDOS, MODELO_PRESET,
    comando_da_formacao, comando_preset, ferramenta_e_pool, rodar,
)

LIMITE_JSON = 24000
LIMIAR_EQUILIBRIO = 15
LIMIAR_GEMINI_SEMANAL = 80
LIMIAR_GEMINI_5H = 90
LIMIAR_CUSTO = 300
PESOS_MODELO = {
    "luna": 1,
    "haiku": 1,
    "flash": 1,
    "opencode grátis": 0,
    "terra": 10,
    "hydrogen": 15,
    "argon": 15,
    "sol": 20,
    "sonnet": 20,
    "neon": 30,
    "orchestrator": 30,
    "opus": 40,
    "astra": 80,
    "fable": 80,
}
PESOS_EFFORT = {
    "low": 1,
    "medium": 2,
    "high": 4,
    "xhigh": 8,
    "max": 16,
    "ultra": 16,
}
PESOS_TAMANHO = {
    "P": 1,
    "M": 3,
    "G": 9,
}
COLUNAS_CLI = ("ferramenta", "cli", "preset", "preset/modelo", "modelo", "modelo · effort", "modelo/effort", "pool")
RE_PRESET_FORMACAO = re.compile(r"^(.+?)\s*\(preset\s+([^)+]+)(?:\s*\+\s*`--command\s+(.+?)`)?", re.I)
RE_CONTA_FORMACAO = re.compile(r'\bconta\s*[:=]?\s*(?:"([^"]+)"|([^\s),;|]+))', re.I)
RE_CONTA_LIST = re.compile(r'\baccount\s*:\s*(?:"([^"]+)"|([^,|\s]+))', re.I)
RE_MOTIVO_POOL = re.compile(r"^Motivo pool:\s*(\S.*)", re.I)
RE_TAMANHO = re.compile(r"^Tamanho:\s*([PMG])(?:\s|$)", re.I)
RE_ROTEAMENTO = re.compile(r"^Roteamento:\s*(\S.*)", re.I)
RE_JUSTIFICATIVA_CUSTO = re.compile(
    r"\bdescartado:\s*(?!porque\b)[^\s|][^|]*?\bporque(?:\s*:\s*|\s+)[^\s|]",
    re.I,
)
RE_MODELO_PESO = re.compile(
    r"\b(orchestrator|luna|haiku|flash|terra|hydrogen|argon|sol|sonnet|neon|opus|astra|fable)\b",
    re.I,
)
RE_EFFORT = re.compile(r"\b(xhigh|low|medium|high|max|ultra)\b", re.I)
RE_MODELO_TELA = re.compile(
    r"\b(gemini[-\s]\d+(?:\.\d+)?[-\s](?:neon|hydrogen|argon|flash|carbon)"
    r"|gemini-pro-orchestrator-(?:neon|g1-pro)"
    r"|claude[-\s]+(?:opus|sonnet|haiku|fable)(?:[-\s]+\d+(?:\.\d+)?)?"
    r"|gpt[-\s]+\d+(?:\.\d+)?[-\s]+(?:luna|terra|sol|astra)"
    r"|(?:opencode/)?[^\s]+-free)\b",
    re.I,
)
RE_MARCADOR_RODAPE = re.compile(
    r"(?:shift\+tab|for shortcuts|auto mode|accept edits|bypass permissions|"
    r"esc to interrupt|context left|\d+%\s*left|\b(?:Build|Plan)\s*·|\bctrl\+\w)",
    re.I,
)
RE_STATUS_AGY_AUTO = re.compile(
    r"\((?:xhigh|low|medium|high|max|ultra)\)\s+auto\b",
    re.I,
)
RE_STATUS_CODEX_RODAPE = re.compile(
    r"\bgpt-\d+(?:\.\d+)?-(?:luna|terra|sol|astra)\b[^·\n]*\b(?:xhigh|low|medium|high|max|ultra)\b\s*·",
    re.I,
)
RE_URL = re.compile(r"\b(?:https?|file)://\S+", re.I)
RE_CAMINHO_BARRA = re.compile(r"(?<![:\w])(?:[A-Za-z]:[\\/]|\.{1,2}[\\/]|[\w.-]+[\\/])[\w.@-]+(?:[\\/][\w.@-]+)*[\\/]?")
RE_ARQUIVO_EXT = re.compile(
    r"\b[\w.-]+\.(?:py|js|jsx|ts|tsx|mjs|cjs|json|md|txt|yaml|yml|toml|ini|cfg|html|css|scss|"
    r"sql|sh|ps1|bat|cmd|go|rs|java|kt|swift|c|cpp|h|hpp|rb|php|dart|xml|csv|log|env)\b",
    re.I,
)
RE_SECAO = re.compile(r"^###\s+(.+?)\s*(?:\|\s*([A-Za-z0-9][\w.\-]*))?\s*$")
RE_PERMISSAO = re.compile(
    r"(do you want to"
    r"|run this command"
    r"|allow (this|once|always|calling|access|running|reading|writing|editing|the (command|tool|action|file))"
    r"|needs? (your )?permission"
    r"|permission (required|to (run|use|execute|access|edit|write))"
    r"|waiting for (your )?(approval|confirmation)"
    r"|approve (this|the|command|tool)"
    r"|bypass sandbox"
    r"|run (this )?outside"
    r"|requires approval"
    r"|permitir"
    r"|\(y/n\)"
    r"|trust (this|the) (folder|files|contents)"
    r"|❯\s*1\.\s*yes)",
    re.I,
)
CONFIRMACAO_PERDIDA = "confirmação de entrega perdida"
RE_LOTE_REJEITADO = re.compile(
    r"(?:maestri:\s*)?Invalid --batch JSON\. Expected a non-empty agent-to-prompt object\.", re.I,
)
RE_DESTINO_REJEITADO = re.compile(
    r"(?:maestri:\s*)?(?:prompt (?:was )?not (?:sent|delivered)|"
    r"(?:agent|terminal)(?: \"(?P<agente>[^\"]+)\")? (?:is not connected|not found|is still starting(?: up)?)|"
    r"not connected)[.!]?",
    re.I,
)
RE_FERRAMENTA = re.compile(r"\b(codex|claude(?: code)?|antigravity|agy|opencode)\b", re.I)
RE_MODELO_CODEX = re.compile(r"\bgpt-\d+(?:\.\d+)?-(?:luna|terra|sol|astra)\b", re.I)
RE_MODELO_AGY_TELA = re.compile(
    r"\b(gemini[-\s]\d+(?:\.\d+)?[-\s](?:neon|hydrogen|argon|flash|carbon)"
    r"|gemini-pro-orchestrator-(?:neon|g1-pro))\b",
    re.I,
)
RE_METADADOS = re.compile(r'\b(?:tool|cli|agent[_ ]?type|ferramenta|preset|model)\s*:\s*("[^"]+"|[^,|]+)', re.I)
RE_TELA_CODEX = re.compile(r"^(?:[^\w\n]|_)*(?:OpenAI Codex\b|Ask Codex\b)", re.I | re.M)
RE_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
RE_CRITERIO = re.compile(
    r"\bpront[oa][ \t]+quando[ \t]*\**[ \t]*:|"
    r"^[ \t]*(?:[-*]\s+)?(?:#{1,6}[ \t]+)?\**(?:"
    r"(?:(?:está|fica|considere)\s+)?pront[oa]\s+quando\b|"
    r"crit[eé]rios?(?:\s+(?:de\s+)?(?:aceite|aceitação|pronto|conclusão))?\**\s*[:(]|"
    r"aceite\**\s*:|acceptance criteria\b|definition of done\b)",
    re.I | re.M,
)
RE_COMANDO_VALIDACAO = re.compile(
    r"\b(?:valide|verifique|teste)[ \t]+com[ \t]*:?[ \t]*(?:"
    r"`[^\s`][^`]*`|\.[/\\]\S+|[\w./\\-]+[ \t]+--?\w|"
    r"(?:bash|sh|pwsh|powershell|python(?:3)?|node)[ \t]+\S+)|"
    r"\bcomandos?\s+(?:de\s+)?(?:valida[cç][aã]o|teste)\**[ \t]*:\s*\S|"
    r"\b(?:"
    r"pytest|(?:python(?:3)?|py)\s+-m\s+(?:py_compile|compileall|unittest|pytest)|"
    r"(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:test|lint|check|typecheck|build)(?![\w-])|"
    r"(?:go|cargo|dotnet)\s+test\b|"
    r"(?:ruff\s+check|eslint|tsc\s+--noEmit|mvn\s+test|"
    r"(?:make|gradle|gradlew)\s+(?:test|check)|"
    r"git\s+diff\s+--check)\b)",
    re.I,
)

RODAPE = """
---
RELATORIO (obrigatorio ao terminar, ou se bloquear):
1. Grave o relatorio completo no arquivo {arquivo} (UTF-8; a pasta ja existe), um campo por linha:
   TAREFA: {id}
   STATUS: pronto, parcial ou bloqueado
   VEREDITO: aprovado ou reprovado (so em revisao)
   ARQUIVOS: o que criou ou alterou
   VALIDACAO: comandos rodados e resultado
   PENDENCIAS: o que falta ou depende de decisao
   VISAO: opcional, so discordancia ou risco real
   Esse arquivo e a unica escrita permitida mesmo em tarefa SOMENTE LEITURA.
2. Depois rode exatamente este comando (se nao terminou, troque a palavra pronto por parcial ou bloqueado):
   maestri ask "{maestro}" "{id} pronto: .maestri/relatorios/{id}.md"
   O aviso e curto de proposito: nada de aspas extras, barras invertidas ou texto longo nele.
"""
RE_STATUS = re.compile(r"STATUS\s*[:=]\s*\**\s*(pronto|parcial|bloqueado|aprovado|reprovado)", re.I)
RE_VEREDITO = re.compile(r"VEREDITO\s*[:=]\s*\**\s*(aprovado|reprovado)", re.I)
FIM_RODAPE = "O aviso e curto de proposito"
RE_MOLDURA = re.compile(r"^[\s─━═╌┄\-_>❯›?⏵]*$|auto mode|shift\+tab|for shortcuts|bypass permissions|accept edits")


def texto_nao_enviado(saida):
    """O prompt ficou parado na caixa de entrada (despacho durante a abertura do agente)."""
    linhas = [l for l in (saida or "").splitlines() if l.strip() and not RE_MOLDURA.search(l.strip())]
    return any(FIM_RODAPE in l for l in linhas[-3:])


PRONTO = ("for shortcuts", "shift+tab", "Ask anything", "Ask Codex", "Try \"", "Build ·", "Plan ·", "esc to interrupt")
RE_CONFIANCA = re.compile(r"trust (this|the) (folder|contents|files)|Do you trust|Trust this folder", re.I)
RE_PASTA_PAPEL = re.compile(r"\.maestri[\\/]+roles[\\/]+[0-9a-f\-]{8,}", re.I)
RE_SIM_DESTACADO = re.compile(r"[>›❯]\s*(\d\.\s*)?(yes|trust|sim|confiar)", re.I)


def tela(exe, agente, timeout=None):
    p = subprocess.run([exe, "check", agente], capture_output=True, stdin=subprocess.DEVNULL, timeout=timeout)
    return p.stdout.decode("utf-8", "replace")


def esperar_pronto(exe, agente, maximo=90):
    """Despachar para um agente que ainda está abrindo corta ou perde o texto (testado).
    Espera a tela estabilizar com o campo de prompt visível. Devolve None ou o motivo."""
    limite, anterior, aprovados = time.time() + maximo, None, 0
    while time.time() < limite:
        atual = tela(exe, agente)
        if RE_CONFIANCA.search(atual):
            # Pasta de papel criada pelo próprio Maestri dentro do projeto, com "sim/confiar"
            # já destacado: aprova sozinho (Antigravity e Codex perguntam na 1ª vez em cada pasta).
            if aprovados < 2 and RE_PASTA_PAPEL.search(atual) and RE_SIM_DESTACADO.search(atual):
                subprocess.run([exe, "ask", agente, "--raw", "\\r"], capture_output=True, stdin=subprocess.DEVNULL)
                aprovados += 1
                print(f"aviso: aprovei a confiança da pasta de papel do Maestri para {agente}")
                anterior = None
                time.sleep(6)
                continue
            return "pedido de confiança de pasta fora de .maestri/roles: confira com maestri check \"%s\"" % agente
        if anterior is not None and atual == anterior and any(m in atual for m in PRONTO):
            return None
        anterior = atual
        time.sleep(4)
    return None  # segue mesmo assim; o resumo final aponta se o texto ficou parado


def data_relatorio(arq):
    try:
        return arq.stat().st_mtime_ns
    except OSError:
        return None


def relatorio_novo(relatorio, desde):
    if relatorio is None:
        return False
    arq, anterior = relatorio
    atual = data_relatorio(arq)
    return atual is not None and atual != anterior and atual / 1e9 >= desde - 2


def janela_pedido(texto, linhas=25):
    """Acha o último pedido de permissão na tela e devolve (janela, linha casada), ou None.

    As linhas de moldura (barra de status, spinner, atalhos) são descartadas antes da busca,
    senão o trecho mostrado seria só enfeite e o pedido de verdade ficaria de fora.
    A janela tem até 3 linhas: a casada, uma antes e uma depois."""
    limpas = [l for l in (texto or "").splitlines() if l.strip() and not RE_MOLDURA.search(l.strip())][-linhas:]
    for i in range(len(limpas) - 1, -1, -1):
        if RE_PERMISSAO.search(limpas[i]):
            return limpas[max(0, i - 1):i + 2], limpas[i]
    return None


def avisar_pedido(exe, agente, avisados):
    """Imprime o pedido de permissão uma única vez por pedido.

    A deduplicação usa a linha que casou, não a janela inteira: spinner, relógio ou saída
    nova ao redor mudam a cada sondagem e não podem virar spam. O aviso se rearma quando a
    tela deixa de ter pedido, para um pedido novo ser anunciado."""
    try:
        achado = janela_pedido(tela(exe, agente, timeout=5))
    except (OSError, subprocess.TimeoutExpired):
        return
    if not achado:
        avisados.pop(agente, None)
        return
    janela, casada = achado
    if avisados.get(agente) == casada:
        return
    avisados[agente] = casada
    print(f"PERMISSAO pendente: {agente}", flush=True)
    for linha in janela:
        print("   " + linha[:200], flush=True)


def esperar_terminar(exe, pendentes, desde, minutos):
    """Espera, com um prazo global único, os relatórios que ainda faltam.

    O maestri ask --batch volta quando o agente fica quieto, não quando termina: por isso o
    disco de todos os pendentes é conferido a cada 10 s (quem grava sai da lista) e a tela de
    cada um que sobra é conferida a cada 30 s, anunciando pedidos de permissão sem repetir e
    sem aprovar nada. O prazo total é minutos, não minutos por agente.
    Devolve o conjunto de agentes que continuaram sem relatório quando estourou."""
    limite = time.time() + minutos * 60
    faltam, avisados, proxima_tela = dict(pendentes), {}, time.time()
    while faltam:
        for agente, relatorio in list(faltam.items()):
            if relatorio_novo(relatorio, desde):
                del faltam[agente]
        if not faltam:
            break
        agora = time.time()
        if agora >= limite:
            break
        if agora >= proxima_tela:
            proxima_tela = agora + 30
            for agente in faltam:
                avisar_pedido(exe, agente, avisados)
        time.sleep(10)
    return set(faltam)


def maestri_exe():
    exe = shutil.which("maestri") or os.environ.get("MAESTRI_CLI")
    if not exe:
        print("ERRO: maestri não encontrado no PATH nem em MAESTRI_CLI.")
        sys.exit(2)
    return exe


def ler_list(exe):
    p = subprocess.run([exe, "list"], capture_output=True, stdin=subprocess.DEVNULL)
    saida = p.stdout.decode("utf-8", "replace")
    if p.returncode != 0:
        print(f"ERRO em maestri list (código {p.returncode}): {p.stderr.decode('utf-8', 'replace').strip()}")
        print("Dica: rode `maestri debug`.")
        sys.exit(2)
    maestro, nomes, secao = None, set(), None
    for linha in saida.splitlines():
        if re.match(r"^\S.*:\s*$", linha):
            secao = linha.strip().rstrip(":").lower()
            continue
        m = re.search(r'name:\s*"([^"]+)"', linha)
        if not m:
            continue
        if secao == "you" and maestro is None:
            maestro = m.group(1)
        else:
            nomes.add(m.group(1))
    return maestro, nomes, saida


def ler_despacho(texto):
    comum, secoes, atual = [], [], None
    for linha in texto.splitlines():
        m = RE_SECAO.match(linha)
        if m:
            atual = {"agente": m.group(1).strip(), "id": m.group(2), "linhas": []}
            secoes.append(atual)
        elif atual is None:
            comum.append(linha)
        else:
            atual["linhas"].append(linha)
    return "\n".join(comum).strip(), secoes


def ferramenta(texto):
    achado = RE_FERRAMENTA.search(texto)
    if achado:
        return achado.group(1).lower()
    return "codex" if RE_MODELO_CODEX.search(texto) else None


def ferramentas_list(texto):
    ferramentas = {}
    for linha in texto.splitlines():
        nome = re.search(r'name:\s*"([^"]+)"', linha)
        if nome:
            for campo in RE_METADADOS.findall(linha[nome.end():]):
                cli = ferramenta(campo)
                if cli:
                    ferramentas[nome.group(1)] = cli
                    break
    return ferramentas


def contas_list(texto):
    contas = {}
    for linha in texto.splitlines():
        nome = re.search(r'name:\s*"([^"]+)"', linha)
        if nome:
            m = RE_CONTA_LIST.search(linha[nome.end():])
            if m:
                valor = (m.group(1) or m.group(2) or "").strip()
                if valor and valor != "-":
                    contas[nome.group(1)] = valor
    return contas


def ler_formacao(raiz):
    """Lê as linhas das tabelas que identificam terminais da formação."""
    try:
        texto = (raiz / ".maestri" / "equipe.md").read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return {}
    formacao = {}
    coluna_nome, titulos = None, []
    nomes = ("terminal", "agente", "nome", "produtor")
    for linha in texto.splitlines():
        if not linha.lstrip().startswith("|"):
            coluna_nome = None
            continue
        campos = [c.strip(" *`\t") for c in linha.strip().strip("|").split("|")]
        chaves = [c.casefold() for c in campos]
        if any(c in chaves for c in nomes) and any(c in chaves for c in COLUNAS_CLI):
            titulos = chaves
            coluna_nome = next(titulos.index(c) for c in nomes if c in titulos)
        elif coluna_nome is not None and coluna_nome < len(campos) and not all(
            re.fullmatch(r":?-+:?", c) for c in campos
        ):
            formacao[campos[coluna_nome]] = dict(zip(titulos, campos))
    return formacao


def ferramentas_formacao(raiz, formacao=None):
    ferramentas = {}
    if formacao is None:
        formacao = ler_formacao(raiz)
    for agente, linha in formacao.items():
        for coluna in COLUNAS_CLI:
            if cli := ferramenta(linha.get(coluna, "")):
                ferramentas[agente] = cli
                break
    return ferramentas


def _conta_padrao(conta):
    return not conta or conta.strip().casefold() in ("padrão", "padrao", "default", "built-in")


def nome_pool(cota):
    if cota["via_claude"] == "Claude Code" and cota["plano"]:
        return f"Claude {cota['plano'].title()}"
    if cota["via_claude"] == "Antigravity":
        return "Claude and GPT models"
    if cota.get("eh_codex") or (
        cota.get("medidor", "").casefold() == "codex"
        and cota.get("provedor", "").casefold() not in ("codex", "")
    ):
        conta = cota.get("conta") or (
            "Padrão" if cota.get("provedor", "").casefold() in ("codex", "") else cota["provedor"]
        )
        return "Codex" if _conta_padrao(conta) else f"Codex (conta {conta})"
    return cota["medidor"]


def _classificar_comando(comando, plano_claude, medidores):
    cli, pool = ferramenta_e_pool(comando, plano_claude, medidores)
    if cli == "OpenCode":
        return "aberto", pool if pool == "grátis" else "desconhecido"
    if cli == "Codex":
        return "GPT", pool
    if cli == "Claude Code":
        return "Claude", pool if plano_claude else "desconhecido"
    if pool == "Claude and GPT models":
        modelo = MODELO_PRESET.search(comando)
        modelo = modelo.group(1).casefold() if modelo else ""
        return ("Claude" if modelo.startswith("claude-") else "GPT"), pool
    if cli == "Antigravity" and pool in medidores:
        return "Gemini", pool
    return "desconhecido", "desconhecido"


def _ler_tela_limpa(exe, agente, telas):
    """Lê a saída de `maestri check` sem ANSI, cacheando por agente na avaliação."""
    if not exe or not agente:
        return ""
    if agente not in telas:
        saida, _ = rodar([exe, "check", agente], timeout=3)
        telas[agente] = RE_ANSI.sub("", saida) if saida else ""
    return telas[agente]


def _eh_linha_rodape(linha):
    return bool(
        RE_MARCADOR_RODAPE.search(linha)
        or (RE_MODELO_TELA.search(linha) and RE_STATUS_AGY_AUTO.search(linha))
        or RE_STATUS_CODEX_RODAPE.search(linha)
    )


def _linhas_rodape(limpa):
    """Retorna apenas as linhas finais da tela que correspondem a uma barra de status reconhecível."""
    if not limpa:
        return []
    cauda = [l for l in limpa.splitlines() if l.strip()][-6:]
    return [l for l in cauda if _eh_linha_rodape(l)]


def _modelo_rodape_agy(exe, agente, telas=None):
    """Lê o modelo Gemini no rodapé da tela do Antigravity (via `maestri check`)."""
    limpa = _ler_tela_limpa(exe, agente, telas if telas is not None else {})
    for linha in reversed(_linhas_rodape(limpa)):
        achados = RE_MODELO_AGY_TELA.findall(linha)
        if achados:
            return re.sub(r"[^\w]+", "-", achados[-1].casefold()).strip("-")
    return ""


def _extrair_modelo_peso(texto, *, opencode=False, pool=""):
    if not texto:
        return "opencode grátis" if pool == "grátis" else None
    if pool == "grátis" or (opencode and re.search(r"(?:-free\b|\bgr[aá]tis\b|\bbig-pickle\b)", texto, re.I)):
        return "opencode grátis"
    if re.search(r"(?:-free\b|\bbig-pickle\b|\bopencode\s+gr[aá]tis\b)", texto, re.I):
        return "opencode grátis"
    m = RE_MODELO_PESO.search(texto)
    return m.group(1).lower() if m else None


def _extrair_effort(texto):
    if not texto:
        return None
    m = RE_EFFORT.search(texto)
    return m.group(1).lower() if m else None


def _modelo_effort_tela(limpa):
    """Extrai (modelo_peso, effort) apenas de uma linha de rodapé reconhecível."""
    for linha in reversed(_linhas_rodape(limpa)):
        achados = list(RE_MODELO_TELA.finditer(linha))
        if achados:
            return _extrair_modelo_peso(achados[-1].group(0)), _extrair_effort(linha)
        modelo = _extrair_modelo_peso(linha)
        if modelo is not None:
            return modelo, _extrair_effort(linha)
    return None, None


def _caminhos_distintos(linhas):
    """Conta caminhos de arquivo distintos no corpo da seção (ignorando metadados e URLs)."""
    caminhos = set()
    for linha in linhas:
        if RE_TAMANHO.match(linha) or RE_ROTEAMENTO.match(linha) or RE_MOTIVO_POOL.match(linha):
            continue
        sem_urls = RE_URL.sub(" ", linha)
        spans = []
        for m in RE_CAMINHO_BARRA.finditer(sem_urls):
            trecho = m.group(0).strip("`\"'.,;:()[]")
            if ("\\" in trecho or re.match(r"^(?:[A-Za-z]:|\.{1,2}[\\/])", trecho)
                    or RE_ARQUIVO_EXT.search(trecho) or trecho.endswith("/")):
                caminhos.add(re.sub(r"^(?:\./)+", "", trecho.replace("\\", "/")).casefold())
                spans.append((m.start(), m.end()))
        for m in RE_ARQUIVO_EXT.finditer(sem_urls):
            if any(ini <= m.start() and m.end() <= fim for ini, fim in spans):
                continue
            caminhos.add(m.group(0).strip("`\"'.,;:()[]").casefold())
    return caminhos


def _gemini_apertado(cota):
    """Gemini só trava em ≥80% na janela semanal (ou ≥90% na de 5 h)."""
    janelas = cota.get("janelas") or []
    semanais = [
        j["usado"] for j in janelas
        if j.get("usado") is not None and j.get("janela", "").casefold() in ("semanal", "weekly", "mensal", "monthly")
    ]
    cinco_h = [
        j["usado"] for j in janelas
        if j.get("usado") is not None and j.get("janela", "").casefold() == "5h"
    ]
    if semanais or cinco_h:
        return any(u >= LIMIAR_GEMINI_SEMANAL for u in semanais) or any(u >= LIMIAR_GEMINI_5H for u in cinco_h)
    return cota.get("uso_max") is not None and cota["uso_max"] >= LIMIAR_GEMINI_SEMANAL


def _conta_da_formacao(linha, ferr_bruta):
    conta_col = linha.get("conta", "").strip()
    if conta_col:
        m = RE_CONTA_FORMACAO.search(conta_col)
        return (m.group(1) or m.group(2)).strip() if m else conta_col
    for texto in (ferr_bruta, linha.get("pool", "")):
        if m := RE_CONTA_FORMACAO.search(texto or ""):
            return (m.group(1) or m.group(2)).strip()
    return ""


def _resolver_pool_codex(conta_efetiva, pools_por_nome):
    if _conta_padrao(conta_efetiva):
        return "Codex"
    alvo = f"Codex (conta {conta_efetiva})"
    return next((nome for nome in pools_por_nome if nome.casefold() == alvo.casefold()), alvo)


def destino_do_agente(exe, linha, plano_claude, medidores, comandos, telas, agente="", conta="", pools_por_nome=()):
    """Descobre (familia, pool, modelo_peso, effort) usando equipe.md e fallback na tela."""
    ferr_bruta = linha.get("ferramenta", "").strip()
    conta_formacao = _conta_da_formacao(linha, ferr_bruta)
    ferr_sem_conta = re.sub(r"\(\s*conta\s+[^)]+\)", "", ferr_bruta, flags=re.I).strip()
    modelo_col = linha.get("modelo") or next((v for k, v in linha.items() if k.startswith("modelo")), "")
    effort_col = linha.get("effort", "").strip()
    modelo_bruto = re.split(r"[·,]", re.sub(r"\s*\([^)]*\)", "", modelo_col))[0].strip()
    pool_declarado = re.sub(r"\s*\([^)]*\)", "", linha.get("pool", "")).strip()
    comando, ferramenta_declarada, preset = "", "", ""
    achado = RE_PRESET_FORMACAO.match(ferr_sem_conta)
    if achado:
        ferramenta_declarada, preset, comando_extra = achado.groups()
        preset = re.sub(r"[,;]\s*conta\s+.*$", "", preset, flags=re.I).strip()
        if comando_extra:
            comando = comando_extra.strip().strip("'\"")
        else:
            if preset not in comandos:
                detalhes, _ = rodar([exe, "preset", "show", preset], timeout=5) if exe else (None, None)
                comandos[preset] = comando_preset(detalhes)
            comando = comandos[preset]
    elif ferr_sem_conta:
        ferramenta_declarada = re.sub(r"\s*\([^)]*\)", "", ferr_sem_conta).strip()
        if ferramenta_declarada.casefold() == "agy":
            ferramenta_declarada = "Antigravity"
    if not CLI_PRESET.search(comando) and ferramenta_declarada:
        comando = comando_da_formacao(ferramenta_declarada, modelo_bruto, preset or pool_declarado or modelo_bruto)

    familia, pool = "desconhecido", "desconhecido"
    if comando:
        familia, pool = _classificar_comando(comando, plano_claude, medidores)
    if pool == "desconhecido" and pool_declarado.casefold() == "codex":
        familia, pool = "GPT", "Codex"
    if pool == "desconhecido" and pool_declarado and ferramenta_declarada.casefold() in ("antigravity", "agy", ""):
        por_nome = {m.casefold(): m for m in medidores}
        if pool_declarado.casefold() in por_nome:
            pool = por_nome[pool_declarado.casefold()]
            familia = "Gemini" if pool != "Claude and GPT models" else (
                "Claude" if "claude" in modelo_bruto.casefold() else "GPT"
            )
    if pool == "desconhecido":
        modelo_tela = _modelo_rodape_agy(exe, agente, telas)
        if modelo_tela:
            familia, pool = _classificar_comando(f"agy --model {modelo_tela}", plano_claude, medidores)

    eh_opencode = ferramenta_declarada.casefold() == "opencode" or pool == "grátis" or familia == "aberto"
    texto_modelo_formacao = modelo_col.strip() or (
        MODELO_PRESET.search(comando).group(1) if MODELO_PRESET.search(comando) else ""
    )
    modelo_nome = (
        _extrair_modelo_peso(texto_modelo_formacao, opencode=eh_opencode, pool=pool)
        if texto_modelo_formacao else None
    )
    effort_nome = _extrair_effort(f"{modelo_col} {effort_col}") or _extrair_effort(comando)

    falta_modelo = not texto_modelo_formacao
    falta_effort = effort_nome is None and modelo_nome != "opencode grátis"
    if falta_modelo or falta_effort:
        limpa = _ler_tela_limpa(exe, agente, telas)
        modelo_tela, effort_tela = _modelo_effort_tela(limpa)
        if falta_modelo:
            modelo_nome = modelo_tela or ("opencode grátis" if eh_opencode else None)
        if effort_nome is None:
            effort_nome = effort_tela
        if pool == "desconhecido" and modelo_nome in ("luna", "terra", "sol", "astra"):
            familia, pool = "GPT", "Codex"

    if pool == "Codex":
        pool = _resolver_pool_codex((conta or conta_formacao or "").strip(), pools_por_nome)
    return familia, pool, modelo_nome, effort_nome


def pool_do_destino(exe, linha, plano_claude, medidores, comandos, agente=""):
    familia, pool, _, _ = destino_do_agente(exe, linha, plano_claude, medidores, comandos, {}, agente)
    return familia, pool


def avaliar_equilibrio(exe, formacao, secoes, pools, resumo_custos=None, contas=None):
    plano_claude = next((p["plano"].title() for p in pools
                         if p["via_claude"] == "Claude Code" and p["plano"]), "")
    medidores = dict.fromkeys(p["medidor"] for p in pools if p["provedor"].casefold() == "antigravity")
    for medidor in MEDIDORES_GEMINI_CONHECIDOS:
        if medidor.casefold() not in {m.casefold() for m in medidores}:
            medidores[medidor] = None
    por_pool = {nome_pool(p): p for p in pools}
    contas = contas or {}
    menor = min((p for p in pools if p["estado"] == "ready" and p["uso_max"] is not None
                 and not p["veto_despacho"] and nome_pool(p).casefold() not in ("grátis", "opencode")
                 and p["provedor"].casefold() != "opencode"
                 and p["plano"].casefold() not in ("free", "grátis", "gratis")),
                key=lambda p: p["uso_max"], default=None)
    comandos, telas, aceitas, retencoes = {}, {}, {}, []
    for secao in secoes:
        agente, ident = secao["agente"], secao["id"] or "-"
        familia, pool, modelo_nome, effort_nome = destino_do_agente(
            exe, formacao.get(agente, {}), plano_claude, medidores, comandos, telas,
            agente, conta=contas.get(agente, ""), pools_por_nome=por_pool,
        )
        motivo = next((m.group(1).strip() for linha in secao["linhas"] if (m := RE_MOTIVO_POOL.match(linha))), None)
        tamanho = next((m.group(1).upper() for linha in secao["linhas"] if (m := RE_TAMANHO.match(linha))), None)
        if tamanho is None:
            tamanho = "M"
            print(f"aviso: {agente} | {ident}: sem 'Tamanho: P|M|G' (usando M)")
        elif tamanho == "P":
            caminhos = _caminhos_distintos(secao["linhas"])
            if len(caminhos) > 3:
                print(
                    f"aviso: {agente} | {ident}: Tamanho: P com {len(caminhos)} caminhos distintos no corpo "
                    "(considere M ou quebrar)"
                )
        roteamento = next((m.group(1).strip() for linha in secao["linhas"] if (m := RE_ROTEAMENTO.match(linha))), None)

        if modelo_nome == "opencode grátis":
            custo = 0
        elif modelo_nome is None:
            print(f"aviso: {agente} | {ident}: modelo não identificado (sem trava de custo)")
            custo = None
        elif effort_nome is None:
            print(f"aviso: {agente} | {ident}: effort não identificado para {modelo_nome} (sem trava de custo)")
            custo = None
        else:
            custo = PESOS_MODELO[modelo_nome] * PESOS_EFFORT[effort_nome] * PESOS_TAMANHO[tamanho]

        if resumo_custos is not None:
            resumo_custos[agente] = (ident, custo, tamanho)

        cota = por_pool.get(pool)
        uso_pool = cota["uso_max"] if (cota and cota["estado"] == "ready" and cota["uso_max"] is not None) else None
        retida = False
        if pool == "desconhecido":
            print(f"aviso: {agente} | {ident}: pool desconhecido")
        elif pool != "grátis":
            if not cota or cota["estado"] != "ready" or cota["uso_max"] is None:
                print(f"aviso: {agente} | {ident}: {pool} sem leitura fresca ou verificável")
            elif menor is None:
                print(f"aviso: {agente} | {ident}: sem pool pago elegível para comparação")
            elif familia == "Gemini":
                if _gemini_apertado(cota) and motivo is None:
                    retencoes.append(
                        f"RETIDO (equilíbrio): {agente} | {ident}: {pool} {round(cota['uso_max'])}% "
                        f"(Gemini apertado: semanal ≥{LIMIAR_GEMINI_SEMANAL}% ou 5h ≥{LIMIAR_GEMINI_5H}%; "
                        f"menor {nome_pool(menor)} {round(menor['uso_max'])}%); reencaminhe ou justifique com 'Motivo pool:'"
                    )
                    retida = True
            elif cota["uso_max"] - menor["uso_max"] >= LIMIAR_EQUILIBRIO and motivo is None:
                retencoes.append(
                    f"RETIDO (equilíbrio): {agente} | {ident}: {pool} {round(cota['uso_max'])}% vs "
                    f"{nome_pool(menor)} {round(menor['uso_max'])}%; reencaminhe ou justifique com 'Motivo pool:'"
                )
                retida = True
        if custo is not None and custo >= LIMIAR_CUSTO and (
            not roteamento or not RE_JUSTIFICATIVA_CUSTO.search(roteamento)
        ):
            par = f"{modelo_nome} {effort_nome}".strip()
            retencoes.append(
                f"RETIDO (custo): {agente} | {ident}: {par} {tamanho} (custo {custo} ≥ {LIMIAR_CUSTO}); "
                "quebre/rebaixe ou justifique com 'Roteamento: ... descartado: <par> porque <motivo>'"
            )
            retida = True
        if retida:
            continue
        aceitas[agente] = (ident, familia, pool, motivo or "", custo, tamanho, uso_pool)
    return aceitas, retencoes


def _texto_custo(custo, tamanho):
    return f"custo {custo} ({tamanho})" if custo is not None else f"custo ? ({tamanho})"


def imprimir_equilibrio(retencoes, distribuicao, custos=None):
    for retencao in retencoes:
        print(retencao)
    if custos:
        partes = []
        for agente, dados in custos.items():
            custo, tamanho = (dados[1], dados[2]) if len(dados) == 3 else (dados[4], dados[5])
            partes.append(f"{agente} ({dados[0]}) {_texto_custo(custo, tamanho)}")
        if partes:
            print("Custo por seção: " + " · ".join(partes))
    print("Distribuição do lote: " + formatar_distribuicao(dados[1] for dados in distribuicao))


def registrar_envios(pasta, inicio, envios):
    if not envios:
        return
    data = datetime.fromtimestamp(inicio, timezone.utc).isoformat()
    try:
        with (pasta / LOG_DISTRIBUICAO).open("ab", buffering=0) as log:
            for agente, dados in envios.items():
                ident, familia, pool, motivo = dados[:4]
                custo, tamanho, uso_pool = dados[4:7] if len(dados) >= 7 else (None, "", None)
                custo_str = "" if custo is None else str(custo)
                uso_str = "" if uso_pool is None else f"{uso_pool:g}"
                campos = (data, ident, agente, familia, pool, motivo, custo_str, tamanho, uso_str)
                linha = "\t".join(c.replace("\t", " ").replace("\r", " ").replace("\n", " ") for c in campos)
                log.write((linha + "\n").encode("utf-8"))
    except OSError as exc:
        print(f"aviso: não foi possível registrar os envios em {LOG_DISTRIBUICAO}: {exc}")


def avisar_criterios(exe, agente, ident, corpo, cli, conectado):
    if RE_CRITERIO.search(corpo) or RE_COMANDO_VALIDACAO.search(corpo):
        return
    if cli is None and conectado:
        try:
            atual = RE_ANSI.sub("", tela(exe, agente, timeout=3))
            if RE_TELA_CODEX.search(atual):
                cli = "codex"
        except (OSError, subprocess.TimeoutExpired):
            pass
    if cli is None:
        # Sem metadados, um nome de preset explícito ou menção ao Codex/modelo no
        # despacho é só um indício. O aviso é informativo e o envio segue normal.
        cli = ferramenta(agente)
        if cli is None and (re.search(r"\bcodex\b", corpo, re.I) or RE_MODELO_CODEX.search(corpo)):
            cli = "codex"
    if cli == "codex":
        print(f"aviso: despacho Codex para {agente} ({ident or '-'}) sem critério de pronto "
              "nem comando de validação. Inclua 'Pronto quando' e 'Valide com'.", flush=True)


def destino_rejeitado(agente, erro):
    achado = RE_DESTINO_REJEITADO.fullmatch(erro.strip())
    return achado is not None and achado["agente"] in (None, agente)


def enviar_um(exe, agente, prompt, timeout):
    """Envio individual (sem --batch), usado quando o lote falha; devolve (saida|None, erro|None).

    O maestri ask decodifica \\n e \\t no argumento, então as barras invertidas do prompt (os
    caminhos do rodapé) vão duplicadas para chegarem literais."""
    try:
        p = subprocess.run(
            [exe, "ask", agente, prompt.replace("\\", "\\\\")],
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, CONFIRMACAO_PERDIDA
    except OSError as exc:
        if exc.errno in (errno.ENOENT, errno.EACCES, errno.E2BIG) or getattr(exc, "winerror", None) == 206:
            return None, f"envio individual não iniciou: {exc}"
        return None, CONFIRMACAO_PERDIDA
    saida = p.stdout.decode("utf-8", "replace")
    erro = p.stderr.decode("utf-8", "replace").strip()
    if p.returncode != 0:
        motivo = (erro or saida).strip()
        if destino_rejeitado(agente, motivo):
            return None, f"envio individual rejeitado: {motivo}"
        return None, CONFIRMACAO_PERDIDA
    return saida, None


def menciona_id(texto, ident):
    return ident and re.search(rf"(?<![\w.-]){re.escape(ident)}(?:\.md)?(?![\w-]|\.[\w.-])", texto or "")


def conferir_entrega(exe, agente, ident, relatorio, desde):
    if relatorio_novo(relatorio, desde):
        return None, None
    try:
        atual = RE_ANSI.sub("", tela(exe, agente, timeout=5))
    except (OSError, subprocess.TimeoutExpired):
        atual = ""
    if relatorio_novo(relatorio, desde):
        return None, None
    if menciona_id(atual, ident):
        return atual, CONFIRMACAO_PERDIDA
    return None, CONFIRMACAO_PERDIDA


def enviar(exe, lote, timeout, *, ids=None, relatorios=None, desde=0):
    """Entrega um lote e confere destinos sem confirmação antes de decidir por reenvio."""
    ids = ids or {}
    relatorios = relatorios or {}
    payload = json.dumps(lote, ensure_ascii=False)
    rejeitado = False
    respostas = []
    try:
        # stdin=DEVNULL evita que o maestri.exe herde o pipe já consumido do despacho.
        p = subprocess.run(
            [exe, "ask", "--batch", payload], capture_output=True, stdin=subprocess.DEVNULL, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        pass
    except OSError as exc:
        if exc.errno in (errno.ENOENT, errno.EACCES):
            return {a: (None, f"envio em lote não iniciou: {exc}") for a in lote}
        rejeitado = exc.errno == errno.E2BIG or getattr(exc, "winerror", None) == 206
    else:
        try:
            dados = json.loads(p.stdout)
        except (ValueError, UnicodeError):
            dados = None
        if isinstance(dados, list):
            respostas = dados
        elif p.returncode != 0:
            motivo = (p.stderr or p.stdout).decode("utf-8", "replace").strip()
            rejeitado = RE_LOTE_REJEITADO.fullmatch(motivo) is not None

    por_destino = {}
    for item in respostas:
        if isinstance(item, dict) and isinstance(agente := item.get("name"), str) and agente in lote:
            por_destino[agente] = None if agente in por_destino else item

    resultados, repetir = {}, {}
    for agente in lote:
        item = por_destino.get(agente) or {}
        saida, erro = item.get("output"), item.get("error")
        if isinstance(saida, str) and "error" not in item:
            resultados[agente] = saida, None
            continue
        if rejeitado:
            repetir[agente] = ""
            continue
        resultados[agente] = conferir_entrega(exe, agente, ids.get(agente), relatorios.get(agente), desde)
        if (resultados[agente] == (None, CONFIRMACAO_PERDIDA) and isinstance(erro, str)
                and "output" not in item and destino_rejeitado(agente, erro)):
            repetir[agente] = erro

    if any("still starting" in motivo.casefold() for motivo in repetir.values()):
        time.sleep(20)
    for agente, motivo in repetir.items():
        ident, relatorio = ids.get(agente), relatorios.get(agente)
        if motivo and "still starting" in motivo.casefold():
            conferido = conferir_entrega(exe, agente, ident, relatorio, desde)
            if conferido != (None, CONFIRMACAO_PERDIDA):
                resultados[agente] = conferido
                continue
        print(f"aviso: envio anterior rejeitado antes da entrega para {agente}; reenviando só este destino", flush=True)
        resultado = enviar_um(exe, agente, lote[agente], timeout)
        resultados[agente] = (conferir_entrega(exe, agente, ident, relatorio, desde)
                              if resultado[1] == CONFIRMACAO_PERDIDA else resultado)
    return resultados


def dividir(prompts):
    lotes, atual, tam = [], {}, 2
    for agente, prompt in prompts.items():
        t = len(json.dumps({agente: prompt}, ensure_ascii=False))
        if atual and tam + t > LIMITE_JSON:
            lotes.append(atual)
            atual, tam = {}, 2
        atual[agente] = prompt
        tam += t
    if atual:
        lotes.append(atual)
    return lotes


def enviar_tudo(exe, prompts, timeout, *, ids=None, relatorios=None, desde=0):
    resultados = {}

    def trabalho(lote):
        resultados.update(enviar(exe, lote, timeout, ids=ids, relatorios=relatorios, desde=desde))

    threads = [threading.Thread(target=trabalho, args=(l,)) for l in dividir(prompts)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return resultados


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", help="arquivo do despacho, ou - para ler do stdin")
    ap.add_argument("--raiz", help="raiz do projeto (padrão: topo do git ou pasta atual)")
    ap.add_argument("--maestro", help="nome do Maestro para o ask back (padrão: You: do maestri list)")
    ap.add_argument("--sem-rodape", action="store_true", help="não acrescenta o rodapé de relatório")
    ap.add_argument("--mostrar", action="store_true", help="mostra os prompts que passariam pela trava, sem enviar")
    ap.add_argument("--linhas", type=int, default=8, help="linhas finais da tela quando não houve ask back")
    ap.add_argument("--timeout", type=int, default=45, help="minutos de espera por lote")
    ap.add_argument("--espera", type=int, default=30, help="minutos de espera pelo relatório de quem ainda não terminou")
    args = ap.parse_args()

    if args.arquivo == "-":
        # binário: o texto utf-8 do pipe não passa pelo cp1252 do console no Windows
        texto = sys.stdin.buffer.read().decode("utf-8-sig", "replace")
    else:
        texto = Path(args.arquivo).read_text(encoding="utf-8-sig")
    comum, secoes = ler_despacho(texto)
    if not secoes:
        print("ERRO: nenhuma seção '### Agente | ID' no despacho.")
        return 2
    vistos, ids_vistos = set(), set()
    for s in secoes:
        if s["agente"] in vistos:
            print(f"ERRO: {s['agente']} aparece duas vezes; junte as tarefas numa seção só.")
            return 2
        vistos.add(s["agente"])
        if not args.sem_rodape:
            if not s["id"]:
                print(f"ERRO: a seção de {s['agente']} não tem ID ('### {s['agente']} | PJ-T1').")
                return 2
            ident = s["id"].casefold()
            if ident in ids_vistos:
                print(f"ERRO: ID de relatório repetido: {s['id']}. Use um ID por relatório.")
                return 2
            ids_vistos.add(ident)
        if not "\n".join(s["linhas"]).strip():
            print(f"ERRO: a seção de {s['agente']} está vazia.")
            return 2

    raiz = Path(args.raiz) if args.raiz else None
    if raiz is None:
        p = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True)
        raiz = Path(p.stdout.decode("utf-8", "replace").strip()) if p.returncode == 0 else Path.cwd()
    raiz = raiz.resolve()
    pasta = raiz / ".maestri" / "relatorios"

    exe = maestri_exe()
    maestro, conectados, listagem = args.maestro, set(), ""
    if not (args.mostrar and args.maestro):
        achado, conectados, listagem = ler_list(exe)
        maestro = args.maestro or achado
    if not maestro:
        print("ERRO: não achei o seu nome em `maestri list` (seção You:). Passe --maestro \"Nome\".")
        return 2

    formacao = ler_formacao(raiz)
    try:
        pools, avisos_cotas = ler_cotas()
    except Exception as exc:
        pools, avisos_cotas = [], [f"falha ao ler cotas: {exc}"]
    for aviso in avisos_cotas:
        print(f"aviso: {aviso}")
    custos_todas = {}
    contas = contas_list(listagem)
    aceitas, retencoes = avaliar_equilibrio(
        exe, formacao, secoes, pools, resumo_custos=custos_todas, contas=contas,
    )
    secoes = [s for s in secoes if s["agente"] in aceitas]
    if not args.mostrar:
        faltam = [s["agente"] for s in secoes if s["agente"] not in conectados]
        if faltam:
            print(f"ERRO: não conectados: {', '.join(faltam)}. Conectados: {', '.join(sorted(conectados)) or 'nenhum'}")
            imprimir_equilibrio(retencoes, (), custos=custos_todas)
            return 2

    ferramentas = {**ferramentas_formacao(raiz, formacao), **ferramentas_list(listagem)}
    prompts, ids = {}, {}
    for s in secoes:
        corpo = "\n".join(s["linhas"]).strip()
        if comum:
            corpo = comum + "\n\n" + corpo
        agente = s["agente"]
        avisar_criterios(exe, agente, s["id"], corpo, ferramentas.get(agente), agente in conectados)
        if not args.sem_rodape:
            arquivo = pasta / f"{s['id']}.md"
            corpo += "\n" + RODAPE.format(arquivo=arquivo, id=s["id"], maestro=maestro)
        prompts[s["agente"]] = corpo
        ids[s["agente"]] = s["id"]

    if args.mostrar:
        for a, p in prompts.items():
            custo_txt = _texto_custo(aceitas[a][4], aceitas[a][5])
            print(f"===== {a} ({len(p)} caracteres | {custo_txt})\n{p}\n")
        imprimir_equilibrio(retencoes, aceitas.values(), custos=custos_todas)
        return 0

    pasta.mkdir(parents=True, exist_ok=True)
    bloqueios = {}

    def conferir(agente):
        motivo = esperar_pronto(exe, agente)
        if motivo:
            bloqueios[agente] = motivo

    threads = [threading.Thread(target=conferir, args=(a,)) for a in prompts]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for agente, motivo in bloqueios.items():
        print(f"== {agente} ({ids[agente] or '-'}): NÃO ENVIADO, {motivo}")
        prompts.pop(agente)
    if not prompts:
        imprimir_equilibrio(retencoes, (), custos=custos_todas)
        return 1
    relatorios = {}
    if not args.sem_rodape:
        for agente in prompts:
            arquivo = pasta / f"{ids[agente]}.md"
            anterior = data_relatorio(arquivo)
            relatorios[agente] = arquivo, anterior
            if anterior is not None:
                print(f"aviso: {arquivo.name} já existia e será sobrescrito pelo produtor; prefira um ID novo por rodada")
    inicio = time.time()
    resultados = enviar_tudo(exe, prompts, args.timeout * 60, ids=ids, relatorios=relatorios, desde=inicio)

    # Despacho que caiu durante a abertura do agente fica parado na caixa de entrada:
    # um Enter envia o texto que já está lá; depois espera o arquivo de relatório.
    parados = [a for a, (out, err) in resultados.items()
               if err is None and not relatorio_novo(relatorios.get(a), inicio)
               and menciona_id(out, ids[a]) and texto_nao_enviado(out)]
    enter_falhou = set()
    for a in parados:
        print(f"aviso: o despacho para {a} ficou na caixa de entrada sem envio; mandei Enter e estou esperando o relatório")
        p = subprocess.run([exe, "ask", a, "--raw", "\\r"], capture_output=True, stdin=subprocess.DEVNULL)
        if p.returncode != 0:
            enter_falhou.add(a)

    envios = {a: aceitas[a] for a, (_, erro) in resultados.items()
              if erro is None and a not in enter_falhou}
    registrar_envios(pasta.parent, inicio, envios)

    # Quem ainda não gravou relatório pode estar trabalhando em silêncio ou parado num pedido
    # de permissão: uma espera só, com prazo global de --espera, cobre todos os pendentes.
    # Com --sem-rodape nenhum relatório foi pedido, então não há o que esperar nem cobrar.
    sem_relatorio = set()
    pendentes = {}
    for agente, relatorio in relatorios.items():
        _, err = resultados.get(agente, (None, "sem retorno"))
        if err in (None, CONFIRMACAO_PERDIDA) and not relatorio_novo(relatorio, inicio):
            pendentes[agente] = relatorio
    if pendentes:
        print(f"aguardando {', '.join(sorted(pendentes))}: até {args.espera} min no total,"
              " relatório a cada 10 s, tela a cada 30 s", flush=True)
        sem_relatorio = esperar_terminar(exe, pendentes, inicio, args.espera)
        if sem_relatorio:
            print(f"aviso: sem relatório em {args.espera} min: {', '.join(sorted(sem_relatorio))}", flush=True)

    confirmados_por_relatorio = {a: aceitas[a] for a, relatorio in relatorios.items()
                                 if a not in envios and relatorio_novo(relatorio, inicio)}
    registrar_envios(pasta.parent, inicio, confirmados_por_relatorio)
    envios.update(confirmados_por_relatorio)
    falhou = bool(bloqueios or retencoes)
    print(f"Maestro: {maestro} | relatórios em {pasta} | {round(time.time() - inicio)} s")
    for agente in prompts:
        out, err = resultados.get(agente, (None, "sem retorno"))
        ident = ids[agente] or "-"
        arq = pasta / f"{ident}.md"
        if err and err != CONFIRMACAO_PERDIDA:
            print(f"== {agente} ({ident}): ERRO {err}")
            falhou = True
            continue
        if relatorio_novo(relatorios.get(agente), inicio):
            conteudo = arq.read_text(encoding="utf-8", errors="replace")[:3000]
            achado, veredito = RE_STATUS.search(conteudo), RE_VEREDITO.search(conteudo)
            status = achado.group(1).lower() if achado else "sem STATUS no arquivo"
            extra = f" | veredito {veredito.group(1).lower()}" if veredito else ""
            print(f"== {agente} ({ident}): {status}{extra} | relatório: {arq}")
            falhou = falhou or achado is None or status == "bloqueado"
            continue
        if err == CONFIRMACAO_PERDIDA:
            detalhe = "atividade do ID observada" if out else "entrega ainda indeterminada"
            print(f"== {agente} ({ident}): PENDENTE, {err} ({detalhe}). Confira com maestri check \"{agente}\".")
            falhou = True
            continue
        if not args.sem_rodape and ids[agente] and arq.exists():
            print(f"== {agente} ({ident}): o relatório existente é ANTERIOR a este despacho (use um ID novo por rodada)")
        # O retorno do --batch pode ser de minutos atrás: para quem passou pela espera, a tela atual.
        texto_out = tela(exe, agente) if agente in sem_relatorio else (out or "")
        achado = janela_pedido(texto_out)
        if achado:
            print(f"== {agente} ({ident}): PENDENTE, pedido de permissão na tela (maestri check \"{agente}\")")
            print("\n".join("   " + l[:200] for l in achado[0]))
        else:
            cauda = [l for l in texto_out.splitlines() if l.strip() and not RE_MOLDURA.search(l.strip())][-args.linhas:]
            print(f"== {agente} ({ident}): terminou sem relatório; últimas linhas:")
            print("\n".join("   " + l[:200] for l in cauda))
        falhou = falhou or not args.sem_rodape
    imprimir_equilibrio(retencoes, envios.values(), custos=custos_todas)
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
