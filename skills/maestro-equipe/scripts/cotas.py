"""Mostra a cota de cada provedor (Claude, Codex, Antigravity...) lida do Maestri.

Uso:
    python cotas.py [--json]

Fonte: <MAESTRI_DATA_DIR>/usage/providers/.status.json, que o próprio Maestri
atualiza a cada 5-10 min. Nada é enviado para fora; só leitura local.
A linha "Gaste primeiro" ordena os pools pela folga (100% - o maior uso entre
as janelas) e, no empate, pelo reset mais próximo: cota que vai renovar logo
e está sobrando é cota que se perde se ninguém usar.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

JANELAS = {18000: "5h", 604800: "semanal", 2592000: "mensal", 86400: "diária"}


def arquivo_status() -> Path:
    base = os.environ.get("MAESTRI_DATA_DIR") or str(Path.home() / ".maestri")
    return Path(base) / "usage" / "providers" / ".status.json"


def _data(texto):
    if not texto:
        return None
    try:
        return datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        return None


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


def ler_cotas():
    """Devolve (pools, avisos). Cada pool: provedor, medidor, plano, janelas[], uso_max, reset_min."""
    caminho = arquivo_status()
    if not caminho.exists():
        return [], [f"sem dados de cota: {caminho} não existe (Maestri sem monitor de uso?)"]
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    agora = datetime.now(timezone.utc)
    pools, avisos = [], []
    for prov in dados.get("providers", []):
        if not prov.get("enabled", True):
            continue
        nome = prov.get("name") or prov.get("id", "?")
        ultimo = _data(prov.get("lastSuccessAt"))
        if ultimo and (agora - ultimo).total_seconds() > 3600:
            horas = round((agora - ultimo).total_seconds() / 3600, 1)
            avisos.append(f"{nome}: última leitura há {horas} h (dados podem estar velhos)")
        if prov.get("state") not in (None, "ready"):
            avisos.append(f"{nome}: estado {prov.get('state')}")
        for med in prov.get("meters", []):
            janelas = []
            for j in med.get("windows", []):
                dur = j.get("durationSeconds")
                rotulo = JANELAS.get(dur) or (f"{round(dur / 3600)}h" if dur else (j.get("title") or "?"))
                usado = float(j.get("usedPercent") or 0)
                reset = _data(j.get("resetsAt"))
                janelas.append({"janela": rotulo, "usado": usado, "reset": reset, "falta": _falta(reset, agora)})
            if not janelas:
                continue
            uso_max = max(j["usado"] for j in janelas)
            resets = [j["reset"] for j in janelas if j["reset"]]
            pools.append({
                "provedor": nome,
                "plano": prov.get("plan") or "",
                "medidor": med.get("label") or med.get("id") or "",
                "janelas": janelas,
                "uso_max": uso_max,
                "reset_min": min(resets) if resets else None,
            })
    return pools, avisos


def resumo_linhas(pools, avisos):
    linhas = []
    if not pools:
        return avisos or ["sem dados de cota"]
    for p in pools:
        partes = " · ".join(f"{j['janela']} {round(j['usado'])}% (reset {j['falta']})" for j in p["janelas"])
        plano = f" [{p['plano']}]" if p["plano"] else ""
        linhas.append(f"{p['provedor']}{plano} / {p['medidor']}: {partes}")
    ordem = sorted(pools, key=lambda p: (p["uso_max"], p["reset_min"] or datetime.max.replace(tzinfo=timezone.utc)))
    folga = [f"{p['provedor']}/{p['medidor']} ({100 - round(p['uso_max'])}% livre)" for p in ordem if p["uso_max"] < 80]
    poupe = [f"{p['provedor']}/{p['medidor']} ({round(p['uso_max'])}%)" for p in ordem if p["uso_max"] >= 80]
    if folga:
        linhas.append("Gaste primeiro: " + " > ".join(folga))
    if poupe:
        linhas.append("Poupe (>=80%): " + ", ".join(poupe))
    return linhas + [f"aviso: {a}" for a in avisos]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    pools, avisos = ler_cotas()
    if "--json" in sys.argv:
        for p in pools:
            p["reset_min"] = p["reset_min"].isoformat() if p["reset_min"] else None
            for j in p["janelas"]:
                j["reset"] = j["reset"].isoformat() if j["reset"] else None
        print(json.dumps({"pools": pools, "avisos": avisos}, ensure_ascii=False, indent=1))
        return 0
    print("\n".join(resumo_linhas(pools, avisos)))
    return 0 if pools else 1


if __name__ == "__main__":
    sys.exit(main())
