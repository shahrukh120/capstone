// AI-Powered ATS — professional deck (17 slides)
// Palette: Midnight Executive (indigo/navy) with emerald accent.
const PptxGenJS = require("pptxgenjs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.title = "AI-Powered ATS — Capstone";
pptx.author = "Shahrukh Khan";

const C = {
  navy:"0B1437", ink:"1E2761", indigo:"4F46E5", violet:"6366F1",
  ice:"CADCFC", mint:"10B981", amber:"F59E0B", coral:"EF4444",
  white:"FFFFFF", off:"F5F7FB", line:"E5E7EB", gray:"6B7280", dark:"1F2937",
};
const FONT_H = "Calibri", FONT_B = "Calibri";

// ── Helpers ──────────────────────────────────────────────────────
const addFooter = (slide, n, onDark=false) => {
  const col = onDark ? C.ink : C.line;
  const txt = onDark ? C.ice : C.gray;
  slide.addShape("line", { x: 0.5, y: 7.05, w: 12.333, h: 0, line: { color: col, width: 0.75 } });
  slide.addText("AI-Powered ATS — Capstone", { x: 0.5, y: 7.12, w: 6, h: 0.28, fontSize: 9, color: txt, fontFace: FONT_B });
  slide.addText(String(n).padStart(2, "0"), { x: 12.0, y: 7.12, w: 0.83, h: 0.28, fontSize: 9, color: txt, fontFace: FONT_B, align: "right" });
};

const sectionHeader = (slide, num, title, subtitle, darkText=false) => {
  const titleColor = darkText ? C.white : C.dark;
  const subColor = darkText ? C.ice : C.gray;
  slide.addShape("roundRect", { x: 0.5, y: 0.5, w: 0.55, h: 0.55, fill: { color: C.indigo }, line: { color: C.indigo }, rectRadius: 0.1 });
  slide.addText(num, { x: 0.5, y: 0.5, w: 0.55, h: 0.55, fontSize: 20, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
  slide.addText(title, { x: 1.2, y: 0.45, w: 11, h: 0.55, fontSize: 28, bold: true, color: titleColor, fontFace: FONT_H, valign: "middle" });
  if (subtitle) slide.addText(subtitle, { x: 1.2, y: 1.0, w: 11, h: 0.4, fontSize: 14, color: subColor, fontFace: FONT_B, italic: true });
};

const pill = (slide, x, y, w, h, text, color = C.indigo) => {
  slide.addShape("roundRect", { x, y, w, h, fill: { color: C.white }, line: { color, width: 1.25 }, rectRadius: h/2 });
  slide.addText(text, { x, y, w, h, fontSize: 11, color, align: "center", valign: "middle", bold: true, fontFace: FONT_B });
};

const card = (slide, opts) => {
  const { x, y, w, h, accent = C.indigo, title, body, icon } = opts;
  slide.addShape("roundRect", { x, y, w, h, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
  slide.addShape("rect", { x, y, w: 0.1, h, fill: { color: accent }, line: { color: accent } });
  if (icon) {
    slide.addShape("ellipse", { x: x + 0.28, y: y + 0.25, w: 0.5, h: 0.5, fill: { color: accent }, line: { color: accent } });
    slide.addText(icon, { x: x + 0.28, y: y + 0.25, w: 0.5, h: 0.5, fontSize: 18, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
  }
  if (title) slide.addText(title, { x: icon ? x + 0.9 : x + 0.3, y: y + 0.25, w: w - (icon ? 1.1 : 0.45), h: 0.5, fontSize: 14, bold: true, color: C.dark, fontFace: FONT_H, valign: "middle" });
  if (body)  slide.addText(body, { x: x + 0.3, y: y + 0.85, w: w - 0.55, h: h - 1.0, fontSize: 11, color: C.gray, fontFace: FONT_B, valign: "top" });
};

// ═══ SLIDE 1 — Cover ═══════════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addShape("ellipse", { x: 10, y: -2, w: 5, h: 5, fill: { color: C.indigo, transparency: 70 }, line: { type: "none" } });
  s.addShape("ellipse", { x: -1, y: 5.5, w: 4, h: 4, fill: { color: C.violet, transparency: 80 }, line: { type: "none" } });
  s.addShape("rect", { x: 0, y: 7.4, w: 13.333, h: 0.1, fill: { color: C.mint }, line: { type: "none" } });
  s.addShape("roundRect", { x: 0.9, y: 1.2, w: 2.4, h: 0.4, fill: { color: C.indigo }, line: { type: "none" }, rectRadius: 0.2 });
  s.addText("CAPSTONE PROJECT", { x: 0.9, y: 1.2, w: 2.4, h: 0.4, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_B, charSpacing: 3 });
  s.addText("AI-Powered ATS", { x: 0.9, y: 1.9, w: 11, h: 1.3, fontSize: 66, bold: true, color: C.white, fontFace: FONT_H });
  s.addText("Applicant Tracking System with RAG, Multi-Agent Orchestration,\nBias Auditing, and Automated Candidate Communication", { x: 0.9, y: 3.2, w: 11, h: 1.1, fontSize: 20, color: C.ice, fontFace: FONT_B });
  const addStat = (x, value, label) => {
    s.addText(value, { x, y: 5.2, w: 2.4, h: 0.7, fontSize: 40, bold: true, color: C.mint, fontFace: FONT_H });
    s.addText(label, { x, y: 5.9, w: 2.4, h: 0.3, fontSize: 11, color: C.ice, fontFace: FONT_B, charSpacing: 2 });
  };
  addStat(0.9, "2,484", "CANDIDATES INDEXED");
  addStat(3.4, "30+", "API ENDPOINTS");
  addStat(5.9, "7", "GUARDRAIL LAYERS");
  addStat(8.4, "3", "LLM PROVIDERS");
  s.addText("Shahrukh Khan  ·  April 2026", { x: 0.9, y: 6.7, w: 11, h: 0.3, fontSize: 12, color: C.ice, fontFace: FONT_B, italic: true });
}

// ═══ SLIDE 2 — Problem ═════════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "01", "The Problem", "Recruiting is broken — and AI can fix the boring 80%");
  s.addShape("roundRect", { x: 0.5, y: 1.7, w: 4.5, h: 4.9, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.2 });
  s.addText("250+", { x: 0.8, y: 2.0, w: 4, h: 1.4, fontSize: 96, bold: true, color: C.mint, fontFace: FONT_H });
  s.addText("RÉSUMÉS PER JOB", { x: 0.8, y: 3.5, w: 4, h: 0.4, fontSize: 13, color: C.ice, fontFace: FONT_B, charSpacing: 3, bold: true });
  s.addText("The average corporate opening receives 250+ applications. Recruiters spend 6–8 seconds per résumé, miss strong candidates, and re-invent the same outreach flow for every hire.",
    { x: 0.8, y: 4.1, w: 4, h: 2.3, fontSize: 13, color: C.ice, fontFace: FONT_B, valign: "top" });
  const pains = [
    { icon: "1", title: "Manual screening doesn't scale", body: "Keyword search misses context. A Python-Django candidate is invisible to a 'backend engineer' keyword filter." },
    { icon: "2", title: "Bias creeps in silently", body: "Name, school, and demographic cues influence decisions before anyone reads the CV." },
    { icon: "3", title: "Scattered tools", body: "One tool for parsing, one for search, one for email, one for Kanban — no single source of truth." },
    { icon: "4", title: "Slow, repetitive comms", body: "Drafting the same interview-invite email 50 times per week. Meeting links are created by hand." },
  ];
  pains.forEach((p, i) => card(s, { x: 5.5 + Math.floor(i/2)*3.9, y: 1.7 + (i%2)*2.5, w: 3.7, h: 2.3, accent: C.coral, title: p.title, body: p.body, icon: p.icon }));
  addFooter(s, 2);
}

// ═══ SLIDE 3 — Solution ════════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "02", "Our Solution", "One cohesive platform — from raw PDF to signed offer");
  s.addText("An end-to-end AI hiring copilot.", { x: 0.5, y: 1.7, w: 5.2, h: 1.2, fontSize: 32, bold: true, color: C.dark, fontFace: FONT_H, valign: "top" });
  s.addText("Upload a résumé, the system parses it with an LLM, embeds it semantically, ranks it against open roles, lets recruiters drag cards through a Kanban pipeline, and sends templated interview invites with meeting links — all while auditing for bias.",
    { x: 0.5, y: 3.0, w: 5.2, h: 3.0, fontSize: 14, color: C.gray, fontFace: FONT_B, valign: "top" });
  ["RAG", "Multi-agent", "Guardrails", "Bias-audited", "SMTP + Meet"].forEach((t, i) => pill(s, 0.5 + (i%3)*1.7, 5.6 + Math.floor(i/3)*0.55, 1.5, 0.4, t));
  const boxes = [
    { label: "PDF", c: C.indigo, desc: "Upload résumé" },
    { label: "Parser", c: C.violet, desc: "LLM + regex" },
    { label: "Embedding", c: C.indigo, desc: "pgvector 384d" },
    { label: "Match", c: C.mint, desc: "Cosine top-k" },
    { label: "Interview", c: C.amber, desc: "Invite email" },
    { label: "Hire", c: C.mint, desc: "Pipeline → Offer" },
  ];
  boxes.forEach((b, i) => {
    const y = 1.8 + i * 0.9;
    s.addShape("roundRect", { x: 6.3, y, w: 0.7, h: 0.75, fill: { color: b.c }, line: { type: "none" }, rectRadius: 0.08 });
    s.addText(String(i+1), { x: 6.3, y, w: 0.7, h: 0.75, fontSize: 18, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
    s.addShape("roundRect", { x: 7.1, y, w: 3.0, h: 0.75, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.08 });
    s.addText(b.label, { x: 7.25, y: y + 0.05, w: 2.7, h: 0.35, fontSize: 13, bold: true, color: C.dark, fontFace: FONT_H });
    s.addText(b.desc, { x: 7.25, y: y + 0.38, w: 2.7, h: 0.3, fontSize: 10, color: C.gray, fontFace: FONT_B });
    if (i < boxes.length - 1) s.addText("▼", { x: 6.55, y: y + 0.75, w: 0.2, h: 0.15, fontSize: 8, color: C.gray, align: "center", fontFace: FONT_B });
  });
  s.addShape("rect", { x: 10.3, y: 1.8, w: 2.5, h: 5.4, fill: { color: C.ice, transparency: 60 }, line: { type: "none" } });
  s.addText("Every step guarded by input validation, prompt-injection scan, and rate limits.",
    { x: 10.4, y: 1.9, w: 2.3, h: 5, fontSize: 11, color: C.ink, fontFace: FONT_B, italic: true, valign: "top" });
  addFooter(s, 3);
}

// ═══ SLIDE 4 — Tech Stack ══════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "03", "Tech Stack", "Production-grade choices, not demo-ware");
  const groups = [
    { title: "Backend", color: C.indigo, items: ["Python 3.11", "FastAPI", "Uvicorn", "Pydantic v2", "SQLAlchemy"] },
    { title: "Data", color: C.violet, items: ["PostgreSQL", "pgvector", "JSONB columns", "SentenceTransformers", "MiniLM-L6-v2 (384d)"] },
    { title: "AI / LLM", color: C.mint, items: ["Groq (llama-3.3-70b)", "NVIDIA NIM (fallback)", "Ollama (local)", "LangGraph", "ReAct agents"] },
    { title: "Frontend", color: C.amber, items: ["Vanilla JS SPA", "Tailwind CSS", "Lucide icons", "HTML5 drag-drop", "Jinja2 shell"] },
    { title: "Communication", color: C.ink, items: ["smtplib (STARTTLS)", "Gmail App Password", "Jitsi Meet (free)", "HTML + plain text", "Prompt-injection guard"] },
    { title: "DevOps", color: C.coral, items: ["Docker multi-arch", "Azure App Service", "Azure Container Registry", "GitHub CI", "pytest"] },
  ];
  groups.forEach((g, i) => {
    const col = i%3, row = Math.floor(i/3);
    const x = 0.5 + col*(4.1 + 0.1), y = 1.7 + row*(2.55 + 0.15);
    s.addShape("roundRect", { x, y, w: 4.1, h: 2.55, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
    s.addShape("roundRect", { x, y, w: 4.1, h: 0.5, fill: { color: g.color }, line: { type: "none" }, rectRadius: 0.12 });
    s.addText(g.title.toUpperCase(), { x: x + 0.2, y, w: 3.7, h: 0.5, fontSize: 14, bold: true, color: C.white, valign: "middle", fontFace: FONT_H, charSpacing: 3 });
    const lines = g.items.map(it => ({ text: "  " + it, options: { bullet: { code: "25AA" }, color: C.dark, fontSize: 12, fontFace: FONT_B } }));
    s.addText(lines, { x: x + 0.25, y: y + 0.65, w: 3.7, h: 1.75, valign: "top", paraSpaceAfter: 4 });
  });
  addFooter(s, 4);
}

// ═══ SLIDE 5 — Architecture (high-level layers) ════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "04", "Architecture", "Strict layering · cross-cutting guardrails");
  const layers = [
    { name: "PRESENTATION", sub: "templates/index.html · static/js/app.js · Tailwind SPA · Kanban drag-drop", color: C.indigo },
    { name: "API", sub: "FastAPI · 30+ endpoints · Pydantic schemas · CORS + rate limit middleware", color: C.violet },
    { name: "GUARDRAILS", sub: "input_validator · prompt_guard · resume_validator · pii_detector · sql_guard · llm_output_guard · rate_limiter", color: C.coral },
    { name: "DOMAIN", sub: "parser · rag · agents · bias · communication", color: C.mint },
    { name: "DATA", sub: "SQLAlchemy ORM · PostgreSQL + pgvector · vector(384) embeddings", color: C.amber },
  ];
  layers.forEach((L, i) => {
    const y = 1.7 + i * (0.95 + 0.12);
    s.addShape("roundRect", { x: 0.5, y, w: 8.3, h: 0.95, fill: { color: C.white }, line: { color: C.line, width: 0.5 }, rectRadius: 0.08 });
    s.addShape("rect", { x: 0.5, y, w: 0.12, h: 0.95, fill: { color: L.color }, line: { type: "none" } });
    s.addText(L.name, { x: 0.8, y, w: 2.0, h: 0.95, fontSize: 14, bold: true, color: L.color, valign: "middle", fontFace: FONT_H, charSpacing: 2 });
    s.addText(L.sub, { x: 2.9, y, w: 5.8, h: 0.95, fontSize: 11, color: C.gray, valign: "middle", fontFace: FONT_B });
  });
  s.addText("EXTERNAL", { x: 9.2, y: 1.7, w: 3.8, h: 0.3, fontSize: 10, bold: true, color: C.gray, fontFace: FONT_B, charSpacing: 3 });
  const ext = [
    { icon: "◆", label: "PostgreSQL + pgvector", color: C.indigo, detail: "Azure Database" },
    { icon: "✦", label: "Groq / NVIDIA NIM", color: C.mint, detail: "Cloud LLM APIs" },
    { icon: "✉", label: "Gmail SMTP", color: C.amber, detail: "STARTTLS 587" },
    { icon: "▲", label: "Azure App Service", color: C.violet, detail: "Linux container" },
  ];
  ext.forEach((e, i) => {
    const y = 2.1 + i * 1.05;
    s.addShape("roundRect", { x: 9.2, y, w: 3.8, h: 0.9, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.1 });
    s.addShape("ellipse", { x: 9.35, y: y + 0.2, w: 0.5, h: 0.5, fill: { color: e.color }, line: { type: "none" } });
    s.addText(e.icon, { x: 9.35, y: y + 0.2, w: 0.5, h: 0.5, fontSize: 18, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
    s.addText(e.label, { x: 9.95, y: y + 0.1, w: 3.0, h: 0.4, fontSize: 12, bold: true, color: C.white, fontFace: FONT_H, valign: "middle" });
    s.addText(e.detail, { x: 9.95, y: y + 0.45, w: 3.0, h: 0.35, fontSize: 9, color: C.ice, fontFace: FONT_B });
  });
  addFooter(s, 5);
}

// ═══ SLIDE 6 — System Architecture (detailed) ══════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "05", "System Architecture", "Request path · middleware pipeline · internal calls");

  // Client tier
  s.addShape("roundRect", { x: 0.5, y: 1.7, w: 2.4, h: 1.0, fill: { color: C.indigo }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("CLIENT", { x: 0.5, y: 1.7, w: 2.4, h: 0.35, fontSize: 10, bold: true, color: C.ice, align: "center", valign: "middle", fontFace: FONT_H, charSpacing: 3 });
  s.addText("Browser SPA", { x: 0.5, y: 2.05, w: 2.4, h: 0.35, fontSize: 13, bold: true, color: C.white, align: "center", fontFace: FONT_H });
  s.addText("Tailwind + vanilla JS", { x: 0.5, y: 2.38, w: 2.4, h: 0.3, fontSize: 10, color: C.ice, align: "center", fontFace: FONT_B });

  // HTTPS arrow
  s.addShape("rightTriangle", { x: 2.95, y: 2.1, w: 0.25, h: 0.25, fill: { color: C.gray }, line: { type: "none" }, flipV: false, rotate: 90 });
  s.addText("HTTPS", { x: 2.9, y: 1.85, w: 0.6, h: 0.25, fontSize: 8, color: C.gray, align: "center", fontFace: FONT_B });

  // App Service (big box)
  s.addShape("roundRect", { x: 3.2, y: 1.55, w: 7.3, h: 4.6, fill: { color: C.white }, line: { color: C.ink, width: 1.5 }, rectRadius: 0.1 });
  s.addShape("roundRect", { x: 3.2, y: 1.55, w: 7.3, h: 0.45, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("AZURE APP SERVICE  ·  FastAPI + Uvicorn  ·  Linux container", { x: 3.3, y: 1.55, w: 7.1, h: 0.45, fontSize: 11, bold: true, color: C.white, valign: "middle", fontFace: FONT_H, charSpacing: 2 });

  // Middleware pipeline
  s.addText("MIDDLEWARE PIPELINE", { x: 3.4, y: 2.1, w: 7.0, h: 0.3, fontSize: 9, bold: true, color: C.gray, fontFace: FONT_B, charSpacing: 2 });
  const mws = [
    { label: "CORS", c: C.indigo },
    { label: "Rate Limit", c: C.coral },
    { label: "Route", c: C.mint },
  ];
  mws.forEach((m, i) => {
    const x = 3.4 + i * 2.35;
    s.addShape("roundRect", { x, y: 2.4, w: 2.2, h: 0.5, fill: { color: m.c, transparency: 15 }, line: { color: m.c, width: 1 }, rectRadius: 0.08 });
    s.addText(m.label, { x, y: 2.4, w: 2.2, h: 0.5, fontSize: 12, bold: true, color: m.c, align: "center", valign: "middle", fontFace: FONT_H });
    if (i < 2) s.addText("→", { x: x + 2.2, y: 2.42, w: 0.15, h: 0.5, fontSize: 14, bold: true, color: C.gray, fontFace: FONT_H });
  });

  // Guardrails row
  s.addShape("roundRect", { x: 3.4, y: 3.1, w: 6.9, h: 0.6, fill: { color: C.coral, transparency: 85 }, line: { color: C.coral, width: 1 }, rectRadius: 0.08 });
  s.addText("GUARDRAILS", { x: 3.5, y: 3.1, w: 1.3, h: 0.6, fontSize: 10, bold: true, color: C.coral, valign: "middle", fontFace: FONT_H, charSpacing: 2 });
  s.addText("input · prompt · resume · pii · sql · llm-output · rate", { x: 4.8, y: 3.1, w: 5.4, h: 0.6, fontSize: 10, color: C.dark, valign: "middle", fontFace: FONT_B });

  // Domain modules
  s.addText("DOMAIN MODULES", { x: 3.4, y: 3.85, w: 7.0, h: 0.3, fontSize: 9, bold: true, color: C.gray, fontFace: FONT_B, charSpacing: 2 });
  const modules = [
    { n: "parser",       c: C.indigo },
    { n: "rag",          c: C.violet },
    { n: "agents",       c: C.mint },
    { n: "bias",         c: C.amber },
    { n: "communication",c: C.coral },
  ];
  modules.forEach((m, i) => {
    const x = 3.4 + i * 1.4;
    s.addShape("roundRect", { x, y: 4.15, w: 1.3, h: 0.6, fill: { color: C.white }, line: { color: m.c, width: 1.5 }, rectRadius: 0.08 });
    s.addText(m.n, { x, y: 4.15, w: 1.3, h: 0.6, fontSize: 10, bold: true, color: m.c, align: "center", valign: "middle", fontFace: FONT_H });
  });

  // Data access
  s.addShape("roundRect", { x: 3.4, y: 4.95, w: 6.9, h: 0.5, fill: { color: C.amber, transparency: 85 }, line: { color: C.amber, width: 1 }, rectRadius: 0.08 });
  s.addText("SQLAlchemy ORM  ·  Session factory  ·  pgvector adapter", { x: 3.5, y: 4.95, w: 6.7, h: 0.5, fontSize: 10, color: C.dark, valign: "middle", align: "center", fontFace: FONT_B });

  s.addText("Every request: CORS → Rate limit → Route handler → (optional guard) → Domain module → DB",
    { x: 3.4, y: 5.55, w: 6.9, h: 0.5, fontSize: 9, italic: true, color: C.gray, fontFace: FONT_B, align: "center", valign: "middle" });

  // External services on right
  const ext = [
    { t: "PostgreSQL\n+ pgvector", c: C.indigo },
    { t: "Groq /\nNVIDIA NIM",     c: C.mint },
    { t: "Gmail SMTP\n(STARTTLS)",  c: C.amber },
  ];
  ext.forEach((e, i) => {
    const y = 1.7 + i * 1.6;
    s.addShape("roundRect", { x: 10.8, y, w: 2.2, h: 1.4, fill: { color: C.navy }, line: { color: e.c, width: 1.5 }, rectRadius: 0.1 });
    s.addShape("ellipse", { x: 11.75, y: y + 0.15, w: 0.3, h: 0.3, fill: { color: e.c }, line: { type: "none" } });
    s.addText(e.t, { x: 10.9, y: y + 0.5, w: 2.0, h: 0.8, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
  });

  // Key note
  s.addShape("roundRect", { x: 0.5, y: 6.35, w: 12.3, h: 0.55, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText([
    { text: "Contract: ", options: { bold: true, color: C.mint, fontSize: 11 } },
    { text: "user input flows top-to-bottom; domain modules never skip the guardrail layer; data access is centralized in one session factory.", options: { color: C.ice, fontSize: 11 } },
  ], { x: 0.7, y: 6.35, w: 12, h: 0.55, fontFace: FONT_B, valign: "middle" });

  addFooter(s, 6);
}

// ═══ SLIDE 7 — Orchestrator & Agents ═══════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "06", "Orchestrator & Agents", "LangGraph StateGraph · pluggable LLM providers");

  // LLM router on top
  s.addShape("roundRect", { x: 0.5, y: 1.7, w: 12.3, h: 0.85, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("LLM CLIENT  (provider router)", { x: 0.7, y: 1.78, w: 3.5, h: 0.3, fontSize: 11, bold: true, color: C.mint, fontFace: FONT_H, charSpacing: 2 });
  s.addText("llm_chat() / llm_chat_json()", { x: 0.7, y: 2.1, w: 3.5, h: 0.3, fontSize: 10, color: C.ice, fontFace: "Consolas", italic: true });
  ["Groq", "NVIDIA NIM", "Ollama"].forEach((p, i) => {
    const x = 5.0 + i * 2.6;
    s.addShape("roundRect", { x, y: 1.85, w: 2.3, h: 0.55, fill: { color: C.white }, line: { color: C.mint, width: 1.25 }, rectRadius: 0.08 });
    s.addText(p, { x, y: 1.85, w: 2.3, h: 0.55, fontSize: 12, bold: true, color: C.mint, align: "center", valign: "middle", fontFace: FONT_H });
  });

  // State graph (LangGraph nodes)
  s.addText("LANGGRAPH ORCHESTRATOR", { x: 0.5, y: 2.8, w: 7.5, h: 0.3, fontSize: 11, bold: true, color: C.gray, fontFace: FONT_B, charSpacing: 3 });
  const nodes = [
    { name: "parser_node",    detail: "PDF → ResumeData\n(LLM JSON parse)", c: C.indigo },
    { name: "matching_node",  detail: "Embed + cosine\ntop-K candidates", c: C.violet },
    { name: "interview_node", detail: "Generate ranked Qs\nwith rationale",   c: C.mint },
  ];
  nodes.forEach((n, i) => {
    const x = 0.5 + i * 2.5;
    const y = 3.2;
    s.addShape("roundRect", { x, y, w: 2.3, h: 1.4, fill: { color: C.white }, line: { color: n.c, width: 1.5 }, rectRadius: 0.1 });
    s.addShape("rect", { x, y, w: 2.3, h: 0.4, fill: { color: n.c }, line: { type: "none" } });
    s.addShape("roundRect", { x, y, w: 2.3, h: 0.45, fill: { color: n.c }, line: { type: "none" }, rectRadius: 0.1 });
    s.addText(n.name, { x, y, w: 2.3, h: 0.4, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
    s.addText(n.detail, { x: x + 0.1, y: y + 0.5, w: 2.1, h: 0.85, fontSize: 10, color: C.dark, align: "center", valign: "middle", fontFace: FONT_B });
    if (i < 2) s.addText("→", { x: x + 2.3, y: y + 0.5, w: 0.2, h: 0.4, fontSize: 20, bold: true, color: C.gray, fontFace: FONT_H });
  });
  // END marker
  s.addShape("ellipse", { x: 7.55, y: 3.65, w: 0.5, h: 0.5, fill: { color: C.navy }, line: { type: "none" } });
  s.addText("END", { x: 7.55, y: 3.65, w: 0.5, h: 0.5, fontSize: 9, bold: true, color: C.mint, align: "center", valign: "middle", fontFace: FONT_H });

  // State box
  s.addShape("roundRect", { x: 0.5, y: 4.85, w: 7.5, h: 1.1, fill: { color: C.navy }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("PipelineState (TypedDict)", { x: 0.7, y: 4.9, w: 7, h: 0.3, fontSize: 10, bold: true, color: C.mint, fontFace: FONT_H, charSpacing: 2 });
  s.addText("pdf_path → parsed_resume, candidate_id → matches → interview_questions", { x: 0.7, y: 5.2, w: 7, h: 0.35, fontSize: 11, color: C.ice, fontFace: "Consolas" });
  s.addText("each node mutates the state and hands it to the next", { x: 0.7, y: 5.55, w: 7, h: 0.35, fontSize: 10, color: C.ice, fontFace: FONT_B, italic: true });

  // Separate agent: Text-to-SQL on the right
  s.addShape("roundRect", { x: 8.3, y: 2.8, w: 4.5, h: 3.15, fill: { color: C.white }, line: { color: C.coral, width: 1.5 }, rectRadius: 0.1 });
  s.addShape("rect", { x: 8.3, y: 2.8, w: 4.5, h: 0.45, fill: { color: C.coral }, line: { type: "none" } });
  s.addShape("roundRect", { x: 8.3, y: 2.8, w: 4.5, h: 0.5, fill: { color: C.coral }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("TEXT-TO-SQL AGENT", { x: 8.5, y: 2.8, w: 4.3, h: 0.45, fontSize: 13, bold: true, color: C.white, valign: "middle", fontFace: FONT_H, charSpacing: 2 });
  s.addText("ReAct loop with conversation memory", { x: 8.5, y: 3.35, w: 4.3, h: 0.3, fontSize: 10, color: C.gray, fontFace: FONT_B, italic: true });
  const react = [
    { t: "THOUGHT",     d: "which tables/columns?" },
    { t: "ACTION",      d: "generate SQL (SELECT-only)" },
    { t: "OBSERVATION", d: "sql_guard → execute → rows" },
    { t: "ANSWER",      d: "natural-language response" },
  ];
  react.forEach((r, i) => {
    const y = 3.75 + i * 0.52;
    s.addShape("roundRect", { x: 8.5, y, w: 1.45, h: 0.38, fill: { color: C.coral, transparency: 80 }, line: { color: C.coral, width: 0.75 }, rectRadius: 0.05 });
    s.addText(r.t, { x: 8.5, y, w: 1.45, h: 0.38, fontSize: 10, bold: true, color: C.coral, align: "center", valign: "middle", fontFace: FONT_H });
    s.addText(r.d, { x: 10.05, y, w: 2.7, h: 0.38, fontSize: 10, color: C.dark, valign: "middle", fontFace: FONT_B });
  });

  // Footer tip
  s.addText("Also: interview_agent (JD + résumé → ranked Qs) runs standalone for one-off generation.",
    { x: 0.5, y: 6.25, w: 12.3, h: 0.4, fontSize: 10, italic: true, color: C.gray, fontFace: FONT_B, align: "center" });

  addFooter(s, 7);
}

// ═══ SLIDE 8 — Data Flow ═══════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "07", "Data Flow · Résumé Upload", "Eight guards · two LLM calls · one vector insert");
  const stages = [
    { n: "1", title: "Upload",      detail: "Extension + size",       c: C.indigo },
    { n: "2", title: "Magic bytes", detail: "%PDF- header",           c: C.indigo },
    { n: "3", title: "Extract",     detail: "pdfplumber → text",      c: C.violet },
    { n: "4", title: "Heuristic",   detail: "Looks-like-résumé?",     c: C.coral  },
    { n: "5", title: "PI scan",     detail: "Prompt-injection guard", c: C.coral  },
    { n: "6", title: "LLM parse",   detail: "Groq JSON mode",         c: C.mint   },
    { n: "7", title: "Embed",       detail: "MiniLM → 384d vector",   c: C.amber  },
    { n: "8", title: "Persist",     detail: "pgvector INSERT",        c: C.ink    },
  ];
  const tlY = 3.0, nodeR = 0.55;
  s.addShape("line", { x: 0.95, y: tlY + nodeR/2 + 0.02, w: 11.45, h: 0, line: { color: C.line, width: 3 } });
  stages.forEach((st, i) => {
    const x = 0.7 + i * 1.59;
    s.addShape("ellipse", { x, y: tlY, w: nodeR, h: nodeR, fill: { color: st.c }, line: { color: C.white, width: 3 } });
    s.addText(st.n, { x, y: tlY, w: nodeR, h: nodeR, fontSize: 16, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
    const above = i % 2 === 0;
    const ly = above ? tlY - 1.25 : tlY + 0.85;
    s.addShape("roundRect", { x: x - 0.55, y: ly, w: 1.65, h: 1.1, fill: { color: C.white }, line: { color: st.c, width: 1 }, rectRadius: 0.1 });
    s.addText(st.title,  { x: x - 0.55, y: ly + 0.1, w: 1.65, h: 0.35, fontSize: 12, bold: true, color: C.dark, align: "center", fontFace: FONT_H });
    s.addText(st.detail, { x: x - 0.55, y: ly + 0.45, w: 1.65, h: 0.6, fontSize: 9, color: C.gray, align: "center", fontFace: FONT_B });
  });
  s.addShape("roundRect", { x: 0.5, y: 5.7, w: 12.3, h: 1.2, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.12 });
  s.addText("Also: strips NUL (0x00) bytes before Postgres · runs on async upload · rate-limited separately from /query",
    { x: 0.8, y: 5.75, w: 11.7, h: 0.4, fontSize: 12, bold: true, color: C.white, fontFace: FONT_B, valign: "middle" });
  s.addText([
    { text: "Match flow:  ", options: { bold: true, color: C.mint, fontSize: 11 } },
    { text: "embed(job_desc) → ", options: { color: C.ice, fontSize: 11, fontFace: "Consolas" } },
    { text: "ORDER BY embedding <=> :q  ", options: { color: C.ice, fontSize: 11, fontFace: "Consolas" } },
    { text: "→ top-K ranked candidates", options: { color: C.ice, fontSize: 11 } },
  ], { x: 0.8, y: 6.2, w: 11.7, h: 0.6, fontFace: FONT_B, valign: "middle" });
  addFooter(s, 8);
}

// ═══ SLIDE 9 — Core Features ═══════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "08", "Core Features", "Everything a recruiter needs in one place");
  const feats = [
    { icon: "⚙", title: "LLM Resume Parsing",   color: C.indigo, body: "PDFs become structured JSON: name, email, phone, skills, experience, education, summary, total years." },
    { icon: "◎", title: "Semantic Matching",    color: C.violet, body: "pgvector cosine similarity ranks the top-K candidates for any JD in <100ms — no keyword gymnastics." },
    { icon: "▤", title: "Kanban Pipeline",      color: C.amber,  body: "Drag-drop across Applied → Screened → Interview → Offer → Hired/Rejected. Bulk add top matches in one click." },
    { icon: "✉", title: "Email + Meet Invites", color: C.mint,   body: "Templated HTML invites. Paste Google Meet / Teams URL, or auto-generate a free Jitsi room." },
    { icon: "⟲", title: "Text-to-SQL Chat",     color: C.coral,  body: "Ask \"top 5 finance candidates by experience\" in English — ReAct agent writes SQL, executes, answers." },
    { icon: "⚖", title: "Bias Auditing",        color: C.ink,    body: "Anonymize before LLM-as-judge. Per-skill match explanation. Cohort-level score-disparity reports." },
  ];
  feats.forEach((f, i) => {
    const col = i%3, row = Math.floor(i/3);
    const x = 0.5 + col*(4.15 + 0.08), y = 1.7 + row*(2.55 + 0.08);
    s.addShape("roundRect", { x, y, w: 4.15, h: 2.55, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.15 });
    s.addShape("ellipse", { x: x + 0.3, y: y + 0.3, w: 0.8, h: 0.8, fill: { color: f.color }, line: { type: "none" } });
    s.addText(f.icon, { x: x + 0.3, y: y + 0.3, w: 0.8, h: 0.8, fontSize: 28, bold: true, color: C.white, align: "center", valign: "middle", fontFace: FONT_H });
    s.addText(f.title, { x: x + 1.25, y: y + 0.35, w: 2.75, h: 0.5, fontSize: 15, bold: true, color: C.dark, fontFace: FONT_H, valign: "middle" });
    s.addShape("line", { x: x + 0.3, y: y + 1.3, w: 3.55, h: 0, line: { color: f.color, width: 1 } });
    s.addText(f.body, { x: x + 0.3, y: y + 1.4, w: 3.55, h: 1.0, fontSize: 11, color: C.gray, fontFace: FONT_B, valign: "top" });
  });
  addFooter(s, 9);
}

// ─── Helper for 2×2 screenshot grids ──────────────────────────────
const gridShot = (s, x, y, w, h, img, title, sub, accent) => {
  s.addShape("roundRect", { x, y, w, h, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
  s.addShape("rect", { x, y, w, h: 0.08, fill: { color: accent }, line: { type: "none" } });
  s.addImage({ path: img, x: x + 0.12, y: y + 0.15, w: w - 0.24, h: h - 0.85, sizing: { type: "contain", w: w - 0.24, h: h - 0.85 } });
  s.addText(title, { x: x + 0.25, y: y + h - 0.66, w: w - 0.5, h: 0.3, fontSize: 13, bold: true, color: C.dark, fontFace: FONT_H });
  s.addText(sub,   { x: x + 0.25, y: y + h - 0.38, w: w - 0.5, h: 0.3, fontSize: 9.5, color: C.gray, fontFace: FONT_B });
};

// ═══ SLIDE 10 — Product UI · Recruiter Console ═════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "09", "Product UI · Recruiter Console", "Dashboard · Jobs · Candidates · Upload");

  const W = 6.1, H = 2.55, GX = 0.5, GY = 1.55, GAP = 0.13;
  gridShot(s, GX,           GY,           W, H, "assets/screens/dashboard.png",  "Dashboard",        "2,485 candidates · per-category bars", C.indigo);
  gridShot(s, GX+W+GAP,     GY,           W, H, "assets/screens/jobs.png",       "Job Roles",        "8 open positions · Find Matches CTA", C.violet);
  gridShot(s, GX,           GY+H+GAP,     W, H, "assets/screens/candidates.png", "Candidates",       "Full list · skill chips · row actions", C.mint);
  gridShot(s, GX+W+GAP,     GY+H+GAP,     W, H, "assets/screens/upload.png",     "Upload Résumé",    "Drag-drop · guardrails on every file",   C.amber);

  addFooter(s, 10);
}

// ═══ SLIDE 11 — AI Workflows (screenshots) ═════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "10", "AI Workflows", "Matching · Pipeline · Interview Prep · SQL Chat");

  const W = 6.1, H = 2.55, GX = 0.5, GY = 1.55, GAP = 0.13;
  gridShot(s, GX,           GY,           W, H, "assets/screens/matching.png",  "Semantic Matching",       "pgvector cosine · ranked shortlist",   C.indigo);
  gridShot(s, GX+W+GAP,     GY,           W, H, "assets/screens/kanban.png",    "Kanban Pipeline",         "Drag candidates across stages",         C.violet);
  gridShot(s, GX,           GY+H+GAP,     W, H, "assets/screens/interview.png", "Interview Questions",     "LLM-generated from JD + résumé",        C.mint);
  gridShot(s, GX+W+GAP,     GY+H+GAP,     W, H, "assets/screens/sqlchat.png",   "Conversation with DB",    "ReAct text-to-SQL · recruiter chat",    C.amber);

  addFooter(s, 11);
}

// ═══ SLIDE 12 — Communication In Action (screenshots) ══════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "11", "Communication In Action", "From in-app modal to inbox — one click");

  // Left: Invite modal
  const L = { x: 0.5, y: 1.55, w: 6.1, h: 5.2 };
  s.addShape("roundRect", { x: L.x, y: L.y, w: L.w, h: L.h, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
  s.addShape("rect", { x: L.x, y: L.y, w: L.w, h: 0.08, fill: { color: C.indigo }, line: { type: "none" } });
  s.addImage({ path: "assets/screens/invite_modal.png", x: L.x + 0.15, y: L.y + 0.2, w: L.w - 0.3, h: L.h - 1.05, sizing: { type: "contain", w: L.w - 0.3, h: L.h - 1.05 } });
  s.addText("① Send Interview Invite", { x: L.x + 0.3, y: L.y + L.h - 0.8, w: L.w - 0.6, h: 0.35, fontSize: 15, bold: true, color: C.dark, fontFace: FONT_H });
  s.addText("Job dropdown · Auto-Jitsi link · custom message · recruiter override", { x: L.x + 0.3, y: L.y + L.h - 0.45, w: L.w - 0.6, h: 0.35, fontSize: 10, color: C.gray, fontFace: FONT_B });

  // Arrow between
  s.addShape("rightArrow", { x: 6.75, y: 3.9, w: 0.55, h: 0.5, fill: { color: C.indigo }, line: { type: "none" } });

  // Right: Gmail screenshot
  const R = { x: 7.4, y: 1.55, w: 5.4, h: 5.2 };
  s.addShape("roundRect", { x: R.x, y: R.y, w: R.w, h: R.h, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
  s.addShape("rect", { x: R.x, y: R.y, w: R.w, h: 0.08, fill: { color: C.mint }, line: { type: "none" } });
  s.addImage({ path: "assets/screens/invite_email.png", x: R.x + 0.15, y: R.y + 0.2, w: R.w - 0.3, h: R.h - 1.05, sizing: { type: "contain", w: R.w - 0.3, h: R.h - 1.05 } });
  s.addText("② Delivered to Inbox", { x: R.x + 0.3, y: R.y + R.h - 0.8, w: R.w - 0.6, h: 0.35, fontSize: 15, bold: true, color: C.dark, fontFace: FONT_H });
  s.addText("Templated HTML · Jitsi link · branded footer · via Gmail SMTP", { x: R.x + 0.3, y: R.y + R.h - 0.45, w: R.w - 0.6, h: 0.35, fontSize: 10, color: C.gray, fontFace: FONT_B });

  s.addShape("roundRect", { x: 0.5, y: 6.82, w: 12.3, h: 0.22, fill: { color: C.ice }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("STARTTLS · Gmail App Password · jitsi meet rooms via UUID  ·  zero-config for recruiters", {
    x: 0.5, y: 6.82, w: 12.3, h: 0.22, fontSize: 10, color: C.ink, align: "center", valign: "middle", fontFace: FONT_B, italic: true,
  });
  addFooter(s, 12);
}

// ═══ SLIDE 12 — Security ═══════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addShape("roundRect", { x: 0.5, y: 0.5, w: 0.55, h: 0.55, fill: { color: C.mint }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText("12", { x: 0.5, y: 0.5, w: 0.55, h: 0.55, fontSize: 20, bold: true, color: C.navy, align: "center", valign: "middle", fontFace: FONT_H });
  s.addText("Security & Guardrails", { x: 1.2, y: 0.45, w: 11, h: 0.55, fontSize: 28, bold: true, color: C.white, fontFace: FONT_H, valign: "middle" });
  s.addText("Seven layers of defense · input → LLM → output", { x: 1.2, y: 1.0, w: 11, h: 0.4, fontSize: 14, color: C.ice, fontFace: FONT_B, italic: true });
  const zones = [
    { title: "INPUT-SIDE",  color: C.mint,  items: ["Length + sanitize", "Category whitelist", "PDF magic bytes (%PDF-)", "Résumé-shape heuristic", "Rate limit (per-IP, tiered)"] },
    { title: "LLM-FACING",  color: C.amber, items: ["Prompt-injection scan", "LLM output JSON validator", "SQL guard (SELECT-only)", "Blocks pg_*, info_schema", "Auto-retry on bad JSON"] },
    { title: "OUTPUT-SIDE", color: C.coral, items: ["PII redaction in logs", "Bias anonymizer", "Fairness audit report", "NUL-byte stripping", "CORS allow-list"] },
  ];
  zones.forEach((z, i) => {
    const x = 0.5 + i * (4.15 + 0.1);
    s.addShape("roundRect", { x, y: 1.7, w: 4.15, h: 4.5, fill: { color: C.ink }, line: { color: z.color, width: 1.5 }, rectRadius: 0.12 });
    s.addShape("roundRect", { x, y: 1.7, w: 4.15, h: 0.65, fill: { color: z.color }, line: { type: "none" }, rectRadius: 0.12 });
    s.addText(z.title, { x: x + 0.3, y: 1.7, w: 3.55, h: 0.55, fontSize: 15, bold: true, color: C.navy, fontFace: FONT_H, valign: "middle", charSpacing: 3 });
    z.items.forEach((it, j) => {
      const ly = 2.55 + j * 0.65;
      s.addShape("ellipse", { x: x + 0.25, y: ly + 0.05, w: 0.3, h: 0.3, fill: { color: z.color, transparency: 30 }, line: { color: z.color, width: 1 } });
      s.addText("✓", { x: x + 0.25, y: ly + 0.05, w: 0.3, h: 0.3, fontSize: 13, bold: true, color: z.color, align: "center", valign: "middle", fontFace: FONT_H });
      s.addText(it, { x: x + 0.65, y: ly, w: 3.3, h: 0.4, fontSize: 12, color: C.white, fontFace: FONT_B, valign: "middle" });
    });
  });
  s.addShape("roundRect", { x: 0.5, y: 6.4, w: 12.3, h: 0.55, fill: { color: C.mint }, line: { type: "none" }, rectRadius: 0.1 });
  s.addText([
    { text: "Zero trust on user input:  ", options: { bold: true, color: C.navy, fontSize: 13 } },
    { text: "every PDF, prompt, and SQL query passes through validation before it reaches the model or the database.", options: { color: C.navy, fontSize: 13 } },
  ], { x: 0.7, y: 6.4, w: 12, h: 0.55, fontFace: FONT_B, valign: "middle" });
  addFooter(s, 13, true);
}

// ═══ SLIDE 11 — Deployment ═════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "13", "Deployment", "CI pipeline · container registry · Azure App Service");

  // CI/CD pipeline flow across top
  const pipe = [
    { label: "GitHub",                 sub: "main branch",              c: C.ink },
    { label: "docker buildx",          sub: "linux/amd64",              c: C.indigo },
    { label: "Azure ACR",              sub: "ats-app:email-v1",         c: C.violet },
    { label: "Webhook",                sub: "DOCKER_ENABLE_CI=true",    c: C.coral },
    { label: "Azure App Service",      sub: "ai-ats-app · India region",c: C.mint },
  ];
  const pY = 1.8, pW = 2.35, pH = 1.1, pG = 0.15;
  pipe.forEach((p, i) => {
    const x = 0.5 + i * (pW + pG);
    s.addShape("roundRect", { x, y: pY, w: pW, h: pH, fill: { color: C.white }, line: { color: p.c, width: 1.25 }, rectRadius: 0.1 });
    s.addShape("rect", { x, y: pY, w: pW, h: 0.2, fill: { color: p.c }, line: { type: "none" } });
    s.addShape("roundRect", { x, y: pY, w: pW, h: 0.25, fill: { color: p.c }, line: { type: "none" }, rectRadius: 0.1 });
    s.addText(p.label, { x: x + 0.1, y: pY + 0.3, w: pW - 0.2, h: 0.4, fontSize: 13, bold: true, color: p.c, fontFace: FONT_H, valign: "middle" });
    s.addText(p.sub, { x: x + 0.1, y: pY + 0.65, w: pW - 0.2, h: 0.4, fontSize: 10, color: C.gray, fontFace: "Consolas", valign: "middle" });
    if (i < pipe.length - 1) s.addText("→", { x: x + pW, y: pY + 0.35, w: 0.18, h: 0.4, fontSize: 16, bold: true, color: C.gray, fontFace: FONT_H });
  });

  // Two-column detail below
  // Left column: runtime stack
  const lx = 0.5, ly = 3.2, lw = 6.2, lh = 3.5;
  s.addShape("roundRect", { x: lx, y: ly, w: lw, h: lh, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
  s.addShape("rect", { x: lx, y: ly, w: lw, h: 0.5, fill: { color: C.ink }, line: { type: "none" } });
  s.addShape("roundRect", { x: lx, y: ly, w: lw, h: 0.55, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.12 });
  s.addText("RUNTIME STACK", { x: lx + 0.3, y: ly, w: lw - 0.6, h: 0.5, fontSize: 14, bold: true, color: C.white, fontFace: FONT_H, valign: "middle", charSpacing: 2 });
  const rtRows = [
    ["Platform",  "Azure App Service (Linux, B2 tier)"],
    ["Container", "atscapstoneacr123.azurecr.io/ats-app:email-v1"],
    ["Base image","python:3.11-slim + uvicorn"],
    ["Database",  "Azure DB for PostgreSQL + pgvector"],
    ["Region",    "India (Central)"],
    ["Scaling",   "Single instance · manual scale-out ready"],
  ];
  rtRows.forEach(([k, v], i) => {
    const y = ly + 0.75 + i * 0.43;
    s.addText(k.toUpperCase(), { x: lx + 0.3, y, w: 1.7, h: 0.35, fontSize: 10, bold: true, color: C.indigo, fontFace: FONT_B, valign: "middle", charSpacing: 2 });
    s.addText(v, { x: lx + 2.0, y, w: lw - 2.2, h: 0.35, fontSize: 10.5, color: C.dark, fontFace: "Consolas", valign: "middle" });
  });

  // Right column: env + ops
  const rx = 6.9, ry = 3.2, rw = 5.9, rh = 3.5;
  s.addShape("roundRect", { x: rx, y: ry, w: rw, h: rh, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
  s.addShape("rect", { x: rx, y: ry, w: rw, h: 0.5, fill: { color: C.mint }, line: { type: "none" } });
  s.addShape("roundRect", { x: rx, y: ry, w: rw, h: 0.55, fill: { color: C.mint }, line: { type: "none" }, rectRadius: 0.12 });
  s.addText("ENV & OPS", { x: rx + 0.3, y: ry, w: rw - 0.6, h: 0.5, fontSize: 14, bold: true, color: C.navy, fontFace: FONT_H, valign: "middle", charSpacing: 2 });
  const envItems = [
    "GROQ_API_KEY · NVIDIA_API_KEY",
    "DATABASE_URL (pgvector enabled)",
    "LLM_PROVIDER · LLM_MODEL",
    "SMTP_HOST · SMTP_USER · SMTP_PASSWORD",
    "SMTP_FROM · SMTP_USE_TLS",
    "ALLOWED_ORIGINS (CORS)",
  ];
  envItems.forEach((e, i) => {
    const y = ry + 0.75 + i * 0.38;
    s.addShape("ellipse", { x: rx + 0.3, y: y + 0.07, w: 0.22, h: 0.22, fill: { color: C.mint }, line: { type: "none" } });
    s.addText(e, { x: rx + 0.65, y, w: rw - 0.9, h: 0.35, fontSize: 10.5, color: C.dark, fontFace: "Consolas", valign: "middle" });
  });
  // Small ops footer
  s.addShape("line", { x: rx + 0.3, y: ry + 3.05, w: rw - 0.6, h: 0, line: { color: C.line, width: 0.5 } });
  s.addText([
    { text: "Rollback:  ", options: { bold: true, color: C.mint, fontSize: 9 } },
    { text: "switch DOCKER_CUSTOM_IMAGE_NAME back to prior tag (:kanban, :latest)", options: { color: C.gray, fontSize: 9 } },
  ], { x: rx + 0.3, y: ry + 3.12, w: rw - 0.6, h: 0.3, fontFace: FONT_B, valign: "middle" });

  addFooter(s, 14);
}

// ═══ SLIDE 15 — Conclusion ═════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "14", "Conclusion", "Shipped, deployed, measurable");
  const stats = [
    { value: "90%",    label: "TIME SAVED",          detail: "on résumé screening per JD", color: C.mint },
    { value: "<100ms", label: "MATCH LATENCY",       detail: "over 2,484 indexed candidates", color: C.indigo },
    { value: "7",      label: "GUARDRAIL LAYERS",    detail: "input · LLM · output", color: C.coral },
    { value: "2 min",  label: "TO INTERVIEW INVITE", detail: "from shortlist to inbox", color: C.amber },
  ];
  stats.forEach((st, i) => {
    const col = i%2, row = Math.floor(i/2);
    const x = 0.5 + col*(3.0 + 0.15), y = 1.7 + row*(2.4 + 0.15);
    s.addShape("roundRect", { x, y, w: 3.0, h: 2.4, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.12 });
    s.addShape("rect", { x, y: y + 2.32, w: 3.0, h: 0.08, fill: { color: st.color }, line: { type: "none" } });
    s.addText(st.value,  { x: x + 0.2, y: y + 0.2, w: 2.6, h: 1.1, fontSize: 44, bold: true, color: st.color, fontFace: FONT_H, valign: "middle" });
    s.addText(st.label,  { x: x + 0.2, y: y + 1.35, w: 2.6, h: 0.4, fontSize: 11, bold: true, color: C.dark, fontFace: FONT_H, charSpacing: 2 });
    s.addText(st.detail, { x: x + 0.2, y: y + 1.75, w: 2.6, h: 0.5, fontSize: 11, color: C.gray, fontFace: FONT_B });
  });
  s.addShape("roundRect", { x: 7.0, y: 1.7, w: 5.83, h: 5.0, fill: { color: C.ink }, line: { type: "none" }, rectRadius: 0.15 });
  s.addText("Key Takeaways", { x: 7.3, y: 1.9, w: 5.3, h: 0.5, fontSize: 22, bold: true, color: C.white, fontFace: FONT_H });
  s.addShape("line", { x: 7.3, y: 2.55, w: 2.0, h: 0, line: { color: C.mint, width: 2 } });
  const takeaways = [
    { h: "Production-ready", b: "Deployed on Azure with Docker multi-arch builds and SMTP wired up. Not a notebook." },
    { h: "Responsible AI",   b: "Every LLM call is guarded, every output audited for bias. Explainability built in." },
    { h: "End-to-end",       b: "From raw PDF → shortlisted candidate → interview invite → pipeline tracking, no gaps." },
    { h: "Extensible",       b: "Pluggable LLM providers, modular guardrails, clean domain boundaries." },
  ];
  takeaways.forEach((t, i) => {
    const y = 2.9 + i * 0.9;
    s.addShape("ellipse", { x: 7.3, y: y + 0.1, w: 0.25, h: 0.25, fill: { color: C.mint }, line: { type: "none" } });
    s.addText(t.h, { x: 7.65, y: y, w: 5.0, h: 0.4, fontSize: 14, bold: true, color: C.white, fontFace: FONT_H });
    s.addText(t.b, { x: 7.65, y: y + 0.4, w: 5.0, h: 0.5, fontSize: 11, color: C.ice, fontFace: FONT_B });
  });
  addFooter(s, 15);
}

// ═══ SLIDE 16 — Future Scope ═══════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.off };
  sectionHeader(s, "15", "Future Scope", "Where this goes next");
  const phases = [
    { q: "NEXT",   title: "AI Voice Interviewer", color: C.indigo,
      points: ["OpenAI Realtime API / LiveKit", "15-min screening call in browser", "Adaptive follow-up questions", "Post-call rubric scoring"] },
    { q: "LATER",  title: "Enterprise Features",  color: C.violet,
      points: ["Multi-tenant workspaces + SSO", "Calendar sync (Google/Outlook)", "Webhook events + Zapier", "Role-based permissions"] },
    { q: "VISION", title: "Platform Expansion",   color: C.mint,
      points: ["Candidate self-service portal", "ATS integrations (Greenhouse, Lever)", "EEOC / DPDP compliance exports", "Mobile recruiter app"] },
  ];
  phases.forEach((p, i) => {
    const x = 0.5 + i * (4.15 + 0.1);
    s.addShape("roundRect", { x, y: 1.8, w: 4.15, h: 4.8, fill: { color: C.white }, line: { color: C.line, width: 0.75 }, rectRadius: 0.15 });
    s.addShape("roundRect", { x, y: 1.8, w: 4.15, h: 0.95, fill: { color: p.color }, line: { type: "none" }, rectRadius: 0.15 });
    s.addShape("roundRect", { x: x + 0.3, y: 2.0, w: 1.0, h: 0.3, fill: { color: C.white }, line: { type: "none" }, rectRadius: 0.15 });
    s.addText(p.q, { x: x + 0.3, y: 2.0, w: 1.0, h: 0.3, fontSize: 10, bold: true, color: p.color, align: "center", valign: "middle", fontFace: FONT_H, charSpacing: 2 });
    s.addText(p.title, { x: x + 0.3, y: 2.3, w: 3.55, h: 0.45, fontSize: 17, bold: true, color: C.white, fontFace: FONT_H, valign: "middle" });
    p.points.forEach((pt, j) => {
      const ly = 3.0 + j * 0.85;
      s.addText("›", { x: x + 0.3, y: ly, w: 0.3, h: 0.5, fontSize: 20, bold: true, color: p.color, fontFace: FONT_H });
      s.addText(pt, { x: x + 0.65, y: ly, w: 3.2, h: 0.75, fontSize: 12, color: C.dark, fontFace: FONT_B, valign: "top" });
    });
  });
  addFooter(s, 16);
}

// ═══ SLIDE 17 — Thank You ══════════════════════════════════════════
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addShape("ellipse", { x: -2, y: -2, w: 6, h: 6, fill: { color: C.indigo, transparency: 75 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 9.5, y: 4, w: 5, h: 5, fill: { color: C.violet, transparency: 80 }, line: { type: "none" } });
  s.addShape("rect", { x: 0, y: 7.4, w: 13.333, h: 0.1, fill: { color: C.mint }, line: { type: "none" } });
  s.addText("Thank You", { x: 0.9, y: 2.4, w: 11.5, h: 1.6, fontSize: 96, bold: true, color: C.white, fontFace: FONT_H });
  s.addShape("line", { x: 0.9, y: 4.1, w: 2.0, h: 0, line: { color: C.mint, width: 3 } });
  s.addText("Questions, live demo, or deep dive?", { x: 0.9, y: 4.3, w: 11.5, h: 0.6, fontSize: 22, color: C.ice, fontFace: FONT_B, italic: true });
  s.addText([
    { text: "Live: ",   options: { bold: true, color: C.mint,  fontSize: 14 } },
    { text: "ai-ats-app.azurewebsites.net", options: { color: C.white, fontSize: 14 } },
    { text: "     Repo: ", options: { bold: true, color: C.mint, fontSize: 14 } },
    { text: "github.com/shahrukh120/capstone", options: { color: C.white, fontSize: 14 } },
  ], { x: 0.9, y: 5.7, w: 11.5, h: 0.5, fontFace: FONT_B });
  s.addText("Shahrukh Khan  ·  Capstone  ·  2026", { x: 0.9, y: 6.8, w: 11.5, h: 0.3, fontSize: 11, color: C.ice, fontFace: FONT_B, italic: true });
}

pptx.writeFile({ fileName: "ATS_Presentation.pptx" }).then((f) => console.log("Wrote", f));
