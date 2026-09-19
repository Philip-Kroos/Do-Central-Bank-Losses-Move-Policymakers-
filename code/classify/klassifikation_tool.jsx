import { useState, useRef, useEffect } from "react";

const MODEL = "claude-sonnet-4-6";
const PROMPT_VERSION = "PAPv2-Y4-p2";
const BATCH = 5;
const C = { paper: "#F3F5F7", ink: "#1B2430", muted: "#5B6675", rule: "#D5DBE2", focus: "#0F6B66", warn: "#9B3326", card: "#FFFFFF" };
const SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
const SERIF = "'Iowan Old Style', 'Charter', Georgia, serif";

const SYSTEM = "You code passages from speeches by euro area central bankers for a research project. Follow the codebook exactly. Names, institutions, roles and countries are masked. Return only a JSON array, no prose, no code fences.";

const CODEBOOK = `CODEBOOK (rate stance)
TOPIC = true if the passage states or reports a view on the direction, level or pace of policy interest rates or on the overall monetary policy stance. TOPIC = false for inflation or growth forecasts without reference to policy, for statements only about the balance sheet or asset purchases, for financial regulation or any other topic.
POSITION (only if TOPIC = true):
-1 = the speaker favours lower rates, rate cuts, earlier or larger cuts, slower or smaller hikes, or warns against over-tightening.
+1 = the speaker favours higher rates, hikes, faster or larger tightening, or warns against easing too early.
0 = neutral: purely reporting decisions, data-dependent without a direction, or balanced.
RETROSPECTIVE (only if TOPIC = true): true if the passage only evaluates past decisions and says nothing about the future course; otherwise false.
RULES: Only the speaker's own view counts; views attributed to others are coded 0. Defending past hikes = +1; defending past cuts = -1. "We should not cut yet" = +1. "Rates stay; decisions depend on data" without contrast = 0. Masked tokens are not evidence.
OUTPUT: a JSON array with one object per passage, in the given order:
{"id": "<id>", "topic": true|false, "position": -1|0|1|null, "retrospective": true|false|null, "evidence": "<exact quote of at most 15 consecutive words from the passage that supports the code; empty string if topic is false>"}`;

const norm = (s) => (s || "").toLowerCase().replace(/[\u2018\u2019\u201c\u201d"'`]/g, "").replace(/\s+/g, " ").trim();

function validate(item, r) {
  if (!r || r.id !== item.id) return "id mismatch";
  if (typeof r.topic !== "boolean") return "topic not boolean";
  if (r.topic && ![-1, 0, 1].includes(r.position)) return "invalid position";
  if (!r.topic && r.position !== null && r.position !== undefined) return "position without topic";
  if (r.topic && typeof r.retrospective !== "boolean") return "retrospective not boolean";
  if (r.topic) {
    const ev = norm(r.evidence);
    if (!ev || ev.split(" ").length > 20 || !norm(item.text).includes(ev)) return "evidence not found in passage";
  }
  return null;
}

async function callModel(items) {
  const body = items.map((it, k) => `PASSAGE ${k + 1}\nid: ${it.id}\ncontext (previous text, do not code): ${it.context || "(none)"}\ntext to code: ${it.text}`).join("\n\n");
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: MODEL, max_tokens: 1000, temperature: 0, system: SYSTEM,
      messages: [{ role: "user", content: `${CODEBOOK}\n\n${body}` }] }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  const raw = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("\n");
  let parsed = null;
  try { parsed = JSON.parse(raw.replace(/```json|```/g, "").trim()); } catch (e) { parsed = null; }
  return { raw, parsed: Array.isArray(parsed) ? parsed : null };
}

export default function Klassifikation() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState({});
  const [log, setLog] = useState([]);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState("");
  const stopRef = useRef(false);
  const stateRef = useRef({ results: {}, log: [] });

  useEffect(() => { stateRef.current = { results, log }; }, [results, log]);

  const keyRes = (f) => `cls-v1-res-${f}`;
  const keyLog = (f) => `cls-v1-log-${f}`;

  const onFile = async (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    try {
      const data = JSON.parse(await f.text());
      if (!data.file || !Array.isArray(data.items)) throw new Error("format");
      setFile(data); setMsg("Gespeicherte Ergebnisse werden geladen …");
      let r = {}, l = [];
      try { const a = await window.storage.get(keyRes(data.file), false); if (a) r = JSON.parse(a.value); } catch (err) {}
      try { const b = await window.storage.get(keyLog(data.file), false); if (b) l = JSON.parse(b.value); } catch (err) {}
      setResults(r); setLog(l); setMsg(`${data.items.length} Passagen geladen`);
    } catch (err) { setMsg("Die Datei hat nicht das erwartete Format (klass_input_*.json)."); }
  };

  const save = async (r, l) => {
    try {
      await window.storage.set(keyRes(file.file), JSON.stringify(r), false);
      await window.storage.set(keyLog(file.file), JSON.stringify(l), false);
    } catch (err) { setMsg("Speichern fehlgeschlagen – bitte jetzt exportieren."); }
  };

  const runBatch = async (items, r, l, attempt) => {
    let out;
    for (let t = 0; t < 3; t++) {
      try { out = await callModel(items); break; } catch (err) { await new Promise((ok) => setTimeout(ok, 2000 * (t + 1))); }
    }
    const at = new Date().toISOString();
    l.push({ at, model: MODEL, prompt_version: PROMPT_VERSION, ids: items.map((x) => x.id), attempt, raw: out ? out.raw : "REQUEST FAILED" });
    const retry = [];
    items.forEach((it, k) => {
      const cand = out && out.parsed ? (out.parsed.find((x) => x && x.id === it.id) || out.parsed[k]) : null;
      const err = validate(it, cand);
      if (!err) r[it.id] = { topic: cand.topic, position: cand.topic ? cand.position : null, retrospective: cand.topic ? cand.retrospective : null, evidence: cand.evidence || "", valid: true, attempt, at };
      else if (attempt === 1) retry.push(it);
      else r[it.id] = { topic: null, position: null, evidence: "", valid: false, reason: err, attempt, at };
    });
    return retry;
  };

  const start = async () => {
    if (!file) return;
    stopRef.current = false; setRunning(true);
    const r = { ...stateRef.current.results }; const l = [...stateRef.current.log];
    const todo = file.items.filter((it) => !r[it.id]);
    for (let s = 0; s < todo.length; s += BATCH) {
      if (stopRef.current) break;
      const batch = todo.slice(s, s + BATCH);
      setMsg(`Batch ${Math.floor(s / BATCH) + 1} von ${Math.ceil(todo.length / BATCH)}`);
      const retry = await runBatch(batch, r, l, 1);
      for (const it of retry) { if (stopRef.current) break; await runBatch([it], r, l, 2); }
      setResults({ ...r }); setLog([...l]);
      await save(r, l);
      await new Promise((ok) => setTimeout(ok, 800));
    }
    setRunning(false);
    setMsg(stopRef.current ? "Pausiert. Fortsetzen macht dort weiter." : "Fertig. Bitte beide Dateien exportieren.");
  };

  const download = (name, text, type) => {
    const url = URL.createObjectURL(new Blob([text], { type }));
    const a = document.createElement("a"); a.href = url; a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  const exportCSV = () => {
    const head = "file,id,topic,position,retrospective,valid,reason,attempt,evidence,model,prompt_version,at";
    const rows = Object.entries(results).map(([id, v]) => [file.file, id, v.topic, v.position ?? "", v.retrospective ?? "", v.valid, v.reason || "", v.attempt, JSON.stringify(v.evidence || ""), MODEL, PROMPT_VERSION, v.at].join(","));
    download(file.file.replace(".json", "_results.csv"), [head, ...rows].join("\n"), "text/csv");
  };
  const exportLog = () => download(file.file.replace(".json", "_rawlog.jsonl"), log.map((x) => JSON.stringify(x)).join("\n"), "application/json");

  const total = file ? file.items.length : 0;
  const n = Object.keys(results).length;
  const invalid = Object.values(results).filter((v) => !v.valid).length;

  return (
    <div style={{ background: C.paper, minHeight: "100vh", color: C.ink, fontFamily: SANS, padding: "40px 20px" }}>
      <div style={{ maxWidth: 640, margin: "0 auto" }}>
        <h1 style={{ fontFamily: SERIF, fontWeight: 400, fontSize: 32, lineHeight: 1.15, margin: "0 0 10px" }}>Blinde Klassifikation der Zinsstance</h1>
        <p style={{ color: C.muted, fontSize: 16, lineHeight: 1.55, margin: "0 0 24px" }}>
          Modell {MODEL}, Prompt {PROMPT_VERSION}, Temperatur 0, {BATCH} Passagen pro Anfrage. Jede Rohantwort wird archiviert. Starte erst, wenn die Human-Validierung die Schwelle erreicht hat.
        </p>
        <label style={{ display: "block", background: C.card, border: `1px dashed ${C.rule}`, borderRadius: 8, padding: "18px 16px", cursor: "pointer" }}>
          <span style={{ fontSize: 15 }}>{file ? `Datei: ${file.file}` : "Eingabedatei wählen (klass_input_*.json)"}</span>
          <input type="file" accept=".json,application/json" onChange={onFile} disabled={running} style={{ display: "block", marginTop: 10 }} />
        </label>
        {file && (
          <div style={{ marginTop: 24 }}>
            <div style={{ height: 6, background: C.rule, borderRadius: 3 }}>
              <div style={{ height: 6, width: `${(100 * n) / total}%`, background: C.focus, borderRadius: 3, transition: "width .3s" }} />
            </div>
            <p style={{ fontSize: 15, margin: "10px 0 20px" }}>
              {n} von {total} klassifiziert{invalid > 0 && <span style={{ color: C.warn }}>, {invalid} ungültig nach zweitem Versuch</span>}
            </p>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              {!running
                ? <button onClick={start} disabled={n >= total} style={btn(C.ink, "#fff")}>{n > 0 && n < total ? "Fortsetzen" : "Klassifikation starten"}</button>
                : <button onClick={() => { stopRef.current = true; setMsg("Wird nach dem laufenden Batch pausiert …"); }} style={btn("#fff", C.ink, C.rule)}>Pausieren</button>}
              <button onClick={exportCSV} disabled={n === 0} style={btn("#fff", C.ink, C.rule)}>Ergebnisse als CSV</button>
              <button onClick={exportLog} disabled={log.length === 0} style={btn("#fff", C.ink, C.rule)}>Rohantworten als JSONL</button>
            </div>
          </div>
        )}
        <p style={{ fontSize: 14, color: C.muted, marginTop: 18 }} aria-live="polite">{msg}</p>
      </div>
    </div>
  );
}

function btn(bg, fg, border) {
  return { background: bg, color: fg, border: `1px solid ${border || bg}`, borderRadius: 8, padding: "12px 18px", fontFamily: SANS, fontSize: 15, fontWeight: 600, cursor: "pointer" };
}
