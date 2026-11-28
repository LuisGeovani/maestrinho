"""Mostra a cota de cada provedor (Claude, Codex, Antigravity...) lida do Maestri.

Uso:
    python cotas.py [--json]

Fonte principal: <MAESTRI_DATA_DIR>/usage/providers/.status.json. Quando a leitura
do Codex é desconhecida, busca limites válidos nos cinco rollouts mais recentes.
"Gaste primeiro" prioriza pools Gemini de rotina (cota enche mais devagar; só apertam em ≥80% semanal ou ≥90% em 5h) e depois os demais pools de rotina pela folga na janela mais usada e, no empate, pelo reset mais próximo.
"Ordem Claude agora" vale depois de escolher a família Claude.
"""
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from heapq import nlargest
from pathlib import Path

JANELAS = {18000: "5h", 604800: "semanal", 2592000: "mensal", 86400: "diária"}
MODELOS_PAGOS_CODEX = {"gpt-6.2-sol", "gpt-6.2-astra"}
RITMO = {604800, 2592000}
MEDIDORES_AGY_CLAUDE = {"claude and gpt", "claude and gpt models"}
FAMILIAS = ("Claude", "GPT", "Gemini", "aberto", "desconhecido")
LOG_DISTRIBUICAO = "distribuicao.log"


def arquivo_status() -> Path:
    base = os.environ.get("MAESTRI_DATA_DIR") or str(Path.home() / ".maestri")
    return Path(base) / "usage" / "providers" / ".status.json"


def _data(texto):
    if not texto:
        return None
    try:
        data = datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
        return data if data.tzinfo is not None else None
    except ValueError:
        return None


def formatar_distribuicao(familias):
    contagem = dict.fromkeys(FAMILIAS, 0)
    for familia in familias:
        contagem[familia if familia in contagem else "desconhecido"] += 1
    return " · ".join(f"{familia} {n}" for familia, n in contagem.items())


def distribuicao_recente(pasta, agora=None):
    agora = agora or datetime.now(timezone.utc)
    limite = agora - timedelta(hours=5)
    familias = []
    try:
        with (pasta / LOG_DISTRIBUICAO).open(encoding="utf-8", errors="replace") as linhas:
            for linha in linhas:
                campos = linha.rstrip("\r\n").split("\t")
                if len(campos) >= 6:
                    data = _data(campos[0])
                    if data is not None and limite <= data <= agora:
                        familias.append(campos[3])
    except FileNotFoundError:
        return None
    except OSError as exc:
        return f"aviso: não foi possível ler {LOG_DISTRIBUICAO}: {exc}"
    return "Despachos nas últimas 5 h por família: " + formatar_distribuicao(familias)


def custo_por_despacho(pasta, agora=None):
    """Média de delta de uso do pool (pp) e de custo estimado por terminal nos últimos 7 dias."""
    agora = agora or datetime.now(timezone.utc)
    limite = agora - timedelta(days=7)
    entradas = []
    try:
        with (pasta / LOG_DISTRIBUICAO).open(encoding="utf-8", errors="replace") as linhas:
            for idx, linha in enumerate(linhas):
                campos = linha.rstrip("\r\n").split("\t")
                if len(campos) < 9:
                    continue
                data = _data(campos[0])
                if data is None or not (limite <= data <= agora):
                    continue
                agente = campos[2].strip()
                if not agente:
                    continue
                entradas.append({
                    "data": data,
                    "idx": idx,
                    "agente": agente,
                    "pool": campos[4].strip(),
                    "custo": _numero(campos[6]),
                    "uso": _numero(campos[8]),
                })
    except FileNotFoundError:
        return None
    except OSError as exc:
        return f"aviso: não foi possível ler {LOG_DISTRIBUICAO}: {exc}"

    if not entradas:
        return None
    entradas.sort(key=lambda e: (e["data"], e["idx"]))

    contagem = {}
    custos = {}
    por_pool = {}
    for e in entradas:
        agente = e["agente"]
        contagem[agente] = contagem.get(agente, 0) + 1
        if e["custo"] is not None:
            custos.setdefault(agente, []).append(e["custo"])
        por_pool.setdefault(e["pool"], []).append(e)

    deltas = {}
    compartilhados = set()
    for pool, lista in por_pool.items():
        if pool == "desconhecido":
            continue
        lotes = []
        for e in lista:
            if lotes and lotes[-1]["data"] == e["data"]:
                lotes[-1]["agentes"].add(e["agente"])
                if lotes[-1]["uso"] is None and e["uso"] is not None:
                    lotes[-1]["uso"] = e["uso"]
            else:
                lotes.append({"data": e["data"], "agentes": {e["agente"]}, "uso": e["uso"]})
        for atual, seguinte in zip(lotes, lotes[1:]):
            if atual["uso"] is not None and seguinte["uso"] is not None and seguinte["uso"] >= atual["uso"]:
                if len(atual["agentes"]) == 1:
                    unico = next(iter(atual["agentes"]))
                    deltas.setdefault(unico, []).append(seguinte["uso"] - atual["uso"])
                else:
                    compartilhados.update(atual["agentes"])

    partes = []
    for agente in sorted(a for a, n in contagem.items() if n >= 2):
        ds = deltas.get(agente, [])
        cs = custos.get(agente, [])
        if ds:
            pp_txt = f"{sum(ds) / len(ds):.1f} pp"
        elif agente in compartilhados:
            pp_txt = "indeterminado"
        else:
            pp_txt = "? pp"
        custo_txt = f"{round(sum(cs) / len(cs))}" if cs else "?"
        partes.append(f"{agente} {pp_txt} (custo médio {custo_txt})")
    if not partes:
        return None
    return "Custo por despacho (aprox.): " + " · ".join(partes)


def _falta(ate, agora):
    if not ate:
        return "?"
    seg = int((ate - agora).total_seconds())
    if seg <= 0:
        return "agora"
    dias, seg = divmod(seg, 86400)
    horas, seg = divmod(seg, 3600)
    if dias:
        return f"{dias}d{horas:02d}h"
    return f"{horas}h{seg // 60:02d}"


def _casa_codex():
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def modelos_codex_cache():
    try:
        dados = json.loads((_casa_codex() / "models_cache.json").read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError):
        return []
    modelos = dados.get("models") if isinstance(dados, dict) else None
    return [m for m in modelos if isinstance(m, dict)] if isinstance(modelos, list) else []


def _snapshot_codex(arquivo):
    """Adapta o último evento de cota de um rollout ao formato do Maestri."""
    ultimo = None
    try:
        with arquivo.open("rb") as linhas:
            for linha in linhas:
                if b'"rate_limits"' not in linha:
                    continue
                try:
                    evento = json.loads(linha)
                except (UnicodeError, ValueError):
                    continue
                if not isinstance(evento, dict) or evento.get("type") != "event_msg":
                    continue
                payload = evento.get("payload")
                if not isinstance(payload, dict) or payload.get("type") != "token_count":
                    continue
                limites = payload.get("rate_limits")
                if isinstance(limites, dict) and limites.get("limit_id") == "codex":
                    ultimo = evento.get("timestamp"), limites
    except OSError:
        return None
    if ultimo is None:
        return None
    instante, limites = ultimo
    janelas = []
    for chave in ("primary", "secondary"):
        janela = limites.get(chave)
        if not isinstance(janela, dict):
            return None
        minutos = janela.get("window_minutes")
        if type(minutos) is not int or minutos <= 0:
            return None
        try:
            reset = datetime.fromtimestamp(janela["resets_at"], timezone.utc).isoformat()
        except (KeyError, TypeError, ValueError, OverflowError, OSError):
            return None
        janelas.append({"durationSeconds": minutos * 60, "usedPercent": janela.get("used_percent"), "resetsAt": reset})
    return {
        "id": "codex", "name": "Codex", "plan": limites.get("plan_type"),
        "state": "ready", "lastSuccessAt": instante, "meters": [{"id": "codex", "label": "Codex", "windows": janelas}],
    }


def _numero(valor):
    try:
        numero = float(valor) if not isinstance(valor, bool) else -1
    except (TypeError, ValueError, OverflowError):
        return None
    return numero if math.isfinite(numero) and numero >= 0 else None


def _janela(janela, agora):
    dur = _numero(janela.get("durationSeconds"))
    rotulo = JANELAS.get(dur) or (f"{round(dur / 3600)}h" if dur else (janela.get("title") or "?"))
    usado = _numero(janela.get("usedPercent"))
    reset = _data(janela.get("resetsAt"))
    ritmo = None
    if dur in RITMO or rotulo.casefold() in ("semanal", "mensal", "weekly", "monthly"):
        if dur in RITMO and reset and usado is not None:
            restante = (reset - agora).total_seconds()
            decorrido = 100 * min(dur, max(0, dur - restante)) / dur
            limite = max(25, decorrido + 10)
            adiantado = usado > limite and not math.isclose(usado, limite, rel_tol=0, abs_tol=1e-9)
            ritmo = {"decorrido": decorrido, "limite": limite, "estado": "adiantado" if adiantado else "folga"}
        else:
            ritmo = {"decorrido": None, "limite": None, "estado": "desconhecido"}
    return {"janela": rotulo, "usado": usado, "reset": reset, "falta": _falta(reset, agora), "ritmo": ritmo}


def _gemini_apertado(janelas, uso_max):
    """Pool Gemini só vira 'só insubstituível' a partir de 80% semanal ou 90% em 5h."""
    semanais = [
        j["usado"] for j in janelas
        if j["usado"] is not None and j["janela"].casefold() in ("semanal", "weekly", "mensal", "monthly")
    ]
    cinco_h = [j["usado"] for j in janelas if j["usado"] is not None and j["janela"].casefold() == "5h"]
    if semanais or cinco_h:
        return any(u >= 80 for u in semanais) or any(u >= 90 for u in cinco_h)
    return uso_max is not None and uso_max >= 80


def _medidores(provedor, agora, origem, avisos):
    nome = provedor.get("name") or provedor.get("id") or "?"
    plano = provedor.get("plan") or ""
    claude_code = provedor.get("id") == "claude" or nome.casefold() == "claude code"
    antigravity = provedor.get("id") == "antigravity" or nome.casefold() == "antigravity"
    estado = provedor.get("state")
    ultimo = _data(provedor.get("lastSuccessAt"))
    motivos_provedor = []
    if estado != "ready":
        motivos_provedor.append(f"estado {estado or 'ausente'}")
    if ultimo is None or ultimo > agora:
        motivos_provedor.append("última leitura ausente ou inválida")
    elif (agora - ultimo).total_seconds() > 3600:
        horas = (agora - ultimo).total_seconds() / 3600
        motivos_provedor.append(f"última leitura há {horas:.1f} h")

    medidores = provedor.get("meters")
    if medidores is not None and not isinstance(medidores, list):
        avisos.append(f"{nome}: meters inválido (esperada uma lista)")
        return
    for i, medidor in enumerate(medidores or [{}]):
        if not isinstance(medidor, dict) or any(
            medidor.get(campo) is not None and not isinstance(medidor[campo], str)
            for campo in ("label", "id")
        ):
            avisos.append(f"{nome}: meters[{i}] inválido, ignorado")
            continue
        medidor_nome = medidor.get("label") or medidor.get("id") or nome
        janelas_brutas = medidor.get("windows")
        if janelas_brutas is not None and (
            not isinstance(janelas_brutas, list) or any(
                not isinstance(j, dict) or (j.get("title") is not None and not isinstance(j["title"], str))
                for j in janelas_brutas
            )
        ):
            avisos.append(f"{nome}/{medidor_nome}: windows inválido, medidor ignorado")
            continue
        via_claude = None
        if claude_code:
            via_claude = "Claude Code"
        elif antigravity and (
            medidor_nome.casefold() in MEDIDORES_AGY_CLAUDE
            or (medidor.get("id") or "").casefold() in MEDIDORES_AGY_CLAUDE
        ):
            via_claude = "Antigravity"
        eh_codex = (
            provedor.get("id") == "codex"
            or nome.casefold() == "codex"
            or (not claude_code and not antigravity and (
                (medidor.get("id") or "").casefold() == "codex" or medidor_nome.casefold() == "codex"
            ))
        )
        conta = ("Padrão" if (provedor.get("id") == "codex" or nome.casefold() == "codex") else nome) if eh_codex else None
        janelas = [_janela(j, agora) for j in (janelas_brutas or [])]
        usos = [j["usado"] for j in janelas if j["usado"] is not None]
        resets = [j["reset"] for j in janelas if j["reset"]]
        uso_max = max(usos, default=None)
        motivos = list(motivos_provedor)
        if uso_max is None or len(usos) != len(janelas):
            motivos.append("uso ausente ou inválido")
        if not claude_code and any(j["ritmo"] and j["ritmo"]["estado"] == "desconhecido" for j in janelas):
            motivos.append("faltam dados para o ritmo semanal ou mensal")
        adiantado = any(j["ritmo"] and j["ritmo"]["estado"] == "adiantado" for j in janelas)
        gemini_pool = antigravity and via_claude is None
        veto_provedor = provedor.get("usageAllowed") is False or medidor.get("usageAllowed") is False
        veto_janela = uso_max is not None and uso_max >= 95
        veto = "usageAllowed=false" if veto_provedor else "janela com uso ≥95%" if veto_janela else None
        if veto:
            despacho = "fila" if veto_janela and uso_max >= 100 else "nenhum"
        elif motivos:
            despacho = "reconferir" if claude_code else "sondagem"
        elif claude_code:
            despacho = "reserva Claude"
        elif gemini_pool:
            despacho = "só insubstituível" if _gemini_apertado(janelas, uso_max) else "rotina"
        elif uso_max >= 80 or adiantado:
            despacho = "só insubstituível"
        else:
            despacho = "rotina"

        yield {
            "provedor": nome, "plano": plano, "medidor": medidor_nome,
            "conta": conta, "eh_codex": eh_codex,
            "janelas": janelas, "uso_max": uso_max, "reset_min": min(resets, default=None),
            "estado": "desconhecido" if motivos else "ready", "estado_provedor": estado,
            "origem": origem, "ultima_leitura": ultimo, "notas": provedor.get("notes") or [],
            "reserva_maestro": claude_code, "via_claude": via_claude, "despacho": despacho, "veto_despacho": veto,
            "elegivel": despacho in ("rotina", "só insubstituível", "reserva Claude"),
            "motivos": motivos,
        }


def ler_cotas():
    """Devolve (pools, avisos), incluindo os medidores sem leitura confiável."""
    caminho = arquivo_status()
    agora = datetime.now(timezone.utc)
    pools, avisos = [], []
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
        provedores = dados.get("providers", []) if isinstance(dados, dict) else None
    except (OSError, UnicodeError, ValueError, AttributeError):
        provedores = []
        avisos.append(f"sem dados de cota do Maestri: {caminho} ausente ou ilegível")
    if not isinstance(provedores, list):
        provedores = []
        avisos.append(f"sem dados de cota do Maestri: {caminho} inválido (esperada lista em providers)")
    tem_codex = False
    for i, prov in enumerate(provedores):
        if not isinstance(prov, dict) or any(
            prov.get(campo) is not None and not isinstance(prov[campo], str)
            for campo in ("name", "id", "plan")
        ):
            avisos.append(f"Maestri: providers[{i}] inválido, ignorado")
            continue
        nome = prov.get("name") or prov.get("id") or "?"
        codex = prov.get("id") == "codex" or nome.casefold() == "codex"
        tem_codex = tem_codex or codex
        if not prov.get("enabled", True):
            continue
        notas = prov.get("notes")
        if notas is not None and not isinstance(notas, list):
            avisos.append(f"{nome}: notes inválido, ignorado")
            prov = {**prov, "notes": []}
        medidores = list(_medidores(prov, agora, "maestri", avisos))
        avisos.extend(f"{nome}: {nota}" for nota in (prov.get("notes") or []))
        if codex:
            plano = (prov.get("plan") or "").casefold()
            if plano in ("", "free") or prov.get("state") == "failed":
                pagos = sorted({m.get("slug") for m in modelos_codex_cache()} & MODELOS_PAGOS_CODEX)
                if pagos:
                    avisos.append(f"Codex: possível divergência de plano (Maestri: {plano or 'ausente'}, "
                                  f"estado {prov.get('state') or 'ausente'}; cache lista {', '.join(pagos)}). "
                                  "Confira a conta e atualize a leitura do Maestri.")
            if all(p["estado"] == "desconhecido" and not p["veto_despacho"] for p in medidores):
                fallback = _cotas_rollout(plano_esperado=plano or None)
                if fallback:
                    avisos.append("Codex: leitura do Maestri suprida pelo rollout local (rate_limits)")
                    for p in fallback:
                        p["notas"] = prov.get("notes") or []
                        p["estado_provedor"] = prov.get("state")
                    medidores = fallback
        for p in medidores:
            if p["motivos"]:
                avisos.append(f"{nome}/{p['medidor']}: desconhecido ({'; '.join(p['motivos'])})")
        pools.extend(medidores)
    if not tem_codex:
        fallback = _cotas_rollout()
        if fallback:
            avisos.append("Codex: usando rate_limits do rollout local")
            pools.extend(fallback)
    return pools, avisos


def _mtime_rollout(arquivo):
    try:
        return arquivo.stat().st_mtime_ns
    except OSError:
        return -1


def _cotas_rollout(plano_esperado=None):
    sessoes = _casa_codex() / "sessions"
    try:
        arquivos = nlargest(5, sessoes.rglob("rollout-*.jsonl"), key=_mtime_rollout)
    except OSError:
        return []
    for arquivo in arquivos:
        provedor = _snapshot_codex(arquivo)
        if provedor is None:
            continue
        plano_rollout = (provedor.get("plan") or "").casefold()
        if plano_esperado and plano_rollout and plano_rollout != plano_esperado.casefold():
            continue
        medidores = list(_medidores(provedor, datetime.now(timezone.utc), "codex_rollout", []))
        if medidores and all(p["estado"] == "ready" for p in medidores):
            return medidores
    return []


def _reset_veto(pool):
    bloqueadas = [j["reset"] for j in pool["janelas"] if j["usado"] is not None and j["usado"] >= 95]
    if bloqueadas:
        return max(bloqueadas) if all(bloqueadas) else None
    return pool["reset_min"]


def ordem_claude(pools):
    """Indica o destino dentro da família já escolhida e quando reconferir a cota."""
    agy = next((p for p in pools if p["via_claude"] == "Antigravity"), None)
    claude_code = next((p for p in pools if p["via_claude"] == "Claude Code"), None)
    if agy is None:
        destino = "Claude Code" if claude_code and claude_code["elegivel"] else "bloqueado"
        return {"destino": destino, "reset": None}
    if agy["elegivel"]:
        return {"destino": "Antigravity", "reset": None}
    if not agy["veto_despacho"]:
        return {"destino": "reconferir Antigravity", "reset": None}
    reset_agy = _reset_veto(agy)
    if claude_code and claude_code["elegivel"]:
        return {"destino": "Claude Code", "reset": reset_agy}
    reset_claude_code = _reset_veto(claude_code) if claude_code and claude_code["veto_despacho"] else None
    return {"destino": "bloqueado", "reset": min((r for r in (reset_agy, reset_claude_code) if r), default=None)}


def resumo_linhas(pools, avisos):
    claude = ordem_claude(pools)
    linha_claude = f"Ordem Claude agora: {claude['destino']}"
    if claude["destino"] in ("Claude Code", "bloqueado"):
        reset = claude["reset"]
        quando = reset.astimezone().isoformat(timespec="minutes") if reset else "desconhecido"
        linha_claude += f" (reset {quando})"
    linhas = []
    if not pools:
        return (avisos or ["sem dados de cota"]) + [linha_claude]
    for p in pools:
        partes = []
        for j in p["janelas"]:
            usado = f"{round(j['usado'])}%" if j["usado"] is not None else "?"
            parte = f"{j['janela']} {usado} (reset {j['falta']})"
            ritmo = j["ritmo"]
            if ritmo and ritmo["decorrido"] is not None:
                parte += (f" [ritmo: {usado} usado × {ritmo['decorrido']:.0f}% do tempo, "
                          f"limite {ritmo['limite']:.0f}%, {ritmo['estado']}]")
            elif ritmo:
                parte += " [ritmo: desconhecido]"
            janela_cheia = j["usado"] is not None and j["usado"] >= 95
            if j["reset"] and (janela_cheia or p["veto_despacho"] == "usageAllowed=false"):
                rotulo = "reset da fila" if janela_cheia and j["usado"] >= 100 else "reset conhecido"
                parte += f" [{rotulo}: {j['reset'].astimezone().isoformat(timespec='minutes')}]"
            partes.append(parte)
        plano = f" [{p['plano']}]" if p["plano"] else ""
        reserva = ""
        if p["reserva_maestro"]:
            reserva = " | pool compartilhado com o Maestro (acompanhe 5h)"
        detalhe = ""
        if p["veto_despacho"]:
            detalhe = f" (veto: {p['veto_despacho']}, só reconferir a leitura)"
        elif p["despacho"] == "reconferir":
            detalhe = " (confira o banner com maestri check)"
        elif p["estado"] == "desconhecido":
            detalhe = " (tarefa pequena de sondagem ou confira com maestri check)"
        janelas = " · ".join(partes) or "sem janelas"
        elegivel = "sim" if p["elegivel"] else "não"
        if p.get("eh_codex"):
            cabecalho = f"Codex conta {p.get('conta') or 'Padrão'}{plano} / {p['medidor']}"
        elif p.get("via_claude") == "Antigravity":
            cabecalho = f"{p['provedor']}{plano} / {p['medidor']} (cota Claude/GPT do plano Gemini, não o Claude Pro)"
        else:
            cabecalho = f"{p['provedor']}{plano} / {p['medidor']}"
        linhas.append(f"{cabecalho}: {janelas} | estado {p['estado']} | "
                      f"elegível: {elegivel}, {p['despacho']}{detalhe}{reserva}")
    linhas.append(linha_claude)
    def _eh_gemini(p):
        return p["provedor"].casefold() == "antigravity" and p["via_claude"] is None

    ordem = sorted(
        (p for p in pools if p["uso_max"] is not None and (p["estado"] == "ready" or p["veto_despacho"])),
        key=lambda p: (0 if _eh_gemini(p) else 1, p["uso_max"], p["reset_min"] or datetime.max.replace(tzinfo=timezone.utc)),
    )
    folga = [f"{p['provedor']}/{p['medidor']} ({100 - round(p['uso_max'])}% livre)" for p in ordem if p["despacho"] == "rotina"]
    poupe = [
        f"{p['provedor']}/{p['medidor']} ({round(p['uso_max'])}%)"
        for p in ordem
        if (_gemini_apertado(p["janelas"], p["uso_max"]) if _eh_gemini(p) else p["uso_max"] >= 80)
    ]
    if folga:
        linhas.append("Gaste primeiro: " + " > ".join(folga))
    if poupe:
        linhas.append("Poupe (>=80%): " + ", ".join(poupe))
    return linhas + [f"aviso: {a}" for a in avisos]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    pools, avisos = ler_cotas()
    if "--json" in sys.argv:
        claude = ordem_claude(pools)
        if claude["reset"]:
            claude["reset"] = claude["reset"].isoformat()
        for p in pools:
            p["reset_min"] = p["reset_min"].isoformat() if p["reset_min"] else None
            p["ultima_leitura"] = p["ultima_leitura"].isoformat() if p["ultima_leitura"] else None
            for j in p["janelas"]:
                j["reset"] = j["reset"].isoformat() if j["reset"] else None
        print(json.dumps({"pools": pools, "avisos": avisos, "ordem_claude": claude}, ensure_ascii=False, indent=1))
        return 0
    linhas = resumo_linhas(pools, avisos)
    atual = Path.cwd()
    pasta = next((raiz / ".maestri" for raiz in (atual, *atual.parents)
                  if (raiz / ".maestri").is_dir()), atual / ".maestri")
    if linha := distribuicao_recente(pasta):
        linhas.append(linha)
    if linha := custo_por_despacho(pasta):
        linhas.append(linha)
    print("\n".join(linhas))
    return 0 if pools else 1


if __name__ == "__main__":
    sys.exit(main())
