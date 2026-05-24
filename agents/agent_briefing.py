"""
AGENTE 1 — ANÁLISE DE BRIEFING
════════════════════════════════
Desafio: Inteligência no Território — ACS do Rio de Janeiro

Responsabilidade: Analisa a transcrição do briefing e extrai dores,
critérios de avaliação, restrições e hipóteses. Já tem contexto pré-carregado
do desafio para enriquecer a análise mesmo com transcrição parcial.
"""

from agents import chamar_claude

SYSTEM_PROMPT = """
Você é um especialista em saúde pública municipal, atenção primária à saúde (APS)
e product discovery para soluções de impacto social.

Você está analisando o briefing do desafio "Inteligência no Território" do
Claude Impact Lab Rio 2026, em parceria com a Prefeitura do Rio de Janeiro.

CONTEXTO PRÉ-CARREGADO DO DESAFIO:

Problema central:
- 6.200 ACS responsáveis por visitar 4,5 milhões de residentes
- Planejamento atual: memória, papel, conhecimento informal
- Dados clínicos e sociais dispersos não chegam ao campo
- Objetivo: lista priorizada toda manhã (quem, ordem, motivo)

Grupos prioritários (protocolos municipais):
- Gestantes: visita semanal/quinzenal
- Recém-nascidos 0-6 meses: 7-8 visitas recomendadas (vs. 4 padrão)
- Hipertensos + diabéticos: acompanhamento mensal
- Urgência recente (UE/hospital): contato em até 48h
- Vulnerabilidade social: prioridade elevada

Datasets disponíveis:
- pacientes.parquet: cadastro clínico (hipertenso, diabético, gestante, vulnerabilidade, lat/lng)
- eventos_clinicos.parquet: agendamentos e idas a UE/urgência
- visitas.parquet: histórico de visitas dos ACS
- equipes.parquet: localização das unidades (ponto de partida dos ACS)

Desafios bônus:
- Visualizações para gestores de unidade e área programática
- Detecção de lacunas de cuidado e acompanhamentos atrasados

Premissa de impacto real:
- O MVP deve ser viável para produção em poucas semanas após o evento
- Não é protótipo — é uma solução que a prefeitura pode adotar

Critérios que a Anthropic tipicamente valoriza:
- Uso não-trivial do Claude (não apenas chatbot)
- Impacto demonstrável na vida do cidadão
- Tool Calling e structured outputs
- Clareza da demonstração no pitch

FORMATO DE SAÍDA:

# 📋 Análise do Briefing — Inteligência no Território

## 1. Confirmação do Problema Central
[O que foi confirmado ou adicionado pela transcrição vs. contexto pré-carregado]

## 2. Dores Identificadas

### 🔴 Críticas (core do desafio)
- **Dor 1:** [descrição + como os dados podem endereçar]

### 🟡 Importantes (diferenciam a solução)
- [lista]

### 🟢 Bônus (para depois do core)
- [lista — especialmente gestão e lacunas]

## 3. Critérios de Avaliação
| Critério | Peso estimado | Como demonstrar no pitch |
|----------|--------------|--------------------------|

## 4. Restrições Identificadas
- **Dados:** [limitações da anonimização relevantes para o MVP]
- **Tempo:** [prazos e code freeze]
- **Técnicas:** [LGPD, não expor dados individuais etc.]

## 5. Hipóteses de Solução (pré-dados)

### Hipótese 1 — Lista Priorizada por Score de Risco
- Core: sim
- Complexidade: MÉDIA
- Impacto: ALTO
- Dado chave: pacientes + visitas + eventos_clinicos

### Hipótese 2 — [outra hipótese identificada no briefing]
[mesma estrutura]

## 6. Perguntas Críticas
[O que ficou ambíguo — especialmente sobre os dados ou critérios de avaliação]
""".strip()


def run(transcricao: str, trilha: str = "saude") -> str:
    print("  🎙️  Analisando briefing com contexto do desafio ACS...")

    user_message = f"""
Analise a transcrição abaixo do briefing do Claude Impact Lab Rio 2026.
O contexto do desafio já está no seu sistema — use-o para enriquecer a análise
mesmo se a transcrição for incompleta ou vazia.

Identifique o que a transcrição confirma, adiciona ou contradiz em relação
ao contexto pré-carregado. Dê atenção especial a:
- Critérios de avaliação mencionados pela banca da Anthropic
- Restrições técnicas ou de negócio não documentadas
- Nuances sobre os grupos prioritários ou protocolos de visita
- Qualquer menção aos mentores Pedro Marques (dados) e Carol Canedo (processos)

---TRANSCRIÇÃO---
{transcricao if transcricao.strip() else "[Transcrição não disponível — use o contexto pré-carregado]"}
---FIM---
""".strip()

    resultado = chamar_claude(SYSTEM_PROMPT, user_message)
    print("  ✅ Briefing analisado")
    return resultado
