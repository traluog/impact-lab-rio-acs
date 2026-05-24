# Inteligência no Território — ACS Rio

> **Claude Impact Lab Rio 2026** · Desafio: Saúde  
> Priorização inteligente de visitas domiciliares dos Agentes Comunitários de Saúde

---

## Nome da equipe

**Equipe 23 ACS Rio**

---

## Membros da equipe

| Nome | Papel |
|------|-------|
| Marina Micas | |
| Jessica Andrade | |
| Pedro Mick | |
| Camila Peira | |
| Junior Goulart | |

---

## Tema

**Saúde** — Atenção Primária à Saúde (APS) · otimização de visitas domiciliares

---

## Resumo

O Rio de Janeiro tem **6.200 Agentes Comunitários de Saúde** responsáveis por visitar 4,5 milhões de residentes. Hoje o planejamento dessas visitas depende de memória, papel e conhecimento informal — dados clínicos e sociais dispersos não chegam a campo.

Nossa solução gera automaticamente, toda manhã, uma **lista priorizada de visitas** para cada ACS, ordenada por um score de risco calculado a partir de dados reais de saúde (hipertensão, diabetes, gestação, vulnerabilidade social, urgências recentes e lacunas de visita). O Claude explica em linguagem simples *por que* cada paciente é prioridade, tornando a IA um copiloto prático para o trabalho de campo, não uma caixa preta.

A aplicação Streamlit roda no celular do ACS e inclui: mapa territorial com rotas otimizadas, agenda semanal com triagem por WhatsApp, alertas de lacuna de cuidado e fichas digitais estruturadas por condição clínica.

---

## Arquitetura / Abordagem

### Como o Claude foi usado para construir a solução

Antes de escrever uma linha de código, rodamos um **pipeline de 5 agentes autônomos** (`orchestrator.py`) que usam o Claude para compactar horas de product discovery em ~10 minutos:

```
python orchestrator.py
```

```
Parquets (Google Drive)
        │
        ▼
  Agente 1 — Briefing      → analisa contexto do desafio + transcrição
        │
  Agente 2 — Data Engineer → inspeciona schemas, propõe score de risco, gera código pandas
        │
  Agente 3 — Research      → pesquisa CHW com IA (web search) + Impact Labs anteriores
        │
  Agente 4 — Consolidador  → apresenta 3–4 opções de MVP ranqueadas
        │                    ⏸️  PAUSA — time escolhe
  Agente 5 — Arquiteto     → gera TECHNICAL_SPEC.md completo → Cursor → código
```

| Agente | Uso do Claude |
|--------|--------------|
| **Briefing** | Interpreta o briefing, extrai dores, critérios de avaliação e hipóteses de solução |
| **Data Engineer** | Analisa schemas reais dos Parquets, propõe fórmula de score com pesos pelos protocolos municipais e gera código pandas completo |
| **Research** | Usa Claude com `web_search` para buscar referências de CHW com IA em outros países e iniciativas brasileiras (e-SUS, projetos municipais) |
| **Consolidador** | Apresenta 3–4 opções de MVP ranqueadas com análise honesta de riscos — a decisão final é humana |
| **Arquiteto** | Produz o `TECHNICAL_SPEC.md` autocontido que guiou toda a implementação no Cursor |

O pipeline termina com uma pausa interativa: o time lê as opções e escolhe. O Agente 5 gera a especificação técnica para a opção escolhida, já com código real e pronto para implementar.

---

### Como o Claude atua dentro da aplicação

A aplicação usa o Claude (`claude-sonnet-4-6`) em dois pontos principais:

#### 1. Justificativas de visita em linguagem natural

Para cada paciente na lista, o Claude recebe o perfil de risco calculado localmente e gera uma explicação direta para o ACS em português:

> *"Visitar hoje: gestante em vulnerabilidade social, 28 dias sem visita. Protocolo exige acompanhamento semanal — situação requer atenção imediata."*

As justificativas são geradas em **batch** (uma única chamada à API para toda a lista do dia), economizando créditos e reduzindo a latência.

#### 2. Resumo executivo para gestores

Para a visão de gestão, o Claude agrega métricas de cobertura e lacunas de cuidado em um resumo executivo, destacando equipes com maior concentração de pacientes críticos sem visita recente.

---

### Motor de Score de Risco

O score é calculado **localmente** (sem Claude) com base nos protocolos municipais do Rio de Janeiro:

| Fator clínico | Peso | Protocolo |
|---------------|------|-----------|
| Gestante | 10 | Visita semanal / quinzenal |
| Recém-nascido (0–6 meses) | 9 | 7–8 visitas recomendadas |
| Urgência/emergência nos últimos 7 dias | 8 | Contato em até 48h |
| Vulnerabilidade social | 5 | Prioridade elevada |
| Hipertenso | 4 | Acompanhamento mensal |
| Diabético | 4 | Acompanhamento mensal |
| Lacuna de visita (escala progressiva) | 0–10 | ≥ 60 dias = máximo |

**Score total** = soma dos fatores ativos → classificado em **Crítico / Alto / Padrão**.

O Claude recebe esse score e os fatores ativos para gerar a justificativa — garantindo rastreabilidade e explicabilidade para o ACS.

---

### Funcionalidades da Aplicação

#### 📋 Lista do Dia
- Lista priorizada de visitas ordenada por score de risco
- Cards com badges de condição clínica (gestante, HAS, DM, vulnerabilidade, urgência)
- Marcação de visita como concluída ou substituída por WhatsApp
- Envio em massa de mensagem WhatsApp para pacientes padrão (triagem antecipada)
- Barra de progresso do dia

#### 🗺️ Mapa do Território
- Mapa SVG interativo do micro-território do ACS
- Dois modos de rota: menor distância total ou por criticidade clínica
- Indicação visual de pacientes por prioridade e status de visita

#### 📅 Agenda Semanal
- Distribuição das visitas pelos dias da semana
- Envio antecipado de WhatsApp (1–2 dias antes) para pacientes padrão
- Registro de resposta SIM/NÃO para substituir visita presencial quando adequado

#### 🚨 Alertas
- Detecção de pacientes que deram entrada em urgência/emergência sem visita prévia do ACS
- Crônicos (hipertensos/diabéticos) com lacuna de cuidado superior a 30 dias
- Notificação da equipe clínica com um toque

#### 📋 Fichas Digitais Estruturadas
Fichas baseadas nos instrumentos municipais reais da SMS-Rio:

| Ficha | Condição |
|-------|---------|
| Ficha A | Visita Geral (moradia, saneamento, situação social, saúde geral) |
| Ficha B-HA | Hipertensão Arterial |
| Ficha B-DIA | Diabetes Mellitus |
| Ficha B-GES | Gestante |
| Ficha C | Primeira Infância |
| Guia VV | Violências e Vulnerabilidade (SMS 2024) |

Cada ficha tem perguntas marcadas como campo-chave (`🔑`) ou alerta clínico (`⚠️`), com rastreamento de progresso por visita.

#### 🎙️ Áudio e Transcrição
- Gravação de notas de voz vinculadas a perguntas específicas da ficha
- Transcrição automática via Claude
- Histórico de gravações por paciente e por ficha

---

### Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Frontend / App | Streamlit |
| Motor de IA | Claude API (`claude-sonnet-4-6`) via Anthropic SDK |
| Dados | pandas + pyarrow (4 datasets Parquet) |
| Pipeline de agentes | Python + Anthropic SDK |
| Deploy | Streamlit Community Cloud |

---

### Datasets Utilizados

Fornecidos pela Prefeitura do Rio de Janeiro (anonimizados com SHA256 e date shifting):

| Dataset | Registros | Conteúdo |
|---------|-----------|---------|
| `pacientes.parquet` | ~98.000 | Cadastro clínico e demográfico, coordenadas geográficas |
| `eventos_clinicos.parquet` | ~118.000 | Agendamentos e idas a urgência/emergência |
| `visitas.parquet` | ~160.000 | Histórico de visitas domiciliares dos ACS |
| `equipes.parquet` | — | Localização das unidades de saúde (ponto de partida) |

---

## Links

| Recurso | URL |
|---------|-----|
| Aplicação (Streamlit Cloud) | *em breve* |
| Repositório GitHub | *em breve* |

---

## Vídeo Demo

*Em breve — demonstração de 60 segundos mostrando o fluxo completo: lista priorizada do dia → detalhes de paciente → mapa de rota → alertas de lacuna de cuidado.*

---

## Como Rodar Localmente

### Instalar dependências

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
pip install streamlit anthropic pandas pyarrow gdown python-dotenv
```

### Configurar a chave de API

```bash
cp ".env copy.example" .env
# Edite .env e adicione sua ANTHROPIC_API_KEY
export $(cat .env | grep -v '#' | xargs)
```

### Rodar a aplicação

```bash
streamlit run app.py
```

### Rodar o pipeline de agentes (opcional)

```bash
# Com transcrição do briefing
python orchestrator.py --transcricao transcricao_briefing.txt

# Sem transcrição (usa contexto pré-carregado)
python orchestrator.py

# Pulando o download dos Parquets (se já estão em data/parquet/)
python orchestrator.py --skip-dados
```

---

## Estrutura do Projeto

```
impact-lab-rio/
│
├── app.py                       # Entry point — Streamlit
├── orchestrator.py              # Pipeline de 5 agentes
├── .env.example
│
├── agents/
│   ├── __init__.py              # Cliente Claude compartilhado
│   ├── agent_briefing.py        # Agente 1 — análise do briefing
│   ├── agent_data_engineer.py   # Agente 2 — dados + score de risco
│   ├── agent_research.py        # Agente 3 — referências internacionais
│   ├── agent_consolidator.py    # Agente 4 — opções de MVP
│   └── agent_architect.py       # Agente 5 — TECHNICAL_SPEC.md
│
├── pages/
│   ├── lista.py                 # 📋 Lista do Dia
│   ├── mapa.py                  # 🗺️ Mapa do Território
│   ├── semana.py                # 📅 Agenda Semanal
│   └── alertas.py               # 🚨 Alertas e Lacunas
│
├── components/
│   ├── header.py                # Cabeçalho e navegação
│   └── patient_card.py          # Cards, fichas e gravação de áudio
│
├── data/
│   ├── patients.py              # Mock dos pacientes (substituir por scoring real)
│   ├── fichas.py                # Definição das fichas clínicas
│   └── parquet/                 # Datasets da Prefeitura (não commitados)
│
└── outputs/                     # Gerado pelo orchestrator
    ├── *_briefing.md
    ├── *_dados_parquet.md
    ├── *_research.md
    ├── *_opcoes_mvp.md
    └── *_TECHNICAL_SPEC.md
```

---

## Caminho para Produção

A solução foi desenhada para ser viável em produção em poucas semanas após o evento:

- **Integração e-SUS**: substituir os dados mock por query à API do e-SUS AB
- **Autenticação por equipe**: cada ACS acessa apenas sua micro-área
- **Atualização diária automatizada**: pipeline de scoring rodando toda madrugada
- **Notificações push**: alertar o ACS quando um paciente der entrada em urgência
- **Histórico de listas**: rastrear evolução do cuidado por paciente ao longo do tempo
- **Painel do gestor**: cobertura por área programática para coordenadores de UBS

---

> O Rio precisa desse sistema. 🤙
