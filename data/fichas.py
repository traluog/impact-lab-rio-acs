"""
Definição das fichas estruturadas por condição clínica.
Cada ficha contém seções com perguntas tipadas, marcadores de alerta e de campo-chave.

Baseado em:
- Ficha A (cadastramento familiar)
- Ficha B-HA (hipertensão)
- Ficha B-DIA (diabetes)
- Ficha Gestante / B-GES
- Ficha Primeira Infância / Ficha C
- Ficha TB (tuberculose)
- Guia de Violências e Vulnerabilidade (SMS 2024)
"""

FICHAS_DEF = {
    "geral": {
        "label": "Ficha A — Visita Geral",
        "icon": "📋",
        "color": "#1d4ed8",
        "bg": "#eff6ff",
        "border": "#bfdbfe",
        "sections": [
            {
                "title": "Moradia e saneamento",
                "questions": [
                    {"id": "agua",    "text": "Como está o abastecimento de água? (rede, poço, carro-pipa)", "type": "text"},
                    {"id": "lixo",    "text": "Destino do lixo? (coletado, queimado, céu aberto)",           "type": "text"},
                    {"id": "esgoto",  "text": "Tem esgoto ou fossa?",                                        "type": "bool"},
                    {"id": "energia", "text": "Tem energia elétrica?",                                       "type": "bool"},
                ],
            },
            {
                "title": "Situação social e econômica",
                "questions": [
                    {"id": "renda",   "text": "Renda familiar aproximada (faixas de salário mínimo)?",     "type": "text"},
                    {"id": "caduni",  "text": "Tem CadÚnico? Recebe Auxílio Brasil ou Cartão Família Carioca?", "type": "bool"},
                    {"id": "rua",     "text": "Alguém da família em situação de rua?",                     "type": "bool", "alert": True},
                ],
            },
            {
                "title": "Saúde geral",
                "questions": [
                    {"id": "doencas",  "text": "Há doença crônica na família? (HAS, DM, TB, asma, transtorno mental, alcoolismo)",
                     "type": "text", "alert": True, "key": True},
                    {"id": "suicidio", "text": "Houve tentativa de suicídio recente na família?",  "type": "bool", "alert": True},
                    {"id": "fuma",     "text": "Alguém fuma?",                                     "type": "bool"},
                    {"id": "dentista", "text": "Há dor de dente ou lesão na boca?",               "type": "bool"},
                    {"id": "horario",  "text": "Melhor horário e dia para visitas futuras?",       "type": "text"},
                    {"id": "obs",      "text": "Observações livres relevantes para a equipe",      "type": "text"},
                ],
            },
        ],
    },

    "has": {
        "label": "Ficha B-HA — Hipertensão",
        "icon": "🩺",
        "color": "#c0392b",
        "bg": "#fdf2f1",
        "border": "#e8b4b0",
        "sections": [
            {
                "title": "Adesão ao tratamento",
                "questions": [
                    {"id": "med",      "text": "Está tomando a medicação regularmente? Qual medicamento e dose?", "type": "text", "key": True},
                    {"id": "falta",    "text": "Faltou alguma dose esta semana? Por quê?",                       "type": "text"},
                    {"id": "dieta",    "text": "Está seguindo dieta (redução de sal e gordura)?",                "type": "bool"},
                    {"id": "exercicio","text": "Faz exercícios físicos? Quantas vezes por semana?",              "type": "bool"},
                    {"id": "fuma_has", "text": "Ainda fuma? Quantos cigarros por dia?",                          "type": "text"},
                ],
            },
            {
                "title": "Sinais e sintomas",
                "questions": [
                    {"id": "pa",        "text": "Mediu a pressão arterial recentemente? Qual foi o valor?", "type": "text", "key": True},
                    {"id": "cefaleia",  "text": "Teve dor de cabeça, tontura ou visão turva?",              "type": "bool", "alert": True},
                    {"id": "dor_peito", "text": "Sentiu dor no peito, falta de ar ou palpitações?",         "type": "bool", "alert": True},
                    {"id": "incha_has", "text": "Tem inchaço nas pernas ou pés?",                           "type": "bool", "alert": True},
                ],
            },
            {
                "title": "Acompanhamento na UBS",
                "questions": [
                    {"id": "consulta_has", "text": "Quando foi a última consulta médica? Retorno marcado?",  "type": "text"},
                    {"id": "exames_has",   "text": "Tem exames pendentes (sangue, urina, eletrocardiograma)?","type": "bool"},
                    {"id": "duvidas_has",  "text": "Tem dúvidas sobre o tratamento ou a doença?",           "type": "text"},
                ],
            },
        ],
    },

    "dm": {
        "label": "Ficha B-DIA — Diabetes",
        "icon": "💉",
        "color": "#b45309",
        "bg": "#fefbf0",
        "border": "#f0d090",
        "sections": [
            {
                "title": "Adesão ao tratamento",
                "questions": [
                    {"id": "insulin",       "text": "Usa insulina? Está aplicando corretamente? Tem quantidade suficiente?", "type": "text", "key": True},
                    {"id": "hipoglicemiante","text": "Toma hipoglicemiante oral regularmente?",                              "type": "bool", "key": True},
                    {"id": "dieta_dm",      "text": "Está seguindo dieta (controle de carboidratos e açúcar)?",             "type": "bool"},
                    {"id": "exercicio_dm",  "text": "Faz exercícios físicos?",                                              "type": "bool"},
                ],
            },
            {
                "title": "Sinais e sintomas",
                "questions": [
                    {"id": "glicemia", "text": "Mediu a glicemia recentemente? Qual foi o valor?",                        "type": "text", "key": True},
                    {"id": "hipo",     "text": "Sentiu tontura, suor frio ou tremor (hipoglicemia)?",                     "type": "bool", "alert": True},
                    {"id": "sede",     "text": "Tem sentido muita sede, urina frequente ou cansaço excessivo?",           "type": "bool", "alert": True},
                    {"id": "pes",      "text": "Como estão os pés? Alguma ferida, dormência ou formigamento?",            "type": "text", "alert": True},
                    {"id": "visao",    "text": "Notou alteração na visão?",                                               "type": "bool", "alert": True},
                ],
            },
            {
                "title": "Acompanhamento na UBS",
                "questions": [
                    {"id": "consulta_dm", "text": "Quando foi a última consulta? Tem hemoglobina glicada recente?", "type": "text"},
                    {"id": "oftalmo",     "text": "Já foi ao oftalmologista este ano?",                             "type": "bool"},
                ],
            },
        ],
    },

    "gestante": {
        "label": "Ficha Gestante — B-GES",
        "icon": "🤱",
        "color": "#7c3aed",
        "bg": "#f5f3ff",
        "border": "#c4b5fd",
        "sections": [
            {
                "title": "Estado geral",
                "questions": [
                    {"id": "semanas",    "text": "Quantas semanas de gestação tem atualmente?",                            "type": "text", "key": True},
                    {"id": "enjoo",      "text": "Está com enjoos ou vômitos? (0–12 semanas)",                             "type": "bool"},
                    {"id": "sangramento","text": "Teve sangramento ou dor abdominal?",                                     "type": "bool", "alert": True},
                    {"id": "mexeu",      "text": "Sentiu o bebê mexer nas últimas 24 horas? (a partir de 25 semanas)",     "type": "bool", "alert": True, "key": True},
                    {"id": "incha_ges",  "text": "Tem inchaço nas pernas? Dor de cabeça ou visão turva?",                  "type": "bool", "alert": True},
                ],
            },
            {
                "title": "Pré-natal e exames",
                "questions": [
                    {"id": "pa_ges",      "text": "Mediu a pressão arterial? Qual o valor?",                          "type": "text", "key": True},
                    {"id": "exames_ges",  "text": "Realizou os exames solicitados pelo médico?",                       "type": "bool"},
                    {"id": "consultas_ges","text": "Está indo às consultas de pré-natal regularmente?",               "type": "bool"},
                    {"id": "maternidade", "text": "Já conheceu/visitou a maternidade de referência?",                 "type": "bool"},
                    {"id": "parto",       "text": "Qual a data provável do parto?",                                    "type": "text"},
                ],
            },
            {
                "title": "Vacinas e proteção",
                "questions": [
                    {"id": "vacinas_ges",  "text": "Vacinas em dia? (Hepatite B, Influenza, Covid-19)",             "type": "bool"},
                    {"id": "violencia_ges","text": "Está passando por alguma situação de violência doméstica?",     "type": "bool", "alert": True},
                    {"id": "duvidas_ges",  "text": "Tem dúvidas ou preocupações sobre a gestação?",                "type": "text"},
                ],
            },
        ],
    },

    "infancia": {
        "label": "Ficha Primeira Infância",
        "icon": "👶",
        "color": "#0891b2",
        "bg": "#e0f2fe",
        "border": "#7dd3fc",
        "sections": [
            {
                "title": "Alimentação",
                "questions": [
                    {"id": "aleitamento", "text": "Como está a alimentação? (aleitamento exclusivo, complementar, fórmula?)", "type": "text", "key": True},
                    {"id": "comida",      "text": "No último mês, a comida acabou antes de ter dinheiro para comprar mais?",  "type": "bool", "alert": True},
                ],
            },
            {
                "title": "Saúde e sinais de risco",
                "questions": [
                    {"id": "febre_inf",      "text": "Teve febre, tosse, diarreia ou dificuldade para respirar?",    "type": "bool", "alert": True},
                    {"id": "vomito_inf",     "text": "Está vomitando? Tem lesão de pele ou irritabilidade intensa?", "type": "bool", "alert": True},
                    {"id": "internacao_inf", "text": "Foi internada recentemente?",                                  "type": "bool", "alert": True},
                    {"id": "desenvolvimento","text": "Percebeu alteração no desenvolvimento? (fala, andar, visão, audição)", "type": "bool", "alert": True},
                    {"id": "sono",           "text": "Onde dorme a criança? (berço próprio, cama, com adulto?)",    "type": "text"},
                ],
            },
            {
                "title": "Rotina e social",
                "questions": [
                    {"id": "vacinas_inf",  "text": "Vacinas em dia? (conferir caderneta)",                         "type": "bool"},
                    {"id": "consulta_inf", "text": "Está indo às consultas de crescimento e desenvolvimento?",     "type": "bool"},
                    {"id": "creche",       "text": "(4–6 anos) Está matriculada em creche ou pré-escola? Faltou?", "type": "text"},
                ],
            },
        ],
    },

    "tb": {
        "label": "Ficha TB — Tuberculose",
        "icon": "🫁",
        "color": "#b45309",
        "bg": "#fefbf0",
        "border": "#f0d090",
        "sections": [
            {
                "title": "Adesão ao tratamento",
                "questions": [
                    {"id": "med_tb",     "text": "Tomou a medicação todos os dias esta semana?",                             "type": "bool", "key": True},
                    {"id": "resistencia","text": "Apresenta resistência para tomar o remédio? Por quê?",                    "type": "text", "alert": True},
                    {"id": "nausea_tb",  "text": "A medicação causou náuseas, vômitos ou dor no estômago?",                 "type": "bool"},
                    {"id": "febre_tb",   "text": "Teve febre acima de 38°C, urina escura ou pele amarelada?",               "type": "bool", "alert": True},
                ],
            },
            {
                "title": "Sintomas e evolução",
                "questions": [
                    {"id": "tosse",    "text": "Ainda está tossindo? A tosse piorou, melhorou ou está igual?",  "type": "text", "key": True},
                    {"id": "escarro",  "text": "Escarro com sangue ou mudança de cor/consistência?",            "type": "bool", "alert": True},
                    {"id": "peso_tb",  "text": "Perdeu peso? Está com fraqueza ou suor noturno?",               "type": "bool", "alert": True},
                ],
            },
            {
                "title": "Contatos e isolamento",
                "questions": [
                    {"id": "contatos",    "text": "Quantas pessoas na casa? Alguma com sintomas?",                       "type": "text", "alert": True},
                    {"id": "examinados",  "text": "Os contatos domiciliares foram examinados na UBS?",                   "type": "bool", "alert": True},
                    {"id": "isolamento",  "text": "Consegue se isolar dentro de casa quando necessário?",                "type": "bool"},
                ],
            },
        ],
    },

    "violencia": {
        "label": "Sinais de Violência e Vulnerabilidade",
        "icon": "⚠️",
        "color": "#7c3aed",
        "bg": "#f5f3ff",
        "border": "#c4b5fd",
        "sections": [
            {
                "title": "Crianças e adolescentes",
                "questions": [
                    {"id": "marcas",       "text": "Há marcas físicas inexplicadas, hematomas ou queimaduras?",    "type": "bool", "alert": True},
                    {"id": "comportamento","text": "Mudança de comportamento, isolamento ou medo excessivo?",      "type": "bool", "alert": True},
                    {"id": "escola",       "text": "Está frequentando a escola regularmente?",                     "type": "bool"},
                ],
            },
            {
                "title": "Mulheres",
                "questions": [
                    {"id": "tristeza",      "text": "Tristeza persistente, apatia ou isolamento?",                     "type": "bool", "alert": True},
                    {"id": "violencia_dom", "text": "Há suspeita ou relato de violência doméstica?",                   "type": "bool", "alert": True},
                    {"id": "preventivo",    "text": "(25–64 anos) Quando foi o último preventivo (papanicolau)?",      "type": "text"},
                    {"id": "mamografia",    "text": "(50–69 anos) Quando foi a última mamografia?",                    "type": "text"},
                ],
            },
            {
                "title": "Idosos",
                "questions": [
                    {"id": "negligencia",    "text": "Há sinais de negligência (fome, higiene, medicação negada)?",  "type": "bool", "alert": True},
                    {"id": "isolamento_id",  "text": "O idoso está isolado? Tem acesso à família e serviços?",       "type": "bool", "alert": True},
                    {"id": "quedas",         "text": "Teve quedas recentes? Há risco de queda no domicílio?",        "type": "bool"},
                ],
            },
        ],
    },
}
