import streamlit as st

st.set_page_config(
    page_title="ACS · Inteligência no Território",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── session state init ────────────────────────────────────────────────────────
from data.patients import PATIENTS
from data.fichas import FICHAS_DEF

if "statuses" not in st.session_state:
    st.session_state.statuses = {}          # pid -> "done" | "wpp_ok" | "wpp_sent"
if "forms_done" not in st.session_state:
    st.session_state.forms_done = {}        # pid -> {ficha_id: [answered_qids]}
if "audios" not in st.session_state:
    st.session_state.audios = {}            # f"{pid}_{ficha_id}" -> [{id, label, duration, question, transcript}]
if "wpp_sent_week" not in st.session_state:
    st.session_state.wpp_sent_week = set()  # pids with wpp sent this week
if "active_view" not in st.session_state:
    st.session_state.active_view = "lista"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', 'Segoe UI', sans-serif;
}
.block-container {
    max-width: 520px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* Score badges */
.badge-critico  { background:#fdf2f1; border:1px solid #e8b4b0; color:#c0392b;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }
.badge-alto     { background:#fefbf0; border:1px solid #f0d090; color:#b45309;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }
.badge-padrao   { background:#f0faf4; border:1px solid #a8dbb8; color:#166534;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }
.badge-wpp      { background:#d1fae5; border:1px solid #6ee7b7; color:#047857;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }
.badge-done     { background:#f0faf4; border:1px solid #a8dbb8; color:#166534;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }
.badge-info     { background:#eff6ff; border:1px solid #bfdbfe; color:#1d4ed8;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }
.badge-warn     { background:#fefbf0; border:1px solid #f0d090; color:#b45309;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }
.badge-purple   { background:#f5f3ff; border:1px solid #c4b5fd; color:#7c3aed;  border-radius:5px; padding:3px 8px; font-weight:700; font-size:11px; display:inline-block; }

/* Patient cards */
.patient-card {
    background:#fff; border:1px solid #e2ddd6; border-radius:10px;
    padding:13px 14px; margin-bottom:10px;
}
.patient-card.critico  { border-left:4px solid #c0392b; }
.patient-card.alto     { border-left:4px solid #b45309; }
.patient-card.padrao   { border-left:4px solid #166534; }
.patient-card.done     { opacity:0.45; }

/* Alert / info boxes */
.alert-box  { background:#fdf2f1; border:1px solid #e8b4b0; border-radius:9px; padding:12px 14px; margin-bottom:10px; }
.warn-box   { background:#fefbf0; border:1px solid #f0d090; border-radius:9px; padding:12px 14px; margin-bottom:10px; }
.ok-box     { background:#f0faf4; border:1px solid #a8dbb8; border-radius:9px; padding:12px 14px; margin-bottom:10px; }
.info-box   { background:#eff6ff; border:1px solid #bfdbfe; border-radius:9px; padding:12px 14px; margin-bottom:10px; }
.purple-box { background:#f5f3ff; border:1px solid #c4b5fd; border-radius:9px; padding:12px 14px; margin-bottom:10px; }

/* Question items */
.q-item       { background:#f9f8f5; border:2px solid transparent; border-radius:8px; padding:10px 12px; margin-bottom:6px; }
.q-item.alert { border-left:3px solid #c0392b; }
.q-item.done  { background:#f0faf4; border-color:#a8dbb8; }

/* Map area */
.map-container { background:#e8f4f0; border:1px solid #e2ddd6; border-radius:10px; padding:0; overflow:hidden; }

/* Transcript box */
.transcript-box { background:#f0faf4; border:1px solid #a8dbb8; border-radius:7px; padding:9px 11px; margin-top:6px; font-size:12px; line-height:1.6; }

/* Week card */
.week-card { background:#fff; border:1px solid #e2ddd6; border-radius:9px; padding:10px 12px; margin-bottom:8px; }

/* Header */
.acs-header { background:#1a1612; color:#fff; padding:14px 18px 12px; border-radius:0 0 12px 12px; margin-bottom:16px; }

/* Progress bar */
.prog-bg   { background:#e2ddd6; border-radius:4px; height:8px; }
.prog-fill { background:#1d4ed8; border-radius:4px; height:8px; transition:width .4s; }

/* Divider */
hr.thin { border:none; border-top:1px solid #e2ddd6; margin:10px 0; }

/* Form section header */
.section-title { font-size:10px; font-weight:700; color:#9c948c; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px; margin-top:12px; }
</style>
""", unsafe_allow_html=True)

# ── navigation ────────────────────────────────────────────────────────────────
from components.header import render_header
render_header()

view = st.session_state.active_view

if view == "lista":
    from pages.lista import render_lista
    render_lista()
elif view == "mapa":
    from pages.mapa import render_mapa
    render_mapa()
elif view == "semana":
    from pages.semana import render_semana
    render_semana()
elif view == "alertas":
    from pages.alertas import render_alertas
    render_alertas()
