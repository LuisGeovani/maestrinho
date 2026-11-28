import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "criar_papel.py"


class TestCriarPapel(unittest.TestCase):
    def test_raiz_sem_agents_md_e_regras_antigravity(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.assertFalse((raiz / "AGENTS.md").exists())
            self.assertFalse((raiz / "CLAUDE.md").exists())
            self.assertFalse((raiz / "GEMINI.md").exists())

            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "Teste",
                    "--projeto",
                    "proj-teste",
                    "--raiz",
                    str(raiz),
                    "--modelo",
                    "Gemini 4 Hydrogen",
                    "--effort",
                    "medium",
                    "--familia",
                    "Gemini",
                    "--perfis",
                    "Volume,Revisor",
                    "--ferramenta",
                    "agy",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

            destino = raiz / ".maestri" / "papeis" / "Teste.md"
            self.assertTrue(destino.is_file())
            texto = destino.read_text(encoding="utf-8")

            self.assertIn("leia os que existirem entre AGENTS.md, CLAUDE.md e GEMINI.md", texto)
            self.assertIn("insumo indispensável citado no despacho", texto)
            self.assertIn("AGENTS.md, CLAUDE.md e GEMINI.md nunca são insumo indispensável", texto)
            self.assertNotIn("arquivo faltando", texto.lower())
            self.assertIsNone(re.search(r"arquivo\s+(?:faltando|ausente).{0,30}pare", texto, re.I))
            for frase in re.split(r"[.;\n]", texto):
                if any(doc in frase for doc in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")):
                    self.assertNotIn("pare", frase.lower())

            self.assertIn("Comandos de leitura e teste dentro da raiz do projeto", texto)
            self.assertIn("a aprovação vale só para os comandos da lista, dentro da raiz", texto)
            self.assertIn("python -m unittest", texto)
            self.assertIn("git status/diff/log", texto)
            self.assertIn("Continuam proibidos git de escrita, instalar pacote, rede para hosts não citados no despacho e escrita fora da raiz.", texto)

            self.assertNotIn("até 5 apontamentos", texto)
            self.assertIn("Se o plugin superpowers estiver disponível, use as skills de método", texto)
            self.assertIn("não use subagent-driven-development, dispatching-parallel-agents nem finishing-a-development-branch", texto)
            self.assertIn("nunca faça commit, merge, worktree ou PR por conta de uma skill: o despacho e o Maestro mandam.", texto)


if __name__ == "__main__":
    unittest.main()
