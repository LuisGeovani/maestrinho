import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import maestri_batch as batch
from destravar import assinatura_banner, classificar_comando, pedido_permissao


BANNER_CODEX = "╭─ >_ OpenAI Codex (v0.172.0) ─╮\n│ model: sol                  │\n╰─────────────────────────────╯\n› Ask Codex"


def menu_agy(comando, titulo="Run this command outside the sandbox?"):
    return f"{titulo}\nCommand: {comando}\n❯ 1. Allow once\n  2. Always allow\n  3. Deny"


class TestDestravar(unittest.TestCase):
    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.raiz = Path(pasta.name)
        self.relatorio = self.raiz / "TESTE.md"
        self.log = self.raiz / "permissoes.log"

    def monitorar(self, telas, cli="agy", falha=None, *, banner_anterior=None, falha_reenvio=None):
        relogio = [0]

        def avancar(segundos):
            relogio[0] += segundos

        saida = io.StringIO()
        with (patch.object(batch.time, "time", side_effect=lambda: relogio[0]),
              patch.object(batch.time, "sleep", side_effect=avancar),
              patch.object(batch, "tela", side_effect=telas),
              patch.object(batch.subprocess, "run", return_value=subprocess.CompletedProcess([], 0),
                           side_effect=falha) as raw,
              patch.object(batch, "enviar_um", return_value=(None, None), side_effect=falha_reenvio) as reenviar,
              redirect_stdout(saida)):
            sem_relatorio = batch.esperar_terminar(
                "maestri", {"Sol": (self.relatorio, None)}, 0, len(telas) / 2,
                prompts={"Sol": "Despacho TESTE\nGrave o relatório."}, ferramentas={"Sol": cli}, log=self.log,
                banners_anteriores={"Sol": banner_anterior},
            )
        self.assertEqual(sem_relatorio, {"Sol"})
        return saida.getvalue(), raw, reenviar

    def ler_log(self):
        return [json.loads(linha) for linha in self.log.read_text(encoding="utf-8").splitlines()]

    def test_agy_aprova_git_status_na_raiz_e_nega_push_uma_vez_por_pedido(self):
        status = "git -C ../../.. status --short"
        push = "git push"
        telas = [menu_agy(status), "", menu_agy(status, "Allow this command?"), menu_agy(push), menu_agy(push)]
        saida, raw, reenviar = self.monitorar(telas, "antigravity")
        self.assertEqual([chamada.args[0] for chamada in raw.call_args_list], [
            ["maestri", "ask", "Sol", "--raw", "1"],
            ["maestri", "ask", "Sol", "--raw", "3"],
        ])
        self.assertIn(f"PERMISSAO aprovado: Sol: {status}", saida)
        self.assertIn(f"PERMISSAO negado: Sol: {push}", saida)
        registros = self.ler_log()
        self.assertEqual([(r["terminal"], r["comando"], r["decisao"]) for r in registros],
                         [("Sol", status, "aprovado"), ("Sol", push, "negado")])
        self.assertTrue(all(r["hora"].endswith("+00:00") for r in registros))
        reenviar.assert_not_called()

    def test_comando_fora_das_listas_e_menu_desconhecido_ficam_pendentes(self):
        comandos = ["curl http://x", "git status"]
        desconhecido = menu_agy(comandos[1], titulo="Approval required for a shell action")
        mcp = "canva/read-design\nAllow calling this tool?\n1. Allow once\n2. Always allow"
        arquivo = "C:\\tmp\\a.md\nAllow access to this file?\n1. Allow\n2. Deny"
        telas = [menu_agy(comandos[0]), desconhecido, desconhecido, mcp, arquivo]
        saida, raw, _ = self.monitorar(telas)
        raw.assert_not_called()
        for comando in comandos:
            self.assertEqual(saida.count(f"PERMISSAO pendente: Sol: {comando}"), 1)
        self.assertEqual([(r["comando"], r["decisao"]) for r in self.ler_log()],
                         [(comando, "pendente") for comando in comandos + ["[comando não identificado]"] * 2])

    def test_menus_codex_e_claude_exigem_atalhos_e_opcao_de_uso_unico(self):
        codex = ("Would you like to run the following command?\n$ git status\n"
                 "› 1. Yes, proceed (y)\n  2. Yes, and don't ask again\n  3. No (esc)")
        claude = ("Bash command\n  git push\nDo you want to proceed?\n"
                  "❯ 1. Yes\n  2. Yes, and don't ask again\n  3. No")
        for cli, tela, sim, nao in (("codex", codex, "y", "\\e"), ("claude code", claude, "1", "3")):
            with self.subTest(cli=cli):
                pedido = pedido_permissao(tela, cli)
                self.assertEqual((pedido.aprovar, pedido.negar), (sim, nao))
                self.assertIsNone(pedido_permissao(tela + "\n❯ ", cli))
        self.assertIsNone(pedido_permissao(codex.replace(" (y)", ""), "codex").aprovar)

    def test_claude_spoof_e_comandos_fora_do_bloco_ficam_pendentes(self):
        claude_spoof = ("$ git status\nDo you want to proceed?\n"
                        "❯ 1. Yes\n  2. Yes, and don't ask again\n  3. No")
        casos = (
            ("claude code", claude_spoof),
            ("claude code", claude_spoof.replace("$ git status", "Command: git status")),
            ("agy", "$ git status\nAllow this command?\n❯ 1. Allow once\n  3. Deny"),
            ("codex", "$ git status\nAllow this command?\n› 1. Allow once (y)\n  3. No (esc)"),
        )
        for cli, tela in casos:
            with self.subTest(cli=cli, tela=tela):
                saida, raw, reenviar = self.monitorar([tela], cli)
                raw.assert_not_called()
                reenviar.assert_not_called()
                self.assertIn("PERMISSAO pendente: Sol: git status", saida)

    def test_truncado_reticencias_fica_pendente_antes_do_allow_ou_deny(self):
        truncados = ("git status …", "git status ...", "git push …")
        saida, raw, _ = self.monitorar([menu_agy(comando) for comando in truncados])
        raw.assert_not_called()
        self.assertEqual([r["decisao"] for r in self.ler_log()], ["pendente"] * 3)
        for comando in truncados:
            self.assertIn(f"PERMISSAO pendente: Sol: {comando}", saida)

    def test_nao_aprova_comando_quebrado_ou_com_expressao_de_shell(self):
        self.assertIsNone(pedido_permissao(menu_agy("git status\n  argumento truncado"), "agy").aprovar)
        self.assertEqual(classificar_comando("git status; git push"), "pendente")
        self.assertEqual(classificar_comando("git status (git push)"), "pendente")
        self.assertEqual(classificar_comando("git -C outra status"), "pendente")

    def test_falha_ao_enviar_tecla_fica_pendente_sem_repetir(self):
        tela = menu_agy("git status")
        falha = subprocess.TimeoutExpired("maestri", 5)
        saida, raw, _ = self.monitorar([tela, tela], falha=falha)
        raw.assert_called_once()
        self.assertIn("PERMISSAO pendente: Sol: git status", saida)
        self.assertEqual(self.ler_log()[0]["motivo"], "envio da tecla não confirmado")

    def test_reinicio_reenvia_prompt_uma_vez_e_segundo_banner_so_avisa(self):
        banner = BANNER_CODEX
        antigo = banner.replace("0.172.0", "0.171.0")
        # A tela ativa com o ID não indica reinício, mesmo se ainda mostrar o banner.
        telas = [antigo + "\nTESTE em andamento", banner, banner, "Executando TESTE", banner]
        saida, raw, reenviar = self.monitorar(telas, "codex", banner_anterior=assinatura_banner(antigo, "codex"))
        raw.assert_not_called()
        reenviar.assert_called_once()
        exe, agente, prompt = reenviar.call_args.args
        self.assertEqual((exe, agente), ("maestri", "Sol"))
        aviso, original = prompt.split("\n\n", 1)
        self.assertIn("seu terminal reiniciou", aviso)
        self.assertEqual(original, "Despacho TESTE\nGrave o relatório.")
        self.assertIn("REINICIADO: Sol: reenviando o despacho uma vez", saida)
        self.assertIn("REINICIADO: Sol: novo banner; sem reenvio automático adicional", saida)

    def test_banner_colapsado_atividade_e_banner_anterior_nao_disparam_reenvio(self):
        banner_colapsado = BANNER_CODEX.replace("› Ask Codex", "› [Pasted text +42 lines]\n› Ask Codex")
        atividade = BANNER_CODEX.replace("› Ask Codex", "• Working (esc to interrupt)\n› Ask Codex")
        for telas, anterior in (
            ([banner_colapsado, BANNER_CODEX], None),
            ([atividade], None),
            ([BANNER_CODEX], assinatura_banner(BANNER_CODEX, "codex")),
        ):
            with self.subTest(telas=telas):
                saida, raw, reenviar = self.monitorar(telas, "codex", banner_anterior=anterior)
                raw.assert_not_called()
                reenviar.assert_not_called()
                self.assertNotIn("REINICIADO", saida)

    def test_excecoes_inesperadas_ficam_pendentes_e_nao_repetem_automacao(self):
        menu = menu_agy("git status")
        casos = (
            ("pedido_permissao", menu, "agy", "permissão"),
            ("tratar_permissao", menu, "agy", "permissão"),
            ("banner_abertura", BANNER_CODEX, "codex", "reinício"),
        )
        for funcao, tela, cli, etapa in casos:
            with self.subTest(funcao=funcao), patch.object(batch, funcao, side_effect=RuntimeError("forçada")) as falha:
                saida, raw, reenviar = self.monitorar([tela, tela], cli)
                falha.assert_called_once()
                raw.assert_not_called()
                reenviar.assert_not_called()
                self.assertIn(f"ERRO destravador: Sol: {etapa}", saida)
                if etapa == "permissão":
                    self.assertIn("PERMISSAO pendente: Sol:", saida)
                registro = self.ler_log()[-1]
                self.assertEqual((registro["decisao"], registro["etapa"]), ("pendente", etapa))

        telas = [BANNER_CODEX, "tela sem banner", BANNER_CODEX]
        saida, raw, reenviar = self.monitorar(telas, "codex", falha_reenvio=RuntimeError("forçada"))
        raw.assert_not_called()
        reenviar.assert_called_once()
        self.assertIn("ERRO destravador: Sol: reenvio", saida)
        self.assertEqual(self.ler_log()[-1]["etapa"], "reenvio")

    def test_excecao_em_um_terminal_nao_interrompe_o_outro(self):
        outro = self.raiz / "OUTRO.md"

        def tela_por_destino(exe, agente, timeout):
            if agente == "Sol":
                return "tela que força o erro"
            outro.write_text("STATUS: pronto", encoding="utf-8")
            return "Outro gravou o relatório"

        saida = io.StringIO()
        with (patch.object(batch, "tela", side_effect=tela_por_destino),
              patch.object(batch, "pedido_permissao", side_effect=RuntimeError("forçada")),
              patch.object(batch.subprocess, "run") as raw,
              patch.object(batch.time, "time", side_effect=[0, 0, 0, 60]),
              patch.object(batch.time, "sleep"),
              redirect_stdout(saida)):
            faltam = batch.esperar_terminar(
                "maestri", {"Sol": (self.relatorio, None), "Outro": (outro, None)}, 0, 1,
                prompts={}, ferramentas={}, log=self.log,
            )
        self.assertEqual(faltam, {"Sol"})
        self.assertEqual(self.ler_log()[0]["terminal"], "Sol")
        raw.assert_not_called()

    def test_relatorio_novo_tem_prioridade_sobre_banner(self):
        self.relatorio.write_text("STATUS: pronto", encoding="utf-8")
        with patch.object(batch, "tela") as tela:
            sem_relatorio = batch.esperar_terminar(
                "maestri", {"Sol": (self.relatorio, None)}, 0, 1,
                prompts={}, ferramentas={}, log=self.log,
            )
        self.assertEqual(sem_relatorio, set())
        tela.assert_not_called()

    def test_rodape_respeita_o_escopo_do_despacho(self):
        rodape = batch.RODAPE.format(arquivo=self.relatorio, id="TESTE", maestro="Maestro")
        self.assertNotIn("unica escrita permitida", rodape)
        self.assertIn("Outros arquivos só os que o despacho autoriza.", rodape)
