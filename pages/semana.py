import streamlit as st
from data.patients import PATIENTS, WEEK_DAYS
from utils.helpers import is_padrao, get_status, set_status, score_label
from components.patient_card import render_patient_detail


def render_semana():
    st.markdown("### 📅 Agenda Semanal")

    st.info(
        "⏰ **Dica:** Envie o WhatsApp com **1–2 dias de antecedência**. "
        "Contato no mesmo dia pode não ser respondido a tempo."
    )

    day_idx = st.selectbox(
        "Selecionar dia",
        options=range(len(WEEK_DAYS)),
        format_func=lambda i: WEEK_DAYS[i] + (" (hoje)" if i == 0 else ""),
        key="semana_day",
    )

    day_patients = [p for p in PATIENTS if p["week_day"] == day_idx]

    if not day_patients:
        st.caption("Nenhuma visita programada para este dia.")
    else:
        for p in day_patients:
            _render_week_card(p, is_today=(day_idx == 0))

    st.divider()

    upcoming_padrao = [
        p for p in PATIENTS
        if p["week_day"] > 0
        and is_padrao(p)
        and not get_status(p["id"])
        and p["id"] not in st.session_state.wpp_sent_week
    ]
    if upcoming_padrao:
        st.markdown("**💬 WPP em massa — semana toda**")
        st.caption(f"{len(upcoming_padrao)} pacientes PADRÃO com visita futura ainda não contactados")
        if st.button(f"📲 Enviar WPP para todos os {len(upcoming_padrao)} pacientes PADRÃO da semana",
                     use_container_width=True, type="primary"):
            for p in upcoming_padrao:
                st.session_state.wpp_sent_week.add(p["id"])
            st.success(f"✅ {len(upcoming_padrao)} pacientes marcados como 'WPP enviado'.")
            st.rerun()


def _render_week_card(p, is_today=False):
    s = get_status(p["id"])
    wpp_sent = p["id"] in st.session_state.wpp_sent_week
    sc = score_label(p["score"])

    flags = []
    if p.get("gestacao"):      flags.append("🤱 Gestante")
    if p.get("hipertenso"):    flags.append("HAS")
    if p.get("diabetico"):     flags.append("DM")
    if p.get("alerta_urgencia"): flags.append("⚡ Urgência")
    if s == "done":            flags.append("✔ Visitado")
    if s == "wpp_ok":          flags.append("💬 WPP OK")
    if wpp_sent and not s:     flags.append("📲 WPP enviado")
    flags_str = " · ".join(flags)

    with st.container():
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(
                f"**{p['code']}** · {sc} · Score {p['score']}"
                f"  \n📍 {p['endereco']} · 🚶 {p['distancia']}"
                f"  \n{flags_str}"
            )
        with c2:
            st.metric("Score", p["score"])

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            if is_padrao(p) and not is_today and not wpp_sent and not s:
                days_ahead = p["week_day"]
                if st.button(f"📲 WPP ({days_ahead}d antes)", key=f"wk_wpp_{p['id']}", use_container_width=True):
                    st.session_state.wpp_sent_week.add(p["id"])
                    st.rerun()
        with bc2:
            if wpp_sent and not s:
                if st.button("✅ SIM", key=f"wk_sim_{p['id']}", use_container_width=True, type="primary"):
                    set_status(p["id"], "wpp_ok")
        with bc3:
            if wpp_sent and not s:
                if st.button("❌ NÃO", key=f"wk_nao_{p['id']}", use_container_width=True):
                    st.session_state.statuses.pop(p["id"], None)
                    st.rerun()
            elif not is_padrao(p) and not s:
                st.warning("Visita obrigatória")

        if s or wpp_sent:
            with st.expander(f"Ver detalhes · {p['code']}"):
                render_patient_detail(p)

        st.divider()
