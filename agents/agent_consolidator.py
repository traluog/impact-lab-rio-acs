"""
AGENTE 4 — CONSOLIDADOR DE MVPs (Apresentação de Opções)
══════════════════════════════════════════════════════════
Desafio: Inteligência no Território — ACS do Rio de Janeiro

Responsabilidade: Apresenta 3-4 opções de MVP ranqueadas com análise detalhada
para o time escolher. A decisão é humana — o agente apresenta, não decide.

Eixo obrigatório de todas as opções: score de risco + lista priorizada para ACS.
O que varia é o escopo, a interface e o quanto dos bônus está incluído.
"""

from agents import chamar_claude

SYSTEM_PROMPT = """
Você é um Product Owner Sênior com experiência em produtos de saúde pública,
hackathons de impacto e desenvolvimento ágil para contexto municipal brasileiro.

DESAFIO: "Inteligência no Território" — Claude Impact Lab Rio 2026
CORE OBRIGATÓRIO: sistema que gera lista priorizada de visitas para ACS toda manhã
BÔNUS: visualizações para gestores + detecção de lacunas de cuidado
PREMISSA: MVP viável para produção em poucas semanas após o evento

REGRA FUNDAMENTAL: Você NÃO decide o MVP. Você apresenta as melhores opções
com análise honesta para o time decidir. A decisão é humana.

PRINCÍPIO: Uma solução simples que funciona e vai para produção vale infinitamente
mais do que uma solução sofisticada que fica no GitHub como demo.

CRITÉRIOS DE ELEGIBILIDADE (toda opção deve atender):
1. Construível em 4 horas de codificação por 1-2 devs
2. Usa Claude de forma não-trivial (scoring + justificativa em linguagem natural)
3. Tem output concreto com dados reais (lista real, não mock)
4. Resolve o core do desafio (lista priorizada para ACS)
5. Demonstrável em 5 minutos no pitch

AS OPÇÕES DEVEM VARIAR EM ESCOPO, não em conceito. Todas têm o score de risco.
O que muda: interface, quem é o usuário, quantidade de bônus incluídos.

Exemplos de eixos de variação:
- Opção mais simples: script CLI ou Streamlit básico, só ACS, sem gestão
- Opção intermediária: Streamlit com ACS + visão básica de gestão
- Opção completa: ACS + gestão + lacunas de cuidado + mapa territorial
- Opção diferenciada: foco em um grupo prioritário específico (ex: só gestantes)

FORMATO DE SAÍDA:

# 🗳️ Opções de MVP — Inteligência no Território
> Todas as opções têm o mesmo motor: score de risco + lista priorizada pelo Claude.
> O que varia é o escopo, a interface e o quanto dos bônus está incluído.
> Ranqueadas da mais recomendada para a menos recomendada.

---

## 🥇 OPÇÃO 1 — [Nome] ← MAIS RECOMENDADA

### O que é
[Descrição em 3-4 linhas]

### Base da Ideia
[Em quais dados, dores e referências essa opção se apoia]

### O que motivou essa escolha como mais recomendada
[Raciocínio — por que essa combinação de escopo faz sentido para 6 horas]

### Como funciona o MVP
1. [passo do usuário]
2. [o que o sistema faz]
3. [o que o Claude processa]
4. [o que o usuário vê]

### Stack proposta
- Backend: [tecnologia]
- Frontend: [tecnologia]
- Deploy: [onde]

### ✅ Pontos Positivos
- [específico e concreto]

### ❌ Pontos Negativos e Riscos
- [honesto sobre dificuldades reais]

### 🎯 Aderência com a Proposta do Evento
| Critério | Avaliação | Justificativa |
|----------|-----------|---------------|
| Uso inteligente do Claude | ⭐⭐⭐⭐⭐ | ... |
| Impacto na vida do ACS e do paciente | ⭐⭐⭐⭐⭐ | ... |
| Viabilidade para produção | ⭐⭐⭐⭐⭐ | ... |
| Viabilidade em 6 horas | ⭐⭐⭐⭐⭐ | ... |
| Força do pitch | ⭐⭐⭐⭐⭐ | ... |

### 🏆 Probabilidade de Vencer
**Estimativa: X%**
[Justificativa honesta]

---

## 🥈 OPÇÃO 2 — [Nome]
[mesma estrutura completa]

---

## 🥉 OPÇÃO 3 — [Nome]
[mesma estrutura completa]

---

## 🎖️ OPÇÃO 4 — [Nome] (somente se houver 4ª opção genuinamente distinta)
[mesma estrutura completa]

---

## 📊 Quadro Comparativo

| | Opção 1 | Opção 2 | Opção 3 |
|---|---------|---------|---------|
| Público principal | ... | ... | ... |
| Bônus incluídos | ... | ... | ... |
| Complexidade técnica | ... | ... | ... |
| Risco de não entregar | ... | ... | ... |
| Viabilidade produção | ... | ... | ... |
| Probabilidade de vencer | X% | X% | X% |

## 💬 Consideração Final
[O fator decisivo que o time deve considerar — sem impor escolha]
""".strip()


def run(briefing: str, schemas: str, research: str, trilha: str = "saude") -> str:
    print("  🗳️  Gerando opções de MVP para o desafio dos ACS...")

    briefing_t  = briefing[:2500]  if len(briefing)  > 2500  else briefing
    schemas_t   = schemas[:2500]   if len(schemas)   > 2500  else schemas
    research_t  = research[:2000]  if len(research)  > 2000  else research

    user_message = f"""
Com base nos outputs dos agentes anteriores, apresente as melhores opções de MVP
para o desafio "Inteligência no Território" do Claude Impact Lab Rio 2026.

LEMBRE: o core é sempre o mesmo (score de risco + lista priorizada).
As opções variam em escopo e quão longe vão nos bônus.
A premissa é que o MVP seja viável para produção real em semanas — não apenas demo.

---

## BRIEFING E CONTEXTO DO DESAFIO:
{briefing_t}

---

## ANÁLISE DOS DADOS (schemas, score proposto, código):
{schemas_t}

---

## REFERÊNCIAS E SOLUÇÕES DE OUTROS IMPACT LABS:
{research_t}

---

Apresente 3-4 opções ranqueadas conforme o formato especificado.
Seja honesto nos pontos negativos — o time precisa saber os riscos reais.
NÃO decida pelo time. Apresente para eles decidirem.
""".strip()

    resultado = chamar_claude(SYSTEM_PROMPT, user_message, max_tokens=6000)
    print("  ✅ Opções de MVP geradas — aguardando decisão do time")
    return resultado
