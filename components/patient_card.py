"""
Shared patient UI components: card, detail expander, ficha viewer, audio recorder.
"""
import streamlit as st
from utils.helpers import (
    score_color, score_bg, score_label, score_badge_class, is_padrao,
    get_status, set_status, clear_status,
    get_forms_done, mark_form_done, unmark_form_done, ficha_progress,
    get_audios, add_audio, set_transcript, delete_audio, total_audios_for_patient,
    wpp_link,
)
from data.fichas import FICHAS_DEF


# ── badge helpers ─────────────────────────────────────────────────────────────

def badge(text, cls=""):
    return f'<span class="badge-{cls or "info"}">{text}</span>'


def condition_badges(p):
    parts = []
    if p.get("gestacao"):     parts.append(badge("🤱 Gestante", "purple"))
    if p.get("hipertenso"):   parts.append(badge("🩺 HAS", "critico"))
    if p.get("diabetico"):    parts.append(badge("💉 DM", "warn"))
    if p.get("vulneravel"):   parts.append(badge("🏚️ Vulnerável", "purple"))
    if p.get("alerta_urgencia"): parts.append(badge("⚡ Urgência", "critico"))
    return " ".join(parts) if parts else badge("Sem condição crônica")


# ── patient card ──────────────────────────────────────────────────────────────

def render_patient_card(p, ordem=None):
    """
    Renders a compact patient card. Returns True if the card was clicked
    (Streamlit button inside the card).
    """
    s = get_status(p["id"])
    inactive = s in ("done", "wpp_ok")
    sc = score_color(p["score"])
    fichas = p.get("fichas", [])
    n_audios = total_audios_for_patient(p["id"], fichas)

    status_html = ""
    if s == "wpp_ok":     status_html = badge("💬 WPP OK", "wpp")
    elif s == "done":     status_html = badge("✔ Visitado", "done")
    elif s == "wpp_sent": status_html = badge("📲 WPP enviado", "info")

    ord_label = str(ordem) if ordem is not None else "·"

    # Pre-build conditional tags outside the f-string.
    # A conditional like {"..." if cond else ""} inside the f-string produces a
    # whitespace-only line when False, which CommonMark treats as a blank line and
    # terminates the HTML block — causing everything after to render as raw text.
    audio_tag = f"<span style='font-size:10px;color:#1d4ed8;font-weight:700'>A:{n_audios}</span>" if n_audios > 0 else ""
    card_class = "padrao" if p["score"] < 55 else "alto" if p["score"] < 80 else "critico"
    done_class = "done" if inactive else ""
    dsv_color = "#c0392b" if p["dias_sem_visita"] > 30 else "#9c948c"

    st.markdown(f"""
<div class="patient-card {card_class} {done_class}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div style="display:flex;gap:10px;align-items:flex-start">
      <div style="width:28px;height:28px;border-radius:50%;background:{score_bg(p['score'])};border:2px solid {sc};display:flex;align-items:center;justify-content:center;color:{sc};font-weight:800;font-size:12px;flex-shrink:0">{ord_label}</div>
      <div>
        <div style="font-family:monospace;font-size:11px;color:#6b6560;margin-bottom:3px">{p['code']}</div>
        <div style="display:flex;gap:4px;flex-wrap:wrap">{condition_badges(p)} {status_html}</div>
      </div>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <div style="font-size:20px;font-weight:800;color:{sc};line-height:1">{p['score']}</div>
      <div style="font-size:9px;color:{sc};font-weight:700">{score_label(p['score'])}</div>
      <div style="font-size:10px;color:{dsv_color};margin-top:2px">{p['dias_sem_visita']}d sem visita</div>
    </div>
  </div>
  <div style="margin-top:7px;padding-top:6px;border-top:1px solid #e2ddd6;display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:11px;color:#6b6560">📍 {p['endereco']}</span>
    <div style="display:flex;gap:8px;align-items:center"><span style="font-size:10px;color:#1d4ed8">F:{len(fichas)}</span>{audio_tag}<span style="font-size:11px;color:#1d4ed8;font-weight:600">🚶 {p['distancia']}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

    return st.button("Abrir detalhes", key=f"open_{p['id']}", use_container_width=True)


# ── patient detail ────────────────────────────────────────────────────────────

def render_patient_detail(p):
    """Renders full patient detail inside a st.expander or container."""
    s = get_status(p["id"])
    fichas = p.get("fichas", [])

    tab_labels = ["ℹ️ Info", "📋 Fichas", "🎙️ Áudio"]
    tabs = st.tabs(tab_labels)

    # ── tab Info ──────────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown(condition_badges(p), unsafe_allow_html=True)
        st.markdown("<hr class='thin'>", unsafe_allow_html=True)

        for m in p["motivos"]:
            st.markdown(f"<div style='font-size:12px;color:#1a1612;padding:2px 0'>● {m}</div>", unsafe_allow_html=True)

        st.markdown("<hr class='thin'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#f9f8f5;border-radius:7px;padding:8px 11px;
             display:flex;justify-content:space-between;margin-bottom:10px">
            <span style="font-size:12px;color:#1a1612">📍 {p['endereco']}</span>
            <span style="font-size:11px;color:#1d4ed8;font-weight:600">🚶 {p['distancia']}</span>
        </div>
        """, unsafe_allow_html=True)

        if is_padrao(p) and not s:
            wpp_url = wpp_link(p["tel"], "Olá! Aqui é a ACS Maria da ESF Cascadura III. Você está bem de saúde? Responda SIM ou NÃO. Obrigada! 🏥")
            st.link_button("💬 Enviar WhatsApp individual", wpp_url, use_container_width=True)

        if is_padrao(p) and s == "wpp_sent":
            st.info("📲 WPP enviado — Registrar resposta do paciente:")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ SIM — Dispensar visita", key=f"sim_{p['id']}", use_container_width=True, type="primary"):
                    set_status(p["id"], "wpp_ok")
            with c2:
                if st.button("❌ NÃO — Visitar", key=f"nao_{p['id']}", use_container_width=True):
                    clear_status(p["id"])

        if s != "wpp_ok":
            label = "✔ Visita já registrada" if s == "done" else "✔ Marcar como visitado"
            if st.button(label, key=f"visit_{p['id']}", use_container_width=True, type="primary"):
                set_status(p["id"], "done")

        if s:
            if st.button("↩ Reabrir atendimento", key=f"reopen_{p['id']}", use_container_width=True):
                clear_status(p["id"])

    # ── tab Fichas ────────────────────────────────────────────────────────────
    with tabs[1]:
        if not fichas:
            st.caption("Nenhuma ficha associada.")
        else:
            ficha_sel = st.selectbox(
                "Selecionar ficha",
                options=fichas,
                format_func=lambda fid: f"{FICHAS_DEF[fid]['icon']} {FICHAS_DEF[fid]['label']}",
                key=f"ficha_sel_{p['id']}",
            )
            fd = FICHAS_DEF.get(ficha_sel)
            if fd:
                done_qs, total_qs = ficha_progress(p["id"], ficha_sel, fd)
                pct = int(done_qs / total_qs * 100) if total_qs else 0
                st.progress(pct / 100, text=f"{done_qs}/{total_qs} perguntas respondidas")

                for section in fd["sections"]:
                    st.markdown(f"<div class='section-title'>{section['title']}</div>", unsafe_allow_html=True)
                    for q in section["questions"]:
                        answered = q["id"] in get_forms_done(p["id"], ficha_sel)
                        prefix = ""
                        if q.get("key"):   prefix += "🔑 "
                        if q.get("alert"): prefix += "⚠️ "
                        label_txt = f"{prefix}{q['text']}"
                        val = st.checkbox(label_txt, value=answered, key=f"fq_{p['id']}_{ficha_sel}_{q['id']}")
                        if val and not answered:
                            mark_form_done(p["id"], ficha_sel, q["id"])
                        elif not val and answered:
                            unmark_form_done(p["id"], ficha_sel, q["id"])

                if pct == 100:
                    st.success("✅ Todas as perguntas desta ficha respondidas!")

    # ── tab Áudio ─────────────────────────────────────────────────────────────
    with tabs[2]:
        render_audio_recorder(p)


# ── audio recorder ────────────────────────────────────────────────────────────

SAMPLE_TRANSCRIPTS = {
    "pa":         "Pressão de 14 por 9 medida ontem em casa. Monitorando com aparelho próprio.",
    "med":        "Tomando Losartana 50mg pela manhã. Não faltou doses nesta semana.",
    "glicemia":   "Glicemia em jejum anteontem: 148 mg/dL.",
    "tosse":      "Tosse produtiva pela manhã. Melhora em relação à semana passada.",
    "mexeu":      "Bebê mexendo bem nos últimos dias. Sem sangramento ou dor.",
    "aleitamento":"Amamentação exclusiva, a cada 2–3 horas, sem dificuldades.",
    "contatos":   "Três pessoas na casa: marido e dois filhos. Nenhum com sintomas.",
    "pes":        "Sem feridas visíveis. Formigamento leve ocasional.",
    "pa_ges":     "PA 12 por 8. Dentro do normal para a gestação atual.",
    "semanas":    "26 semanas. Pré-natal em dia, última consulta há 2 semanas.",
}


def render_audio_recorder(p):
    fichas = p.get("fichas", [])
    if not fichas:
        st.caption("Nenhuma ficha associada para gravar.")
        return

    ficha_sel = st.selectbox(
        "Ficha para este áudio",
        options=fichas,
        format_func=lambda fid: f"{FICHAS_DEF[fid]['icon']} {FICHAS_DEF[fid]['label']}",
        key=f"audio_ficha_{p['id']}",
    )
    fd = FICHAS_DEF.get(ficha_sel, {})
    all_qs = [q for s in fd.get("sections", []) for q in s["questions"]]

    if all_qs:
        q_labels = [f"{'⚠️ ' if q.get('alert') else ''}{'🔑 ' if q.get('key') else ''}{q['text']}" for q in all_qs]
        q_idx = st.selectbox("Pergunta que será respondida", range(len(all_qs)),
                             format_func=lambda i: q_labels[i],
                             key=f"audio_q_{p['id']}_{ficha_sel}")
        selected_q = all_qs[q_idx]
        st.markdown(f"""
        <div class="info-box" style="font-size:12px;font-style:italic;margin-bottom:8px">
            Pergunta ativa: <strong>{selected_q['text']}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        selected_q = None

    st.markdown("---")
    st.caption("🎙️ Simulação de gravação (produção: usar `streamlit-webrtc` ou upload de arquivo)")

    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Duração (segundos)", min_value=1, max_value=300, value=30,
                                   key=f"dur_{p['id']}_{ficha_sel}")
    with col2:
        label_input = st.text_input("Rótulo", value="Nota de visita",
                                    key=f"lbl_{p['id']}_{ficha_sel}")

    if st.button("💾 Salvar áudio simulado", key=f"save_audio_{p['id']}_{ficha_sel}",
                 use_container_width=True):
        q_text = selected_q["text"] if selected_q else ""
        add_audio(p["id"], ficha_sel, label_input, duration, q_text)
        st.success("Áudio salvo!")
        st.rerun()

    audios = get_audios(p["id"], ficha_sel)
    if audios:
        st.markdown("<div class='section-title'>Gravações salvas</div>", unsafe_allow_html=True)
        for a in audios:
            mins, secs = divmod(a["duration"], 60)
            time_str = f"{mins:02d}:{secs:02d}"
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**{a['label']}** · {time_str}")
                    if a.get("question"):
                        st.caption(a["question"][:60] + "...")
                    if a.get("transcript"):
                        st.markdown(f"""
                        <div class="transcript-box">
                            <strong style="font-size:9px;color:#166534">TRANSCRIÇÃO</strong><br>
                            {a['transcript']}
                        </div>
                        """, unsafe_allow_html=True)
                with c2:
                    if not a.get("transcript"):
                        if st.button("✦ Transcrever", key=f"tr_{a['id']}", use_container_width=True):
                            qid = selected_q["id"] if selected_q else ""
                            txt = SAMPLE_TRANSCRIPTS.get(qid, "[Transcrição automática — revisar com ACS]")
                            set_transcript(p["id"], ficha_sel, a["id"], txt)
                            st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_{a['id']}", use_container_width=True):
                        delete_audio(p["id"], ficha_sel, a["id"])
                        st.rerun()
                st.divider()
