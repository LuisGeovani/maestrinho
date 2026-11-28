"""Configura as regras de comando do Codex para a equipe do Maestri. Idempotente.

Uso:
    python configurar_codex.py --regras-globais            # grava ~/.codex/rules/maestri.rules (backup se mudou)
    python configurar_codex.py --regras-globais --checar   # só confere (não altera nada)

O que faz: cria ~/.codex/rules/maestri.rules, arquivo SEPARADO do default.rules (não toca no que o Codex
gravou sozinho nem no config.toml do usuário). As regras são prefix_rule do execpolicy do Codex:
allow para leitura e teste, forbidden para git que grava, instalação de pacote e remoção recursiva.
Comando que não casa com nenhuma regra segue a política de aprovação da sessão.

O que NÃO faz: não muda approval_policy nem sandbox_mode no config.toml. Hoje o config.toml global tem
approval_policy="never" e sandbox_mode="danger-full-access" (é o "YOLO mode" da tela). Para os produtores
use as flags no preset, que vencem o config.toml só naquela sessão:
    codex -s workspace-write -a on-request --add-dir ../../.. ...
Opt-in: o arquivo só é gravado com --regras-globais (as regras forbidden valem para todo uso do Codex,
inclusive o pessoal do usuário, ex.: git commit). Sem a flag, o script não grava nada.
Limite do prefix_rule: casa só o início do comando, na ordem dada; flags fora de ordem escapam
(Remove-Item a -Recurse e rm a -r NÃO casam; rm -rf e Remove-Item -Recurse a casam).
Efeito em sessão real (prompt sumindo para os comandos allow) ainda NÃO foi testado (AUD-F5).
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

ARQUIVO = Path.home() / ".codex" / "rules" / "maestri.rules"

LEITURA = [
    ["rg"], ["grep"], ["wc"], ["ls"], ["cat"], ["head"], ["tail"],
    ["Get-ChildItem"], ["Get-Content"], ["Select-String"],
    ["git", ["status", "diff", "log", "show"]],
    ["python", "-m", "unittest"],
    ["python", "-I", "-m", "unittest"],
]
PROIBIDO = [
    ["git", ["add", "commit", "push", "reset", "checkout", "stash", "switch", "rebase", "merge", "clean"]],
    ["python", "-m", "pip"], ["pip", ["install", "uninstall"]], ["pip3", ["install", "uninstall"]],
    ["npm", ["install", "i", "ci", "add"]], ["npx"], ["pnpm", ["install", "add"]], ["yarn", ["install", "add"]],
    ["rm", "-rf"], ["rm", "-r"], ["Remove-Item", "-Recurse"],
]


def _fmt(p):
    return "[" + ", ".join(_fmt(x) if isinstance(x, list) else '"' + x + '"' for x in p) + "]"


def conteudo():
    linhas = ["# Gerado por skills/maestro-equipe/scripts/configurar_codex.py (não edite à mão).", ""]
    linhas += [f'prefix_rule(pattern={_fmt(p)}, decision="allow")' for p in LEITURA]
    linhas += [f'prefix_rule(pattern={_fmt(p)}, decision="forbidden")' for p in PROIBIDO]
    return "\n".join(linhas) + "\n"


def estado():
    if not ARQUIVO.parent.parent.exists():
        return None, "Codex não configurado nesta máquina (sem ~/.codex)"
    if not ARQUIVO.exists():
        return False, "FALTA ~/.codex/rules/maestri.rules"
    atual = ARQUIVO.read_text(encoding="utf-8")
    return (atual == conteudo()), ("rules ok" if atual == conteudo() else "FALTA atualizar ~/.codex/rules/maestri.rules")


def resumo():
    ok, msg = estado()
    return "Codex: " + msg + ("" if ok else " (rode scripts/configurar_codex.py --regras-globais)" if ok is False else "")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if "--regras-globais" not in sys.argv:
        print("Codex: regras globais são opt-in; nada gravado (use --regras-globais se o usuário pedir).")
        return 0
    ok, msg = estado()
    if "--checar" in sys.argv or ok is None:
        print(resumo())
        return 0 if ok else 1
    if ok:
        print("Codex: rules ok, nada a mudar.")
        return 0
    if ARQUIVO.exists():
        backup = ARQUIVO.with_name(f"maestri.rules.bak-{datetime.now():%Y%m%d-%H%M%S}")
        shutil.copy2(ARQUIVO, backup)
        print(f"backup: {backup}")
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(conteudo(), encoding="utf-8", newline="\n")
    print("Codex: regras gravadas em " + str(ARQUIVO))
    print("Preset dos produtores: codex -s workspace-write -a on-request --add-dir ../../.. (flags vencem o config.toml).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
