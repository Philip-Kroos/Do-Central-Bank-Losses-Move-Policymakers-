import { useState, useEffect, useCallback, useMemo } from "react";

const ITEMS = __ITEMS__;

const C = { paper: "#F3F5F7", ink: "#1B2430", muted: "#5B6675", rule: "#D5DBE2", dove: "#2E5E9E", neutral: "#6E7885", hawk: "#9B3326", focus: "#0F6B66", card: "#FFFFFF" };
const SERIF = "'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif";
const SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
const POS = [
  { v: -1, label: "Niedrigere Sätze", hint: "Senkungen, langsamere Straffung, Warnung vor Überstraffung", color: C.dove, key: "1" },
  { v: 0, label: "Neutral", hint: "berichtend, datenabhängig ohne Richtung", color: C.neutral, key: "2" },
  { v: 1, label: "Höhere Sätze", hint: "Straffung, keine frühe Lockerung", color: C.hawk, key: "3" },
];

function toCSV(codes, coder) {
  const head = "coder,id,y4_topic,y4_position,y4_retrospective,y1_reserves,y2_own_losses,note,updated_at";
  const rows = Object.entries(codes).map(([id, c]) =>
    [coder, id, c.topic ?? "", c.topic ? (c.pos ?? "") : "", c.topic ? (c.retro ? 1 : 0) : "", c.y1 ? 1 : 0, c.y2 ? 1 : 0, JSON.stringify(c.note || ""), c.at || ""].join(","));
  return [head, ...rows].join("\n");
}

export default function CodingTool() {
  const [coder, setCoder] = useState(null);
  const [codes, setCodes] = useState({});
  const [i, setI] = useState(0);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [showRules, setShowRules] = useState(false);
  const [showContext, setShowContext] = useState(false);

  const list = useMemo(() => (coder === "B" ? ITEMS.filter((x) => x.double) : ITEMS), [coder]);
  const item = list[i];
  const code = (item && codes[item.id]) || {};
  const done = useMemo(() => list.filter((x) => codes[x.id] && codes[x.id].topic !== undefined && (codes[x.id].topic === false || codes[x.id].pos !== undefined)).length, [codes, list]);

  const load = async (who) => {
    setLoading(true); setCoder(who); setI(0);
    try {
      const r = await window.storage.get(`codes-v1-${who}`, false);
      setCodes(r ? JSON.parse(r.value) : {});
    } catch (e) { setCodes({}); }
    setLoading(false);
  };

  const persist = useCallback(async (next) => {
    setCodes(next);
    try {
      const ok = await window.storage.set(`codes-v1-${coder}`, JSON.stringify(next), false);
      setStatus(ok ? "Gespeichert" : "Speichern fehlgeschlagen – bitte CSV exportieren");
    } catch (e) { setStatus("Speichern fehlgeschlagen – bitte CSV exportieren"); }
  }, [coder]);

  const update = (patch) => {
    if (!item) return;
    const merged = { ...code, ...patch, at: new Date().toISOString() };
    if (merged.topic === false) delete merged.pos;
    persist({ ...codes, [item.id]: merged });
  };

  const go = (d) => { setShowContext(false); setI((k) => Math.max(0, Math.min(list.length - 1, k + d))); };
  const nextOpen = () => {
    const k = list.findIndex((x, j) => j > i && !(codes[x.id] && (codes[x.id].topic === false || codes[x.id].pos !== undefined)));
    const any = k >= 0 ? k : list.findIndex((x) => !(codes[x.id] && (codes[x.id].topic === false || codes[x.id].pos !== undefined)));
    if (any >= 0) { setShowContext(false); setI(any); }
  };

  useEffect(() => {
    if (!coder) return;
    const h = (e) => {
      if (e.target.tagName === "TEXTAREA") return;
      if (e.key === "j" || e.key === "J") update({ topic: true });
      if (e.key === "n" || e.key === "N") update({ topic: false });
      const p = POS.find((x) => x.key === e.key);
      if (p) update({ topic: true, pos: p.v });
      if (e.key === "ArrowRight") go(1);
      if (e.key === "ArrowLeft") go(-1);
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  });

  const exportCSV = async () => {
    const csv = toCSV(codes, coder);
    try { await navigator.clipboard.writeText(csv); setStatus("CSV in die Zwischenablage kopiert"); } catch (e) { setStatus("Kopieren nicht möglich – Download nutzen"); }
  };
  const downloadCSV = () => {
    const url = URL.createObjectURL(new Blob([toCSV(codes, coder)], { type: "text/csv" }));
    const a = document.createElement("a"); a.href = url; a.download = `validation_codes_${coder}.csv`; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  if (!coder) {
    return (
      <div style={{ background: C.paper, minHeight: "100vh", color: C.ink, fontFamily: SANS, padding: "48px 20px" }}>
        <div style={{ maxWidth: 640, margin: "0 auto" }}>
          <h1 style={{ fontFamily: SERIF, fontWeight: 400, fontSize: 34, lineHeight: 1.15, margin: "0 0 12px" }}>Wofür plädiert die Passage beim Zinskurs?</h1>
          <p style={{ color: C.muted, fontSize: 16, lineHeight: 1.55, margin: "0 0 28px" }}>
            {ITEMS.length} Redepassagen aus Reden europäischer Zentralbanker. Namen, Institutionen und Länder sind geschwärzt. Du kodierst nur, was im Text steht. Fortschritt wird automatisch gespeichert.
          </p>
          <div style={{ display: "grid", gap: 12 }}>
            <button onClick={() => load("A")} style={btn(C.ink, "#fff")}>Als Kodierer A starten ({ITEMS.length} Passagen)</button>
            <button onClick={() => load("B")} style={btn("#fff", C.ink, C.rule)}>Als Kodierer B starten ({ITEMS.filter((x) => x.double).length} Doppelkodierungen)</button>
          </div>
        </div>
      </div>
    );
  }
  if (loading) return <div style={{ padding: 40, fontFamily: SANS, color: C.muted }}>Gespeicherte Kodierungen werden geladen …</div>;

  return (
    <div style={{ background: C.paper, minHeight: "100vh", color: C.ink, fontFamily: SANS }}>
      <div style={{ height: 3, background: C.rule }}><div style={{ height: 3, width: `${(100 * done) / list.length}%`, background: C.focus, transition: "width .3s" }} /></div>
      <header style={{ maxWidth: 720, margin: "0 auto", padding: "14px 20px 0", display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
        <span style={{ fontSize: 14, color: C.muted }}>Passage {i + 1} von {list.length}, {done} kodiert, Kodierer {coder}</span>
        <span style={{ display: "flex", gap: 14, fontSize: 14 }}>
          <button onClick={() => setShowRules((s) => !s)} style={link()}>{showRules ? "Regeln schließen" : "Regeln"}</button>
          <button onClick={nextOpen} style={link()}>Nächste offene</button>
        </span>
      </header>

      {showRules && (
        <section style={{ maxWidth: 720, margin: "12px auto 0", padding: "0 20px" }}>
          <div style={{ background: C.card, border: `1px solid ${C.rule}`, borderRadius: 6, padding: "14px 18px", fontSize: 15, lineHeight: 1.55 }}>
            <p style={{ margin: "0 0 8px" }}><strong>Zinskurs-Thema ja</strong>, wenn die Passage Richtung oder Tempo der Leitzinsen bzw. den geldpolitischen Kurs bewertet oder berichtet. Reine Inflationsprognosen ohne Politikbezug und reine Bilanz- oder QT-Aussagen: nein.</p>
            <p style={{ margin: "0 0 8px" }}>Nur die eigene Position des Sprechers zählt. Zitiert er Kritiker oder Märkte, ist das neutral.</p>
            <p style={{ margin: "0 0 8px" }}>Verteidigung vergangener Erhöhungen zählt als höher, Verteidigung vergangener Senkungen als niedriger. „Nicht zu früh senken" ist höher. „Sätze bleiben, Daten entscheiden" ohne Gegenüberstellung ist neutral.</p>
            <p style={{ margin: "0 0 8px" }}>„Nur Rückblick" ankreuzen, wenn die Passage ausschließlich vergangene Entscheidungen bewertet und nichts über den künftigen Kurs sagt.</p>
            <p style={{ margin: 0 }}>Tastatur: J/N für das Thema, 1/2/3 für die Position, Pfeile zum Blättern.</p>
          </div>
        </section>
      )}

      <main style={{ maxWidth: 720, margin: "0 auto", padding: "18px 20px 260px" }}>
        {item.context && (
          <button onClick={() => setShowContext((s) => !s)} style={{ ...link(), fontSize: 14, marginBottom: 10 }}>{showContext ? "Vorherigen Absatz ausblenden" : "Vorherigen Absatz zeigen"}</button>
        )}
        {showContext && <p style={{ fontFamily: SERIF, fontStyle: "italic", color: C.muted, fontSize: 16, lineHeight: 1.6, margin: "0 0 16px", borderLeft: `2px solid ${C.rule}`, paddingLeft: 12 }}>… {item.context}</p>}
        <article style={{ fontFamily: SERIF, fontSize: 19, lineHeight: 1.65, maxWidth: "68ch" }}>{item.text}</article>
        {item.double && <p style={{ fontSize: 13, color: C.focus, marginTop: 14 }}>Wird auch von Kodierer B kodiert.</p>}
      </main>

      <footer style={{ position: "fixed", left: 0, right: 0, bottom: 0, background: C.card, borderTop: `1px solid ${C.rule}` }}>
        <div style={{ maxWidth: 720, margin: "0 auto", padding: "12px 20px 14px", display: "grid", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <span style={{ fontSize: 15 }}>Äußert sich die Passage zum Zinskurs?</span>
            <button onClick={() => update({ topic: true })} style={chip(code.topic === true)}>Ja</button>
            <button onClick={() => update({ topic: false })} style={chip(code.topic === false)}>Nein</button>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, opacity: code.topic === false ? 0.35 : 1 }}>
            {POS.map((p) => (
              <button key={p.v} disabled={code.topic === false} onClick={() => update({ topic: true, pos: p.v })}
                style={{ border: `2px solid ${p.color}`, background: code.pos === p.v && code.topic ? p.color : "#fff", color: code.pos === p.v && code.topic ? "#fff" : p.color, borderRadius: 8, padding: "10px 6px", fontFamily: SANS, fontSize: 15, fontWeight: 600, cursor: "pointer", minHeight: 48 }}
                title={p.hint}>{p.label}</button>
            ))}
          </div>
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap", fontSize: 14, color: C.muted }}>
            <label style={{ opacity: code.topic === false ? 0.35 : 1 }}><input type="checkbox" disabled={code.topic === false} checked={!!code.retro} onChange={(e) => update({ retro: e.target.checked })} /> Nur Rückblick auf frühere Entscheidungen</label>
            <label><input type="checkbox" checked={!!code.y1} onChange={(e) => update({ y1: e.target.checked })} /> Reservenverzinsung/Mindestreserve</label>
            <label><input type="checkbox" checked={!!code.y2} onChange={(e) => update({ y2: e.target.checked })} /> Eigene Verluste der Zentralbank</label>
          </div>
          <textarea value={code.note || ""} onChange={(e) => update({ note: e.target.value })} placeholder="Notiz (optional, z. B. unsicher weil …)" rows={1}
            style={{ fontFamily: SANS, fontSize: 14, padding: 8, border: `1px solid ${C.rule}`, borderRadius: 6, resize: "vertical" }} />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ display: "flex", gap: 8 }}>
              <button onClick={() => go(-1)} style={btn("#fff", C.ink, C.rule)} disabled={i === 0}>Zurück</button>
              <button onClick={() => go(1)} style={btn(C.ink, "#fff")} disabled={i === list.length - 1}>Weiter</button>
            </span>
            <span style={{ display: "flex", gap: 12, alignItems: "center", fontSize: 13 }}>
              <span style={{ color: C.muted }}>{status}</span>
              <button onClick={exportCSV} style={link()}>CSV kopieren</button>
              <button onClick={downloadCSV} style={link()}>CSV herunterladen</button>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function btn(bg, fg, border) {
  return { background: bg, color: fg, border: `1px solid ${border || bg}`, borderRadius: 8, padding: "12px 18px", fontFamily: SANS, fontSize: 15, fontWeight: 600, cursor: "pointer" };
}
function chip(active) {
  return { background: active ? C.focus : "#fff", color: active ? "#fff" : C.ink, border: `1px solid ${active ? C.focus : C.rule}`, borderRadius: 999, padding: "6px 16px", fontSize: 15, cursor: "pointer", minHeight: 36 };
}
function link() {
  return { background: "none", border: "none", color: C.focus, textDecoration: "underline", textUnderlineOffset: 3, cursor: "pointer", fontFamily: SANS, padding: 0 };
}
