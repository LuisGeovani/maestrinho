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

    def test_veto_do_destino_precede_as_demais_travas(self):
        self.cotas_do_caso()
        dados = json.loads(self.status.read_text(encoding="utf-8"))
        codex = dados["providers"][1]
        semanal, cinco_horas = codex["meters"][0]["windows"]
        texto = (
            "### Prumo | VETO\nTamanho: G\n"
            "Motivo pool: ambiente obrigatório.\n"
            "Roteamento: Sol medium | descartado: Luna high porque exige contexto.\n"
        )
        for uso, permitido, motivo in (
            (96, True, "janela com uso ≥95%"),
            (95, True, "janela com uso ≥95%"),
            (0, False, "usageAllowed=false"),
        ):
            with self.subTest(uso=uso, permitido=permitido):
                semanal["usedPercent"] = uso
                cinco_horas["usedPercent"] = 0
                codex["usageAllowed"] = permitido
                self.status.write_text(json.dumps({"providers": [codex]}), encoding="utf-8")
                pools, _ = cotas.ler_cotas()
                aceitas, retidas, _ = self.avaliar(texto, pools)
                janela = semanal if permitido else cinco_horas
                reset = datetime.fromisoformat(janela["resetsAt"]).astimezone().isoformat(timespec="minutes")
                self.assertEqual(aceitas, {})
                self.assertEqual(retidas, [f"RETIDO (veto): Prumo | VETO: Codex ({motivo}) | reset {reset}"])

    def test_veto_do_claude_code_quando_o_provedor_omite_o_plano(self):
        self.cotas_do_caso()
        dados = json.loads(self.status.read_text(encoding="utf-8"))
        claude = dados["providers"][0]
        del claude["plan"]
        claude["usageAllowed"] = False
        self.status.write_text(json.dumps(dados), encoding="utf-8")
        pools, _ = cotas.ler_cotas()
        texto = "### Tocha | VETO\nTamanho: M\nMotivo pool: ambiente obrigatório.\n"

        aceitas, retidas, _ = self.avaliar(texto, pools)

        reset = datetime.fromisoformat(claude["meters"][0]["windows"][1]["resetsAt"])
        self.assertEqual(aceitas, {})
        self.assertEqual(retidas, [
            "RETIDO (veto): Tocha | VETO: Claude Code (plano não identificado) (usageAllowed=false) | "
            f"reset {reset.astimezone().isoformat(timespec='minutes')}"
        ])

    def test_tamanho_g_exige_indivisibilidade_e_preserva_a_trava_de_custo(self):
        pools = self.cotas_do_caso()
        secao = "### Prumo | GRANDE\nTamanho: G\n"
        rota = "Roteamento: Sol medium | descartado: Luna high porque a análise exige contexto.\n"
        for motivo in ("", "Indivisível: \t\n"):
            with self.subTest(motivo=motivo):
                aceitas, retidas, _ = self.avaliar(secao + motivo + rota, pools)
                self.assertEqual(aceitas, {})
                self.assertEqual(len(retidas), 1)
                self.assertIn("RETIDO (tamanho): Prumo | GRANDE", retidas[0])
        consulta = secao + "Indivisível: uma decisão depende de todo o histórico.\n"
        aceitas, retidas, _ = self.avaliar(consulta, pools)
        self.assertEqual(aceitas, {})
        self.assertEqual(len(retidas), 1)
        self.assertIn("RETIDO (custo): Prumo | GRANDE", retidas[0])
        aceitas, retidas, _ = self.avaliar(consulta + rota, pools)
        self.assertEqual(retidas, [])
        self.assertEqual(aceitas["Prumo"][4:6], (360, "G"))

    def test_rota_minimo_apto_basta_abaixo_do_limiar(self):
        texto = (
            "### Prumo | BARATO\nTamanho: M\n"
            "Roteamento: Hydrogen medium | custo 90 | mínimo apto\n"
        )
        aceitas, retidas, _ = self.avaliar(texto, self.cotas_do_caso())
        self.assertEqual(retidas, [])
        self.assertEqual(aceitas["Prumo"][4:6], (120, "M"))

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
        agy = next(p for p in pools if p["via_claude"] == "Antigravity")
        agy.update(uso_max=18, veto_despacho=None)
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
        self.assertTrue(all(len(linha) == 9 and cotas._data(linha[0]) for linha in linhas))
        self.assertIn(["T2", "Vela", "Claude", "Claude Pro", "Precisa deste pool.", "120", "M", ""],
                      [l[1:] for l in linhas])
        self.assertIn(["T3", "Prumo", "GPT", "Codex", "", "120", "M", "10"], [l[1:] for l in linhas])
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

        def gravar_relatorios(exe, pendentes, inicio, minutos, **_):
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

    def test_resumo_do_batch_preserva_veredito_do_relatorio_eco_real(self):
        original = Path(__file__).resolve().parents[3] / ".maestri" / "relatorios" / "ECO-T1-R.md"
        if not original.exists():
            self.skipTest("relatório local ECO-T1-R.md ausente")
        self.cotas_do_caso()
        self.despacho.write_text("### Prumo | ECO-T1-R\nTamanho: M\nConfira.\n", encoding="utf-8")

        def gravar_relatorio(exe, pendentes, inicio, minutos, **_):
            caminho, _ = pendentes["Prumo"]
            caminho.write_bytes(original.read_bytes())
            return set()

        with patch.object(batch, "esperar_terminar", side_effect=gravar_relatorio):
            codigo, saida, _, _ = self.rodar_lote()
        self.assertEqual(codigo, 0)
        self.assertIn("== Prumo (ECO-T1-R): pronto | veredito aprovado com ajustes (decisão pendente)", saida)

    def test_veredito_so_le_campo_inteiro_e_sinaliza_valor_desconhecido(self):
        self.assertEqual(batch.resumo_veredito("Texto com VEREDITO: aprovado"), "")
        self.assertEqual(
            batch.resumo_veredito("STATUS: pronto\r\nVEREDITO: aprovado com ajustes\r\n"),
            " | veredito aprovado com ajustes (decisão pendente)",
        )
        self.assertEqual(batch.resumo_veredito("**VEREDITO:** reprovado"), " | veredito reprovado")
        self.assertEqual(
            batch.resumo_veredito("VEREDITO: aprovado provisoriamente"),
            " | veredito desconhecido: aprovado provisoriamente",
        )

    def test_enter_com_erro_e_relatorio_novo_preserva_sucesso(self):
        self.cotas_do_caso(idade_claude=2)

        def gravar_relatorios(exe, pendentes, inicio, minutos, **_):
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

    def test_formacao_sem_preset_coluna_pool_e_modelo_effort(self):
        self.equipe.write_text(
            "| Terminal | Ferramenta | Modelo · effort | Perfis | Pool |\n"
            "|---|---|---|---|---|\n"
            "| Hydrogen | Antigravity | Gemini 4 Hydrogen · high | Batedor, Volume | Gemini Models |\n"
            "| Neon | Antigravity | Gemini 4 Neon · high | Crítico, Revisor | Gemini Models |\n"
            "| Argon | Antigravity | Gemini 4 Argon · high | Volume de cuidado | Gemini 4 Argon |\n"
            "| Sol | Codex | GPT-6.2 Sol · medium | Volume | Codex |\n"
            "| OpenCode | OpenCode | grátis · medium | Batedor | grátis |\n",
            encoding="utf-8",
        )
        pools = self.cotas_do_caso()
        texto = (
            "### Hydrogen | H1\nOk.\n"
            "### Neon | N1\nTamanho: P\nOk.\n"
            "### Argon | A1\nOk.\n"
            "### Sol | S1\nValide com: pytest\n"
            "### OpenCode | O1\nOk.\n"
        )
        aceitas, retidas, avisos = self.avaliar(texto, pools)
        self.assertEqual(retidas, [])
        self.assertNotIn("pool desconhecido", avisos)
        self.assertEqual({k: v[1:3] for k, v in aceitas.items()}, {
            "Hydrogen": ("Gemini", "Gemini Models"),
            "Neon": ("Gemini", "Gemini Models"),
            "Argon": ("Gemini", "Gemini 4 Argon"),
            "Sol": ("GPT", "Codex"),
            "OpenCode": ("aberto", "grátis"),
        })

    def test_fallback_rodape_tela_antigravity(self):
        self.equipe.unlink()
        pools = self.cotas_do_caso()
        self.preset.side_effect = [
            ("  Gemini 4 Hydrogen (High)  auto  shift+tab\n", ""),
            ("  Gemini 4 Argon (High)  auto  shift+tab\n", ""),
        ]
        texto = "### Hydrogen | H1\nOk.\n### Argon | A1\nOk.\n"
        aceitas, retidas, avisos = self.avaliar(texto, pools)
        self.assertEqual(retidas, [])
        self.assertNotIn("pool desconhecido", avisos)
        self.assertEqual(aceitas["Hydrogen"][1:3], ("Gemini", "Gemini Models"))
        self.assertEqual(aceitas["Argon"][1:3], ("Gemini", "Gemini 4 Argon"))

    def test_equilibrio_aplica_mesmo_limiar_a_gemini_e_argon(self):
        def pools_custom(gem_sem, gem_5h, codex_sem, claude_sem):
            def med(nome, sem, cinco=None):
                js = [{"durationSeconds": 604800, "usedPercent": sem,
                       "resetsAt": (self.agora + timedelta(days=3)).isoformat()}]
                if cinco is not None:
                    js.append({"durationSeconds": 18000, "usedPercent": cinco,
                               "resetsAt": (self.agora + timedelta(hours=3)).isoformat()})
                return {"label": nome, "windows": js}

            def prov(ident, nome, plano, meds):
                return {"id": ident, "name": nome, "plan": plano, "meters": meds,
                        "state": "ready", "lastSuccessAt": self.agora.isoformat()}

            self.status.write_text(json.dumps({"providers": [
                prov("claude", "Claude Code", "Pro", [med("Limites do plano", claude_sem, 10)]),
                prov("codex", "Codex", "Plus", [med("Codex", codex_sem, 10)]),
                prov("antigravity", "Antigravity", "", [
                    med("Gemini Models", gem_sem, gem_5h),
                    med("Gemini 4 Argon", gem_sem),
                ]),
            ]}), encoding="utf-8")
            return cotas.ler_cotas()[0]

        pools = pools_custom(gem_sem=40, gem_5h=20, codex_sem=20, claude_sem=30)
        aceitas, retidas, _ = self.avaliar("### Malho | G1\nOk.\n### Ferro | G2\nOk.\n", pools)
        self.assertEqual(aceitas, {})
        self.assertEqual(len(retidas), 2)
        self.assertIn("RETIDO (equilíbrio): Malho | G1: Gemini Models 40% vs Codex 20%", retidas[0])
        self.assertIn("RETIDO (equilíbrio): Ferro | G2: Gemini 4 Argon 40% vs Codex 20%", retidas[1])

        # A justificativa libera o Argon mesmo acima do limiar relativo.
        pools = pools_custom(gem_sem=85, gem_5h=20, codex_sem=40, claude_sem=40)
        aceitas, retidas, _ = self.avaliar("### Malho | G3\nOk.\n### Ferro | G4\nMotivo pool: necessário.\n", pools)
        self.assertEqual(len(retidas), 1)
        self.assertIn("RETIDO (equilíbrio): Malho | G3", retidas[0])
        self.assertIn("Ferro", aceitas)

        # A janela de 5 h determina o uso quando é a mais apertada.
        pools = pools_custom(gem_sem=50, gem_5h=90, codex_sem=40, claude_sem=40)
        aceitas, retidas, _ = self.avaliar("### Malho | G5\nOk.\n", pools)
        self.assertEqual(len(retidas), 1)
        self.assertIn("RETIDO (equilíbrio): Malho | G5", retidas[0])

        # 4) Claude 70% vs Gemini 40% -> Claude RETIDO como antes
        pools = pools_custom(gem_sem=40, gem_5h=10, codex_sem=50, claude_sem=70)
        aceitas, retidas, _ = self.avaliar("### Tocha | C1\nOk.\n", pools)
        self.assertEqual(len(retidas), 1)
        self.assertIn("RETIDO (equilíbrio): Tocha | C1: Claude Pro 70% vs Gemini Models 40%", retidas[0])

        pools = pools_custom(gem_sem=85, gem_5h=90, codex_sem=80, claude_sem=80)
        aceitas, retidas, _ = self.avaliar("### Malho | G6\nOk.\n### Ferro | G7\nOk.\n", pools)
        self.assertEqual(retidas, [])
        self.assertEqual(set(aceitas), {"Malho", "Ferro"})

    def test_cotas_ordenam_por_folga_sem_preferir_gemini(self):
        self.status.write_text(json.dumps({"providers": [
            {"id": "codex", "name": "Codex", "plan": "Plus", "state": "ready",
             "lastSuccessAt": self.agora.isoformat(),
             "meters": [{"label": "Codex", "windows": [
                 {"durationSeconds": 604800, "usedPercent": 20,
                  "resetsAt": (self.agora + timedelta(days=6)).isoformat()},
             ]}]},
            {"id": "antigravity", "name": "Antigravity", "plan": "", "state": "ready",
             "lastSuccessAt": self.agora.isoformat(),
             "meters": [
                 {"label": "Gemini Models", "windows": [
                     {"durationSeconds": 604800, "usedPercent": 60,
                      "resetsAt": (self.agora + timedelta(days=3)).isoformat()},
                     {"durationSeconds": 18000, "usedPercent": 50,
                      "resetsAt": (self.agora + timedelta(hours=4)).isoformat()},
                 ]},
                 {"label": "Gemini 4 Argon", "windows": [
                     {"durationSeconds": 604800, "usedPercent": 85,
                      "resetsAt": (self.agora + timedelta(days=6)).isoformat()},
                 ]},
             ]},
        ]}), encoding="utf-8")
        pools, _ = cotas.ler_cotas()
        gem = next(p for p in pools if p["medidor"] == "Gemini Models")
        argon = next(p for p in pools if p["medidor"] == "Gemini 4 Argon")
        self.assertEqual(gem["despacho"], "rotina")
        self.assertEqual(argon["despacho"], "só insubstituível")
        resumo = "\n".join(cotas.resumo_linhas(pools, []))
        gaste = next(l for l in resumo.splitlines() if l.startswith("Gaste primeiro:"))
        self.assertLess(gaste.index("Codex/Codex"), gaste.index("Antigravity/Gemini Models"))

    def test_ordem_claude_prioriza_antigravity_ate_o_veto(self):
        self.cotas_do_caso()
        dados = json.loads(self.status.read_text(encoding="utf-8"))
        medidor_agy = dados["providers"][2]["meters"][2]
        medidor_agy["windows"][0]["usedPercent"] = 70
        self.status.write_text(json.dumps(dados), encoding="utf-8")
        pools, _ = cotas.ler_cotas()
        self.assertEqual(cotas.ordem_claude(pools)["destino"], "Antigravity")
        medidor_agy["windows"][0]["usedPercent"] = 96
        self.status.write_text(json.dumps(dados), encoding="utf-8")
        pools, _ = cotas.ler_cotas()
        self.assertEqual(cotas.ordem_claude(pools)["destino"], "Claude Code")

    def test_trava_custo_limiar_e_justificativa(self):
        self.equipe.write_text(
            "| Terminal | Ferramenta | Modelo · effort | Perfis | Pool |\n"
            "|---|---|---|---|---|\n"
            "| Astra | Codex | GPT-6.2 Astra · high | N3 | Codex |\n"
            "| Hydrogen | Antigravity | Gemini 4 Hydrogen · high | Volume | Gemini Models |\n"
            "| Orch | Antigravity | gemini-pro-orchestrator-neon · medium | Multi | Gemini Models |\n"
            "| OpenCode | OpenCode | deepseek-v4.1-flash-free | Batedor | grátis |\n"
            "| Desconhecido | Antigravity | Modelo X · high | Outro | Gemini Models |\n",
            encoding="utf-8",
        )
        pools = self.cotas_do_caso()

        # 1) Astra high M sem descartado -> RETIDO (custo 960 >= 300)
        aceitas, retidas, avisos = self.avaliar("### Astra | A1\nTamanho: M\nValide com: pytest\n", pools)
        self.assertEqual(aceitas, {})
        self.assertEqual(len(retidas), 1)
        self.assertIn("RETIDO (custo): Astra | A1", retidas[0])
        self.assertIn("custo 960", retidas[0])
        self.assertIn("descartado:", retidas[0])

        # 2) Astra high M com Roteamento descartado ... porque ... -> passa
        aceitas, retidas, _ = self.avaliar(
            "### Astra | A2\n"
            "tamanho: m\n"
            "roteamento: Astra high | custo 960 | DESCARTADO: Sol medium PORQUE é tarefa N3.\n"
            "Valide com: pytest\n",
            pools,
        )
        self.assertEqual(retidas, [])
        self.assertEqual(aceitas["Astra"][4:7], (960, "M", 10))

        # 3) Descartado inválido (vazio, sem 'porque', ou cruzando '|') -> ainda RETIDO (custo)
        for rot in (
            "Roteamento: Astra high | descartado: porque sim",
            "Roteamento: Astra high | descartado: Sol medium",
            "Roteamento: Astra high | descartado: Sol medium porque | custo 960",
            "Roteamento: Astra high | descartado: | porque sim",
        ):
            with self.subTest(rot=rot):
                aceitas, retidas, _ = self.avaliar(f"### Astra | A3\nTamanho: M\n{rot}\n", pools)
                self.assertEqual(aceitas, {})
                self.assertEqual(len(retidas), 1)
                self.assertIn("RETIDO (custo)", retidas[0])

        # 3b) Justificativa válida com outro campo separado por '|' depois -> passa
        aceitas, retidas, _ = self.avaliar(
            "### Astra | A4\nTamanho: M\n"
            "Roteamento: Astra high | descartado: Sol medium porque é N3 | custo 960\n",
            pools,
        )
        self.assertEqual(retidas, [])
        self.assertIn("Astra", aceitas)

        # 4) Hydrogen high P -> passa sem justificativa (custo 60 < 300)
        aceitas, retidas, _ = self.avaliar("### Hydrogen | H1\nTamanho: P\nOk.\n", pools)
        self.assertEqual(retidas, [])
        self.assertEqual(aceitas["Hydrogen"][4:7], (60, "P", 18))

        # 5) Sem linha Tamanho -> assume M com aviso; OpenCode grátis -> custo 0; modelo desconhecido -> só aviso
        aceitas, retidas, avisos = self.avaliar(
            "### Hydrogen | H2\nOk.\n"
            "### OpenCode | O1\nTamanho: G\nIndivisível: auditoria conjunta.\n"
            "### Orch | OR1\nTamanho: M\nOk.\n"
            "### Desconhecido | D1\nTamanho: G\nIndivisível: auditoria conjunta.\n",
            pools,
        )
        self.assertEqual(retidas, [])
        self.assertIn("Hydrogen | H2: sem 'Tamanho: P|M|G' (usando M)", avisos)
        self.assertIn("Desconhecido | D1: modelo não identificado", avisos)
        self.assertEqual(aceitas["Hydrogen"][4:6], (180, "M"))
        self.assertEqual(aceitas["OpenCode"][4:6], (0, "G"))
        self.assertEqual(aceitas["Orch"][4:6], (180, "M"))
        self.assertIsNone(aceitas["Desconhecido"][4])

        # 6) --mostrar exibe custo por seção e RETIDO (custo)
        self.despacho.write_text(
            "### Astra | A1\nTamanho: M\nValide com: pytest\n"
            "### Hydrogen | H1\nTamanho: P\nOk.\n",
            encoding="utf-8",
        )
        codigo, saida, _, enviar = self.rodar_lote("--mostrar")
        self.assertEqual(codigo, 0)
        self.assertIn("RETIDO (custo): Astra | A1", saida)
        self.assertIn("===== Hydrogen", saida)
        self.assertIn("custo 60", saida)
        self.assertIn("Custo por seção: Astra (A1) custo 960 (M) · Hydrogen (H1) custo 60 (P)", saida)
        enviar.assert_not_called()

    def test_cotas_custo_por_despacho_ignora_antigas_e_calcula_delta_no_pool(self):
        agora = datetime.now(timezone.utc)
        linhas = [
            # Entradas antigas (6 colunas) -> ignoradas sem erro em custo_por_despacho
            f"{(agora - timedelta(hours=4)).isoformat()}\tOLD1\tMalho\tGemini\tGemini Models\t\n",
            f"{(agora - timedelta(hours=3)).isoformat()}\tOLD2\tMalho\tGemini\tGemini Models\t\n",
            # Mais antiga que 7 dias -> ignorada
            f"{(agora - timedelta(days=8)).isoformat()}\tD0\tMalho\tGemini\tGemini Models\t\t180\tM\t5\n",
            # Últimos 7 dias (Malho e Neon compartilham Gemini Models; Prumo tem só 1 despacho)
            f"{(agora - timedelta(days=2)).isoformat()}\tD1\tMalho\tGemini\tGemini Models\t\t180\tM\t10\n",
            f"{(agora - timedelta(days=2) + timedelta(minutes=20)).isoformat()}\tD2\tNeon\tGemini\tGemini Models\t\t360\tM\t13\n",
            f"{(agora - timedelta(days=1)).isoformat()}\tD3\tMalho\tGemini\tGemini Models\t\t60\tP\t19\n",
            # Reset de janela (19 -> 2) ignorado no delta, mas D4 conta na contagem/custo de Malho
            f"{(agora - timedelta(hours=6)).isoformat()}\tD4\tMalho\tGemini\tGemini Models\t\t120\tM\t2\n",
            f"{(agora - timedelta(hours=3)).isoformat()}\tD5\tNeon\tGemini\tGemini Models\t\t180\tM\t6\n",
            f"{(agora - timedelta(hours=2)).isoformat()}\tD6\tPrumo\tGPT\tCodex\t\t120\tM\t10\n",
        ]
        self.log.write_text("".join(linhas), encoding="utf-8")
        # Malho: D1->D2 delta 3, D3->D4 reset ignorado (só conta delta 3), D4->D5 delta 4 => média (3+4)/2 = 3.5 pp; custos [180, 60, 120] => média 120
        # Neon: D2->D3 delta 6 (D5 não tem seguinte no pool) => média 6.0 pp; custos [360, 180] => média 270
        # Prumo: apenas 1 despacho -> não aparece
        linha = cotas.custo_por_despacho(self.pasta, agora=agora)
        self.assertEqual(
            linha,
            "Custo por despacho (aprox.): Malho 3.5 pp (custo médio 120) · Neon 6.0 pp (custo médio 270)",
        )
        # distribuicao_recente lê tanto antigas (6 col) quanto novas (9 col) nas últimas 5h: OLD1, OLD2, D5 (Gemini) e D6 (GPT)
        dist = cotas.distribuicao_recente(self.pasta, agora=agora)
        self.assertEqual(dist, "Despachos nas últimas 5 h por família: Claude 0 · GPT 1 · Gemini 3 · aberto 0 · desconhecido 0")

    def test_fallback_parcial_rodape_e_ignora_conversa(self):
        self.equipe.write_text(
            "| Terminal | Ferramenta | Modelo | Effort | Pool |\n"
            "|---|---|---|---|---|\n"
            "| AstraSemEffort | Codex | GPT-6.2 Astra | | Codex |\n"
            "| SoEffort | Codex | | high | Codex |\n"
            "| SemNada | Antigravity | | | Gemini Models |\n",
            encoding="utf-8",
        )
        pools = self.cotas_do_caso()
        self.preset.side_effect = [
            ("› pronto\n  gpt-6.2-astra high · 95% left · C:\\proj\n", ""),
            ("› pronto\n  gpt-6.2-astra medium · 90% left · C:\\proj\n", ""),
            ("Sugestao: use GPT-6.2 Astra high\n", ""),
        ]
        # 1) Modelo sem effort -> completa pelo rodapé (astra high M = 960 -> retido)
        aceitas, retidas, _ = self.avaliar("### AstraSemEffort | E1\nTamanho: M\n", pools)
        self.assertEqual(aceitas, {})
        self.assertIn("RETIDO (custo): AstraSemEffort | E1", retidas[0])

        # 2) Effort sem modelo -> completa modelo do rodapé mantendo effort da formação (astra high M = 960)
        aceitas, retidas, _ = self.avaliar("### SoEffort | E2\nTamanho: M\n", pools)
        self.assertEqual(aceitas, {})
        self.assertIn("RETIDO (custo): SoEffort | E2", retidas[0])

        # 3) Texto da conversa com modelo sem rodapé reconhecível -> só aviso, não retém
        aceitas, retidas, avisos = self.avaliar("### SemNada | E3\nTamanho: M\n", pools)
        self.assertEqual(retidas, [])
        self.assertIn("SemNada | E3: modelo não identificado", avisos)
        self.assertIsNone(aceitas["SemNada"][4])

    def test_rodapes_estritos_completam_formacao(self):
        pools = self.cotas_do_caso()
        casos = (
            ("Codex", "GPT-6.2 Astra", "GPT-6.2 Astra · high", 960),
            ("Codex", "-", "gpt-6.2-astra high · 95% left", 960),
            ("Codex", "GPT-6.2 Astra", r"gpt-6.2-astra high · C:\proj", 960),
            ("Antigravity", "Gemini 4 Neon", "Gemini 4 Neon · high", 360),
            ("Antigravity", "-", "auto · Gemini 4 Neon · high", 360),
            ("Claude Code", "Claude Sonnet 5.5", "Claude Sonnet 5.5 · high", 240),
        )
        for ferramenta, modelo, rodape, custo in casos:
            with self.subTest(rodape=rodape):
                self.equipe.write_text(
                    "| Terminal | Ferramenta | Modelo |\n"
                    "|---|---|---|\n"
                    f"| A | {ferramenta} | {modelo} |\n",
                    encoding="utf-8",
                )
                self.preset.return_value = (f"Pronto.\n  {rodape}\n", "")
                aceitas, retidas, _ = self.avaliar(
                    "### A | V1\nTamanho: M\nMotivo pool: teste do custo.\n", pools
                )
                if custo >= batch.LIMIAR_CUSTO:
                    self.assertEqual(aceitas, {})
                    self.assertEqual(len(retidas), 1)
                    self.assertIn(f"RETIDO (custo): A | V1:", retidas[0])
                    self.assertIn(f"custo {custo}", retidas[0])
                else:
                    self.assertEqual(retidas, [])
                    self.assertEqual(aceitas["A"][4], custo)

    def test_rodapes_capturados_e_variacoes_de_status(self):
        pools = self.cotas_do_caso()
        casos = (
            ("? for shortcuts                                                                   auto · Gemini 4 Neon · high", 120),
            ("esc to cancel                                                                 auto · Gemini 4 Hydrogen · high", 60),
            (
                r"  GPT-6-Luna high · ~\Documents\Desenvolvimento Web\maestrinho\.maestri\roles\3d646786-047a-49c4-b2b6-"
                "\n  32a4d1450c0f",
                4,
            ),
            (
                r"  GPT-6.2-Sol medium · ~\Documents\Desenvolvimento Web\maestrinho\.maestri\roles\8b1120c0-f14f-4479-a645-"
                "\n  e8edfc99891c · Revise a implementação ECO-T3",
                40,
            ),
            ("  ┃  Build · DeepSeek V4.1 Flash Free OpenCode", 0),
            (r"gpt-6.2-sol medium · C:\proj · 98% left", 40),
            (r"gpt-6.2-sol medium · 98% context left · C:\proj", 40),
            ("Gemini 4 Neon (High)  auto mode  shift+tab", 120),
        )
        for rodape, custo in casos:
            with self.subTest(rodape=rodape):
                self.preset.return_value = (rodape, "")
                aceitas, retidas, _ = self.avaliar("### A | C1\nTamanho: P\n", pools)
                self.assertEqual(retidas, [])
                self.assertEqual(aceitas["A"][4], custo)

    def test_rodape_claude_sem_modelo_depende_da_formacao(self):
        pools = self.cotas_do_caso()
        self.preset.return_value = ("⏵⏵ auto mode on (shift+tab to cycle)", "")
        for modelo, custo in (("-", None), ("Claude Sonnet 5.5 · medium", 40)):
            with self.subTest(modelo=modelo):
                self.equipe.write_text(
                    "| Terminal | Ferramenta | Modelo · effort |\n"
                    "|---|---|---|\n"
                    f"| A | Claude Code | {modelo} |\n",
                    encoding="utf-8",
                )
                aceitas, retidas, avisos = self.avaliar(
                    "### A | C1\nTamanho: P\nMotivo pool: teste do custo.\n", pools
                )
                self.assertEqual(retidas, [])
                self.assertEqual(aceitas["A"][4], custo)
                if custo is None:
                    self.assertIn("modelo não identificado", avisos)

    def test_rodape_de_outro_modelo_nao_completa_effort(self):
        self.equipe.write_text(
            "| Terminal | Ferramenta | Modelo |\n"
            "|---|---|---|\n"
            "| A | Codex | GPT-6.2 Astra |\n",
            encoding="utf-8",
        )
        pools = self.cotas_do_caso()
        for rodape in ("gpt-6.2-sol high · 95% left", "GPT-6.1 Astra · high"):
            with self.subTest(rodape=rodape):
                self.preset.return_value = (f"{rodape}\n", "")
                aceitas, retidas, avisos = self.avaliar("### A | V1\nTamanho: M\n", pools)
                self.assertEqual(retidas, [])
                self.assertIsNone(aceitas["A"][4])
                self.assertIn("effort não identificado para astra", avisos)

    def test_marcadores_de_status_na_conversa_nao_identificam_modelo(self):
        pools = self.cotas_do_caso()
        telas = (
            "Sugestao: use GPT-6.2 Astra high\nmodelo indisponivel\n",
            "Relato: GPT-6.2 Astra high\nsol medium\n",
            "Sugestao: use GPT-6.2 Astra high e shift+tab\nmodelo indisponivel\n",
            "Exemplo: auto · Gemini 4 Neon · high\nshift+tab\n",
            "Explique ? for shortcuts                      auto · Gemini 4 Neon · high\n",
            "Exemplo: GPT-6-Luna high · ~/projeto · título\n",
        )
        for tela in telas:
            with self.subTest(tela=tela):
                self.preset.return_value = (tela, "")
                aceitas, retidas, avisos = self.avaliar("### A | V1\nTamanho: M\n", pools)
                self.assertEqual(retidas, [])
                self.assertEqual(aceitas["A"][1:3], ("desconhecido", "desconhecido"))
                self.assertIsNone(aceitas["A"][4])
                self.assertIn("modelo não identificado", avisos)

    def test_resumo_real_mostra_custo_de_todas_secoes_e_aviso_tamanho_p(self):
        self.cotas_do_caso()
        # Inclui Tocha (retida por equilíbrio) e Ferro (falha no envio) e 4 caminhos em Tamanho: P
        self.despacho.write_text(
            "### Tocha | T1\nTamanho: M\nFaça o teste.\n"
            "### Malho | T4\nTamanho: P\n"
            "Veja https://exemplo.com/a/b/c.html e P/M/G.\n"
            "Altere skills/maestro-equipe/scripts/maestri_batch.py, "
            "skills/maestro-equipe/scripts/cotas.py, "
            ".maestri/equipe.md e tests/test_equilibrio.py.\n"
            "### Ferro | T5\nTamanho: G\n"
            "Indivisível: auditoria conjunta.\n"
            "Roteamento: Argon high | descartado: Hydrogen high porque precisa de cuidado.\n"
            "Faça o teste.\n",
            encoding="utf-8",
        )
        codigo, saida, _, _ = self.rodar_lote("--sem-rodape", falhas={"Ferro": "rejeitado"})
        self.assertEqual(codigo, 1)
        self.assertIn("Malho | T4: Tamanho: P com 4 caminhos distintos no corpo", saida)
        self.assertIn("Custo por seção: Tocha (T1) custo 120 (M) · Malho (T4) custo 60 (P) · Ferro (T5) custo 540 (G)", saida)

    def test_cotas_lote_compartilhado_indeterminado_e_rotulos_contas(self):
        agora = datetime.now(timezone.utc)
        linhas = []
        for idx, uso in enumerate((10, 14, 18), start=1):
            ts = (agora - timedelta(hours=4 - idx)).isoformat()
            linhas.append(f"{ts}\tA{idx}\tA\tGemini\tGemini Models\t\t120\tM\t{uso}\n")
            linhas.append(f"{ts}\tB{idx}\tB\tGemini\tGemini Models\t\t120\tM\t{uso}\n")
        self.log.write_text("".join(linhas), encoding="utf-8")
        linha = cotas.custo_por_despacho(self.pasta, agora=agora)
        self.assertEqual(
            linha,
            "Custo por despacho (aprox.): A indeterminado (custo médio 120) · B indeterminado (custo médio 120)",
        )

        # Rótulos claros de contas Codex e Antigravity Claude/GPT
        self.status.write_text(json.dumps({"providers": [
            {
                "id": "codex", "name": "Codex", "plan": "plus", "state": "ready",
                "lastSuccessAt": agora.isoformat(),
                "meters": [{"id": "codex", "label": "Codex", "windows": [
                    {"durationSeconds": 18000, "usedPercent": 0, "resetsAt": (agora + timedelta(hours=4)).isoformat()},
                    {"durationSeconds": 604800, "usedPercent": 85, "resetsAt": (agora + timedelta(days=1)).isoformat()},
                ]}],
                "notes": ['meters/1: duplicate meter id "codex" skipped'],
            },
            {
                "id": "account-lm", "name": "lm", "plan": "team", "state": "ready",
                "lastSuccessAt": agora.isoformat(),
                "meters": [{"id": "codex", "label": "Codex", "windows": [
                    {"durationSeconds": 18000, "usedPercent": 1, "resetsAt": (agora + timedelta(hours=4)).isoformat()},
                    {"durationSeconds": 604800, "usedPercent": 0, "resetsAt": (agora + timedelta(days=6)).isoformat()},
                ]}],
                "notes": ['meters/1: duplicate meter id "codex" skipped'],
            },
            {
                "id": "antigravity", "name": "Antigravity", "plan": "", "state": "ready",
                "lastSuccessAt": agora.isoformat(),
                "meters": [
                    {"id": "Gemini Models", "label": "Gemini Models", "windows": [
                        {"durationSeconds": 604800, "usedPercent": 4, "resetsAt": (agora + timedelta(days=6)).isoformat()},
                    ]},
                    {"id": "Claude and GPT models", "label": "Claude and GPT models", "windows": [
                        {"durationSeconds": 604800, "usedPercent": 100, "resetsAt": (agora + timedelta(days=3)).isoformat()},
                    ]},
                ],
            },
        ]}), encoding="utf-8")
        pools, avisos = cotas.ler_cotas()
        resumo = "\n".join(cotas.resumo_linhas(pools, avisos))
        self.assertIn("Codex conta Padrão [plus] / Codex: 5h 0%", resumo)
        self.assertIn("semanal 85%", resumo)
        self.assertIn("Codex conta lm [team] / Codex: 5h 1%", resumo)
        self.assertIn("Antigravity / Claude and GPT models (cota Claude/GPT do plano Gemini, não o Claude Pro)", resumo)

        # Rollout de plano diferente (team) não sobrescreve conta Padrão (plus) antiga
        dados = json.loads(self.status.read_text(encoding="utf-8"))
        dados["providers"][0]["lastSuccessAt"] = (agora - timedelta(hours=2)).isoformat()
        self.status.write_text(json.dumps(dados), encoding="utf-8")
        codex_home = self.raiz / "codex_home"
        sess = codex_home / "sessions"
        sess.mkdir(parents=True)
        (sess / "rollout-1.jsonl").write_text(json.dumps({
            "type": "event_msg",
            "timestamp": agora.isoformat(),
            "payload": {
                "type": "token_count",
                "rate_limits": {
                    "limit_id": "codex",
                    "plan_type": "team",
                    "primary": {"window_minutes": 300, "used_percent": 1, "resets_at": int((agora + timedelta(hours=4)).timestamp())},
                    "secondary": {"window_minutes": 10080, "used_percent": 0, "resets_at": int((agora + timedelta(days=6)).timestamp())},
                },
            },
        }) + "\n", encoding="utf-8")
        with patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}):
            pools2, avisos2 = cotas.ler_cotas()
        resumo2 = "\n".join(cotas.resumo_linhas(pools2, avisos2))
        self.assertIn("Codex conta Padrão [plus] / Codex: 5h 0%", resumo2)
        self.assertIn("semanal 85%", resumo2)
        self.assertNotIn("suprida pelo rollout local", resumo2)

    def test_duas_contas_codex_pools_separados_equilibrio_e_custo(self):
        agora = self.agora
        self.status.write_text(json.dumps({"providers": [
            {
                "id": "codex", "name": "Codex", "plan": "plus", "state": "ready",
                "lastSuccessAt": agora.isoformat(),
                "meters": [{"id": "codex", "label": "Codex", "windows": [
                    {"durationSeconds": 18000, "usedPercent": 0, "resetsAt": (agora + timedelta(hours=4)).isoformat()},
                    {"durationSeconds": 604800, "usedPercent": 85, "resetsAt": (agora + timedelta(days=1)).isoformat()},
                ]}],
            },
            {
                "id": "account-lm", "name": "lm", "plan": "team", "state": "ready",
                "lastSuccessAt": agora.isoformat(),
                "meters": [{"id": "codex", "label": "Codex", "windows": [
                    {"durationSeconds": 18000, "usedPercent": 0, "resetsAt": (agora + timedelta(hours=4)).isoformat()},
                    {"durationSeconds": 604800, "usedPercent": 0, "resetsAt": (agora + timedelta(days=6)).isoformat()},
                ]}],
            },
            {
                "id": "antigravity", "name": "Antigravity", "plan": "", "state": "ready",
                "lastSuccessAt": agora.isoformat(),
                "meters": [{"id": "Gemini Models", "label": "Gemini Models", "windows": [
                    {"durationSeconds": 604800, "usedPercent": 18, "resetsAt": (agora + timedelta(days=6)).isoformat()},
                ]}],
            },
        ]}), encoding="utf-8")
        pools, _ = cotas.ler_cotas()

        # 1) Pela formação .maestri/equipe.md ("Codex (conta lm)" vs Padrão)
        self.equipe.write_text(
            "| Terminal | Ferramenta | Modelo · effort | Perfis |\n"
            "|---|---|---|---|\n"
            "| SolPadrao | Codex | GPT-6.2 Sol · medium | Volume |\n"
            "| SolLM | Codex (conta lm) | GPT-6.2 Sol · medium | Volume |\n"
            "| AstraLM | Codex (conta lm) | GPT-6.2 Astra · high | N3 |\n",
            encoding="utf-8",
        )
        aceitas, retidas, _ = self.avaliar(
            "### SolPadrao | P1\nTamanho: M\nValide com: pytest\n"
            "### SolLM | L1\nTamanho: M\nValide com: pytest\n"
            "### AstraLM | A1\nTamanho: M\nValide com: pytest\n",
            pools,
        )
        # SolPadrao (85% vs lm 0%) -> RETIDO (equilíbrio); SolLM (0%) -> passa; AstraLM (0%, custo 960) -> RETIDO (custo)
        self.assertNotIn("SolPadrao", aceitas)
        self.assertIn("SolLM", aceitas)
        self.assertEqual(aceitas["SolLM"][2], "Codex (conta lm)")
        self.assertEqual(aceitas["SolLM"][6], 0)
        self.assertNotIn("AstraLM", aceitas)
        self.assertTrue(any("RETIDO (equilíbrio): SolPadrao | P1: Codex 85%" in r for r in retidas))
        self.assertTrue(any("RETIDO (custo): AstraLM | A1" in r for r in retidas))

        # 2) Pelo campo account do maestri list (mesmo sem conta anotada na formação)
        self.equipe.write_text(
            "| Terminal | Ferramenta | Modelo · effort | Perfis |\n"
            "|---|---|---|---|\n"
            "| SolPadrao | Codex | GPT-6.2 Sol · medium | Volume |\n"
            "| SolLM | Codex | GPT-6.2 Sol · medium | Volume |\n",
            encoding="utf-8",
        )
        self.despacho.write_text(
            "### SolPadrao | P2\nTamanho: M\nValide com: pytest\n"
            "### SolLM | L2\nTamanho: M\nValide com: pytest\n",
            encoding="utf-8",
        )
        listagem = (
            "You:\n"
            '  - name: "Maestro", role: "Maestro"\n'
            "Connected agents:\n"
            '  - name: "SolPadrao", cli: "codex", account: "Padrão"\n'
            '  - name: "SolLM", cli: "codex", account: "lm"\n'
        )
        argv = ["maestri_batch.py", str(self.despacho), "--raiz", str(self.raiz), "--sem-rodape"]
        saida = Saida()
        with (patch.object(sys, "argv", argv), redirect_stdout(saida),
              patch.object(batch, "maestri_exe", return_value="maestri"),
              patch.object(batch, "ler_list", return_value=("Maestro", {"SolPadrao", "SolLM"}, listagem)),
              patch.object(batch, "tela", return_value=""),
              patch.object(batch, "esperar_pronto", return_value=None),
              patch.object(batch, "enviar_tudo", side_effect=lambda exe, prompts, *a, **kw: {
                  ag: ("entregue", None) for ag in prompts
              }) as enviar):
            codigo = batch.main()
        self.assertEqual(codigo, 1)  # SolPadrao foi retido
        self.assertEqual(list(enviar.call_args.args[1]), ["SolLM"])
        self.assertIn("RETIDO (equilíbrio): SolPadrao | P2: Codex 85%", saida.getvalue())
        linhas_log = [l.split("\t") for l in self.log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(linhas_log), 1)
        self.assertEqual(linhas_log[0][2:9], ["SolLM", "GPT", "Codex (conta lm)", "", "120", "M", "0"])

    def test_mostrar_com_maestro_usa_a_mesma_conta_codex(self):
        self.equipe.write_text(
            "| Terminal | Ferramenta | Modelo · effort |\n"
            "|---|---|---|\n"
            "| SolLM | Codex | GPT-6.2 Sol · medium |\n",
            encoding="utf-8",
        )
        self.despacho.write_text(
            "### SolLM | T1\nTamanho: M\nValide com: pytest\n",
            encoding="utf-8",
        )
        padrao = next(p for p in self.cotas_do_caso() if p["provedor"] == "Codex")
        pools = [dict(padrao, uso_max=85), dict(padrao, provedor="lm", conta="lm", uso_max=0)]
        listagem = 'Connected agents:\n  - name: "SolLM", cli: "codex", account: "lm"\n'
        argv = ["maestri_batch.py", str(self.despacho), "--raiz", str(self.raiz), "--mostrar", "--sem-rodape"]
        previas = []
        with (patch.object(batch, "maestri_exe", return_value="maestri"),
              patch.object(batch, "ler_cotas", return_value=(pools, [])),
              patch.object(batch, "ler_list", return_value=("Maestro", {"SolLM"}, listagem)),
              patch.object(batch, "enviar_tudo") as enviar):
            for flags in ([], ["--maestro", "Maestro"]):
                saida = Saida()
                with patch.object(sys, "argv", argv + flags), redirect_stdout(saida):
                    self.assertEqual(batch.main(), 0)
                previas.append(saida.getvalue())
            enviar.assert_not_called()
        self.assertEqual(previas[0], previas[1])
        self.assertIn("===== SolLM", previas[1])
        self.assertIn("custo 120 (M)", previas[1])
        self.assertNotIn("RETIDO (equilíbrio)", previas[1])
        self.assertFalse(self.log.exists())

        formacao = self.equipe.read_text(encoding="utf-8")
        self.equipe.write_text(formacao.replace("| Codex |", "| Codex (conta lm) |"), encoding="utf-8")
        saida = Saida()
        falha_list = subprocess.CompletedProcess(["maestri", "list"], 1, b"", b"indisponivel")
        with (patch.object(sys, "argv", argv + ["--maestro", "Maestro"]),
              patch.object(batch, "maestri_exe", return_value="maestri"),
              patch.object(batch, "ler_cotas", return_value=(pools, [])),
              patch.object(batch.subprocess, "run", return_value=falha_list),
              redirect_stdout(saida)):
            self.assertEqual(batch.main(), 0)
        self.assertIn("usando as contas da formação", saida.getvalue())
        self.assertIn("===== SolLM", saida.getvalue())
        self.assertNotIn("RETIDO (equilíbrio)", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
