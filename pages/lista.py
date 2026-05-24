import streamlit as st
from data.patients import PATIENTS
from utils.helpers import (
    is_padrao, get_status, set_status, clear_status,
    active_patients, done_patients, route_by_distance, wpp_link,
)
from components.patient_card import render_patient_card, render_patient_detail


def render_lista():
    st.markdown("### 📋 Lista do Dia")

    active = active_patients(PATIENTS)
    done = done_patients(PATIENTS)
    total = len(PATIENTS)
    pct = int(len(done) / total * 100) if total else 0

    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(pct / 100, text=f"Progresso: {len(done)}/{total} visitas")
    with col2:
        st.metric("Concluídas", f"{pct}%")

    c1, c2, c3 = st.columns(3)
    with c1:
        n_urg = sum(1 for p in PATIENTS if p["alerta_urgencia"])
        st.metric("⚡ Urgências", n_urg)
    with c2:
        n_wpp_ok = sum(1 for p in PATIENTS if get_status(p["id"]) == "wpp_ok")
        st.metric("💬 WPP OK", n_wpp_ok)
    with c3:
        n_done = sum(1 for p in PATIENTS if get_status(p["id"]) == "done")
        st.metric("✔ Visitados", n_done)

    st.divider()

    padrao_active = [p for p in PATIENTS if is_padrao(p) and not get_status(p["id"])]
    if padrao_active:
        with st.expander(f"💬 {len(padrao_active)} pacientes PADRÃO — Enviar WhatsApp em massa"):
            _render_wpp_section(padrao_active)

    st.divider()

    route = route_by_distance(active)

    if route:
        st.markdown("**📋 Pendentes**")
        for i, p in enumerate(route):
            if get_status(p["id"]) in ("done", "wpp_ok"):
                continue
            clicked = render_patient_card(p, ordem=i + 1)
            if clicked:
                key = f"detail_open_{p['id']}"
                st.session_state[key] = not st.session_state.get(key, False)
            if st.session_state.get(f"detail_open_{p['id']}", False):
                with st.container():
                    render_patient_detail(p)
                    st.divider()

    if done:
        st.markdown(f"**✔ Concluídos ({len(done)})**")
        for p in done:
            render_patient_card(p)


def _render_wpp_section(padrao_active):
    default_msg = (
        "Olá! Aqui é a ACS Maria da ESF Cascadura III. "
        "Você está bem de saúde? Precisamos confirmar se vai precisar de visita esta semana. "
        "Responda SIM (estou bem) ou NÃO (preciso de visita). Obrigada! 🏥"
    )
    msg = st.text_area("Mensagem WhatsApp", value=default_msg, height=100)

    st.markdown("**Pacientes selecionados:**")
    selected = []
    for p in padrao_active:
        if st.checkbox(f"{p['code']} · {p['faixa']} · {p['endereco']}", value=True,
                       key=f"wpp_check_{p['id']}"):
            selected.append(p)

    if selected:
        if st.button(f"📲 Marcar {len(selected)} como 'WPP enviado'", type="primary", use_container_width=True):
            for p in selected:
                st.session_state.statuses[p["id"]] = "wpp_sent"
            st.success(f"{len(selected)} pacientes marcados. Abra cada um para registrar a resposta SIM/NÃO.")
            st.rerun()

        st.caption("💡 Após enviar manualmente no WhatsApp, abra o paciente na lista para registrar a devolutiva.")
        st.caption("⏰ Recomendado: enviar 1–2 dias antes para garantir resposta a tempo.")
