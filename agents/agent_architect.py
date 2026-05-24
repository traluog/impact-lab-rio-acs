"""
AGENTE 5 — ARQUITETO DE SOFTWARE (SDD)
════════════════════════════════════════
Desafio: Inteligência no Território — ACS do Rio de Janeiro

Deploy: Streamlit Community Cloud (gratuito, link público, sem servidor)
"""

from agents import chamar_claude

SYSTEM_PROMPT = """
Você é um Arquiteto de Software Sênior especializado em sistemas de saúde pública,
dados abertos municipais e aplicações Python para hackathon e produção.

Você pratica Specification-Driven Development (SDD): especificação completa ANTES
do código, para que o time implemente no Cursor sem ambiguidade.

CONTEXTO DO PROJETO:
- Desafio: "Inteligência no Território" — lista priorizada de visitas para ACS
- Dados: 4 Parquets (pacientes, eventos_clinicos, visitas, equipes)
- Motor de IA: Claude API — justificativas em linguagem natural para cada visita
- Interface: Streamlit
- Deploy: Streamlit Community Cloud — gratuito, link público em 2 minutos
- Premissa: código que pode ir para produção real em semanas

USO DO CLAUDE NO PRODUTO (não-trivial):
- Recebe score calculado + contexto do paciente
- Gera justificativa em português para o ACS: "Visitar hoje porque..."
- Agrega múltiplos fatores de risco numa explicação coerente
- Para gestores: resumo executivo da cobertura da equipe

REGRA CRÍTICA SOBRE OS DADOS NO COMMUNITY CLOUD:
Os Parquets NÃO podem ser commitados no GitHub (são grandes demais).
O app.py deve usar gdown para baixar os arquivos do Google Drive na primeira
execução e cachear com @st.cache_data. Os IDs dos arquivos são:
  pacientes.parquet        → 1cRvsx5poNTi4EOfWHYvilSDF4_i6hcZy
  eventos_clinicos.parquet → 1rcWQbi_vA_RAnXLQV79oe4Z2mql8cn3_
  visitas.parquet          → 1dKJ8BpqrmsFNQoVcs9tjJ-Gaag1WzCML
  equipes.parquet          → 1h8DijXrZM_hnhYMAdkggp5mnb2zckFOW

CHAVE DE API NO COMMUNITY CLOUD:
  - NÃO usar .env no Cloud
  - Configurar pelo painel: App settings → Secrets → secrets.toml
  - No código: st.secrets["ANTHROPIC_API_KEY"] com fallback para os.environ

FORMATO DE SAÍDA — TECHNICAL_SPEC.md completo:

# 📐 TECHNICAL_SPEC.md — [Nome do Produto]

> **Versão:** 1.0 | **Status:** FECHADO
> Fonte única de verdade técnica. Não iniciar código sem ler este documento.

---

## 1. Visão Geral

```
Parquets (Google Drive)
        │ gdown + @st.cache_data
        ▼
  data_loader.py → pandas DataFrames
        │
  scoring.py → score de risco por paciente
        │
  claude_agent.py → justificativa em português (Claude API)
        │
  app.py (Streamlit)
   ├── Tela ACS: lista priorizada do dia
   └── Tela Gestor: painel de cobertura (bônus)
        │
  Deploy: Streamlit Community Cloud → link público
```

**Stack:** Python 3.10+ | pandas + pyarrow | anthropic SDK | streamlit | gdown

---

## 2. Estrutura de Arquivos (raiz do repositório)

```
nome-do-projeto/         ← raiz do repo (app.py DEVE estar aqui)
├── app.py               ← entry point — obrigatório na raiz para o Cloud
├── requirements.txt     ← obrigatório na raiz
├── scoring.py
├── claude_agent.py
├── data_loader.py
├── .streamlit/
│   ├── secrets.toml     ← ⚠️ NO .gitignore — configurar pelo painel do Cloud
│   └── config.toml      ← configurações visuais (opcional)
├── .env.example
├── .env                 ← ⚠️ NUNCA commitar
└── README.md            ← com link do deploy
```

---

## 3. requirements.txt
```
anthropic>=0.40.0
pandas>=2.0.0
pyarrow>=14.0.0
streamlit>=1.30.0
gdown>=5.1.0
python-dotenv>=1.0.0
```

---

## 4. Leitura da chave de API (local + Cloud)

```python
# utils.py
import os
import streamlit as st

def get_api_key() -> str:
    \"\"\"Funciona tanto local (.env) quanto no Streamlit Community Cloud (secrets).\"\"\"
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY", "")
```

---

## 5. Carregamento de Dados (data_loader.py)

```python
import gdown
import pandas as pd
import streamlit as st
from pathlib import Path

DRIVE_IDS = {
    "pacientes.parquet":        "1cRvsx5poNTi4EOfWHYvilSDF4_i6hcZy",
    "eventos_clinicos.parquet": "1rcWQbi_vA_RAnXLQV79oe4Z2mql8cn3_",
    "visitas.parquet":          "1dKJ8BpqrmsFNQoVcs9tjJ-Gaag1WzCML",
    "equipes.parquet":          "1h8DijXrZM_hnhYMAdkggp5mnb2zckFOW",
}

DATA_DIR = Path("data/parquet")

@st.cache_data(show_spinner="Carregando dados de saúde...")
def carregar_dados():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for nome, file_id in DRIVE_IDS.items():
        caminho = DATA_DIR / nome
        if not caminho.exists():
            gdown.download(
                f"https://drive.google.com/uc?id={file_id}",
                str(caminho), quiet=False
            )
    return (
        pd.read_parquet(DATA_DIR / "pacientes.parquet"),
        pd.read_parquet(DATA_DIR / "eventos_clinicos.parquet"),
        pd.read_parquet(DATA_DIR / "visitas.parquet"),
        pd.read_parquet(DATA_DIR / "equipes.parquet"),
    )
```

---

## 6. Motor de Score de Risco (scoring.py)

### Pesos (protocolos municipais do Rio)
```python
PESOS = {
    "gestante":         10,   # visita semanal/quinzenal
    "recem_nascido":     9,   # faixa 0-6 meses — 7-8 visitas recomendadas
    "urgencia_recente":  8,   # UE nos últimos 7 dias — contato em 48h
    "vulnerabilidade":   5,   # situacao_vulnerabilidade = True
    "hipertenso":        4,   # acompanhamento mensal
    "diabetico":         4,   # acompanhamento mensal
    # dias_sem_visita: escala progressiva aplicada abaixo
}
```

### Função principal
```python
from datetime import date
import pandas as pd
import numpy as np

def calcular_score(
    pacientes: pd.DataFrame,
    eventos: pd.DataFrame,
    visitas: pd.DataFrame,
    data_ref: date = None,
) -> pd.DataFrame:
    \"\"\"
    Retorna DataFrame com:
    paciente_id, equipe_id, score_total, score_clinico, score_urgencia,
    score_lacuna, dias_sem_visita, fatores_ativos (lista), prioridade (1-3)
    \"\"\"
    if data_ref is None:
        # Usa a data máxima do dataset como referência (date shifting)
        data_ref = pd.to_datetime(visitas["registrados_em"]).max().date()

    # ── Score clínico ─────────────────────────────────────────────
    pac = pacientes.copy()
    pac["score_clinico"] = (
        pac["gestante"].astype(int)    * PESOS["gestante"]    +
        pac["hipertenso"].astype(int)  * PESOS["hipertenso"]  +
        pac["diabetico"].astype(int)   * PESOS["diabetico"]   +
        pac["situacao_vulnerabilidade"].astype(int) * PESOS["vulnerabilidade"]
    )
    # Recém-nascido: faixa etária "0-6"
    pac["score_clinico"] += (pac["faixa_etaria"] == "0-6").astype(int) * PESOS["recem_nascido"]

    # ── Score de urgência ─────────────────────────────────────────
    eventos["data_referencia"] = pd.to_datetime(eventos["data_referencia"])
    corte_urgencia = pd.Timestamp(data_ref) - pd.Timedelta(days=7)
    urgencias = (
        eventos[
            (eventos["data_referencia"] >= corte_urgencia) &
            (eventos["tipo"].str.contains("urgência|emergência|hospital", case=False, na=False))
        ]
        .groupby("paciente_id")
        .size()
        .reset_index(name="urgencias_recentes")
    )

    # ── Lacuna de visita ──────────────────────────────────────────
    visitas["registrados_em"] = pd.to_datetime(visitas["registrados_em"])
    ultima = (
        visitas.groupby("paciente_id")["registrados_em"]
        .max()
        .reset_index()
        .rename(columns={"registrados_em": "ultima_visita"})
    )
    ultima["dias_sem_visita"] = (pd.Timestamp(data_ref) - ultima["ultima_visita"]).dt.days

    # Score de lacuna: progressivo (7d=1, 14d=3, 30d=6, 60d+=10)
    def score_lacuna(dias):
        if pd.isna(dias) or dias > 365: return 10  # nunca visitado
        if dias >= 60:  return 10
        if dias >= 30:  return 6
        if dias >= 14:  return 3
        if dias >= 7:   return 1
        return 0

    ultima["score_lacuna"] = ultima["dias_sem_visita"].apply(score_lacuna)

    # ── Join final ────────────────────────────────────────────────
    resultado = (
        pac
        .merge(ultima, on="paciente_id", how="left")
        .merge(urgencias, on="paciente_id", how="left")
    )
    resultado["urgencias_recentes"] = resultado["urgencias_recentes"].fillna(0)
    resultado["score_urgencia"] = resultado["urgencias_recentes"].clip(upper=1) * PESOS["urgencia_recente"]
    resultado["score_lacuna"] = resultado["score_lacuna"].fillna(10)
    resultado["score_total"] = (
        resultado["score_clinico"] +
        resultado["score_urgencia"] +
        resultado["score_lacuna"]
    )

    # Fatores ativos (para o Claude gerar a justificativa)
    def fatores(row):
        f = []
        if row.get("gestante"):         f.append("gestante")
        if row.get("faixa_etaria") == "0-6": f.append("recém-nascido")
        if row.get("hipertenso"):       f.append("hipertenso")
        if row.get("diabetico"):        f.append("diabético")
        if row.get("situacao_vulnerabilidade"): f.append("vulnerabilidade social")
        if row.get("urgencias_recentes", 0) > 0: f.append("urgência recente")
        if row.get("dias_sem_visita", 999) >= 30: f.append(f"{int(row['dias_sem_visita'])} dias sem visita")
        return f
    resultado["fatores_ativos"] = resultado.apply(fatores, axis=1)

    # Prioridade: 1=crítico, 2=alto, 3=regular
    resultado["prioridade"] = pd.cut(
        resultado["score_total"],
        bins=[-1, 8, 15, 999],
        labels=[3, 2, 1]
    ).astype(int)

    return resultado.sort_values("score_total", ascending=False)
```

---

## 7. Integração Claude API (claude_agent.py)

```python
import anthropic
from utils import get_api_key

SYSTEM_PROMPT_ACS = \"\"\"
Você é um assistente de saúde pública que ajuda Agentes Comunitários de Saúde
do Rio de Janeiro a priorizar suas visitas domiciliares.

Dado o perfil de risco de um paciente, gere uma justificativa clara, empática
e direta em português para o ACS entender por que esse paciente é prioridade hoje.

REGRAS:
- Máximo 2 frases
- Linguagem simples — o ACS não é médico
- Mencione os fatores mais relevantes
- Nunca exponha dados identificáveis
- Tom: informativo e respeitoso
\"\"\"

def gerar_justificativas_batch(pacientes_contexto: list[dict]) -> list[str]:
    \"\"\"
    Recebe lista de dicts com: fatores_ativos, dias_sem_visita, score_total
    Retorna lista de justificativas em português.
    Chamada única ao Claude para o batch inteiro — economiza créditos.
    \"\"\"
    client = anthropic.Anthropic(api_key=get_api_key())
    ...

def gerar_resumo_gestor(metricas: dict) -> str:
    \"\"\"Resumo executivo para o gestor — cobertura, lacunas, alertas.\"\"\"
    ...
```

---

## 8. Interface Streamlit (app.py)

```python
import streamlit as st
from data_loader import carregar_dados
from scoring import calcular_score
from claude_agent import gerar_justificativas_batch, gerar_resumo_gestor

st.set_page_config(page_title="Inteligência no Território", page_icon="🏥", layout="wide")

pacientes, eventos, visitas, equipes = carregar_dados()

aba = st.sidebar.radio("Perfil", ["👤 ACS", "📊 Gestor"])

if aba == "👤 ACS":
    equipe_id = st.sidebar.selectbox("Equipe", equipes["equipe_id"].unique())
    
    pac_equipe = pacientes[pacientes["equipe_id"] == equipe_id]
    scores = calcular_score(pac_equipe, eventos, visitas)
    top20 = scores.head(20)
    
    if st.button("Gerar lista de hoje com justificativas"):
        with st.spinner("Claude gerando justificativas..."):
            justificativas = gerar_justificativas_batch(
                top20[["fatores_ativos", "dias_sem_visita", "score_total"]].to_dict("records")
            )
        # Exibir lista
        for i, (_, row) in enumerate(top20.iterrows(), 1):
            st.markdown(f"**{i}.** `{row['paciente_id'][:8]}...` — Score {row['score_total']}")
            st.caption(justificativas[i-1])

elif aba == "📊 Gestor":
    # Painel de cobertura
    ...
```

---

## 9. Deploy no Streamlit Community Cloud

### Passo a passo (fazer antes das 15:30)

1. Confirme que o repositório está **público** no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Clique em **New app**
4. Selecione o repositório e `app.py` como main file
5. Em **Advanced settings → Secrets**, adicione:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-sua-chave-aqui"
   ```
6. Clique em **Deploy** — link público em ~2 minutos
7. Teste o link no celular — a banca pode acessar do próprio dispositivo

---

## 10. .gitignore obrigatório

```
.env
.streamlit/secrets.toml
data/parquet/
__pycache__/
*.pyc
.venv/
```

---

## 11. Definition of Done

- [ ] `streamlit run app.py` sobe sem erros localmente
- [ ] Dados carregam via gdown na primeira execução
- [ ] Score calculado para pelo menos 1 equipe com dados reais
- [ ] Claude gera justificativas em português
- [ ] Lista priorizada aparece na tela com justificativa por paciente
- [ ] App deployado no Community Cloud com **link público funcionando**
- [ ] Link testado no celular
- [ ] README.md com o link do deploy
- [ ] Push no GitHub antes das **16:15**

---

## 12. Caminho para Produção
[Autenticação por equipe, integração e-SUS, atualização diária dos dados,
notificações push para o ACS, histórico de listas geradas, etc.]
""".strip()


def run(consolidacao_output: str, schemas_output: str) -> str:
    print("  📐 Gerando TECHNICAL_SPEC.md para o MVP escolhido...")

    consolidacao_t = consolidacao_output[:3500] if len(consolidacao_output) > 3500 else consolidacao_output
    schemas_t      = schemas_output[:2500]       if len(schemas_output)      > 2500 else schemas_output

    user_message = f"""
Gere o TECHNICAL_SPEC.md completo para o MVP do desafio "Inteligência no Território".

O documento deve ser autocontido: um desenvolvedor deve conseguir implementar
o MVP lendo apenas este arquivo, sem precisar tomar decisões de arquitetura.

DEPLOY: Streamlit Community Cloud — inclua o passo a passo completo e o padrão
de leitura de secrets (st.secrets com fallback para os.environ).

DADOS: os Parquets são baixados via gdown do Google Drive — não são commitados.
Inclua o data_loader.py com @st.cache_data e os IDs reais dos arquivos.

Inclua código Python real e completo para:
- Motor de score de risco (scoring.py) com a fórmula e pesos dos protocolos municipais
- System prompt do Claude para justificativas em português
- Função de batch de justificativas (não 1 por paciente — economiza créditos)
- Esqueleto do app.py com telas ACS e Gestor

## MVP ESCOLHIDO PELO TIME:
{consolidacao_t}

## ANÁLISE DOS DADOS (schemas reais + código pandas):
{schemas_t}
""".strip()

    resultado = chamar_claude(SYSTEM_PROMPT, user_message, max_tokens=7000)
    print("  ✅ TECHNICAL_SPEC.md gerado — pronto para codar no Cursor")
    return resultado
