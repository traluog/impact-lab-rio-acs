import streamlit as st
from data.patients import PATIENTS
from utils.helpers import (
    active_patients, get_status, set_status, clear_status, is_padrao,
    route_by_distance, route_by_priority, total_route_dist, meters_label,
    build_map_svg,
)
from components.patient_card import render_patient_detail


def render_mapa():
    st.markdown("### 🗺️ Mapa do Território")

    active = active_patients(PATIENTS)
    statuses = st.session_state.statuses

    # Route mode selector
    route_mode = st.radio(
        "Modo de rota",
        options=["distance", "priority"],
        format_func=lambda x: "📍 Menor distância total" if x == "distance" else "⚡ Por criticidade clínica",
        horizontal=True,
        key="map_route_mode",
    )

    route_color = "#1d4ed8" if route_mode == "distance" else "#c0392b"
    route = route_by_distance(active) if route_mode == "distance" else route_by_priority(active)

    total_d = meters_label(total_route_dist(route))
    st.caption(f"{len(active)} paradas pendentes · {total_d} estimado")

    # SVG Map
    svg = build_map_svg(PATIENTS, statuses, route, st.session_state.audios, route_color)
    st.markdown(f'<div class="map-container">{svg}</div>', unsafe_allow_html=True)

    st.divider()

    # Route list
    route_title = "📍 Rota — menor distância total" if route_mode == "distance" else "⚡ Rota — por criticidade clínica"
    st.markdown(f"**{route_title}**")

    if not route:
        st.success("🎉 Todas as visitas foram concluídas!")
    else:
        for i, p in enumerate(route):
            s = get_status(p["id"])
            from utils.helpers import score_label, score_color
            sc = score_label(p["score"])

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                flags = []
                if p["alerta_urgencia"]: flags.append("⚡")
                if p.get("gestacao"):    flags.append("🤱")
                flag_str = " ".join(flags)
                st.markdown(f"**{i+1}.** {p['endereco']}  \n"
                            f"{sc} · 🚶 {p['distancia']} {flag_str}")
            with col2:
                if not s:
                    if st.button("✔ Visitar", key=f"map_done_{p['id']}", use_container_width=True):
                        set_status(p["id"], "done")
            with col3:
                if not s and is_padrao(p):
                    if st.button("💬 WPP OK", key=f"map_wpp_{p['id']}", use_container_width=True):
                        set_status(p["id"], "wpp_ok")
                elif s:
                    if st.button("↩ Reabrir", key=f"map_reopen_{p['id']}", use_container_width=True):
                        clear_status(p["id"])

            # Expandable detail
            with st.expander(f"Ver detalhes · {p['code']}"):
                render_patient_detail(p)

    st.divider()

    # Legend
    st.markdown("""
    **Legenda:**
    🔴 Crítico/Urgência &nbsp;|&nbsp;
    🟡 Alto &nbsp;|&nbsp;
    🟢 Padrão &nbsp;|&nbsp;
    🟩 WPP OK &nbsp;|&nbsp;
    ⚫ Visitado &nbsp;|&nbsp;
    🔵 Você (ACS) &nbsp;|&nbsp;
    **A** = tem áudio gravado
    """)
