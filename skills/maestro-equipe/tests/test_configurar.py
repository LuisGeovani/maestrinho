import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import configurar_antigravity as agy  # noqa: E402
import configurar_codex as cdx  # noqa: E402


def casa(regras, cmd):
    for r in regras:
        rx = r[len("command(regex:"):-1]
        flags = 0
        if rx.startswith("(?i)"):
            rx, flags = rx[4:], re.I
        if re.search(rx, cmd, flags):
            return True
    return False


def roda(modulo, *args):
    out = io.StringIO()
    with mock.patch.object(sys, "argv", ["x", *args]), contextlib.redirect_stdout(out):
        try:
            modulo.sys.stdout.reconfigure = lambda **k: None
        except Exception:
            pass
        rc = modulo.main()
    return rc, out.getvalue()


class AgyRegras(unittest.TestCase):
    def test_permite_leitura_e_teste(self):
        for c in ["git status --short", "ls ..", "Get-ChildItem skills", "Get-Content a.md",
                  "python -m unittest discover -s skills/maestro-equipe/tests",
                  "python ../../../skills/maestro-equipe/scripts/cotas.py --x"]:
            self.assertTrue(casa(agy.REGRAS_ALLOW, c), c)

    def test_nao_permite_encadeamento(self):
        for c in ["git status; rm x", "Get-ChildItem a | x", "Get-Content $(x)", "ls > f", "git log && git push",
                  "git status || rm x", "ls `whoami`", "Get-Content < f", "git status\nrm x", "git status\r\nrm x",
                  "ls a\ngit push"]:
            self.assertFalse(casa(agy.REGRAS_ALLOW, c), repr(c))

    def test_maestri_ask_sem_quebra_de_linha(self):
        self.assertTrue(casa([agy.REGRA], 'maestri ask "Maestro" "AUD pronto: x.md"'))
        self.assertFalse(casa([agy.REGRA], 'maestri ask "Maestro" "a\nrm x"'))
        self.assertFalse(casa([agy.REGRA], 'maestri ask "Maes\ntro" "a"'))

    def test_deny(self):
        for c in ["git commit -m x", "git add .", "npm install", "pip install x", "rm -rf x", "Remove-Item a -Recurse",
                  "remove-item a -recurse", "GIT COMMIT -m x", "Python -m pip install x"]:
            self.assertTrue(casa(agy.REGRAS_DENY, c), c)
        self.assertFalse(casa(agy.REGRAS_DENY, "git status"))


class AgyAplicacao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "antigravity-cli"
        self.dir.mkdir()
        self.arq = self.dir / "settings.json"
        self.arq.write_text(json.dumps({"permissions": {"allow": [agy.REGRA_V1, "mcp(x)"]}, "trustedWorkspaces": ["a"]}), encoding="utf-8")
        p = mock.patch.object(agy, "ARQUIVO", self.arq)
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)

    def baks(self):
        return list(self.dir.glob("settings.json.bak-*"))

    def test_sem_flag_so_o_basico(self):
        rc, _ = roda(agy)
        d = json.loads(self.arq.read_text(encoding="utf-8"))
        self.assertEqual(rc, 0)
        self.assertIn(agy.REGRA, d["permissions"]["allow"])
        self.assertNotIn(agy.REGRA_V1, d["permissions"]["allow"])
        self.assertIn("mcp(x)", d["permissions"]["allow"])
        self.assertNotIn("deny", d["permissions"])
        self.assertEqual(len(d["permissions"]["allow"]), 2)
        self.assertTrue(d["allowNonWorkspaceAccess"])
        self.assertEqual(d["trustedWorkspaces"], ["a"])
        self.assertEqual(len(self.baks()), 1)
        self.assertEqual(roda(agy, "--checar")[0], 0)

    def test_idempotente(self):
        roda(agy)
        antes = self.arq.read_text(encoding="utf-8")
        rc, out = roda(agy)
        self.assertEqual(rc, 0)
        self.assertIn("nada a mudar", out)
        self.assertEqual(self.arq.read_text(encoding="utf-8"), antes)
        self.assertEqual(len(self.baks()), 1)

    def test_globais(self):
        self.assertEqual(roda(agy, "--regras-globais", "--checar")[0], 1)
        roda(agy, "--regras-globais")
        d = json.loads(self.arq.read_text(encoding="utf-8"))
        self.assertEqual(d["permissions"]["deny"], agy.REGRAS_DENY)
        self.assertTrue(all(r in d["permissions"]["allow"] for r in agy.REGRAS_ALLOW))
        self.assertEqual(roda(agy, "--regras-globais", "--checar")[0], 0)
        n = len(self.baks())
        roda(agy, "--regras-globais")
        self.assertEqual(len(self.baks()), n)

    def test_json_quebrado_nao_e_tocado(self):
        self.arq.write_text("{x", encoding="utf-8")
        rc, _ = roda(agy)
        self.assertEqual(rc, 1)
        self.assertEqual(self.arq.read_text(encoding="utf-8"), "{x")


class CodexRegras(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.arq = Path(self.tmp.name) / ".codex" / "rules" / "maestri.rules"
        self.arq.parent.parent.mkdir(parents=True)
        p = mock.patch.object(cdx, "ARQUIVO", self.arq)
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_conteudo(self):
        c = cdx.conteudo()
        self.assertIn('prefix_rule(pattern=["git", ["status", "diff", "log", "show"]], decision="allow")', c)
        self.assertIn('prefix_rule(pattern=["python", "-m", "pip"], decision="forbidden")', c)
        self.assertEqual(c, cdx.conteudo())

    def test_sem_flag_nao_grava(self):
        rc, out = roda(cdx)
        self.assertEqual(rc, 0)
        self.assertIn("opt-in", out)
        self.assertFalse(self.arq.exists())

    def test_aplica_idempotente_e_backup(self):
        self.assertEqual(roda(cdx, "--regras-globais", "--checar")[0], 1)
        roda(cdx, "--regras-globais")
        self.assertEqual(self.arq.read_text(encoding="utf-8"), cdx.conteudo())
        self.assertEqual(roda(cdx, "--regras-globais", "--checar")[0], 0)
        self.arq.write_text("velho\n", encoding="utf-8")
        roda(cdx, "--regras-globais")
        self.assertEqual(len(list(self.arq.parent.glob("maestri.rules.bak-*"))), 1)
        self.assertEqual(self.arq.read_text(encoding="utf-8"), cdx.conteudo())
        roda(cdx, "--regras-globais")
        self.assertEqual(len(list(self.arq.parent.glob("maestri.rules.bak-*"))), 1)


if __name__ == "__main__":
    unittest.main()
