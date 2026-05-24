import streamlit as st
from data.patients import ACS_NAME, ACS_TEAM, ACS_TERRITORY, TODAY_LABEL, PATIENTS
from utils.helpers import get_status


def render_header():
    urgencias = sum(1 for p in PATIENTS if p["alerta_urgencia"])

    st.markdown(f"""
    <div class="acs-header">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
            <div>
                <div style="font-size:10px;color:#94a3b8;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:2px">
                    ACS · {ACS_TEAM}
                </div>
                <div style="font-size:18px;font-weight:700">Olá, {ACS_NAME.split()[0]} 👋</div>
                <div style="font-size:11px;color:#94a3b8;margin-top:2px">{TODAY_LABEL} · {ACS_TERRITORY}</div>
            </div>
            {"<span style='background:#c0392b;color:#fff;border-radius:8px;padding:6px 10px;font-size:13px;font-weight:700'>🔔 " + str(urgencias) + "</span>" if urgencias > 0 else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    nav_items = [
        ("lista",   "📋 Lista"),
        ("mapa",    "🗺️ Mapa"),
        ("semana",  "📅 Semana"),
        ("alertas", "🚨 Alertas"),
    ]
    for col, (view_id, label) in zip(cols, nav_items):
        with col:
            active = st.session_state.active_view == view_id
            if st.button(label, key=f"nav_{view_id}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.active_view = view_id
                st.rerun()
