import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="ACS · Lista do Dia",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.block-container { max-width: 680px; padding-top: 1.5rem; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { padding: 8px 18px; border-radius: 6px; font-weight: 600; }

/* Score badges */
.score-critico { background:#fdf2f1; border:1px solid #e8b4b0; color:#c0392b;
  border-radius:6px; padding:4px 10px; font-weight:800; font-size:13px; }
.score-alto { background:#fefbf0; border:1px solid #f0d090; color:#b45309;
  border-radius:6px; padding:4px 10px; font-weight:800; font-size:13px; }
.score-padrao { background:#f0faf4; border:1px solid #a8dbb8; color:#166534;
  border-radius:6px; padding:4px 10px; font-weight:800; font-size:13px; }

/* Cards */
.patient-card { background:#fff; border:1px solid #e2ddd6;
  border-radius:10px; padding:14px 16px; margin-bottom:10px; }
.patient-card.urgencia { border-left:4px solid #c0392b; }
.patient-card.alto { border-left:4px solid #b45309; }
.patient-card.padrao { border-left:4px solid #166534; }
.alert-box { background:#fdf2f1; border:1px solid #e8b4b0;
  border-radius:8px; padding:14px; margin-bottom:12px; }
.warn-box { background:#fefbf0; border:1px solid #f0d090;
  border-radius:8px; padding:14px; margin-bottom:12px; }
.info-box { background:#eff6ff; border:1px solid #bfdbfe;
  border-radius:8px; padding:14px; margin-bottom:12px; }
.ok-box { background:#f0faf4; border:1px solid #a8dbb8;
  border-radius:8px; padding:14px; margin-bottom:12px; }
.tag { display:inline-block; background:#f3f4f6; color:#374151;
  border-radius:4px; padding:2px 7px; font-size:11px; font-weight:700;
  margin:2px; letter-spacing:.4px; text-transform:uppercase; }
.tag-danger { background:#fdf2f1; color:#c0392b; }
.tag-warn   { background:#fefbf0; color:#b45309; }
.tag-purple { background:#f5f3ff; color:#7c3aed; }
.tag-blue   { background:#eff6ff; color:#1d4ed8; }
.metric-box { background:#fff; border:1px solid #e2ddd6; border-radius:8px;
  padding:14px; text-align:center; }
.metric-val { font-size:28px; font-weight:800; line-height:1; }
.metric-label { font-size:11px; color:#6b6560; margin-top:4px; text-transform:uppercase; letter-spacing:.5px; }
</style>
""", unsafe_allow_html=True)

# ── DADOS MOCK (output do join dos 4 datasets) ────────────────────────────────
TODAY = date.today()

PATIENTS = [
    dict(id="p001", code="93449...", ordem=1, score=92,
         faixa="66+", sexo="F", raca="Branca",
         hipertenso=True, diabetico=True, gestacao=False, vulneravel=False,
         dias_sem_visita=47, alerta_urgencia=True,
         ultimo_evento="urgencia-emergencia-ou-internacao",
         data_ultimo_evento="03/05/2025",
         motivos=["66+ anos", "Hipertenso + Diabético", "47 dias sem visita", "⚡ Urgência em mai/25"],
         distancia="380m", endereco="Rua das Camélias, próx. nº 42"),
    dict(id="p002", code="70380...", ordem=2, score=78,
         faixa="6-18", sexo="F", raca="Parda",
         hipertenso=False, diabetico=False, gestacao=False, vulneravel=True,
         dias_sem_visita=63, alerta_urgencia=False,
         ultimo_evento="agendamento", data_ultimo_evento="23/03/2025",
         motivos=["Vulnerabilidade social", "63 dias sem visita", "Adolescente em território de risco"],
         distancia="520m", endereco="Beco do Cedro, nº 11"),
    dict(id="p003", code="5a3f1...", ordem=3, score=71,
         faixa="19-45", sexo="F", raca="Parda",
         hipertenso=False, diabetico=False, gestacao=True, vulneravel=True,
         dias_sem_visita=28, alerta_urgencia=False,
         ultimo_evento="agendamento", data_ultimo_evento="28/04/2025",
         motivos=["🤱 Gestante", "Vulnerabilidade social", "28 dias sem visita"],
         distancia="210m", endereco="Trav. Esperança, nº 7A"),
    dict(id="p004", code="867dd...", ordem=4, score=55,
         faixa="45-65", sexo="F", raca="Parda",
         hipertenso=True, diabetico=False, gestacao=False, vulneravel=False,
         dias_sem_visita=38, alerta_urgencia=False,
         ultimo_evento="agendamento", data_ultimo_evento="15/04/2025",
         motivos=["Hipertensa", "38 dias sem visita"],
         distancia="670m", endereco="R. Lins de Vasconcelos, nº 198"),
    dict(id="p005", code="c72ab...", ordem=5, score=48,
         faixa="66+", sexo="M", raca="Preta",
         hipertenso=True, diabetico=False, gestacao=False, vulneravel=False,
         dias_sem_visita=22, alerta_urgencia=False,
         ultimo_evento="agendamento", data_ultimo_evento="04/05/2025",
         motivos=["66+ anos", "Hipertenso", "22 dias sem visita"],
         distancia="290m", endereco="R. Barão de Cotegipe, nº 34"),
    dict(id="p006", code="bb019...", ordem=6, score=35,
         faixa="0-6", sexo="M", raca="Parda",
         hipertenso=False, diabetico=False, gestacao=False, vulneravel=False,
         dias_sem_visita=18, alerta_urgencia=False,
         ultimo_evento="agendamento", data_ultimo_evento="08/05/2025",
         motivos=["Criança 0-6 anos", "18 dias sem visita"],
         distancia="450m", endereco="R. das Orquídeas, nº 3"),
    dict(id="p007", code="f3d88...", ordem=7, score=25,
         faixa="19-45", sexo="M", raca="Branca",
         hipertenso=False, diabetico=False, gestacao=False, vulneravel=False,
         dias_sem_visita=11, alerta_urgencia=False,
         ultimo_evento="agendamento", data_ultimo_evento="15/05/2025",
         motivos=["Sem condição crônica", "11 dias sem visita"],
         distancia="180m", endereco="Pça. General Osório, nº 21"),
]

RESUMO = dict(total=127, cronicas=38, gestantes=4, sem_visita_30d=31, urgencias=1)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "visited" not in st.session_state:
    st.session_state.visited = set()
if "notif_sent" not in st.session_state:
    st.session_state.notif_sent = set()

# ── HEADER ─────────────────────────────────────────────────────────────────────
urgencias_ativas = sum(1 for p in PATIENTS if p["alerta_urgencia"])
notif_badge = f" 🔴{urgencias_ativas}" if urgencias_ativas else ""

st.markdown(f"""
<div style="background:#1a1612;color:#fff;border-radius:12px;padding:18px 20px;margin-bottom:18px;">
  <div style="font-size:11px;color:#94a3b8;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;">
    ACS · ESF Cascadura III
  </div>
  <div style="font-size:20px;font-weight:800;font-family:Georgia,serif;">Olá, Maria 👋</div>
  <div style="font-size:12px;color:#94a3b8;margin-top:2px;">
    {TODAY.strftime('%a, %d %b %Y')} · Micro-área 07 · Cascadura
  </div>
  <div style="display:flex;gap:20px;margin-top:14px;">
    <div><span style="font-size:18px;font-weight:800;color:#00e5b4">{RESUMO['total']}</span>
      <div style="font-size:10px;color:#64748b;text-transform:uppercase">Pacientes</div></div>
    <div><span style="font-size:18px;font-weight:800;color:#f59e0b">{RESUMO['sem_visita_30d']}</span>
      <div style="font-size:10px;color:#64748b;text-transform:uppercase">Sem visita +30d</div></div>
    <div><span style="font-size:18px;font-weight:800;color:#f43f5e">{urgencias_ativas}</span>
      <div style="font-size:10px;color:#64748b;text-transform:uppercase">Alerta urgência</div></div>
    <div><span style="font-size:18px;font-weight:800;color:#a78bfa">{RESUMO['gestantes']}</span>
      <div style="font-size:10px;color:#64748b;text-transform:uppercase">Gestantes</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    f"📋 Lista do Dia",
    f"🚨 Alertas{notif_badge}",
    "📊 Painel",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 · LISTA DO DIA
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    done = len(st.session_state.visited)
    total = len(PATIENTS)
    pct = int((done / total) * 100)

    st.progress(pct / 100, text=f"**{done}/{total} visitas realizadas hoje** · {pct}%")

    st.markdown("""
    <div class="info-box" style="font-size:12px;margin-top:8px;">
    <strong>Como esta lista foi gerada:</strong> Score calculado cruzando
    <code>dados_pacientes</code> (HAS, DM, gestação, vulnerabilidade) +
    <code>dados_visitas</code> (dias sem contato) +
    <code>dados_eventos_clinicos</code> (urgências) +
    <code>dados_equipes</code> (geo). Rota otimizada por proximidade.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    for p in PATIENTS:
        score = p["score"]
        is_done = p["id"] in st.session_state.visited

        # Score styling
        if score >= 80:
            score_class = "score-critico"
            card_class = "urgencia"
            score_label = "CRÍTICO"
        elif score >= 55:
            score_class = "score-alto"
            card_class = "alto"
            score_label = "ALTO"
        else:
            score_class = "score-padrao"
            card_class = "padrao"
            score_label = "PADRÃO"

        # Tags
        tags = []
        if p["gestacao"]:   tags.append('<span class="tag tag-purple">🤱 Gestante</span>')
        if p["hipertenso"]: tags.append('<span class="tag tag-danger">HAS</span>')
        if p["diabetico"]:  tags.append('<span class="tag tag-warn">DM</span>')
        if p["vulneravel"]: tags.append('<span class="tag tag-purple">Vulnerável</span>')
        tags.append(f'<span class="tag">{p["faixa"]}</span>')
        tags.append(f'<span class="tag">{"♀" if p["sexo"]=="F" else "♂"} {p["sexo"]}</span>')
        tags_html = " ".join(tags)

        urgencia_banner = '<span style="background:#c0392b;color:#fff;font-size:9px;font-weight:800;padding:2px 8px;border-radius:3px;letter-spacing:.8px;">⚡ URGÊNCIA PRÉVIA</span>' if p["alerta_urgencia"] else ""
        dias_color = "#c0392b" if p["dias_sem_visita"] > 30 else "#6b6560"
        done_overlay = '<div style="font-size:13px;font-weight:700;color:#166534;margin-top:6px;">✔ Visita registrada</div>' if is_done else ""

        st.markdown(f"""
        <div class="patient-card {card_class}" style="opacity:{'0.5' if is_done else '1'}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-size:18px;font-weight:800;color:{'#c0392b' if score>=80 else '#b45309' if score>=55 else '#166534'}">#{p['ordem']}</span>
                <code style="font-size:11px;color:#6b6560">{p['code']}</code>
                {urgencia_banner}
              </div>
              <div>{tags_html}</div>
            </div>
            <div style="text-align:right">
              <span class="{score_class}">{score}</span>
              <div style="font-size:10px;margin-top:4px;font-weight:700;color:{'#c0392b' if score>=80 else '#b45309' if score>=55 else '#166534'}">{score_label}</div>
              <div style="font-size:11px;margin-top:4px;font-weight:{'700' if p['dias_sem_visita']>30 else '400'};color:{dias_color}">{p['dias_sem_visita']}d sem visita</div>
            </div>
          </div>
          <div style="margin-top:10px;padding-top:8px;border-top:1px solid #e2ddd6;display:flex;justify-content:space-between;font-size:12px;">
            <span>📍 {p['endereco']}</span>
            <span style="color:#1d4ed8;font-weight:600">🚶 {p['distancia']}</span>
          </div>
          {done_overlay}
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            with st.expander("Ver detalhes e motivos do score"):
                st.markdown("**Por que esta prioridade?**")
                for m in p["motivos"]:
                    st.markdown(f"- {m}")
                st.markdown(f"**Último evento:** {p['ultimo_evento']} em {p['data_ultimo_evento']}")
        with col2:
            label = "✔ Feito" if is_done else "Marcar visita"
            if st.button(label, key=f"visit_{p['id']}", disabled=is_done, use_container_width=True):
                st.session_state.visited.add(p["id"])
                st.rerun()

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 · ALERTAS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🚨 Alertas que exigem ação antes de sair a campo")

    # Alerta 1 — urgência
    st.markdown("""
    <div class="alert-box">
    <div style="font-size:15px;font-weight:800;color:#c0392b;margin-bottom:8px;">⚡ Paciente com Urgência sem Visita Prévia</div>
    <div style="font-size:13px;color:#6b6560;line-height:1.7">
      <b>Paciente 93449...</b> deu entrada em urgência/emergência em <b>03/05/2025</b>.<br>
      Última visita do ACS: <b>47 dias antes</b> (19/03/2025).<br>
      O paciente ficou mais de 30 dias sem contato antes da internação — <b>falha preventiva detectada pelos dados</b>.
    </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if "notif_urg" not in st.session_state.notif_sent:
            if st.button("📲 Notificar Equipe Clínica", use_container_width=True, type="primary"):
                st.session_state.notif_sent.add("notif_urg")
                st.rerun()
        else:
            st.success("✔ Equipe clínica notificada")
    with col2:
        st.button("📍 Já é #1 da Lista", use_container_width=True, disabled=True)

    st.markdown("---")

    # Alerta 2 — crônicos
    st.markdown("""
    <div class="warn-box">
    <div style="font-size:15px;font-weight:800;color:#b45309;margin-bottom:8px;">📉 Crônicos com Lacuna de Cuidado</div>
    <div style="font-size:13px;color:#6b6560;line-height:1.7">
      <b>31 pacientes</b> com HAS/DM na micro-área sem visita há +30 dias.<br>
      Média real dos dados: <b>1,6 visitas/paciente em 11 meses</b> — protocolo exige ≥11.<br>
      Gap de cobertura: <b style="color:#c0392b">85% abaixo do mínimo</b>.
    </div>
    </div>
    """, unsafe_allow_html=True)

    cronicos_data = pd.DataFrame([
        {"Paciente": "93449...", "Condição": "HAS + DM · 66+", "Dias sem visita": 47},
        {"Paciente": "867dd...", "Condição": "HAS · 45-65",    "Dias sem visita": 38},
        {"Paciente": "c72ab...", "Condição": "HAS · 66+",      "Dias sem visita": 22},
    ])
    st.dataframe(cronicos_data, use_container_width=True, hide_index=True)

    if "notif_cron" not in st.session_state.notif_sent:
        if st.button("📊 Enviar Relatório à Coordenação", use_container_width=True):
            st.session_state.notif_sent.add("notif_cron")
            st.rerun()
    else:
        st.success("✔ Relatório enviado à coordenação da UBS")

    st.markdown("---")

    # Alerta 3 — gestantes
    st.markdown("""
    <div style="background:#fdf4ff;border:1px solid #e9d5ff;border-radius:8px;padding:14px;margin-bottom:12px;">
    <div style="font-size:15px;font-weight:800;color:#7c3aed;margin-bottom:8px;">🤱 4 Gestantes na Micro-área</div>
    <div style="font-size:13px;color:#6b6560;line-height:1.7">
      Campo <code>gestacao = TRUE</code> em <b>dados_pacientes</b>.
      Antes desta ferramenta, o ACS não sabia disso antes de sair.<br>
      <b>Gestante priorizada hoje:</b> 5a3f1... · Trav. Esperança, 7A · <b>#3 da lista</b>.
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**💡 O que mudou com esta ferramenta:**")
    comparativo = pd.DataFrame([
        {"Antes": "Lista vinha da memória do ACS",            "Agora": "Gerada por score de risco + dados"},
        {"Antes": "ACS não sabia quais são crônicos",         "Agora": "HAS, DM, gestação visíveis antes de sair"},
        {"Antes": "Urgências detectadas reativamente",        "Agora": "Alertadas na manhã seguinte"},
        {"Antes": "1,6 visita/paciente em 11 meses",         "Agora": "Crônicos priorizados no topo da lista"},
    ])
    st.dataframe(comparativo, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 · PAINEL
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Painel da Micro-área · Cascadura 07")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("👥 Pacientes",       RESUMO["total"])
    with c2: st.metric("❤️ Com crônicas",   RESUMO["cronicas"])
    with c3: st.metric("🕐 Sem visita +30d", RESUMO["sem_visita_30d"], delta="-31 descobertos", delta_color="inverse")
    with c4: st.metric("⚡ Urgências s/visita", RESUMO["urgencias"], delta_color="inverse")

    st.markdown("---")
    st.markdown("#### Composição Clínica")

    composicao = pd.DataFrame({
        "Condição":   ["Hipertensos", "Vulneráveis", "Diabéticos", "HAS + DM", "Gestantes"],
        "% Pacientes": [30, 24, 10, 4, 3],
    })
    st.bar_chart(composicao.set_index("Condição"), use_container_width=True, height=220)

    st.markdown("---")
    st.markdown("#### ⚠️ Gap de Cobertura — evidência dos dados")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:#fdf2f1;border:1px solid #e8b4b0;border-radius:8px;padding:16px;text-align:center;">
          <div style="font-size:32px;font-weight:800;color:#c0392b">1,6×</div>
          <div style="font-size:11px;color:#6b6560;margin-top:4px;text-transform:uppercase">Visitas reais / paciente<br>em 11 meses (dado real)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#f0faf4;border:1px solid #a8dbb8;border-radius:8px;padding:16px;text-align:center;">
          <div style="font-size:32px;font-weight:800;color:#166534">11×</div>
          <div style="font-size:11px;color:#6b6560;margin-top:4px;text-transform:uppercase">Protocolo mínimo<br>para crônicos (1/mês)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-box" style="margin-top:12px;font-size:13px;">
    <b>85% abaixo do mínimo.</b> Com a lista priorizada, crônicos passam a ocupar os primeiros
    slots do dia — garantindo atendimento antes de o tempo acabar.
    A lógica de score puxa pacientes com mais dias sem visita para o topo automaticamente.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Arquitetura de Dados por trás do app")
    st.code("""
-- Score de risco por paciente (motor central)
SELECT
  p.paciente_id,
  p.endereco_latitude, p.endereco_longitude,
  (CASE WHEN p.gestacao              THEN 35 ELSE 0 END
  + CASE WHEN p.situacao_vulnerabilidade THEN 25 ELSE 0 END
  + CASE WHEN p.hipertenso AND p.diabetico THEN 20
         WHEN p.hipertenso OR  p.diabetico THEN 12 ELSE 0 END
  + CASE WHEN p.faixa_etaria IN ('66+','0-6') THEN 10 ELSE 0 END
  + LEAST((CURRENT_DATE - MAX(v.registrados_em)), 60) / 2
  ) AS score_risco
FROM pacientes p
LEFT JOIN visitas v USING (paciente_id)
WHERE p.equipe_id = :equipe_id_do_acs
GROUP BY 1,2,3
ORDER BY score_risco DESC;
    """, language="sql")
