"""
AGENTE 3 — RESEARCH DE SOLUÇÕES
══════════════════════════════════
Desafio: Inteligência no Território — ACS do Rio de Janeiro

Responsabilidade: Pesquisa soluções de priorização de visitas domiciliares
e gestão de ACS em Impact Labs anteriores e em iniciativas internacionais
de saúde pública com IA. Adapta aprendizados para o contexto carioca.
"""

import anthropic
import os
from agents import chamar_claude, get_client, MODEL

SYSTEM_PROMPT = """
Você é um especialista em políticas públicas de saúde, sistemas de atenção
primária e inovação em saúde pública com IA, com foco em países em desenvolvimento
e contextos urbanos de alta complexidade social.

Você está pesquisando referências para o desafio "Inteligência no Território"
do Claude Impact Lab Rio 2026: otimizar visitas domiciliares dos ACS com IA.

CONTEXTO DO DESAFIO:
- 6.200 ACS no Rio visitando 4,5 milhões de residentes
- Dados: pacientes (clínico + demográfico), eventos clínicos, visitas históricas, equipes
- Objetivo: lista priorizada por risco toda manhã + visualizações para gestores
- Premissa: viável para produção em semanas

O QUE PESQUISAR:
1. Soluções de Community Health Workers (CHW) com IA em outros países
2. Sistemas de priorização de visitas domiciliares baseados em risco
3. Soluções vencedoras de Impact Labs anteriores (San Diego, Miami, CDMX)
4. Iniciativas brasileiras de digitalização do trabalho dos ACS (ex: e-SUS, Conecte SUS)
5. Modelos de scoring de risco em atenção primária (exemplos práticos)

CRITÉRIOS DE RELEVÂNCIA PARA ADAPTAÇÃO AO RIO:
- Funciona com dados anonimizados/limitados (sem nome, sem endereço exato)
- Explica as razões da priorização para o ACS (não é caixa preta)
- Considera mobilidade territorial (rota otimizada por proximidade)
- Tem interface simples — ACS usa no celular cedo da manhã
- Pode ser mantido pela prefeitura sem dependência de empresa externa

FORMATO DE SAÍDA:

# 🔍 Research — Referências para Inteligência no Território

## 1. Soluções de Referência Internacional

### [Nome] — [País/Organização]
- **O que faz:** [descrição]
- **Por que é relevante:** [conexão com o desafio dos ACS]
- **Lição principal:** [o que adaptar]
- **Adaptabilidade para o Rio:** ALTA / MÉDIA / BAIXA

[3-4 referências]

## 2. Iniciativas Brasileiras Relevantes
[e-SUS, Conecte SUS, experiências municipais]

## 3. Padrões de Sucesso em Sistemas de Priorização
[O que os sistemas que funcionam têm em comum]

## 4. Erros Comuns a Evitar
[Armadilhas em sistemas de IA para saúde pública]

## 5. Recomendação de Abordagem para o MVP
[A estratégia mais inteligente para o contexto do Rio, dado o tempo disponível]

## 6. Narrativa Vencedora para o Pitch
[Estrutura: Dor do ACS → Dado existente → Claude como motor → Impacto mensurável]
""".strip()


def run(briefing_output: str, trilha: str = "saude") -> str:
    print("  🔍 Pesquisando referências para priorização de visitas domiciliares...")

    user_message = f"""
Pesquise referências internacionais e brasileiras para sistemas de priorização
de visitas domiciliares de Agentes Comunitários de Saúde com uso de IA e dados.

Contexto do briefing:
{briefing_output[:2000]}

Foco especial em:
1. Community Health Worker (CHW) systems com scoring de risco — como foram implementados
2. Soluções que Impact Labs anteriores desenvolveram para saúde pública preventiva
3. Iniciativas brasileiras de digitalização do ACS (e-SUS, projetos municipais)
4. Modelos de roteamento de visitas domiciliares baseados em risco e proximidade geográfica

Adapte tudo para a realidade do Rio: dados anonimizados, ACS como usuário principal,
interface simples, viabilidade de produção em semanas após o evento.
""".strip()

    try:
        client = get_client()
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            tools=[{"type": "web_search_20250305", "name": "web_search"}]
        )
        resultado = "\n".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        print("  ✅ Research concluído (com web search)")
    except Exception as e:
        print(f"  ⚠️  Web search falhou ({e}). Usando conhecimento do modelo...")
        resultado = chamar_claude(SYSTEM_PROMPT, user_message)
        print("  ✅ Research concluído (sem web search)")

    return resultado
