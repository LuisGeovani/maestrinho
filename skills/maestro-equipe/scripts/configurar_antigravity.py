"""Configura o Antigravity (agy) para trabalhar na equipe do Maestri. Idempotente.

Uso:
    python configurar_antigravity.py            # aplica o que faltar (com backup) e diz o que mudou
    python configurar_antigravity.py --checar   # só diz se está ok (não altera nada)

O que garante em ~/.gemini/antigravity-cli/settings.json:
- permissions.allow com a regra do aviso de relatório, que serve para qualquer nome de
  Maestro e só aceita o aviso curto (sem ; & | $ crase < >):
      command(regex:^maestri ask "[^"]+" "[^"$`;&|<>]*"$)
- remove a regra antiga do nome fixo "Maestro" com (?s)...(\\s+.*)?$, que aceitava encadear comandos;
- allowNonWorkspaceAccess: true (o produtor abre na pasta de papel e lê o projeto sem pedir).
Backup: settings.json.bak-<data-hora> na mesma pasta, só quando muda algo.
Terminais do Antigravity abertos antes da mudança precisam de `maestri recruit --replace`.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REGRA = 'command(regex:^maestri ask "[^"]+" "[^"$`;&|<>]*"$)'
ARQUIVO = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"


def antiga(regra):
    return regra.startswith("command(regex:(?s)^maestri ask") or regra.startswith("unsandboxed(")


def estado():
    """Devolve (ok, faltando[], dados)."""
    if not ARQUIVO.parent.exists():
        return None, ["Antigravity CLI não configurado nesta máquina (sem ~/.gemini/antigravity-cli)"], None
    try:
        dados = json.loads(ARQUIVO.read_text(encoding="utf-8-sig")) if ARQUIVO.exists() else {}
    except json.JSONDecodeError as e:
        return None, [f"{ARQUIVO} não é JSON válido ({e}); não alterei nada, corrija o arquivo antes"], None
    allow = dados.get("permissions", {}).get("allow", [])
    faltando = []
    if REGRA not in allow:
        faltando.append("regra do aviso de relatório")
    if any(antiga(r) for r in allow):
        faltando.append("remover regra antiga (nome fixo ou unsandboxed)")
    if dados.get("allowNonWorkspaceAccess") is not True:
        faltando.append("allowNonWorkspaceAccess")
    return not faltando, faltando, dados


def resumo():
    ok, faltando, _ = estado()
    if ok is None:
        return "Antigravity: " + faltando[0]
    return "Antigravity: config ok" if ok else "Antigravity: FALTA " + ", ".join(faltando) + " (rode scripts/configurar_antigravity.py)"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ok, faltando, dados = estado()
    if "--checar" in sys.argv or ok is None:
        print(resumo())
        return 0 if ok else 1
    if ok:
        print("Antigravity: config ok, nada a mudar.")
        return 0
    if ARQUIVO.exists():
        backup = ARQUIVO.with_name(f"settings.json.bak-{datetime.now():%Y%m%d-%H%M%S}")
        shutil.copy2(ARQUIVO, backup)
        print(f"backup: {backup}")
    perms = dados.setdefault("permissions", {})
    allow = [r for r in perms.get("allow", []) if not antiga(r)]
    if REGRA not in allow:
        allow.append(REGRA)
    perms["allow"] = allow
    dados["allowNonWorkspaceAccess"] = True
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("Antigravity configurado: " + ", ".join(faltando) + ".")
    print("Terminais do Antigravity abertos antes disto: religue com maestri recruit \"Nome\" --preset P --replace \"Nome\".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
