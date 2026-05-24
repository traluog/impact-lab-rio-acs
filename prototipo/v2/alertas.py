import streamlit as st
from data.patients import PATIENTS


def render_alertas():
    st.markdown("### 🚨 Alertas Ativos")
    st.caption("Situações que exigem ação antes de sair a campo")

    alert_patients = [p for p in PATIENTS if p["alerta_urgencia"]]

    if not alert_patients:
        st.success("Nenhum alerta ativo no momento. ✅")
        return

    for p in alert_patients:
        with st.container():
            st.markdown(f"""
            <div class="alert-box">
                <div style="font-weight:800;font-size:14px;color:#c0392b;margin-bottom:6px">
                    ⚡ Paciente com Urgência sem Visita Prévia
                </div>
                <div style="font-size:12px;color:#6b6560;line-height:1.7">
                    <strong>{p['code']}</strong> · deu entrada em urgência/emergência em
                    <strong>{p['data_ultimo_evento'] if 'data_ultimo_evento' in p else '03/05/2025'}</strong>.<br>
                    Última visita do ACS: <strong>{p['dias_sem_visita']} dias antes</strong> — falha preventiva detectada.
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                notif_key = f"notif_sent_{p['id']}"
                if st.session_state.get(notif_key):
                    st.success("✔ Equipe clínica notificada")
                else:
                    if st.button("📲 Notificar Equipe Clínica", key=f"notif_{p['id']}",
                                 use_container_width=True, type="primary"):
                        st.session_state[notif_key] = True
                        st.rerun()
            with c2:
                st.info("📍 Prioridade #1 na lista de hoje")

    st.divider()

    # Chronic gap
    from data.patients import PATIENTS
    from utils.helpers import get_status
    cronicos_sem_visita = [
        p for p in PATIENTS
        if (p.get("hipertenso") or p.get("diabetico"))
        and p["dias_sem_visita"] > 30
        and not get_status(p["id"])
    ]

    if cronicos_sem_visita:
        st.markdown(f"""
        <div class="warn-box">
            <div style="font-weight:800;font-size:14px;color:#b45309;margin-bottom:6px">
                📉 Crônicos com Lacuna de Cuidado ({len(cronicos_sem_visita)} pacientes)
            </div>
            <div style="font-size:12px;color:#6b6560;line-height:1.7">
                Hipertensos e diabéticos sem visita há mais de 30 dias.
                Protocolo mínimo: 1 visita/mês.
            </div>
        </div>
        """, unsafe_allow_html=True)

        for p in cronicos_sem_visita:
            conds = []
            if p.get("hipertenso"): conds.append("HAS")
            if p.get("diabetico"):  conds.append("DM")
            st.markdown(
                f"- `{p['code']}` · {' + '.join(conds)} · "
                f"**{p['dias_sem_visita']} dias** sem visita · {p['endereco']}"
            )

        report_key = "cronicos_report_sent"
        if st.session_state.get(report_key):
            st.success("✔ Relatório de lacuna de cuidado enviado à coordenação da UBS.")
        else:
            if st.button("📊 Enviar Relatório à Coordenação", use_container_width=True):
                st.session_state[report_key] = True
                st.rerun()
