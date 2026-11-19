"""Prepara o kit do Maestro nesta máquina e imprime o comando do preset.

Uso:
    python instalar.py [--modelo opus] [--effort medium] [--nome Maestro]

Gera settings.gerado.json (ao lado deste arquivo) com o hook PreToolUse
apontando para guarda.py com caminhos absolutos, e imprime:
- o comando do terminal do Maestro (claude com --append-system-prompt-file e --settings);
- a linha `maestri preset create` para cadastrar o preset com o modo Maestro ligado.
Não altera nada fora desta pasta. Rode de novo se mover a skill de lugar.
"""
import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def caminho(p: Path) -> str:
    return p.as_posix()  # barras normais funcionam no Windows e evitam escapes


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="opus")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--nome", default="Maestro")
    args = ap.parse_args()

    python = caminho(Path(sys.executable))
    guarda = caminho(AQUI / "guarda.py")
    settings = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "*",
                    "hooks": [{"type": "command", "command": f'"{python}" "{guarda}"', "timeout": 15}],
                }
            ]
        }
    }
    destino = AQUI / "settings.gerado.json"
    destino.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    comando = (
        f'claude --model {args.modelo} --effort {args.effort} '
        f'--append-system-prompt-file "{caminho(AQUI / "sistema.md")}" '
        f'--settings "{caminho(destino)}"'
    )
    print(f"Gerado: {caminho(destino)}")
    print("\nComando do terminal do Maestro:")
    print(f"  {comando}")
    print("\nCadastrar o preset (rode num terminal com o modo Maestro ligado, ou peça ao usuário):")
    print(f"  maestri preset create \"{args.nome}\" --command '{comando}' --maestro on")
    print("\nTestar o guarda: python " + caminho(AQUI / "guarda.py") + " --teste")
    return 0


if __name__ == "__main__":
    sys.exit(main())
