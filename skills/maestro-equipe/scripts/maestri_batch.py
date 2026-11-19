"""Despacha tarefas aos produtores do Maestri e resume o retorno de cada um.

Uso:
    python maestri_batch.py despacho.md [--raiz PASTA] [--maestro NOME] [--mostrar]
    python maestri_batch.py - < despacho.md          (lê do stdin)

Formato do despacho (texto puro, sem JSON e sem escapar nada):

    Texto opcional antes do primeiro ###: vai no início de TODOS os prompts.
    ### Prisma | PJ-T3
    prompt da tarefa, com qualquer caractere (aspas, C:\\caminhos, acentos)
    ### Lente | PJ-T3-REV
    outro prompt

Cada seção é "### <nome exato do agente> | <ID da tarefa>". O script:
- descobre o nome real do Maestro em `maestri list` (seção You:) e confere os destinos;
- cria <raiz>/.maestri/relatorios/ e acrescenta a cada prompt o rodapé do relatório:
  o produtor grava o relatório completo em .maestri/relatorios/<ID>.md e avisa com
  um ping curto `maestri ask "<Maestro>" "<ID> <status>: .maestri/relatorios/<ID>.md"`;
- monta o JSON com o escape certo e envia com `maestri ask --batch` (em lotes de até
  ~24 mil caracteres por chamada, por causa do limite de linha de comando do Windows);
- reenvia uma vez a quem ainda estava iniciando;
- resume cada retorno: relatório recebido, pedido de permissão pendente, ou últimas linhas.

Rode em background (run_in_background) e encerre o turno: o retorno chega sozinho.
Saída 0 = todos responderam; 1 = algum falhou ou ficou pendente; 2 = erro no despacho.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

LIMITE_JSON = 24000
RE_SECAO = re.compile(r"^###\s+(.+?)\s*(?:\|\s*([A-Za-z0-9][\w.\-]*))?\s*$")
RE_PERMISSAO = re.compile(
    r"(do you want to|allow (this|once|always)|permitir|approve|\(y/n\)|trust (this|the) (folder|files|contents)"
    r"|requires approval|waiting for (your )?(approval|confirmation)|❯\s*1\.\s*yes)",
    re.I,
)
RE_INICIANDO = re.compile(r"(still starting|is starting|starting up|ainda (está )?iniciando|not ready)", re.I)

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


def tela(exe, agente):
    p = subprocess.run([exe, "check", agente], capture_output=True)
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
                subprocess.run([exe, "ask", agente, "--raw", "\\r"], capture_output=True)
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


def relatorio_novo(arq, desde):
    return arq.exists() and arq.stat().st_mtime >= desde - 2


def esperar_relatorios(arquivos, desde, minutos):
    """Espera os arquivos de relatório aparecerem (sondagem leve no disco, sem gastar tokens)."""
    limite = time.time() + minutos * 60
    while time.time() < limite and not all(relatorio_novo(a, desde) for a in arquivos):
        time.sleep(10)


def maestri_exe():
    exe = shutil.which("maestri") or os.environ.get("MAESTRI_CLI")
    if not exe:
        print("ERRO: maestri não encontrado no PATH nem em MAESTRI_CLI.")
        sys.exit(2)
    return exe


def ler_list(exe):
    p = subprocess.run([exe, "list"], capture_output=True)
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


def enviar(exe, lote, timeout):
    """Envia um lote {agente: prompt}; devolve {agente: (saida|None, erro|None)}."""
    try:
        p = subprocess.run(
            [exe, "ask", "--batch", json.dumps(lote, ensure_ascii=False)],
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {a: (None, f"sem resposta em {timeout // 60} min: rode maestri check \"{a}\"") for a in lote}
    saida = p.stdout.decode("utf-8", "replace")
    erro = p.stderr.decode("utf-8", "replace").strip()
    try:
        respostas = json.loads(saida)
        assert isinstance(respostas, list)
    except (json.JSONDecodeError, AssertionError):
        return {a: (None, f"falha no envio (código {p.returncode}): {(erro or saida)[:300]}") for a in lote}
    res = {}
    for r in respostas:
        if isinstance(r, dict) and r.get("name") in lote:
            res[r["name"]] = (r.get("output"), None) if "error" not in r else (None, str(r["error"]))
    for a in lote:
        res.setdefault(a, (None, "sem retorno do maestri para este agente"))
    return res


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


def enviar_tudo(exe, prompts, timeout):
    resultados = {}

    def trabalho(lote):
        resultados.update(enviar(exe, lote, timeout))

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
    ap.add_argument("--mostrar", action="store_true", help="só mostra os prompts finais, sem enviar")
    ap.add_argument("--linhas", type=int, default=8, help="linhas finais da tela quando não houve ask back")
    ap.add_argument("--timeout", type=int, default=45, help="minutos de espera por lote")
    args = ap.parse_args()

    texto = sys.stdin.read() if args.arquivo == "-" else Path(args.arquivo).read_text(encoding="utf-8-sig")
    comum, secoes = ler_despacho(texto)
    if not secoes:
        print("ERRO: nenhuma seção '### Agente | ID' no despacho.")
        return 2
    vistos = set()
    for s in secoes:
        if s["agente"] in vistos:
            print(f"ERRO: {s['agente']} aparece duas vezes; junte as tarefas numa seção só.")
            return 2
        vistos.add(s["agente"])
        if not args.sem_rodape and not s["id"]:
            print(f"ERRO: a seção de {s['agente']} não tem ID ('### {s['agente']} | PJ-T1').")
            return 2
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
    maestro, conectados = args.maestro, set()
    if not (args.mostrar and args.maestro):
        achado, conectados, _ = ler_list(exe)
        maestro = args.maestro or achado
    if not maestro:
        print("ERRO: não achei o seu nome em `maestri list` (seção You:). Passe --maestro \"Nome\".")
        return 2
    if not args.mostrar:
        faltam = [s["agente"] for s in secoes if s["agente"] not in conectados]
        if faltam:
            print(f"ERRO: não conectados: {', '.join(faltam)}. Conectados: {', '.join(sorted(conectados)) or 'nenhum'}")
            return 2

    prompts, ids = {}, {}
    for s in secoes:
        corpo = "\n".join(s["linhas"]).strip()
        if comum:
            corpo = comum + "\n\n" + corpo
        if not args.sem_rodape:
            arquivo = pasta / f"{s['id']}.md"
            corpo += "\n" + RODAPE.format(arquivo=arquivo, id=s["id"], maestro=maestro)
        prompts[s["agente"]] = corpo
        ids[s["agente"]] = s["id"]

    if args.mostrar:
        for a, p in prompts.items():
            print(f"===== {a} ({len(p)} caracteres)\n{p}\n")
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
        return 1
    inicio = time.time()
    for ident in ids.values():
        velho = pasta / f"{ident}.md" if ident else None
        if velho and velho.exists():
            print(f"aviso: {velho.name} já existia e será sobrescrito pelo produtor; prefira um ID novo por rodada")
    resultados = enviar_tudo(exe, prompts, args.timeout * 60)

    reenviar = {a: prompts[a] for a, (out, err) in resultados.items() if out and RE_INICIANDO.search(out[-600:])}
    if reenviar:
        time.sleep(20)
        resultados.update(enviar_tudo(exe, reenviar, args.timeout * 60))

    # Despacho que caiu durante a abertura do agente fica parado na caixa de entrada:
    # um Enter envia o texto que já está lá; depois espera o arquivo de relatório.
    parados = [a for a, (out, err) in resultados.items()
               if out and ids[a] and not relatorio_novo(pasta / f"{ids[a]}.md", inicio) and texto_nao_enviado(out)]
    for a in parados:
        print(f"aviso: o despacho para {a} ficou na caixa de entrada sem envio; mandei Enter e estou esperando o relatório")
        subprocess.run([exe, "ask", a, "--raw", "\\r"], capture_output=True)
    if parados:
        esperar_relatorios([pasta / f"{ids[a]}.md" for a in parados], inicio, args.timeout)

    falhou = bool(bloqueios)
    print(f"Maestro: {maestro} | relatórios em {pasta} | {round(time.time() - inicio)} s")
    for agente in prompts:
        out, err = resultados.get(agente, (None, "sem retorno"))
        ident = ids[agente] or "-"
        arq = pasta / f"{ident}.md"
        if err:
            print(f"== {agente} ({ident}): ERRO {err}")
            falhou = True
            continue
        texto_out = out or ""
        if ids[agente] and relatorio_novo(arq, inicio):
            conteudo = arq.read_text(encoding="utf-8", errors="replace")[:3000]
            achado, veredito = RE_STATUS.search(conteudo), RE_VEREDITO.search(conteudo)
            status = achado.group(1).lower() if achado else "sem STATUS no arquivo"
            extra = f" | veredito {veredito.group(1).lower()}" if veredito else ""
            print(f"== {agente} ({ident}): {status}{extra} | relatório: {arq}")
            falhou = falhou or status in ("bloqueado", "sem status no arquivo")
            continue
        if ids[agente] and arq.exists():
            print(f"== {agente} ({ident}): o relatório existente é ANTERIOR a este despacho (use um ID novo por rodada)")
        cauda = [l for l in texto_out.splitlines() if l.strip()][-args.linhas:]
        if RE_PERMISSAO.search("\n".join(cauda)):
            print(f"== {agente} ({ident}): PENDENTE, pedido de permissão na tela (maestri check \"{agente}\")")
        else:
            print(f"== {agente} ({ident}): terminou sem relatório; últimas linhas:")
        print("\n".join("   " + l[:200] for l in cauda))
        falhou = True
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
