"""
AGENTE 2 — ENGENHARIA DE DADOS (Download + Parquet)
═════════════════════════════════════════════════════
Desafio: Inteligência no Território — ACS do Rio de Janeiro

Responsabilidade: Baixa os 4 arquivos Parquet do Google Drive, inspeciona
schemas e amostras, calcula estatísticas relevantes para o scoring de risco,
e gera código pandas pronto para o MVP.

Arquivos:
  - pacientes.parquet    → cadastro clínico e demográfico (98.000 registros)
  - eventos_clinicos.parquet → consultas e urgências (72k agendamentos + 46k UE)
  - visitas.parquet      → histórico de visitas dos ACS (160.334 registros)
  - equipes.parquet      → localização das unidades de saúde (ponto de partida)
"""

import os
import time
from pathlib import Path

import pandas as pd

from agents import chamar_claude

# ─── Links de download (Google Drive) ────────────────────────────────────────
ARQUIVOS = {
    "pacientes.parquet": "https://drive.google.com/uc?export=download&id=1cRvsx5poNTi4EOfWHYvilSDF4_i6hcZy",
    "eventos_clinicos.parquet": "https://drive.google.com/uc?export=download&id=1rcWQbi_vA_RAnXLQV79oe4Z2mql8cn3_",
    "visitas.parquet": "https://drive.google.com/uc?export=download&id=1dKJ8BpqrmsFNQoVcs9tjJ-Gaag1WzCML",
    "equipes.parquet": "https://drive.google.com/uc?export=download&id=1h8DijXrZM_hnhYMAdkggp5mnb2zckFOW",
}

DATA_DIR = Path("data/parquet")

# ─── SYSTEM PROMPT ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Você é um Engenheiro e Analista de Dados Sênior especializado em dados de saúde
pública e sistemas de atenção primária municipais brasileiros.

Você está trabalhando no desafio "Inteligência no Território" do Claude Impact Lab
Rio 2026. O objetivo é construir um sistema que gere uma lista priorizada de visitas
domiciliares para os Agentes Comunitários de Saúde (ACS) toda manhã.

Com base nos schemas e estatísticas dos dados, você deve:

1. Confirmar o que cada dataset representa e sua qualidade
2. Identificar as colunas essenciais para o score de risco
3. Mapear como os 4 datasets se conectam entre si
4. Propor a fórmula exata do score de risco com pesos justificados
5. Gerar o código pandas completo para calcular o score e gerar a lista
6. Gerar o código pandas para as visualizações de gestão (bônus)
7. Alertar sobre limitações dos dados anonimizados relevantes para o MVP

CONTEXTO DOS DADOS (já conhecido):
- Dados anonimizados com SHA256 (IDs são hashes), date shifting e ~100m de ruído geográfico
- 2.000 pacientes por equipe na amostra
- Dinâmicas e padrões preservados; valores absolutos e datas exatas NÃO representam realidade
- Grupos prioritários (protocolos municipais): gestantes, hipertensos, diabéticos, crianças 0-6

GRUPOS PRIORITÁRIOS POR PROTOCOLO MUNICIPAL:
- Gestantes: visita semanal ou quinzenal
- Recém-nascidos (faixa 0-6 meses): 7-8 visitas recomendadas
- Hipertensos + diabéticos: acompanhamento mensal
- Pacientes com urgência recente: contato em até 48h
- Pacientes em vulnerabilidade social: prioridade elevada

FORMATO DE SAÍDA — responda SEMPRE neste markdown:

# 🗄️ Análise de Dados — Inteligência no Território (ACS Rio)

## 1. Visão Geral dos Datasets

| Dataset | Linhas | Colunas-chave | Qualidade | Observação |
|---------|--------|---------------|-----------|------------|

## 2. Schema Detalhado por Dataset

### `pacientes.parquet`
[colunas, tipos, % nulos, distribuições relevantes]

### `eventos_clinicos.parquet`
[tipos de eventos encontrados, distribuição temporal, contagem por tipo]

### `visitas.parquet`
[range de datas, média de visitas por paciente, gaps identificados]

### `equipes.parquet`
[quantidade de equipes, distribuição geográfica]

## 3. Joins entre Datasets

| De | Para | Campo | Cobertura |
|----|------|-------|-----------|

## 4. Fórmula do Score de Risco

### Dimensões e Pesos Propostos
```
score = (
    peso_clinico    * score_clinico    +   # hipertenso, diabético, gestante
    peso_urgencia   * score_urgencia   +   # eventos UE nos últimos N dias
    peso_lacuna     * score_lacuna     +   # dias desde última visita
    peso_vulnerab   * score_vulnerab   +   # situacao_vulnerabilidade
    peso_faixa      * score_faixa          # faixa etária prioritária (0-6, gestantes)
)
```
[justificativa de cada peso com base nos protocolos municipais]

## 5. Código pandas — Score de Risco Completo

```python
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, timedelta

# ── Carregamento ──────────────────────────────────────────────────
pacientes = pd.read_parquet(Path("data/parquet/pacientes.parquet"))
eventos   = pd.read_parquet(Path("data/parquet/eventos_clinicos.parquet"))
visitas   = pd.read_parquet(Path("data/parquet/visitas.parquet"))
equipes   = pd.read_parquet(Path("data/parquet/equipes.parquet"))

# ── Score de risco (código completo) ─────────────────────────────
[código completo pronto para usar]

# ── Output: lista priorizada para uma equipe ─────────────────────
[código de geração da lista final com justificativa por paciente]
```

## 6. Código pandas — Visualizações para Gestão (Bônus)

```python
# ── Cobertura por equipe ──────────────────────────────────────────
[código]

# ── Pacientes de alto risco sem visita há N dias ──────────────────
[código]

# ── Lacunas por grupo prioritário ────────────────────────────────
[código]
```

## 7. Alertas e Limitações
- ⚠️ [limitação 1 — impacto no MVP]
- ⚠️ [limitação 2]
""".strip()


# ─── Funções auxiliares ───────────────────────────────────────────────────────

def _baixar_arquivo(nome: str, url: str, destino: Path) -> bool:
    """Baixa um arquivo do Google Drive. Retorna True se bem-sucedido."""
    caminho = destino / nome
    if caminho.exists():
        print(f"     → {nome} já existe, pulando download")
        return True

    try:
        import urllib.request
        import urllib.error

        print(f"     → Baixando {nome}...")

        # Google Drive às vezes redireciona para página de confirmação de vírus
        # Usamos o endpoint de export direto para evitar isso
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as response:
            caminho.write_bytes(response.read())

        tamanho_mb = caminho.stat().st_size / 1_048_576
        print(f"        ✅ {nome} — {tamanho_mb:.1f} MB")
        return True

    except Exception as e:
        print(f"        ❌ Erro ao baixar {nome}: {e}")
        # Tenta via gdown se disponível
        try:
            import gdown
            file_id = url.split("id=")[-1]
            gdown.download(f"https://drive.google.com/uc?id={file_id}",
                           str(caminho), quiet=False)
            return caminho.exists()
        except ImportError:
            print("        💡 Dica: pip install gdown pode resolver problemas de download do Drive")
            return False


def _inspecionar(caminho: Path) -> dict:
    """Inspeciona um Parquet e retorna metadados ricos."""
    try:
        df = pd.read_parquet(caminho)
        amostra = df.head(50_000) if len(df) > 50_000 else df

        nulos = (df.isnull().sum() / len(df) * 100).round(1).to_dict()

        colunas = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            pct_nulo = nulos.get(col, 0)

            if dtype == "bool":
                contagem = df[col].value_counts().to_dict()
                exemplo = f"True={contagem.get(True, 0):,}, False={contagem.get(False, 0):,}"
            elif "datetime" in dtype or dtype == "object":
                if "id" in col.lower():
                    exemplo = f"~{df[col].nunique():,} valores únicos"
                elif df[col].dtype == object:
                    top = df[col].value_counts().head(5).to_dict()
                    exemplo = f"top: {top}"
                else:
                    exemplo = f"range: {df[col].min()} → {df[col].max()}"
            else:
                try:
                    exemplo = f"min={df[col].min():.4f}, max={df[col].max():.4f}, média={df[col].mean():.4f}"
                except Exception:
                    exemplo = "—"

            colunas.append({"nome": col, "tipo": dtype, "nulos_pct": pct_nulo, "exemplo": exemplo})

        return {
            "arquivo": caminho.name,
            "linhas": len(df),
            "colunas": len(df.columns),
            "colunas_info": colunas,
            "head_3": df.head(3).to_string(),
            "erro": None,
        }
    except Exception as e:
        return {"arquivo": caminho.name, "linhas": 0, "colunas": 0,
                "colunas_info": [], "head_3": "", "erro": str(e)}


def _formatar_para_claude(metadados: list[dict]) -> str:
    linhas = []
    for m in metadados:
        if m["erro"]:
            linhas.append(f"### {m['arquivo']}\n  ERRO: {m['erro']}\n")
            continue
        linhas.append(f"### {m['arquivo']}")
        linhas.append(f"  {m['linhas']:,} linhas × {m['colunas']} colunas\n")
        for col in m["colunas_info"]:
            linhas.append(
                f"  - {col['nome']} ({col['tipo']}) | {col['nulos_pct']}% nulos | {col['exemplo']}"
            )
        linhas.append(f"\n  Amostra (3 linhas):\n{m['head_3']}\n")
        linhas.append("─" * 60)
    return "\n".join(linhas)


# ─── Função principal ─────────────────────────────────────────────────────────

def run(repo_url: str = None, briefing_output: str = "", repo_dir: Path = None) -> str:
    """
    Executa o agente de engenharia de dados para o desafio dos ACS.
    Baixa os 4 Parquets do Google Drive e gera análise + código pandas completo.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"  📥 Baixando {len(ARQUIVOS)} dataset(s) do Google Drive...")
    falhas = []
    for nome, url in ARQUIVOS.items():
        ok = _baixar_arquivo(nome, url, DATA_DIR)
        if not ok:
            falhas.append(nome)
        time.sleep(0.5)  # evita rate limiting

    if falhas:
        print(f"  ⚠️  Falha ao baixar: {falhas}")
        print("  💡 Tente manualmente: acesse os links no README do repositório de dados")

    # Inspecionar arquivos disponíveis
    disponiveis = list(DATA_DIR.glob("*.parquet"))
    if not disponiveis:
        return (
            "# ⚠️ Nenhum arquivo Parquet disponível\n\n"
            "Baixe os arquivos manualmente em:\n"
            "https://github.com/prefeitura-rio/claude-impact-lab-saude\n"
            "e coloque em `data/parquet/`\n"
        )

    print(f"  🔍 Inspecionando {len(disponiveis)} arquivo(s)...")
    metadados = [_inspecionar(f) for f in sorted(disponiveis)]
    schemas_texto = _formatar_para_claude(metadados)

    print("  🤖 Claude analisando dados e gerando código de scoring...")

    user_message = f"""
Analise os schemas e amostras abaixo dos 4 datasets do desafio
"Inteligência no Território" (ACS Rio de Janeiro).

## CONTEXTO DO BRIEFING:
{briefing_output[:2000]}

## SCHEMAS E AMOSTRAS DOS PARQUETS:
{schemas_texto[:6000]}

Com base nisso:
1. Valide minha compreensão dos datasets com os schemas reais
2. Proponha a fórmula de score de risco com pesos justificados pelos protocolos municipais
3. Gere o código pandas COMPLETO para calcular o score e produzir a lista priorizada
4. Gere o código para as visualizações de gestão (desafio bônus)
5. Aponte as limitações dos dados anonimizados que impactam o MVP

Os arquivos estão em: data/parquet/<nome>.parquet
""".strip()

    resultado = chamar_claude(SYSTEM_PROMPT, user_message, max_tokens=6000)
    print("  ✅ Análise de dados e código gerados")
    return resultado
