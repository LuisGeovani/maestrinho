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
- allowlist estreita de leitura/teste (PowerShell, que é o shell do agy no Windows; rg e wc não existem lá)
  e deny explícito de git que grava, instalação de pacote e remoção recursiva. Regex ancorada, sem ; & | < > $ crase.
- --regras-globais (opt-in, só o usuário pede): grava também a allowlist e o deny abaixo. Sem a flag, só a regra
  do maestri ask e o allowNonWorkspaceAccess. O deny vale para TODO uso do agy (inclusive o pessoal).
- --sem-sandbox (opcional): enableTerminalSandbox=false. Sem isso o shell do agy NÃO enxerga a raiz do
  projeto ("Acesso negado"), mesmo com --add-dir. ATENÇÃO: efeito ainda não testado (AUD-F5); só o Maestro aplica.
Backup: settings.json.bak-<data-hora> na mesma pasta, só quando muda algo.
Terminais do Antigravity abertos antes da mudança precisam de `maestri recruit --replace`.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REGRA_V1 = 'command(regex:^maestri ask "[^"]+" "[^"$`;&|<>]*"$)'  # sem exclusão de quebra de linha; trocada por REGRA
REGRA = r'command(regex:^maestri ask "[^"\r\n]+" "[^"$`;&|<>\r\n]*"$)'
SEG = r"[^;&|<>$`\r\n]"  # nenhum encadeamento, redirecionamento, substituição nem quebra de linha
REGRAS_ALLOW = [
    REGRA,
    f"command(regex:^(Get-ChildItem|ls|dir)( {SEG}*)?$)",
    f"command(regex:^(Get-Content|cat|type) {SEG}+$)",
    f"command(regex:^Select-String {SEG}+$)",
    f"command(regex:^git (status|diff|log|show)( {SEG}*)?$)",
    f"command(regex:^python -m unittest( {SEG}*)?$)",
    f"command(regex:^python ([.][.]/)*skills/[A-Za-z0-9_-]+/scripts/[A-Za-z0-9_]+[.]py( {SEG}*)?$)",
]
REGRAS_DENY = [
    "command(regex:(?i)^git (add|commit|push|reset|checkout|stash|switch|rebase|merge|clean)( .*)?$)",
    "command(regex:(?i)^(pip|pip3|npm|npx|pnpm|yarn) (install|i|add|ci)( .*)?$)",
    "command(regex:(?i)^python -m pip( .*)?$)",
    "command(regex:(?i)^(rm|Remove-Item|del|rd|rmdir)( .*)? -([rR][A-Za-z]*|Recurse)( .*)?$)",
]
ARQUIVO = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"


def antiga(regra):
    return regra == REGRA_V1 or regra.startswith("command(regex:(?s)^maestri ask") or regra.startswith("unsandboxed(")


def estado(sem_sandbox=False, globais=False):
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
    if globais and any(r not in allow for r in REGRAS_ALLOW[1:]):
        faltando.append("allowlist de leitura/teste")
    if globais and any(r not in dados.get("permissions", {}).get("deny", []) for r in REGRAS_DENY):
        faltando.append("deny de git que grava/instalação/remoção")
    if sem_sandbox and dados.get("enableTerminalSandbox") is not False:
        faltando.append("enableTerminalSandbox=false")
    if any(antiga(r) for r in allow):
        faltando.append("remover regra antiga (nome fixo ou unsandboxed)")
    if dados.get("allowNonWorkspaceAccess") is not True:
        faltando.append("allowNonWorkspaceAccess")
    return not faltando, faltando, dados


def resumo(sem_sandbox=False, globais=False):
    ok, faltando, _ = estado(sem_sandbox, globais)
    if ok is None:
        return "Antigravity: " + faltando[0]
    return "Antigravity: config ok" if ok else "Antigravity: FALTA " + ", ".join(faltando) + " (rode scripts/configurar_antigravity.py)"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sem_sandbox = "--sem-sandbox" in sys.argv
    globais = "--regras-globais" in sys.argv
    ok, faltando, dados = estado(sem_sandbox, globais)
    if "--checar" in sys.argv or ok is None:
        print(resumo(sem_sandbox, globais))
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
    for r in (REGRAS_ALLOW if globais else [REGRA]):
        if r not in allow:
            allow.append(r)
    perms["allow"] = allow
    if globais:
        deny = perms.get("deny", [])
        perms["deny"] = deny + [r for r in REGRAS_DENY if r not in deny]
    if sem_sandbox:
        dados["enableTerminalSandbox"] = False
    dados["allowNonWorkspaceAccess"] = True
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("Antigravity configurado: " + ", ".join(faltando) + ".")
    print("Terminais do Antigravity abertos antes disto: religue com maestri recruit \"Nome\" --preset P --replace \"Nome\".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
