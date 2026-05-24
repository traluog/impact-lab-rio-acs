import { useState, useEffect } from "react";

// ─────────────────────────────────────────────────────────────────────────────
// DESIGN TOKENS — utilitarian field-tool aesthetic, high contrast, mobile-first
// ─────────────────────────────────────────────────────────────────────────────
const T = {
  bg: "#f5f4f0",
  surface: "#ffffff",
  card: "#ffffff",
  cardAlt: "#f9f8f5",
  border: "#e2ddd6",
  borderStrong: "#c8c0b4",
  ink: "#1a1612",
  sub: "#6b6560",
  muted: "#9c948c",
  danger: "#c0392b",
  dangerBg: "#fdf2f1",
  dangerBorder: "#e8b4b0",
  warn: "#b45309",
  warnBg: "#fefbf0",
  warnBorder: "#f0d090",
  ok: "#166534",
  okBg: "#f0faf4",
  okBorder: "#a8dbb8",
  accent: "#1d4ed8",
  accentBg: "#eff6ff",
  accentBorder: "#bfdbfe",
  tag: "#374151",
};

// ─────────────────────────────────────────────────────────────────────────────
// MOCK DATA — representing the output of the 4-dataset join + score engine
// ─────────────────────────────────────────────────────────────────────────────
const TODAY = "Seg, 26 Mai 2025";
const ACS_NAME = "Maria dos Santos";
const ACS_TEAM = "ESF Cascadura III";
const ACS_TERRITORY = "Micro-área 07 · Cascadura";

const PATIENTS = [
  {
    id: "p001", code: "93449...", ordem: 1, score: 92,
    faixa: "66+", sexo: "F", raca: "Branca",
    hipertenso: true, diabetico: true, gestacao: false, vulneravel: false,
    dias_sem_visita: 47,
    ultimo_evento: "urgencia-emergencia-ou-internacao",
    data_ultimo_evento: "2025-05-03",
    motivos: ["66+ anos", "Hipertenso + Diabético", "47 dias sem visita", "Urgência em mai/25"],
    alerta_urgencia: true,
    nunca_visitado: false,
    distancia: "380m",
    endereco_hint: "Rua das Camélias, próx. nº 42",
  },
  {
    id: "p002", code: "70380...", ordem: 2, score: 78,
    faixa: "6-18", sexo: "F", raca: "Parda",
    hipertenso: false, diabetico: false, gestacao: false, vulneravel: true,
    dias_sem_visita: 63,
    ultimo_evento: "agendamento",
    data_ultimo_evento: "2025-03-23",
    motivos: ["Vulnerabilidade social", "63 dias sem visita", "Adolescente em território de risco"],
    alerta_urgencia: false,
    nunca_visitado: false,
    distancia: "520m",
    endereco_hint: "Beco do Cedro, nº 11",
  },
  {
    id: "p003", code: "5a3f1...", ordem: 3, score: 71,
    faixa: "19-45", sexo: "F", raca: "Parda",
    hipertenso: false, diabetico: false, gestacao: true, vulneravel: true,
    dias_sem_visita: 28,
    ultimo_evento: "agendamento",
    data_ultimo_evento: "2025-04-28",
    motivos: ["Gestante", "Vulnerabilidade social", "28 dias sem visita"],
    alerta_urgencia: false,
    nunca_visitado: false,
    distancia: "210m",
    endereco_hint: "Trav. Esperança, nº 7A",
  },
  {
    id: "p004", code: "867dd...", ordem: 4, score: 55,
    faixa: "45-65", sexo: "F", raca: "Parda",
    hipertenso: true, diabetico: false, gestacao: false, vulneravel: false,
    dias_sem_visita: 38,
    ultimo_evento: "agendamento",
    data_ultimo_evento: "2025-04-15",
    motivos: ["Hipertensa", "38 dias sem visita"],
    alerta_urgencia: false,
    nunca_visitado: false,
    distancia: "670m",
    endereco_hint: "R. Lins de Vasconcelos, nº 198",
  },
  {
    id: "p005", code: "c72ab...", ordem: 5, score: 48,
    faixa: "66+", sexo: "M", raca: "Preta",
    hipertenso: true, diabetico: false, gestacao: false, vulneravel: false,
    dias_sem_visita: 22,
    ultimo_evento: "agendamento",
    data_ultimo_evento: "2025-05-04",
    motivos: ["66+ anos", "Hipertenso", "22 dias sem visita"],
    alerta_urgencia: false,
    nunca_visitado: false,
    distancia: "290m",
    endereco_hint: "R. Barão de Cotegipe, nº 34",
  },
  {
    id: "p006", code: "bb019...", ordem: 6, score: 35,
    faixa: "0-6", sexo: "M", raca: "Parda",
    hipertenso: false, diabetico: false, gestacao: false, vulneravel: false,
    dias_sem_visita: 18,
    ultimo_evento: "agendamento",
    data_ultimo_evento: "2025-05-08",
    motivos: ["Criança 0-6 anos", "18 dias sem visita"],
    alerta_urgencia: false,
    nunca_visitado: false,
    distancia: "450m",
    endereco_hint: "R. das Orquídeas, nº 3",
  },
  {
    id: "p007", code: "f3d88...", ordem: 7, score: 25,
    faixa: "19-45", sexo: "M", raca: "Branca",
    hipertenso: false, diabetico: false, gestacao: false, vulneravel: false,
    dias_sem_visita: 11,
    ultimo_evento: "agendamento",
    data_ultimo_evento: "2025-05-15",
    motivos: ["Sem condição crônica", "11 dias sem visita"],
    alerta_urgencia: false,
    nunca_visitado: false,
    distancia: "180m",
    endereco_hint: "Pça. General Osório, nº 21",
  },
];

const ALERTAS_URGENCIA = PATIENTS.filter(p => p.alerta_urgencia);

const RESUMO = {
  total_microarea: 127,
  com_cronicas: 38,
  gestantes: 4,
  sem_visita_30d: 31,
  urgencias_sem_visita: 1,
  visitas_hoje: 7,
};

// ─────────────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────────────
function scoreColor(s) {
  if (s >= 80) return T.danger;
  if (s >= 55) return T.warn;
  return T.ok;
}
function scoreBg(s) {
  if (s >= 80) return T.dangerBg;
  if (s >= 55) return T.warnBg;
  return T.okBg;
}
function scoreBorder(s) {
  if (s >= 80) return T.dangerBorder;
  if (s >= 55) return T.warnBorder;
  return T.okBorder;
}
function scoreLabel(s) {
  if (s >= 80) return "CRÍTICO";
  if (s >= 55) return "ALTO";
  return "PADRÃO";
}

function Tag({ children, cor = T.tag, bg = "#f3f4f6" }) {
  return (
    <span style={{
      background: bg, color: cor,
      border: `1px solid ${cor}33`,
      borderRadius: 3, padding: "1px 6px",
      fontSize: 10, fontWeight: 700, letterSpacing: 0.5,
      textTransform: "uppercase", whiteSpace: "nowrap",
    }}>{children}</span>
  );
}

function Divider() {
  return <div style={{ height: 1, background: T.border, margin: "0" }} />;
}

// ─────────────────────────────────────────────────────────────────────────────
// VIEWS
// ─────────────────────────────────────────────────────────────────────────────

function HeaderBar({ view, setView, notifs }) {
  return (
    <div style={{
      background: T.ink, color: "#fff",
      padding: "14px 18px 12px",
      position: "sticky", top: 0, zIndex: 50,
      boxShadow: "0 2px 8px #0003",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 11, color: "#94a3b8", letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 2 }}>
            ACS · {ACS_TEAM}
          </div>
          <div style={{ fontFamily: "'Georgia', serif", fontSize: 19, fontWeight: 700, letterSpacing: -0.3 }}>
            Olá, {ACS_NAME.split(" ")[0]} 👋
          </div>
          <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 1 }}>{TODAY} · {ACS_TERRITORY}</div>
        </div>
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setView("alertas")}
            style={{
              background: notifs > 0 ? T.danger : "#374151",
              border: "none", borderRadius: 8, padding: "8px 12px",
              color: "#fff", cursor: "pointer", fontSize: 18,
              position: "relative",
            }}
          >
            🔔
            {notifs > 0 && (
              <span style={{
                position: "absolute", top: -6, right: -6,
                background: "#ef4444", color: "#fff",
                borderRadius: "50%", width: 18, height: 18,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 10, fontWeight: 800, border: "2px solid #1a1612",
              }}>{notifs}</span>
            )}
          </button>
        </div>
      </div>

      {/* Nav */}
      <div style={{ display: "flex", gap: 6, marginTop: 14 }}>
        {[
          { id: "lista", label: "📋 Lista do Dia" },
          { id: "alertas", label: "🚨 Alertas" },
          { id: "painel", label: "📊 Painel" },
        ].map(n => (
          <button key={n.id} onClick={() => setView(n.id)} style={{
            background: view === n.id ? "#fff" : "transparent",
            color: view === n.id ? T.ink : "#94a3b8",
            border: `1px solid ${view === n.id ? "#fff" : "#374151"}`,
            borderRadius: 6, padding: "6px 12px",
            fontSize: 12, fontWeight: view === n.id ? 700 : 400,
            cursor: "pointer", transition: "all 0.15s",
          }}>{n.label}</button>
        ))}
      </div>
    </div>
  );
}

// ── PATIENT CARD ─────────────────────────────────────────────────────────────
function PatientCard({ p, onOpen }) {
  const sCol = scoreColor(p.score);
  const sBg = scoreBg(p.score);
  const sBorder = scoreBorder(p.score);

  return (
    <div
      onClick={() => onOpen(p)}
      style={{
        background: T.card,
        border: `1px solid ${p.alerta_urgencia ? T.dangerBorder : T.border}`,
        borderLeft: `4px solid ${sCol}`,
        borderRadius: 10,
        padding: "14px 14px 12px",
        cursor: "pointer",
        transition: "box-shadow 0.15s",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Urgency ribbon */}
      {p.alerta_urgencia && (
        <div style={{
          position: "absolute", top: 0, right: 0,
          background: T.danger, color: "#fff",
          fontSize: 9, fontWeight: 800, letterSpacing: 1,
          padding: "3px 10px", borderBottomLeftRadius: 8,
          textTransform: "uppercase",
        }}>⚡ URGÊNCIA PRÉVIA</div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        {/* Left: ordem + info */}
        <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
          <div style={{
            width: 32, height: 32, borderRadius: "50%",
            background: sBg, border: `2px solid ${sBorder}`,
            display: "flex", alignItems: "center", justifyContent: "center",
            color: sCol, fontWeight: 800, fontSize: 14, flexShrink: 0,
          }}>{p.ordem}</div>
          <div>
            <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap", marginBottom: 4 }}>
              <span style={{ fontFamily: "monospace", fontSize: 12, color: T.sub }}>{p.code}</span>
              <Tag>{p.faixa}</Tag>
              <Tag>{p.sexo === "F" ? "♀" : "♂"} {p.sexo}</Tag>
            </div>
            <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
              {p.gestacao && <Tag cor="#7c3aed" bg="#f5f3ff">🤱 Gestante</Tag>}
              {p.hipertenso && <Tag cor={T.danger} bg={T.dangerBg}>HAS</Tag>}
              {p.diabetico && <Tag cor={T.warn} bg={T.warnBg}>DM</Tag>}
              {p.vulneravel && <Tag cor="#6b21a8" bg="#faf5ff">Vulnerável</Tag>}
            </div>
          </div>
        </div>

        {/* Right: score + dias */}
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{
            fontSize: 22, fontWeight: 800, color: sCol, lineHeight: 1,
          }}>{p.score}</div>
          <div style={{ fontSize: 10, color: sCol, fontWeight: 700, letterSpacing: 0.5 }}>{scoreLabel(p.score)}</div>
          <div style={{ fontSize: 11, color: p.dias_sem_visita > 30 ? T.danger : T.muted, marginTop: 4, fontWeight: p.dias_sem_visita > 30 ? 700 : 400 }}>
            {p.dias_sem_visita}d sem visita
          </div>
        </div>
      </div>

      {/* Address hint */}
      <div style={{ marginTop: 10, paddingTop: 8, borderTop: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 12, color: T.sub }}>📍 {p.endereco_hint}</span>
        <span style={{ fontSize: 12, color: T.accent, fontWeight: 600 }}>🚶 {p.distancia}</span>
      </div>
    </div>
  );
}

// ── LISTA DO DIA ─────────────────────────────────────────────────────────────
function ListaView({ onOpen, visited, setVisited }) {
  const done = PATIENTS.filter(p => visited.includes(p.id)).length;
  const pct = Math.round((done / PATIENTS.length) * 100);

  return (
    <div>
      {/* Progress bar */}
      <div style={{ background: T.surface, padding: "14px 18px", borderBottom: `1px solid ${T.border}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
          <span style={{ fontSize: 13, color: T.sub, fontWeight: 600 }}>Progresso do dia</span>
          <span style={{ fontSize: 13, fontWeight: 700, color: T.ink }}>{done}/{PATIENTS.length} visitas</span>
        </div>
        <div style={{ background: T.border, borderRadius: 4, height: 8 }}>
          <div style={{
            background: pct === 100 ? T.ok : T.accent,
            borderRadius: 4, height: 8,
            width: `${pct}%`, transition: "width 0.4s",
          }} />
        </div>
        <div style={{ display: "flex", gap: 16, marginTop: 10 }}>
          {[
            { label: "⚡ Urgência prévia", val: ALERTAS_URGENCIA.length, cor: T.danger },
            { label: "🕐 Sem visita +30d", val: RESUMO.sem_visita_30d, cor: T.warn },
            { label: "🤱 Gestantes", val: RESUMO.gestantes, cor: "#7c3aed" },
          ].map(m => (
            <div key={m.label} style={{ flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: 16, fontWeight: 800, color: m.cor }}>{m.val}</div>
              <div style={{ fontSize: 9, color: T.muted, textTransform: "uppercase", letterSpacing: 0.5 }}>{m.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Why this list? */}
      <div style={{
        margin: "12px 18px 0",
        background: T.accentBg, border: `1px solid ${T.accentBorder}`,
        borderRadius: 8, padding: "10px 14px",
        fontSize: 12, color: T.accent, lineHeight: 1.6,
      }}>
        <strong>Como esta lista foi gerada:</strong> Cruzamento dos 4 datasets (pacientes + visitas + eventos clínicos + equipes).
        Score = risco clínico + vulnerabilidade + dias sem contato + urgências anteriores.
        Rota otimizada por proximidade geográfica.
      </div>

      {/* Cards */}
      <div style={{ padding: "12px 18px", display: "flex", flexDirection: "column", gap: 10 }}>
        {PATIENTS.map(p => (
          <div key={p.id} style={{ opacity: visited.includes(p.id) ? 0.45 : 1, transition: "opacity 0.3s", position: "relative" }}>
            {visited.includes(p.id) && (
              <div style={{
                position: "absolute", inset: 0, zIndex: 5,
                display: "flex", alignItems: "center", justifyContent: "center",
                background: "#f5f4f088", borderRadius: 10,
                fontSize: 13, fontWeight: 700, color: T.ok,
              }}>✔ Visita registrada</div>
            )}
            <PatientCard p={p} onOpen={onOpen} />
          </div>
        ))}
      </div>
    </div>
  );
}

// ── ALERTAS ──────────────────────────────────────────────────────────────────
function AlertasView() {
  const [sent, setSent] = useState([]);

  return (
    <div style={{ padding: "16px 18px" }}>
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 16, fontWeight: 800, color: T.ink, marginBottom: 4 }}>🚨 Alertas Ativos</div>
        <div style={{ fontSize: 13, color: T.sub }}>
          Situações que exigem ação imediata antes de sair a campo
        </div>
      </div>

      {/* Urgência sem visita prévia */}
      <div style={{
        background: T.dangerBg, border: `1px solid ${T.dangerBorder}`,
        borderRadius: 10, padding: 16, marginBottom: 12,
      }}>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 12 }}>
          <span style={{ fontSize: 24 }}>⚡</span>
          <div>
            <div style={{ fontWeight: 800, fontSize: 14, color: T.danger, marginBottom: 2 }}>
              Paciente com Urgência sem Visita Prévia
            </div>
            <div style={{ fontSize: 12, color: T.sub, lineHeight: 1.6 }}>
              <strong>Paciente 93449...</strong> deu entrada em urgência/emergência em <strong>03/05/2025</strong>.
              Última visita do ACS: <strong>47 dias antes</strong> (19/03/2025).
              O paciente ficou mais de 30 dias sem contato antes de uma internação — falha preventiva detectada.
            </div>
          </div>
        </div>
        <Divider />
        <div style={{ paddingTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button
            onClick={() => setSent(s => s.includes("urg1") ? s : [...s, "urg1"])}
            style={{
              background: sent.includes("urg1") ? T.ok : T.danger,
              color: "#fff", border: "none", borderRadius: 7,
              padding: "9px 16px", fontSize: 12, fontWeight: 700,
              cursor: "pointer", flex: 1,
            }}
          >
            {sent.includes("urg1") ? "✔ Notificação Enviada" : "📲 Notificar Equipe Clínica"}
          </button>
          <button style={{
            background: "transparent", border: `1px solid ${T.dangerBorder}`,
            color: T.danger, borderRadius: 7, padding: "9px 14px",
            fontSize: 12, fontWeight: 700, cursor: "pointer",
          }}>
            📍 Prioridade #1 Hoje
          </button>
        </div>
        {sent.includes("urg1") && (
          <div style={{
            marginTop: 10, background: T.okBg, border: `1px solid ${T.okBorder}`,
            borderRadius: 6, padding: "8px 12px", fontSize: 12, color: T.ok, fontWeight: 600,
          }}>
            ✔ Enfermeira da equipe e médico de referência notificados via sistema às {new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
          </div>
        )}
      </div>

      {/* Crônicos sem visita */}
      <div style={{
        background: T.warnBg, border: `1px solid ${T.warnBorder}`,
        borderRadius: 10, padding: 16, marginBottom: 12,
      }}>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 12 }}>
          <span style={{ fontSize: 24 }}>📉</span>
          <div>
            <div style={{ fontWeight: 800, fontSize: 14, color: T.warn, marginBottom: 2 }}>
              Crônicos com Lacuna de Cuidado ({RESUMO.sem_visita_30d} pacientes)
            </div>
            <div style={{ fontSize: 12, color: T.sub, lineHeight: 1.6 }}>
              Hipertensos e diabéticos da sua micro-área sem visita há mais de 30 dias.
              Protocolo mínimo: 1 visita/mês. Média atual da área: <strong>1,6 visitas em 11 meses</strong> — 85% abaixo do necessário.
            </div>
          </div>
        </div>
        <div style={{ background: "#fff", borderRadius: 6, padding: 10, marginBottom: 12 }}>
          {[
            { code: "93449...", dias: 47, cond: "HAS + DM · 66+" },
            { code: "867dd...", dias: 38, cond: "HAS · 45-65" },
            { code: "c72ab...", dias: 22, cond: "HAS · 66+" },
          ].map((r, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 0", borderBottom: i < 2 ? `1px solid ${T.border}` : "none" }}>
              <span style={{ fontFamily: "monospace", fontSize: 11, color: T.sub }}>{r.code}</span>
              <span style={{ fontSize: 11, color: T.sub }}>{r.cond}</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: r.dias > 30 ? T.danger : T.warn }}>{r.dias}d</span>
            </div>
          ))}
          <div style={{ fontSize: 11, color: T.muted, marginTop: 6 }}>+{RESUMO.sem_visita_30d - 3} mais na micro-área</div>
        </div>
        <button
          onClick={() => setSent(s => s.includes("cron1") ? s : [...s, "cron1"])}
          style={{
            width: "100%", background: sent.includes("cron1") ? T.ok : T.warn,
            color: "#fff", border: "none", borderRadius: 7,
            padding: "9px 16px", fontSize: 12, fontWeight: 700, cursor: "pointer",
          }}
        >
          {sent.includes("cron1") ? "✔ Relatório Enviado" : "📊 Enviar Relatório à Coordenação"}
        </button>
        {sent.includes("cron1") && (
          <div style={{ marginTop: 8, fontSize: 12, color: T.ok, fontWeight: 600 }}>
            ✔ Relatório de lacuna de cuidado enviado à coordenação da UBS
          </div>
        )}
      </div>

      {/* ACS sem dado = Gestantes */}
      <div style={{
        background: "#fdf4ff", border: "1px solid #e9d5ff",
        borderRadius: 10, padding: 16, marginBottom: 12,
      }}>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 12 }}>
          <span style={{ fontSize: 24 }}>🤱</span>
          <div>
            <div style={{ fontWeight: 800, fontSize: 14, color: "#7c3aed", marginBottom: 2 }}>
              {RESUMO.gestantes} Gestantes na Micro-área
            </div>
            <div style={{ fontSize: 12, color: T.sub, lineHeight: 1.6 }}>
              Campo <code style={{ background: "#f3f4f6", padding: "1px 4px", borderRadius: 3 }}>gestacao = TRUE</code> no cadastro. Antes desta ferramenta, o ACS não tinha como saber antes de sair.
              Gestantes têm prioridade máxima no protocolo de visitas.
            </div>
          </div>
        </div>
        <div style={{ background: "#fff", borderRadius: 6, padding: 10 }}>
          <div style={{ fontSize: 12, color: "#7c3aed", fontWeight: 700, marginBottom: 6 }}>Gestante priorizada na lista de hoje:</div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontFamily: "monospace", fontSize: 11, color: T.sub }}>5a3f1... · Trav. Esperança, 7A</span>
            <Tag cor="#7c3aed" bg="#f5f3ff">🤱 #3 da lista</Tag>
          </div>
        </div>
      </div>

      {/* Sem dados de risco — contexto */}
      <div style={{
        background: T.accentBg, border: `1px solid ${T.accentBorder}`,
        borderRadius: 10, padding: 16,
      }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.accent, marginBottom: 8 }}>
          💡 O que mudou com esta ferramenta
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {[
            { antes: "Lista de visitas vinha da memória do ACS", depois: "Lista gerada por score de risco + dados clínicos" },
            { antes: "ACS não sabia quais pacientes são crônicos antes de sair", depois: "HAS, DM, gestação visíveis antes da rota" },
            { antes: "Urgências detectadas só depois — reativamente", depois: "Urgências alertadas na manhã seguinte — preventivamente" },
            { antes: "Média: 1,6 visita/paciente em 11 meses", depois: "Priorização garante que crônicos sejam visitados primeiro" },
          ].map((item, i) => (
            <div key={i} style={{ background: "#fff", borderRadius: 7, padding: "10px 12px" }}>
              <div style={{ fontSize: 11, color: T.danger, marginBottom: 2 }}>❌ Antes: {item.antes}</div>
              <div style={{ fontSize: 11, color: T.ok, fontWeight: 600 }}>✔ Agora: {item.depois}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── PAINEL ───────────────────────────────────────────────────────────────────
function PainelView() {
  return (
    <div style={{ padding: "16px 18px" }}>
      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 16, fontWeight: 800, color: T.ink, marginBottom: 2 }}>📊 Painel da Micro-área</div>
        <div style={{ fontSize: 12, color: T.sub }}>{ACS_TERRITORY} · Dados atualizados hoje</div>
      </div>

      {/* Big stats */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
        {[
          { val: RESUMO.total_microarea, label: "Pacientes na micro-área", cor: T.ink, icon: "👥" },
          { val: RESUMO.com_cronicas, label: "Com condição crônica", cor: T.warn, icon: "❤️" },
          { val: RESUMO.sem_visita_30d, label: "Sem visita há +30 dias", cor: T.danger, icon: "🕐" },
          { val: RESUMO.urgencias_sem_visita, label: "Urgências s/ visita prévia", cor: T.danger, icon: "⚡" },
        ].map(s => (
          <div key={s.label} style={{
            background: T.surface, border: `1px solid ${T.border}`,
            borderRadius: 9, padding: "14px 14px",
            borderTop: `3px solid ${s.cor}`,
          }}>
            <div style={{ fontSize: 22 }}>{s.icon}</div>
            <div style={{ fontSize: 26, fontWeight: 800, color: s.cor, lineHeight: 1, marginTop: 4 }}>{s.val}</div>
            <div style={{ fontSize: 11, color: T.sub, marginTop: 3, lineHeight: 1.4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Composição clínica */}
      <div style={{ background: T.surface, border: `1px solid ${T.border}`, borderRadius: 10, padding: 16, marginBottom: 12 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.ink, marginBottom: 12 }}>Composição Clínica da Micro-área</div>
        {[
          { label: "Hipertensos (HAS)", val: 30, cor: T.danger, icon: "🩺" },
          { label: "Diabéticos (DM)", val: 10, cor: T.warn, icon: "💉" },
          { label: "HAS + DM", val: 4, cor: "#7c3aed", icon: "⚠️" },
          { label: "Gestantes", val: 3, cor: "#0891b2", icon: "🤱" },
          { label: "Vulnerabilidade social", val: 24, cor: "#b45309", icon: "🏚️" },
        ].map(r => (
          <div key={r.label} style={{ marginBottom: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
              <span style={{ fontSize: 12, color: T.sub }}>{r.icon} {r.label}</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: r.cor }}>{r.val}%</span>
            </div>
            <div style={{ background: T.border, borderRadius: 3, height: 5 }}>
              <div style={{ background: r.cor, borderRadius: 3, height: 5, width: `${r.val}%` }} />
            </div>
          </div>
        ))}
        <div style={{ fontSize: 11, color: T.muted, marginTop: 8 }}>
          Baseado em dados reais: hipertenso=30% e diabetico=10% confirmados nas amostras
        </div>
      </div>

      {/* Visitas x protocolo */}
      <div style={{ background: T.dangerBg, border: `1px solid ${T.dangerBorder}`, borderRadius: 10, padding: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.danger, marginBottom: 10 }}>
          ⚠️ Gap de Cobertura (evidência dos dados)
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <div style={{ flex: 1, textAlign: "center", background: "#fff", borderRadius: 7, padding: 12 }}>
            <div style={{ fontSize: 22, fontWeight: 800, color: T.danger }}>1,6×</div>
            <div style={{ fontSize: 10, color: T.muted, textTransform: "uppercase", marginTop: 2 }}>Visitas reais / paciente / 11 meses</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", color: T.muted, fontSize: 18 }}>vs</div>
          <div style={{ flex: 1, textAlign: "center", background: "#fff", borderRadius: 7, padding: 12 }}>
            <div style={{ fontSize: 22, fontWeight: 800, color: T.ok }}>11×</div>
            <div style={{ fontSize: 10, color: T.muted, textTransform: "uppercase", marginTop: 2 }}>Protocolo mínimo para crônicos</div>
          </div>
        </div>
        <div style={{ marginTop: 12, background: "#fff", borderRadius: 7, padding: "8px 12px" }}>
          <div style={{ fontSize: 11, color: T.sub, lineHeight: 1.6 }}>
            <strong style={{ color: T.danger }}>85% abaixo do mínimo.</strong> Com a lista priorizada, crônicos passam a ocupar os primeiros slots do dia — garantindo que sejam atendidos antes de o tempo acabar.
          </div>
        </div>
      </div>
    </div>
  );
}

// ── PATIENT DETAIL MODAL ──────────────────────────────────────────────────────
function PatientModal({ p, onClose, onVisit, visited }) {
  if (!p) return null;
  const done = visited.includes(p.id);

  return (
    <div style={{
      position: "fixed", inset: 0, background: "#000a", zIndex: 100,
      display: "flex", alignItems: "flex-end", justifyContent: "center",
    }} onClick={onClose}>
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: T.surface, width: "100%", maxWidth: 480,
          borderRadius: "18px 18px 0 0",
          padding: "20px 20px 32px",
          maxHeight: "90vh", overflowY: "auto",
          boxShadow: "0 -8px 32px #0003",
          animation: "slideUp 0.25s ease-out",
        }}
      >
        <style>{`@keyframes slideUp { from { transform: translateY(60px); opacity:0 } to { transform: translateY(0); opacity:1 } }`}</style>

        {/* Handle */}
        <div style={{ width: 36, height: 4, background: T.border, borderRadius: 2, margin: "0 auto 18px" }} />

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
          <div>
            <div style={{ fontFamily: "monospace", fontSize: 13, color: T.sub, marginBottom: 4 }}>{p.code}</div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              <Tag>{p.faixa}</Tag>
              <Tag>{p.sexo === "F" ? "♀ Feminino" : "♂ Masculino"}</Tag>
              <Tag>{p.raca}</Tag>
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 30, fontWeight: 800, color: scoreColor(p.score), lineHeight: 1 }}>{p.score}</div>
            <div style={{ fontSize: 10, color: scoreColor(p.score), fontWeight: 700 }}>{scoreLabel(p.score)}</div>
          </div>
        </div>

        <Divider />

        {/* Condições */}
        <div style={{ padding: "14px 0" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: T.muted, letterSpacing: 1, textTransform: "uppercase", marginBottom: 10 }}>Condições Clínicas</div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {p.gestacao && <Tag cor="#7c3aed" bg="#f5f3ff">🤱 Gestante · PRIORIDADE MÁXIMA</Tag>}
            {p.hipertenso && <Tag cor={T.danger} bg={T.dangerBg}>🩺 Hipertenso (HAS)</Tag>}
            {p.diabetico && <Tag cor={T.warn} bg={T.warnBg}>💉 Diabético (DM)</Tag>}
            {p.vulneravel && <Tag cor="#6b21a8" bg="#faf5ff">🏚️ Vulnerabilidade Social</Tag>}
            {!p.gestacao && !p.hipertenso && !p.diabetico && !p.vulneravel && (
              <Tag>Sem condição crônica registrada</Tag>
            )}
          </div>
        </div>

        <Divider />

        {/* Histórico */}
        <div style={{ padding: "14px 0" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: T.muted, letterSpacing: 1, textTransform: "uppercase", marginBottom: 10 }}>Histórico Recente</div>

          {p.alerta_urgencia && (
            <div style={{
              background: T.dangerBg, border: `1px solid ${T.dangerBorder}`,
              borderRadius: 7, padding: "10px 12px", marginBottom: 10,
            }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: T.danger, marginBottom: 2 }}>⚡ Urgência / Internação</div>
              <div style={{ fontSize: 12, color: T.sub }}>{p.data_ultimo_evento} · {p.dias_sem_visita} dias desde última visita antes da urgência</div>
            </div>
          )}

          <div style={{ display: "flex", gap: 10 }}>
            <div style={{ flex: 1, background: T.cardAlt, borderRadius: 7, padding: "10px 12px" }}>
              <div style={{ fontSize: 11, color: T.muted }}>Último evento clínico</div>
              <div style={{ fontSize: 12, fontWeight: 600, color: T.ink, marginTop: 2 }}>{p.data_ultimo_evento}</div>
              <div style={{ fontSize: 11, color: T.sub }}>{p.ultimo_evento}</div>
            </div>
            <div style={{ flex: 1, background: p.dias_sem_visita > 30 ? T.dangerBg : T.cardAlt, borderRadius: 7, padding: "10px 12px", border: p.dias_sem_visita > 30 ? `1px solid ${T.dangerBorder}` : "none" }}>
              <div style={{ fontSize: 11, color: T.muted }}>Sem visita há</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: p.dias_sem_visita > 30 ? T.danger : T.ok, marginTop: 2 }}>{p.dias_sem_visita}d</div>
              <div style={{ fontSize: 11, color: T.sub }}>{p.dias_sem_visita > 30 ? "⚠️ Acima do protocolo" : "✔ Dentro do prazo"}</div>
            </div>
          </div>
        </div>

        <Divider />

        {/* Motivos do score */}
        <div style={{ padding: "14px 0" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: T.muted, letterSpacing: 1, textTransform: "uppercase", marginBottom: 10 }}>Por que esta prioridade?</div>
          {p.motivos.map((m, i) => (
            <div key={i} style={{ display: "flex", gap: 8, alignItems: "center", padding: "5px 0" }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: scoreColor(p.score), flexShrink: 0 }} />
              <span style={{ fontSize: 13, color: T.ink }}>{m}</span>
            </div>
          ))}
        </div>

        <Divider />

        {/* Local */}
        <div style={{ padding: "14px 0 0" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: T.muted, letterSpacing: 1, textTransform: "uppercase", marginBottom: 8 }}>Localização</div>
          <div style={{ background: T.cardAlt, borderRadius: 7, padding: "10px 12px", display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 13, color: T.ink }}>📍 {p.endereco_hint}</span>
            <span style={{ fontSize: 13, color: T.accent, fontWeight: 600 }}>🚶 {p.distancia}</span>
          </div>
        </div>

        {/* Action */}
        <button
          onClick={() => { onVisit(p.id); onClose(); }}
          style={{
            width: "100%", marginTop: 18,
            background: done ? T.ok : T.ink,
            color: "#fff", border: "none", borderRadius: 10,
            padding: "14px", fontSize: 15, fontWeight: 800,
            cursor: "pointer", letterSpacing: 0.3,
          }}
        >
          {done ? "✔ Visita já registrada" : "✔ Marcar visita como realizada"}
        </button>

        <button onClick={onClose} style={{
          width: "100%", marginTop: 8, background: "transparent",
          border: `1px solid ${T.border}`, color: T.sub, borderRadius: 10,
          padding: "11px", fontSize: 13, cursor: "pointer",
        }}>Fechar</button>
      </div>
    </div>
  );
}

// ── MAIN ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [view, setView] = useState("lista");
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [visited, setVisited] = useState([]);

  function markVisited(id) {
    setVisited(v => v.includes(id) ? v : [...v, id]);
  }

  return (
    <div style={{
      background: T.bg, minHeight: "100vh",
      maxWidth: 480, margin: "0 auto",
      fontFamily: "'IBM Plex Sans', 'Segoe UI', sans-serif",
      color: T.ink, position: "relative",
      boxShadow: "0 0 40px #0002",
    }}>
      <HeaderBar view={view} setView={setView} notifs={ALERTAS_URGENCIA.length} />

      {view === "lista" && (
        <ListaView
          onOpen={setSelectedPatient}
          visited={visited}
          setVisited={setVisited}
        />
      )}
      {view === "alertas" && <AlertasView />}
      {view === "painel" && <PainelView />}

      <PatientModal
        p={selectedPatient}
        onClose={() => setSelectedPatient(null)}
        onVisit={markVisited}
        visited={visited}
      />

      {/* Bottom safe area */}
      <div style={{ height: 32 }} />
    </div>
  );
}
