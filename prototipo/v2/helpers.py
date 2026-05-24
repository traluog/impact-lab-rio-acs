import math
import streamlit as st
from data.patients import ACS_POS


# ── score helpers ─────────────────────────────────────────────────────────────

def score_color(s):
    if s >= 80: return "#c0392b"
    if s >= 55: return "#b45309"
    return "#166534"

def score_bg(s):
    if s >= 80: return "#fdf2f1"
    if s >= 55: return "#fefbf0"
    return "#f0faf4"

def score_border(s):
    if s >= 80: return "#e8b4b0"
    if s >= 55: return "#f0d090"
    return "#a8dbb8"

def score_label(s):
    if s >= 80: return "CRÍTICO"
    if s >= 55: return "ALTO"
    return "PADRÃO"

def score_badge_class(s):
    if s >= 80: return "badge-critico"
    if s >= 55: return "badge-alto"
    return "badge-padrao"

def is_padrao(p):
    return p["score"] < 55


# ── routing ───────────────────────────────────────────────────────────────────

def dist_2d(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)

def route_by_distance(patients):
    """Nearest-neighbour from ACS position → minimises total SVG distance."""
    if not patients:
        return []
    remaining = list(patients)
    route = []
    cur = ACS_POS
    while remaining:
        best = min(remaining, key=lambda p: dist_2d(cur, p["pos"]))
        route.append(best)
        cur = best["pos"]
        remaining = [p for p in remaining if p["id"] != best["id"]]
    return route

def route_by_priority(patients):
    """Sort by urgency flag first, then descending score."""
    return sorted(patients, key=lambda p: (-int(p["alerta_urgencia"]), -p["score"]))

def total_route_dist(route):
    if not route:
        return 0
    d = dist_2d(ACS_POS, route[0]["pos"])
    for i in range(1, len(route)):
        d += dist_2d(route[i-1]["pos"], route[i]["pos"])
    return d

def meters_label(svg_dist):
    return f"{round(svg_dist * 3.5)}m"


# ── status helpers ────────────────────────────────────────────────────────────

def get_status(pid):
    return st.session_state.statuses.get(pid)

def set_status(pid, value):
    st.session_state.statuses[pid] = value
    st.rerun()

def clear_status(pid):
    st.session_state.statuses.pop(pid, None)
    st.rerun()

def active_patients(patients):
    return [p for p in patients if get_status(p["id"]) not in ("done", "wpp_ok")]

def done_patients(patients):
    return [p for p in patients if get_status(p["id"]) in ("done", "wpp_ok")]


# ── forms helpers ─────────────────────────────────────────────────────────────

def get_forms_done(pid, ficha_id):
    """Return list of answered question ids for a given patient + ficha."""
    return st.session_state.forms_done.get(pid, {}).get(ficha_id, [])

def mark_form_done(pid, ficha_id, qid):
    fd = st.session_state.forms_done.setdefault(pid, {})
    answered = fd.setdefault(ficha_id, [])
    if qid not in answered:
        answered.append(qid)

def unmark_form_done(pid, ficha_id, qid):
    try:
        st.session_state.forms_done[pid][ficha_id].remove(qid)
    except (KeyError, ValueError):
        pass

def ficha_progress(pid, ficha_id, ficha_def):
    all_qids = [q["id"] for s in ficha_def["sections"] for q in s["questions"]]
    done = get_forms_done(pid, ficha_id)
    if not all_qids:
        return 0, 0
    return len([q for q in done if q in all_qids]), len(all_qids)


# ── audio helpers ─────────────────────────────────────────────────────────────

def get_audios(pid, ficha_id):
    key = f"{pid}_{ficha_id}"
    return st.session_state.audios.get(key, [])

def add_audio(pid, ficha_id, label, duration_secs, question_text=""):
    key = f"{pid}_{ficha_id}"
    audios = st.session_state.audios.setdefault(key, [])
    import time
    audios.append({
        "id": int(time.time() * 1000),
        "label": label,
        "duration": duration_secs,
        "question": question_text,
        "transcript": None,
    })

def set_transcript(pid, ficha_id, audio_id, text):
    key = f"{pid}_{ficha_id}"
    for a in st.session_state.audios.get(key, []):
        if a["id"] == audio_id:
            a["transcript"] = text
            break

def delete_audio(pid, ficha_id, audio_id):
    key = f"{pid}_{ficha_id}"
    st.session_state.audios[key] = [
        a for a in st.session_state.audios.get(key, [])
        if a["id"] != audio_id
    ]

def total_audios_for_patient(pid, fichas):
    return sum(len(get_audios(pid, fid)) for fid in fichas)


# ── WhatsApp link builder ─────────────────────────────────────────────────────

def wpp_link(tel, msg=""):
    import urllib.parse
    encoded = urllib.parse.quote(msg)
    return f"https://wa.me/{tel}?text={encoded}"


# ── SVG map builder ───────────────────────────────────────────────────────────

def build_map_svg(patients, statuses, route, audios, route_color="#1d4ed8"):
    """Returns an SVG string for the territory map."""
    W, H = 400, 380

    def pin_color(p):
        s = statuses.get(p["id"])
        if s == "wpp_ok": return "#25D366"
        if s == "done":   return "#9c948c"
        if p["alerta_urgencia"] or p["score"] >= 80: return "#c0392b"
        if p["score"] >= 55: return "#b45309"
        return "#166534"

    lines = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block;background:#e8f4f0">',
        f'<defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">',
        f'<path d="M 40 0 L 0 0 0 40" fill="none" stroke="#c8e0da" stroke-width="0.5"/></pattern></defs>',
        f'<rect width="{W}" height="{H}" fill="url(#grid)"/>',
        f'<path d="M 60,50 Q 200,30 340,60 L 360,190 Q 375,305 200,365 Q 80,355 40,235 Z" fill="#d4ecec" stroke="#a8d8d0" stroke-width="1.5" fill-opacity="0.5"/>',
    ]

    # Grid lines
    for d in ["M 80,90 L 320,90", "M 60,185 L 355,185", "M 150,45 L 120,370", "M 255,38 L 275,375"]:
        lines.append(f'<path d="{d}" stroke="#b8ccc8" stroke-width="0.7" stroke-dasharray="4,3"/>')

    # Route lines
    if len(route) > 0:
        ax, ay = ACS_POS["x"], ACS_POS["y"]
        x0, y0 = route[0]["pos"]["x"], route[0]["pos"]["y"]
        lines.append(f'<line x1="{ax}" y1="{ay}" x2="{x0}" y2="{y0}" stroke="{route_color}" stroke-width="2" stroke-dasharray="5,3" opacity="0.55"/>')
        for i in range(len(route) - 1):
            x1, y1 = route[i]["pos"]["x"], route[i]["pos"]["y"]
            x2, y2 = route[i+1]["pos"]["x"], route[i+1]["pos"]["y"]
            lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{route_color}" stroke-width="2" stroke-dasharray="5,3" opacity="0.55"/>')

    # ACS position
    ax, ay = ACS_POS["x"], ACS_POS["y"]
    lines.append(f'<circle cx="{ax}" cy="{ay}" r="18" fill="#eff6ff" stroke="#1d4ed8" stroke-width="2" opacity="0.3"/>')
    lines.append(f'<circle cx="{ax}" cy="{ay}" r="6" fill="#1d4ed8" stroke="#fff" stroke-width="2"/>')
    lines.append(f'<text x="{ax}" y="{ay+17}" text-anchor="middle" font-size="8" fill="#1d4ed8" font-weight="700">Você</text>')

    # Patient pins
    for p in patients:
        pc = pin_color(p)
        inactive = statuses.get(p["id"]) in ("done", "wpp_ok")
        ri = next((i for i, r in enumerate(route) if r["id"] == p["id"]), -1)
        s = statuses.get(p["id"])
        label = ("W" if s == "wpp_ok" else "v") if inactive else (str(ri + 1) if ri >= 0 else "·")
        sz = 16 if (p["alerta_urgencia"] and not inactive) else 13
        px, py = p["pos"]["x"], p["pos"]["y"]
        op = "0.55" if inactive else "1"
        has_audio = total_audios_for_patient(p["id"], p["fichas"]) > 0

        if p["alerta_urgencia"] and not inactive:
            lines.append(f'<circle cx="{px}" cy="{py}" r="{sz+5}" fill="#c0392b" opacity="0.13"/>')

        lines.append(f'<circle cx="{px}" cy="{py}" r="{sz}" fill="{pc}" stroke="#fff" stroke-width="2" opacity="{op}"/>')
        lines.append(f'<text x="{px}" y="{py+4}" text-anchor="middle" font-size="8" fill="#fff" font-weight="800">{label}</text>')

        if has_audio:
            lines.append(f'<circle cx="{px+sz-1}" cy="{py-sz+1}" r="4" fill="#1d4ed8" stroke="#fff" stroke-width="1.5"/>')
            lines.append(f'<text x="{px+sz-1}" y="{py-sz+4}" text-anchor="middle" font-size="6" fill="#fff">A</text>')

    lines.append('</svg>')
    return "\n".join(lines)
