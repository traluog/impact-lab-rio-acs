"""
╔══════════════════════════════════════════════════════════════════════╗
║   CLAUDE IMPACT LAB RIO 2026 — ORQUESTRADOR                        ║
║   Desafio: Inteligência no Território (ACS)                         ║
╚══════════════════════════════════════════════════════════════════════╝

USO:
  python orchestrator.py
  python orchestrator.py --transcricao transcricao_briefing.txt
  python orchestrator.py --skip-dados    (se quiser pular o download)

FLUXO:
  1. Agente Briefing      → analisa transcrição + contexto pré-carregado do desafio
  2. Agente Data Engineer → baixa 4 Parquets do Drive, inspeciona, gera score + código
  3. Agente Research      → referências de CHW com IA + Impact Labs anteriores
  4. Agente Consolidador  → apresenta 3-4 opções de MVP ranqueadas
     ⏸️  PAUSA — time escolhe o MVP no terminal
  5. Agente Arquiteto     → gera TECHNICAL_SPEC.md completo para o MVP escolhido
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.agent_briefing import run as run_briefing
from agents.agent_data_engineer import run as run_data_engineer
from agents.agent_research import run as run_research
from agents.agent_consolidator import run as run_consolidator
from agents.agent_architect import run as run_architect

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def salvar_output(nome: str, conteudo: str | dict) -> str:
    timestamp = datetime.now().strftime("%H%M")
    filename = OUTPUT_DIR / f"{timestamp}_{nome}.md"
    if isinstance(conteudo, dict):
        conteudo = json.dumps(conteudo, ensure_ascii=False, indent=2)
    filename.write_text(conteudo, encoding="utf-8")
    print(f"  ✅ Salvo em: {filename}")
    return str(filename)


def separador(titulo: str):
    print(f"\n{'═' * 60}")
    print(f"  {titulo}")
    print(f"{'═' * 60}")


def _pausar_e_escolher_mvp(opcoes_output: str, opcoes_path: str) -> str:
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║   ⏸️   PAUSA — DECISÃO DO TIME                                       ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  O Agente 4 gerou as opções de MVP com análise detalhada.            ║
║                                                                      ║
║  👉 Abra o arquivo abaixo e leia todas as opções:                    ║
║     {str(opcoes_path):<64}║
║                                                                      ║
║  Discuta com o time considerando:                                    ║
║  • Habilidades técnicas do grupo                                     ║
║  • Feeling da banca no briefing                                      ║
║  • Quais dados ficaram mais ricos na análise                         ║
║  • Qual escopo é realmente entregável em 4 horas de código           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    opcoes = _extrair_nomes_opcoes(opcoes_output)

    if opcoes:
        print("  Opções identificadas:\n")
        for i, nome in enumerate(opcoes, 1):
            print(f"    [{i}] {nome}")
        print(f"    [0] Ideia própria ou combinação das opções\n")
    else:
        print("  Leia o arquivo acima e informe o número da opção (1, 2, 3...)\n")

    while True:
        try:
            entrada = input("  ✏️  Opção escolhida (ou 0 para descrever): ").strip()

            if entrada == "0":
                print("\n  📝 Descreva o MVP (ENTER duas vezes para finalizar):\n")
                linhas = []
                while True:
                    linha = input("     > ")
                    if linha == "" and linhas and linhas[-1] == "":
                        break
                    linhas.append(linha)
                texto = "\n".join(linhas).strip()
                print("\n  ✅ Registrado. Gerando especificação técnica...\n")
                return f"# MVP Escolhido pelo Time\n\n{texto}"

            numero = int(entrada)
            if opcoes and 1 <= numero <= len(opcoes):
                nome = opcoes[numero - 1]
                secao = _extrair_secao_opcao(opcoes_output, numero)
                print(f"\n  ✅ Opção {numero}: {nome}")
                print("     Gerando especificação técnica...\n")
                return secao
            elif not opcoes and numero >= 1:
                print(f"\n  ✅ Opção {numero} selecionada. Gerando especificação técnica...\n")
                return f"# MVP Escolhido — Opção {numero}\n\n{opcoes_output}"
            else:
                print(f"  ⚠️  Digite entre 1 e {len(opcoes)} (ou 0).")

        except ValueError:
            print("  ⚠️  Digite apenas um número.")
        except KeyboardInterrupt:
            print("\n\n  ⚠️  Usando Opção 1 como padrão.")
            return _extrair_secao_opcao(opcoes_output, 1) or opcoes_output


def _extrair_nomes_opcoes(texto: str) -> list[str]:
    padrao = re.compile(r"##\s+[🥇🥈🥉🎖️]*\s*OPÇ[AÃ]O\s+\d+\s+[—–-]\s+(.+)", re.IGNORECASE)
    nomes = padrao.findall(texto)
    return [re.sub(r"←.*$", "", n).strip() for n in nomes]


def _extrair_secao_opcao(texto: str, numero: int) -> str:
    padrao = re.compile(
        rf"(##\s+[🥇🥈🥉🎖️]*\s*OPÇ[AÃ]O\s+{numero}\b.+?)(?=##\s+[🥇🥈🥉🎖️]*\s*OPÇ[AÃ]O\s+\d|## 📊|$)",
        re.IGNORECASE | re.DOTALL
    )
    match = padrao.search(texto)
    return f"# MVP Escolhido — Opção {numero}\n\n{match.group(1).strip()}" if match else texto


def main():
    parser = argparse.ArgumentParser(
        description="Orquestrador — Claude Impact Lab Rio 2026 (Desafio ACS)"
    )
    parser.add_argument("--transcricao", type=str,
        help="Transcrição do briefing (.txt ou .vtt). Opcional — contexto pré-carregado.")
    parser.add_argument("--skip-dados", action="store_true",
        help="Pula o download dos Parquets (usa arquivos já existentes em data/parquet/)")
    args = parser.parse_args()

    print("\n🚀 CLAUDE IMPACT LAB RIO 2026 — Inteligência no Território")
    print(f"   {datetime.now().strftime('%H:%M:%S')}\n")

    contexto = {}

    # ── AGENTE 1: BRIEFING ────────────────────────────────────────────────────
    separador("AGENTE 1 / 5 — Análise do Briefing")

    transcricao = ""
    if args.transcricao and Path(args.transcricao).exists():
        transcricao = Path(args.transcricao).read_text(encoding="utf-8")
        print(f"  📄 Transcrição carregada: {len(transcricao):,} caracteres")
    else:
        print("  ℹ️  Sem transcrição — usando contexto pré-carregado do desafio ACS")

    contexto["briefing"] = run_briefing(transcricao, "saude")
    salvar_output("briefing", contexto["briefing"])

    # ── AGENTE 2: DATA ENGINEER ───────────────────────────────────────────────
    separador("AGENTE 2 / 5 — Engenharia de Dados (Download + Parquet)")

    if args.skip_dados:
        print("  ⏭️  Download pulado via --skip-dados")
        parquets = list(Path("data/parquet").glob("*.parquet"))
        if parquets:
            print(f"  📂 Usando {len(parquets)} arquivo(s) existente(s) em data/parquet/")
            contexto["dados"] = run_data_engineer(
                briefing_output=contexto["briefing"]
            )
            salvar_output("dados_parquet", contexto["dados"])
        else:
            print("  ⚠️  Nenhum Parquet encontrado. Rode sem --skip-dados.")
            contexto["dados"] = "**Dados não disponíveis.**"
    else:
        contexto["dados"] = run_data_engineer(
            briefing_output=contexto["briefing"]
        )
        salvar_output("dados_parquet", contexto["dados"])

    # ── AGENTE 3: RESEARCH ────────────────────────────────────────────────────
    separador("AGENTE 3 / 5 — Research (CHW com IA + Impact Labs)")

    contexto["research"] = run_research(contexto["briefing"], "saude")
    salvar_output("research", contexto["research"])

    # ── AGENTE 4: CONSOLIDADOR ────────────────────────────────────────────────
    separador("AGENTE 4 / 5 — Opções de MVP (Decisão é do Time)")

    contexto["consolidacao"] = run_consolidator(
        briefing=contexto["briefing"],
        schemas=contexto["dados"],
        research=contexto["research"],
        trilha="saude",
    )
    opcoes_path = salvar_output("opcoes_mvp", contexto["consolidacao"])

    # ── ⏸️  PAUSA ──────────────────────────────────────────────────────────────
    contexto["mvp_escolhido"] = _pausar_e_escolher_mvp(
        contexto["consolidacao"], opcoes_path
    )

    # ── AGENTE 5: ARQUITETO ───────────────────────────────────────────────────
    separador("AGENTE 5 / 5 — Especificação Técnica (SDD)")

    contexto["spec"] = run_architect(contexto["mvp_escolhido"], contexto["dados"])
    salvar_output("TECHNICAL_SPEC", contexto["spec"])

    # ── SUMÁRIO ───────────────────────────────────────────────────────────────
    separador("✅ PIPELINE CONCLUÍDO")
    print(f"\n  Outputs em: ./{OUTPUT_DIR}/")
    print(f"  → Abra TECHNICAL_SPEC.md no Cursor e comece a codar\n")
    print(f"  ⏰ Lembre: Code Freeze às 16:15. Boa sorte! 🤙\n")


if __name__ == "__main__":
    main()
