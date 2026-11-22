import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cotas
import maestri_batch as batch


FORMACAO = """| Terminal | Ferramenta | Modelo | Effort | Perfis | Desde |
|---|---|---|---|---|---|
| Tocha | Claude Code (preset Sonnet) | Claude Sonnet 5.5 | medium | Volume | hoje |
| Vela | Claude Code (preset Claude Code + `--command "claude --model sonnet"`) | Claude Sonnet 5.5 | medium | Volume | hoje |
| Prumo | Codex (preset Codex Sol) | GPT-6.2 Sol | medium | Volume | hoje |
| Malho | Antigravity (preset Agy Hydrogen) | Gemini 4 Hydrogen | high | Volume | hoje |
| Ferro | Antigravity (preset Agy Argon) | Gemini 4 Argon | high | Volume | hoje |
| Pavio | OpenCode (preset OpenCode Gratis) | DeepSeek V4.1 Flash Free | — | Batedor | hoje |
| Agy Claude | Antigravity (preset Agy Sonnet) | Claude Sonnet | high | Volume | hoje |
| Agy GPT | Antigravity (preset Agy GPT) | GPT 5 | high | Volume | hoje |
"""
DESPACHO = """Contexto comum.
### Tocha | T1
Faça o teste.
### Vela | T2
Faça o teste.
mOTIVO Pool: Precisa deste pool.
### Prumo | T3
Valide com: python -m unittest
### Malho | T4
Faça o teste.
### Ferro | T5
Faça o teste.
### Pavio | T6
Faça o teste.
### Ausente | T7
Faça o teste.
"""
DISTRIBUICAO = "Claude 1 · GPT 1 · Gemini 2 · aberto 1 · desconhecido 1"
RETENCAO = ("RETIDO (equilíbrio): Tocha | T1: Claude Pro 33% vs Gemini 4 Argon 7%; "
            "reencaminhe ou justifique com 'Motivo pool:'")


class Saida(io.StringIO):
    def reconfigure(self, **kwargs):
        pass


class TestEquilibrio(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.raiz = Path(temp.name)
        self.pasta = self.raiz / ".maestri"
        self.pasta.mkdir()
        self.equipe = self.pasta / "equipe.md"
        self.equipe.write_text(FORMACAO, encoding="utf-8")
        self.despacho = self.pasta / "lote.md"
        self.despacho.write_text(DESPACHO, encoding="utf-8")
        self.log = self.pasta / cotas.LOG_DISTRIBUICAO
        self.agora = datetime.now(timezone.utc)
        self.status = self.raiz / "status.json"
        self.addCleanup(patch.stopall)
        patch.object(cotas, "arquivo_status", return_value=self.status).start()
        self.preset = patch.object(batch, "rodar", return_value=(None, None)).start()

    def cotas_do_caso(self, idade_claude=0, argon=7, opencode=0):
        def medidor(nome, semanal, cinco_horas=None):
            janelas = [{"durationSeconds": 604800, "usedPercent": semanal,
                        "resetsAt": (self.agora + timedelta(days=3)).isoformat()}]
            if cinco_horas is not None:
                janelas.append({"durationSeconds": 18000, "usedPercent": cinco_horas,
                                "resetsAt": (self.agora + timedelta(hours=3)).isoformat()})
            return {"label": nome, "windows": janelas}

        def provedor(ident, nome, plano, medidores, idade=0):
            return {"id": ident, "name": nome, "plan": plano, "meters": medidores,
                    "state": "ready", "lastSuccessAt": (self.agora - timedelta(hours=idade)).isoformat()}

        self.status.write_text(json.dumps({"providers": [
            provedor("claude", "Claude Code", "Pro", [medidor("Limites do plano", 33, 17)], idade_claude),
            provedor("codex", "Codex", "Plus", [medidor("Codex", 10, 2)]),
            provedor("antigravity", "Antigravity", "", [
                medidor("Gemini Models", 18, 3),
                medidor("Gemini 4 Argon", argon),
                medidor("Claude and GPT models", 100),
            ]),
            provedor("opencode", "OpenCode", "Free", [medidor("grátis", opencode)]),
        ]}), encoding="utf-8")
        return cotas.ler_cotas()[0]

    def avaliar(self, texto, pools):
        _, secoes = batch.ler_despacho(texto)
        saida = Saida()
        with redirect_stdout(saida):
            aceitas, retidas = batch.avaliar_equilibrio("maestri", batch.ler_formacao(self.raiz), secoes, pools)
        return aceitas, retidas, saida.getvalue()

    def rodar_lote(self, *flags, falhas=None, saidas=None):
        _, secoes = batch.ler_despacho(self.despacho.read_text(encoding="utf-8"))
        conectados = {secao["agente"] for secao in secoes}
        argv = ["maestri_batch.py", str(self.despacho), "--raiz", str(self.raiz), *flags]
        falhas = falhas or {}
        saidas = saidas or {}
        saida = Saida()
        with (patch.object(sys, "argv", argv), redirect_stdout(saida),
              patch.object(batch, "maestri_exe", return_value="maestri"),
              patch.object(batch, "ler_list", return_value=("Maestro", conectados, "")),
              patch.object(batch, "tela", return_value=""),
              patch.object(batch, "esperar_pronto", return_value=None) as esperar,
              patch.object(batch, "enviar_tudo", side_effect=lambda exe, prompts, *args, **kwargs: {
                  agente: (saidas.get(agente, "entregue"), falhas.get(agente))
                  for agente in prompts
              }) as enviar):
            codigo = batch.main()
        return codigo, saida.getvalue(), esperar, enviar

    def test_cotas_do_caso_priorizam_maior_janela_e_excluem_opencode(self):
        aceitas, retidas, avisos = self.avaliar(DESPACHO, self.cotas_do_caso())
        self.assertEqual(retidas, [RETENCAO])
        self.assertEqual({agente: dados[2] for agente, dados in aceitas.items()}, {
            "Vela": "Claude Pro", "Prumo": "Codex", "Malho": "Gemini Models",
            "Ferro": "Gemini 4 Argon", "Pavio": "grátis", "Ausente": "desconhecido",
        })
        self.assertEqual(aceitas["Vela"][3], "Precisa deste pool.")
        self.assertIn("Ausente | T7: pool desconhecido", avisos)

    def test_leitura_antiga_e_formacao_ausente_so_avisam(self):
        pools = self.cotas_do_caso(idade_claude=2)
        aceitas, retidas, avisos = self.avaliar(DESPACHO, pools)
        self.assertIn("Tocha", aceitas)
        self.assertEqual(retidas, [])
        self.assertIn("Claude Pro sem leitura fresca", avisos)
        self.equipe.unlink()
        aceitas, retidas, avisos = self.avaliar(DESPACHO, pools)
        self.assertEqual(len(aceitas), 7)
        self.assertEqual(retidas, [])
        self.assertEqual(avisos.count("pool desconhecido"), 7)

    def test_limiar_inclusivo_e_justificativa_da_propria_secao(self):
        pools = self.cotas_do_caso()
        next(p for p in pools if p["via_claude"] == "Claude Code")["uso_max"] = 22
        _, retidas, _ = self.avaliar("Motivo pool: no contexto comum.\n" + DESPACHO, pools)
        self.assertEqual(len(retidas), 1)
        self.assertIn("22% vs Gemini 4 Argon 7%", retidas[0])

    def test_motivo_vazio_nao_libera_secao(self):
        pools = self.cotas_do_caso()
        for motivo in ("Motivo pool:", "Motivo pool: \t", "Motivo pool: \u00a0"):
            with self.subTest(motivo=motivo):
                texto = DESPACHO.replace("mOTIVO Pool: Precisa deste pool.", motivo)
                aceitas, retidas, _ = self.avaliar(texto, pools)
                self.assertNotIn("Vela", aceitas)
                self.assertEqual(len(retidas), 2)
        texto = DESPACHO.replace("mOTIVO Pool: Precisa deste pool.",
                                 "Motivo pool: \t\nmOTIVO Pool: Precisa deste pool.")
        aceitas, retidas, _ = self.avaliar(texto, pools)
        self.assertEqual(aceitas["Vela"][3], "Precisa deste pool.")
        self.assertEqual(retidas, [RETENCAO])

    def test_opencode_gratis_com_uso_alto_passa(self):
        pools = self.cotas_do_caso(opencode=80)
        self.assertTrue(any(p["medidor"] == "grátis" and p["uso_max"] == 80 for p in pools))
        aceitas, retidas, _ = self.avaliar(DESPACHO, pools)
        self.assertEqual(retidas, [RETENCAO])
        self.assertIn("Pavio", aceitas)

    def test_pool_pago_vetado_com_uso_zero_nao_vira_referencia(self):
        self.cotas_do_caso()
        dados = json.loads(self.status.read_text(encoding="utf-8"))
        medidor = dados["providers"][2]["meters"][2]
        medidor["usageAllowed"] = False
        medidor["windows"][0]["usedPercent"] = 0
        self.status.write_text(json.dumps(dados), encoding="utf-8")
        pools, _ = cotas.ler_cotas()
        vetado = next(p for p in pools if p["medidor"] == "Claude and GPT models")
        self.assertEqual((vetado["uso_max"], vetado["veto_despacho"]), (0, "usageAllowed=false"))
        aceitas, retidas, _ = self.avaliar(DESPACHO, pools)
        self.assertEqual(retidas, [RETENCAO])
        self.assertIn("Malho", aceitas)

    def test_status_ausente_ou_com_estrutura_errada_so_avisa(self):
        with patch.object(cotas, "_cotas_rollout", return_value=[]):
            casos = (
                (None, "ausente ou ilegível"),
                ({"providers": "inválido"}, "esperada lista em providers"),
                ({"providers": [None, {"name": "Claude Code", "meters": 7}]},
                 "Claude Code: meters inválido"),
            )
            for dados, aviso in casos:
                with self.subTest(dados=dados):
                    if dados is not None:
                        self.status.write_text(json.dumps(dados), encoding="utf-8")
                    codigo, saida, _, enviar = self.rodar_lote("--sem-rodape")
                    self.assertEqual(codigo, 0)
                    self.assertIn(aviso, saida)
                    self.assertNotIn("RETIDO (equilíbrio)", saida)
                    self.assertEqual(len(enviar.call_args.args[1]), 7)

    def test_status_ignora_entradas_invalidas_e_preserva_pools_validos(self):
        self.cotas_do_caso()
        dados = json.loads(self.status.read_text(encoding="utf-8"))
        dados["providers"][2]["meters"].extend([None, {"label": "Quebrado", "windows": [17]}])
        dados["providers"].append(42)
        self.status.write_text(json.dumps(dados), encoding="utf-8")
        pools, avisos = cotas.ler_cotas()
        self.assertEqual(len(pools), 6)
        self.assertIn("Antigravity: meters[3] inválido, ignorado", avisos)
        self.assertIn("Antigravity/Quebrado: windows inválido, medidor ignorado", avisos)
        self.assertIn("Maestri: providers[4] inválido, ignorado", avisos)

    def test_falha_inesperada_ao_ler_cotas_so_avisa(self):
        with patch.object(batch, "ler_cotas", side_effect=TypeError("estrutura inesperada")):
            codigo, saida, _, enviar = self.rodar_lote("--sem-rodape")
        self.assertEqual(codigo, 0)
        self.assertIn("aviso: falha ao ler cotas: estrutura inesperada", saida)
        self.assertNotIn("RETIDO (equilíbrio)", saida)
        self.assertEqual(len(enviar.call_args.args[1]), 7)

    def test_oserror_ao_gravar_log_so_avisa(self):
        self.cotas_do_caso(idade_claude=2)
        self.log.mkdir()  # Tentar abrir um diretório para escrita produz OSError.
        codigo, saida, _, enviar = self.rodar_lote("--sem-rodape")
        self.assertEqual(codigo, 0)
        self.assertEqual(len(enviar.call_args.args[1]), 7)
        self.assertIn("aviso: não foi possível registrar os envios em distribuicao.log", saida)
        self.assertIn("Distribuição do lote: Claude 2 · GPT 1 · Gemini 2 · aberto 1 · desconhecido 1", saida)

    def test_preset_resolve_as_duas_familias_do_medidor_compartilhado(self):
        pools = self.cotas_do_caso()
        self.preset.side_effect = [("Command: agy --model claude-sonnet", ""),
                                   ("Command: agy --model gpt-5", "")]
        texto = "### Agy Claude | TC\nMotivo pool: teste.\n### Agy GPT | TG\nMotivo pool: teste."
        aceitas, retidas, _ = self.avaliar(texto, pools)
        self.assertEqual(retidas, [])
        self.assertEqual(aceitas["Agy Claude"][1:3], ("Claude", "Claude and GPT models"))
        self.assertEqual(aceitas["Agy GPT"][1:3], ("GPT", "Claude and GPT models"))
        self.assertEqual([c.args[0][-1] for c in self.preset.call_args_list], ["Agy Sonnet", "Agy GPT"])

    def test_mostrar_resume_sem_esperar_enviar_ou_registrar(self):
        self.cotas_do_caso()
        codigo, saida, esperar, enviar = self.rodar_lote("--mostrar")
        self.assertEqual(codigo, 0)
        self.assertIn(RETENCAO, saida)
        self.assertIn("Distribuição do lote: " + DISTRIBUICAO, saida)
        self.assertIn("===== Vela", saida)
        self.assertIn("relatorios", saida)
        self.assertNotIn("===== Tocha", saida)
        self.assertFalse(self.log.exists())
        esperar.assert_not_called()
        enviar.assert_not_called()

    def test_envio_simulado_registra_so_entregas_e_cotas_conta_ultimas_cinco_horas(self):
        self.cotas_do_caso(idade_claude=2)
        codigo, saida, esperar, enviar = self.rodar_lote("--sem-rodape", falhas={"Ferro": "rejeitado"})
        self.assertEqual(codigo, 1)
        prompts = enviar.call_args.args[1]
        self.assertEqual(set(prompts), {"Tocha", "Vela", "Prumo", "Malho", "Ferro", "Pavio", "Ausente"})
        self.assertEqual(esperar.call_count, len(prompts))
        esperado = "Claude 2 · GPT 1 · Gemini 1 · aberto 1 · desconhecido 1"
        self.assertIn("Distribuição do lote: " + esperado, saida)
        linhas = [linha.split("\t") for linha in self.log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(linhas), 6)
        self.assertTrue(all(len(linha) == 6 and cotas._data(linha[0]) for linha in linhas))
        self.assertIn(["T2", "Vela", "Claude", "Claude Pro", "Precisa deste pool."], [l[1:] for l in linhas])
        self.assertNotIn("Ferro", [linha[2] for linha in linhas])
        agora = datetime.now(timezone.utc)
        with self.log.open("a", encoding="utf-8") as log:
            for data in (agora - timedelta(hours=5, seconds=1), agora + timedelta(minutes=1)):
                log.write(f"{data.isoformat()}\tOUTRO\tPrumo\tGPT\tCodex\t\n")
        saida = Saida()
        cwd = Path.cwd()
        try:
            os.chdir(self.pasta)
            with patch.object(sys, "argv", ["cotas.py"]), redirect_stdout(saida):
                self.assertEqual(cotas.main(), 0)
        finally:
            os.chdir(cwd)
        self.assertIn("Despachos nas últimas 5 h por família: " + esperado, saida.getvalue())

    def test_envio_simulado_exclui_retido_do_lote_e_do_log(self):
        self.cotas_do_caso()
        codigo, saida, _, enviar = self.rodar_lote("--sem-rodape")
        self.assertEqual(codigo, 1)
        self.assertNotIn("Tocha", enviar.call_args.args[1])
        self.assertIn(RETENCAO, saida)
        self.assertIn("Distribuição do lote: " + DISTRIBUICAO, saida)
        self.assertNotIn("\tT1\t", self.log.read_text(encoding="utf-8"))

    def test_relatorio_confirma_entrega_tardia_sem_duplicar_envios(self):
        self.cotas_do_caso()

        def gravar_relatorios(exe, pendentes, inicio, minutos):
            self.assertEqual(len(self.log.read_text(encoding="utf-8").splitlines()), 5)
            for caminho, _ in pendentes.values():
                caminho.write_text("STATUS: pronto", encoding="utf-8")
            return set()

        with patch.object(batch, "esperar_terminar", side_effect=gravar_relatorios):
            codigo, saida, _, _ = self.rodar_lote(falhas={"Ferro": batch.CONFIRMACAO_PERDIDA})
        self.assertEqual(codigo, 1)  # Tocha ficou retida.
        self.assertIn("== Ferro (T5): pronto", saida)
        self.assertIn("Distribuição do lote: " + DISTRIBUICAO, saida)
        ids = [linha.split("\t")[1] for linha in self.log.read_text(encoding="utf-8").splitlines()]
        self.assertCountEqual(ids, ["T2", "T3", "T4", "T5", "T6", "T7"])

    def test_enter_com_erro_e_relatorio_novo_preserva_sucesso(self):
        self.cotas_do_caso(idade_claude=2)

        def gravar_relatorios(exe, pendentes, inicio, minutos):
            self.assertNotIn("\tT5\t", self.log.read_text(encoding="utf-8"))
            for caminho, _ in pendentes.values():
                caminho.write_text("STATUS: pronto", encoding="utf-8")
            return set()

        with (patch.object(batch.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as enter,
              patch.object(batch, "esperar_terminar", side_effect=gravar_relatorios)):
            codigo, saida, _, _ = self.rodar_lote(saidas={"Ferro": f"T5\n{batch.FIM_RODAPE}"})
        enter.assert_called_once_with(["maestri", "ask", "Ferro", "--raw", "\\r"],
                                      capture_output=True, stdin=subprocess.DEVNULL)
        self.assertEqual(codigo, 0)
        self.assertIn("== Ferro (T5): pronto", saida)
        self.assertEqual(self.log.read_text(encoding="utf-8").count("\tT5\t"), 1)


if __name__ == "__main__":
    unittest.main()
