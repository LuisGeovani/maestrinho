"""Envia um lote de tarefas aos produtores do Maestri e resume as respostas.

Uso:
    python tools/maestri_batch.py tarefas.json [--linhas N] [--filtro TEXTO]

tarefas.json: objeto {"Nome do agente": "prompt", ...} em UTF-8.
O JSON é validado antes do envio; a saída do maestri é sempre conferida,
para que uma falha nunca passe despercebida.
"""
import argparse
import json
import subprocess
import sys


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--linhas", type=int, default=12, help="últimas linhas de cada resposta")
    ap.add_argument("--filtro", default="", help="mostra só linhas que contêm este texto")
    args = ap.parse_args()

    if args.linhas < 1:
        print("ERRO: --linhas precisa ser 1 ou mais.")
        return 2

    with open(args.arquivo, encoding="utf-8") as f:
        tarefas = json.load(f)
    if (
        not isinstance(tarefas, dict)
        or not tarefas
        or not all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in tarefas.items())
    ):
        print("ERRO: o arquivo precisa ser um objeto JSON não vazio {agente: prompt}, só com textos.")
        return 2

    proc = subprocess.run(
        ["maestri", "ask", "--batch", json.dumps(tarefas, ensure_ascii=False)],
        capture_output=True,
    )
    saida = proc.stdout.decode("utf-8", "replace")
    erro = proc.stderr.decode("utf-8", "replace")
    try:
        respostas = json.loads(saida)
    except json.JSONDecodeError:
        print(f"ERRO no envio (código {proc.returncode}):\n{erro or saida}")
        return 1
    if not isinstance(respostas, list):
        print(f"ERRO: resposta inesperada do maestri (código {proc.returncode}):\n{saida[:2000]}")
        return 1

    falhou = proc.returncode != 0
    if falhou:
        print(f"AVISO: maestri terminou com código {proc.returncode}. {erro.strip()}")
    for r in respostas:
        if not isinstance(r, dict):
            print(f"== resposta em formato inesperado: {r!r}"[:500])
            falhou = True
            continue
        nome = r.get("name", "?")
        if "error" in r:
            print(f"== {nome}: ERRO {r['error']}")
            falhou = True
            continue
        linhas = [l for l in r.get("output", "").splitlines() if l.strip()]
        if args.filtro:
            linhas = [l for l in linhas if args.filtro in l]
        print(f"== {nome}")
        print("\n".join(linhas[-args.linhas:]))
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
