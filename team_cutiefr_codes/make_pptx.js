const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "ReflectAI — NHAI Innovation Hackathon";

// ── Color Palette (NHAI Highway theme) ──────────────────────
const C = {
  navyDark:   "0A2342",
  navy:       "00467F",
  blue:       "0080C0",
  lightBlue:  "4DB8FF",
  white:      "FFFFFF",
  offWhite:   "F0F6FF",
  green:      "28A745",
  orange:     "FD7E14",
  red:        "DC3545",
  grayDark:   "2D3748",
  grayMid:    "718096",
  grayLight:  "E8F0FE",
  yellow:     "FFC107",
};

// ── Helper: title bar ────────────────────────────────────────
function addTitleBar(slide, text, sub) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.15,
    fill: { color: C.navyDark },
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 1.15, w: 10, h: 0.06,
    fill: { color: C.blue },
  });
  slide.addText(text, {
    x: 0.4, y: 0.1, w: 9.2, h: 0.7,
    fontSize: 26, bold: true, color: C.white, fontFace: "Calibri",
    margin: 0,
  });
  if (sub) {
    slide.addText(sub, {
      x: 0.4, y: 0.78, w: 9.2, h: 0.35,
      fontSize: 13, color: C.lightBlue, fontFace: "Calibri",
      margin: 0,
    });
  }
}

// ── Helper: stat card ────────────────────────────────────────
function statCard(slide, x, y, w, h, num, label, color) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: color || C.navy },
    shadow: { type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.2 },
  });
  slide.addText(num, {
    x, y: y + 0.08, w, h: h * 0.55,
    fontSize: 32, bold: true, color: C.white, align: "center",
    fontFace: "Calibri", margin: 0,
  });
  slide.addText(label, {
    x, y: y + h * 0.58, w, h: h * 0.38,
    fontSize: 11, color: "AECBF5", align: "center",
    fontFace: "Calibri", margin: 0,
  });
}

// ── Helper: bullet block ─────────────────────────────────────
function bulletBlock(slide, x, y, w, h, title, bullets, titleColor) {
  slide.addText(title, {
    x, y, w, h: 0.35,
    fontSize: 14, bold: true,
    color: titleColor || C.navy, fontFace: "Calibri", margin: 0,
  });
  const items = bullets.map((b, i) => ({
    text: b,
    options: { bullet: true, breakLine: i < bullets.length - 1, fontSize: 12, color: C.grayDark }
  }));
  slide.addText(items, { x, y: y + 0.38, w, h: h - 0.38, fontFace: "Calibri", paraSpaceAfter: 4 });
}

// ════════════════════════════════════════════════════════════
// SLIDE 1 — TITLE
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navyDark };

  // Big gradient band
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 1.5, w: 10, h: 2.8,
    fill: { color: C.navy },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 1.5, w: 0.18, h: 2.8,
    fill: { color: C.blue },
  });

  s.addText("🛣️ ReflectAI", {
    x: 0.5, y: 0.5, w: 9, h: 0.9,
    fontSize: 44, bold: true, color: C.white, fontFace: "Calibri", align: "center",
  });
  s.addText("AI-Powered Retroreflectivity Measurement System", {
    x: 0.5, y: 1.6, w: 9, h: 0.55,
    fontSize: 20, color: C.lightBlue, fontFace: "Calibri", align: "center",
  });
  s.addText("6th NHAI Innovation Hackathon", {
    x: 0.5, y: 2.2, w: 9, h: 0.45,
    fontSize: 16, color: C.yellow, bold: true, fontFace: "Calibri", align: "center",
  });
  s.addText("YOLOv8 + Grok AI Agent · Automated IRC Compliance · Real-Time Work Orders", {
    x: 0.5, y: 2.72, w: 9, h: 0.45,
    fontSize: 13, color: "AECBF5", fontFace: "Calibri", align: "center",
  });

  // Bottom band
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.85, w: 10, h: 0.775,
    fill: { color: "061428" },
  });
  s.addText("Powered by Groq LLaMA · OpenCV · Ultralytics YOLOv8 · IRC 67:2012 & IRC 35:2015", {
    x: 0.3, y: 4.93, w: 9.4, h: 0.4,
    fontSize: 11, color: C.grayMid, fontFace: "Calibri", align: "center",
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 2 — THE PROBLEM
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addTitleBar(s, "The Problem: India's Highway Safety Crisis", "Why retroreflectivity matters");

  statCard(s, 0.3,  1.4, 2.15, 1.6, "40,000+", "km of National\nHighways (NHAI)", C.navyDark);
  statCard(s, 2.65, 1.4, 2.15, 1.6, "₹8,000+", "per km manual\ninspection cost",  C.navy);
  statCard(s, 5.0,  1.4, 2.15, 1.6, "3 hrs",   "per km with\nhandheld device",    C.blue);
  statCard(s, 7.35, 1.4, 2.15, 1.6, "67%",     "night accidents\nlinked to poor RA", "A83200");

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.3, y: 3.25, w: 9.4, h: 1.55,
    fill: { color: "FFF3CD" },
  });
  s.addText("⚠️  Current Challenge", {
    x: 0.5, y: 3.3, w: 9, h: 0.35,
    fontSize: 14, bold: true, color: "856404", fontFace: "Calibri", margin: 0,
  });
  const probs = [
    "Manual retroreflectometers require lane closures, trained operators, and 3+ hours per km",
    "Subjective inspection misses degraded markings until they cause accidents",
    "No real-time data → reactive maintenance instead of proactive prevention",
    "NHAI cannot affordably survey 40,000 km on regular intervals",
  ];
  const pitems = probs.map((p, i) => ({
    text: p, options: { bullet: true, breakLine: i < probs.length - 1, fontSize: 12, color: "6B4A00" }
  }));
  s.addText(pitems, { x: 0.5, y: 3.65, w: 9, h: 1.05, fontFace: "Calibri" });
}

// ════════════════════════════════════════════════════════════
// SLIDE 3 — OUR SOLUTION
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addTitleBar(s, "ReflectAI Solution", "Camera-equipped vehicle + YOLOv8 + Grok AI Agent");

  const steps = [
    { num: "1", title: "Drive & Capture", desc: "Vehicle-mounted camera captures continuous road footage at highway speed", color: C.navyDark },
    { num: "2", title: "Preprocess", desc: "CLAHE + Gamma + Dehazing adapts images to any lighting or weather condition", color: C.navy },
    { num: "3", title: "YOLOv8 Detect", desc: "Pretrained YOLOv8n detects lane markings, road studs, signs, delineators", color: C.blue },
    { num: "4", title: "Score RA", desc: "Brightness analysis + condition multiplier predicts retroreflectivity (RA) score", color: "0070AA" },
    { num: "5", title: "Grok Agent", desc: "Groq LLaMA AI agent analyses compliance, prioritises issues, generates NHAI work order", color: "005C8A" },
  ];

  steps.forEach((st, i) => {
    const x = 0.28 + i * 1.9;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.4, w: 1.65, h: 2.6, fill: { color: st.color } });
    s.addText(st.num, { x, y: 1.45, w: 1.65, h: 0.55, fontSize: 28, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.0, w: 1.65, h: 0.03, fill: { color: C.lightBlue } });
    s.addText(st.title, { x, y: 2.06, w: 1.65, h: 0.4, fontSize: 11, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0 });
    s.addText(st.desc, { x: x + 0.06, y: 2.5, w: 1.53, h: 1.4, fontSize: 9.5, color: "CCE5FF", align: "center", fontFace: "Calibri" });
    if (i < steps.length - 1) {
      s.addText("→", { x: x + 1.65, y: 2.35, w: 0.25, h: 0.5, fontSize: 18, color: C.navy, align: "center", fontFace: "Calibri" });
    }
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.28, y: 4.2, w: 9.44, h: 0.85,
    fill: { color: C.grayLight },
  });
  s.addText("💡  Result: Survey cost drops from ₹8,000/km to ~₹200/km · Speed increases from 3 hrs/km to highway speed", {
    x: 0.4, y: 4.3, w: 9.2, h: 0.55,
    fontSize: 13, bold: true, color: C.navyDark, align: "center", fontFace: "Calibri",
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 4 — ARCHITECTURE DIAGRAM
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addTitleBar(s, "System Architecture", "End-to-end AI pipeline");

  // Layer boxes
  const layers = [
    { label: "INPUT", text: "Road Image\n(JPG/PNG)", x: 0.3,  color: C.grayDark },
    { label: "STAGE 1", text: "Preprocessing\nCLAHE · Gamma\nDehaze · Denoise", x: 2.2,  color: C.navyDark },
    { label: "STAGE 2", text: "YOLOv8n\nObject Detection\nCOCO Pretrained", x: 4.1,  color: C.navy },
    { label: "STAGE 3", text: "RA Prediction\nBrightness + IRC\nThreshold Check", x: 6.0,  color: C.blue },
    { label: "STAGE 4", text: "Grok Agent\nWork Order\nGeneration",  x: 7.9,  color: "005C8A" },
  ];

  layers.forEach((l, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: l.x, y: 1.5, w: 1.7, h: 2.0, fill: { color: l.color } });
    s.addText(l.label, { x: l.x, y: 1.52, w: 1.7, h: 0.32, fontSize: 9.5, bold: true, color: C.yellow, align: "center", fontFace: "Calibri", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: l.x, y: 1.84, w: 1.7, h: 0.03, fill: { color: C.lightBlue } });
    s.addText(l.text, { x: l.x, y: 1.9, w: 1.7, h: 1.5, fontSize: 10, color: C.white, align: "center", fontFace: "Calibri" });
    if (i < layers.length - 1) {
      s.addText("▶", { x: l.x + 1.7, y: 2.2, w: 0.5, h: 0.6, fontSize: 16, color: C.navy, align: "center" });
    }
  });

  // Output boxes
  const outputs = ["Annotated\nImage", "CSV\nReport", "NHAI\nWork Order", "PDF\nDocument"];
  outputs.forEach((o, i) => {
    const ox = 0.8 + i * 2.15;
    s.addShape(pres.shapes.RECTANGLE, { x: ox, y: 3.75, w: 1.8, h: 0.9, fill: { color: C.grayLight } });
    s.addText(o, { x: ox, y: 3.82, w: 1.8, h: 0.76, fontSize: 11, bold: true, color: C.navyDark, align: "center", fontFace: "Calibri" });
  });
  s.addText("OUTPUT", { x: 0.3, y: 3.78, w: 0.5, h: 0.4, fontSize: 9, bold: true, color: C.grayMid, fontFace: "Calibri" });

  // Tech labels
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 4.85, w: 10, h: 0.775, fill: { color: C.navyDark } });
  s.addText("Stack:  Python · Streamlit · OpenCV · Ultralytics YOLOv8 · PyTorch EfficientNet-B4 · Groq LLaMA (OpenAI-compatible) · FPDF2", {
    x: 0.3, y: 4.93, w: 9.4, h: 0.42,
    fontSize: 11, color: C.lightBlue, fontFace: "Calibri", align: "center",
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 5 — FILE ARCHITECTURE
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addTitleBar(s, "Codebase Architecture", "What each Python file does");

  const files = [
    { file: "reflectai_demo_grok.py", role: "Main App", desc: "Streamlit UI, orchestrates full pipeline, handles uploads, shows results, calls Grok agent", color: C.navyDark },
    { file: "src/agents/maintenance_agent_grok.py", role: "Grok Agent", desc: "Connects to xAI via openai SDK, implements 4 tools (analyze → prioritize → cost → work order), agentic loop", color: C.navy },
    { file: "src/preprocessing/enhance.py", role: "Preprocessor", desc: "CLAHE, gamma correction, dark-channel prior dehazing, wet glare suppression, Gaussian denoise", color: C.blue },
    { file: "src/models/feature_extractor.py", role: "RA Predictor", desc: "EfficientNet-B4 backbone + Gradient Boosting Regressor predicts RA score from ROI image features", color: "0070AA" },
    { file: "src/data/augment.py", role: "Data Aug.", desc: "Synthetic fog, rain, night, motion blur, wet road augmentation to expand training dataset", color: "005C8A" },
  ];

  files.forEach((f, i) => {
    const y = 1.35 + i * 0.82;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y, w: 9.4, h: 0.72,
      fill: { color: i % 2 === 0 ? C.grayLight : C.white },
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 0.12, h: 0.72, fill: { color: f.color } });
    s.addText(f.file, {
      x: 0.55, y: y + 0.04, w: 3.5, h: 0.32,
      fontSize: 11, bold: true, color: f.color, fontFace: "Consolas", margin: 0,
    });
    s.addText(`[${f.role}]`, {
      x: 0.55, y: y + 0.36, w: 1.5, h: 0.26,
      fontSize: 9.5, color: C.grayMid, fontFace: "Calibri", margin: 0,
    });
    s.addText(f.desc, {
      x: 4.2, y: y + 0.1, w: 5.3, h: 0.52,
      fontSize: 11, color: C.grayDark, fontFace: "Calibri",
    });
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 6 — YOLOV8 + PREPROCESSING
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addTitleBar(s, "YOLOv8 Detection + Preprocessing", "Pretrained model + adaptive image enhancement");

  // Left: YOLOv8
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.35, w: 4.3, h: 3.8, fill: { color: C.white },
    shadow: { type: "outer", blur: 8, offset: 2, angle: 135, color: "000000", opacity: 0.1 } });
  s.addText("YOLOv8 Detection", { x: 0.4, y: 1.42, w: 4.1, h: 0.38, fontSize: 14, bold: true, color: C.navyDark, fontFace: "Calibri", margin: 0 });

  const yItems = [
    "Model: yolov8n.pt (pretrained on COCO)",
    "Auto-downloads ~6MB on first run",
    "Detects: lane markings, studs, signs, delineators",
    "COCO class → road element mapping (proxy approach for demo)",
    "Real deployment: fine-tune on NHAI-labeled dataset",
    "Inference: 80+ FPS on CPU, 300+ FPS on GPU",
  ];
  const yi = yItems.map((t, i) => ({
    text: t, options: { bullet: true, breakLine: i < yItems.length - 1, fontSize: 11, color: C.grayDark }
  }));
  s.addText(yi, { x: 0.4, y: 1.88, w: 4.1, h: 2.9, fontFace: "Calibri", paraSpaceAfter: 5 });

  // Right: Preprocessing
  s.addShape(pres.shapes.RECTANGLE, { x: 5.05, y: 1.35, w: 4.65, h: 3.8, fill: { color: C.white },
    shadow: { type: "outer", blur: 8, offset: 2, angle: 135, color: "000000", opacity: 0.1 } });
  s.addText("5-Stage Preprocessing Pipeline", { x: 5.15, y: 1.42, w: 4.45, h: 0.38, fontSize: 14, bold: true, color: C.navyDark, fontFace: "Calibri", margin: 0 });

  const stages = [
    { n: "1", t: "CLAHE", d: "Adaptive contrast for marking visibility" },
    { n: "2", t: "Gamma Correction", d: "Night / low-light image brightening" },
    { n: "3", t: "Dark Channel Prior", d: "He et al. 2009 fog/haze removal" },
    { n: "4", t: "Glare Suppression", d: "Wet road specular highlight removal" },
    { n: "5", t: "Gaussian Denoise", d: "Sensor noise removal" },
  ];
  stages.forEach((st, i) => {
    const y = 1.9 + i * 0.56;
    s.addShape(pres.shapes.RECTANGLE, { x: 5.15, y, w: 0.4, h: 0.4, fill: { color: C.navy } });
    s.addText(st.n, { x: 5.15, y, w: 0.4, h: 0.4, fontSize: 13, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0 });
    s.addText(st.t, { x: 5.65, y: y + 0.02, w: 1.8, h: 0.22, fontSize: 11, bold: true, color: C.navyDark, fontFace: "Calibri", margin: 0 });
    s.addText(st.d, { x: 5.65, y: y + 0.22, w: 3.9, h: 0.22, fontSize: 10, color: C.grayMid, fontFace: "Calibri", margin: 0 });
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 7 — GROK AI AGENT
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addTitleBar(s, "Grok AI Maintenance Agent", "Groq LLaMA with function calling — OpenAI-compatible API");

  // Flow diagram
  const nodes = [
    { t: "Scan\nResults",     color: C.grayDark },
    { t: "analyze_scan\n_results()",   color: C.navyDark },
    { t: "prioritize\n_maintenance()", color: C.navy },
    { t: "estimate\n_repair_cost()",   color: C.blue },
    { t: "generate\n_work_order()",    color: "005C8A" },
    { t: "NHAI Work\nOrder",          color: C.green },
  ];
  nodes.forEach((n, i) => {
    const x = 0.3 + i * 1.6;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.45, w: 1.4, h: 1.1, fill: { color: n.color } });
    s.addText(n.t, { x, y: 1.52, w: 1.4, h: 0.96, fontSize: 10, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
    if (i < nodes.length - 1) {
      s.addText("→", { x: x + 1.4, y: 1.83, w: 0.2, h: 0.36, fontSize: 16, color: C.navy, align: "center" });
    }
  });

  // Code snippet
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 2.75, w: 4.5, h: 2.35, fill: { color: "1E2B3C" } });
  s.addText("# Groq LLaMA — OpenAI-compatible\nfrom groq import Groq\n\nclient = OpenAI(\n    api_key=GROQ_API_KEY,\n    base_url=\"https://api.x.ai/v1\"\n)\n\nresponse = client.chat.completions.create(\n    model=\"llama-3.3-70b-versatile\",\n    messages=messages,\n    tools=AGENT_TOOLS,\n    tool_choice=\"auto\"\n)", {
    x: 0.38, y: 2.8, w: 4.3, h: 2.22,
    fontSize: 9, color: "A8D8FF", fontFace: "Consolas",
  });

  // Features list
  bulletBlock(s, 5.1, 2.75, 4.6, 2.35,
    "Why Grok for This?",
    [
      "OpenAI-compatible — drop-in replacement",
      "llama-3.3-70b-versatile: fast, cost-effective for agentic loops",
      "Native function/tool calling support",
      "Generates professional NHAI work orders",
      "No Anthropic API needed — free xAI quota available",
    ]
  );
}

// ════════════════════════════════════════════════════════════
// SLIDE 8 — IRC COMPLIANCE
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };
  addTitleBar(s, "IRC Compliance Assessment", "IRC 67:2012 & IRC 35:2015 retroreflectivity standards");

  const rows = [
    [{ text: "Road Element", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
     { text: "IRC Standard", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
     { text: "Min RA (mcd·lx⁻¹·m⁻²)", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
     { text: "Warning (<75%)", options: { bold: true, color: C.white, fill: { color: C.navyDark } } }],
    ["Lane Centreline Marking", "IRC 35:2015", "80",  "< 60"],
    ["Edge Lane Marking",       "IRC 35:2015", "80",  "< 60"],
    ["Road Stud / RPM",         "IRC 35:2015", "150", "< 113"],
    ["Shoulder Sign",           "IRC 67:2012", "250", "< 188"],
    ["Gantry Sign",             "IRC 67:2012", "250", "< 188"],
    ["Delineator",              "IRC 35:2015", "100", "< 75"],
  ];

  s.addTable(rows, {
    x: 0.5, y: 1.45, w: 9.0,
    border: { pt: 1, color: "C0D0E0" },
    fontSize: 12, fontFace: "Calibri",
    rowH: 0.44,
    colW: [3.0, 1.8, 2.2, 1.9],
  });

  // Legend
  const legend = [
    { label: "COMPLIANT", desc: "RA ≥ IRC minimum", color: C.green },
    { label: "WARNING",   desc: "RA between 75–100% of minimum", color: C.orange },
    { label: "NON-COMPLIANT", desc: "RA < 75% — immediate action", color: C.red },
  ];
  legend.forEach((l, i) => {
    const x = 0.5 + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 4.65, w: 2.8, h: 0.7, fill: { color: l.color } });
    s.addText(`${l.label}\n${l.desc}`, { x, y: 4.68, w: 2.8, h: 0.64, fontSize: 10, bold: false, color: C.white, align: "center", fontFace: "Calibri" });
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 9 — DEMO RESULTS
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addTitleBar(s, "Live Demo Results", "Sample scan — NH-48 Km 120-180 (Night / Wet / Lights Off)");

  const detections = [
    { el: "Lane Centreline Marking", ra: "85.0", min: "80",  st: "COMPLIANT",     conf: "0.92", gps: "28.6139°N, 77.2090°E" },
    { el: "Edge Lane Marking",        ra: "55.0", min: "80",  st: "WARNING",       conf: "0.88", gps: "28.6142°N, 77.2091°E" },
    { el: "Road Stud / RPM",          ra: "32.0", min: "150", st: "NON-COMPLIANT", conf: "0.95", gps: "28.6145°N, 77.2093°E" },
    { el: "Shoulder Sign",            ra: "320.0",min: "250", st: "COMPLIANT",     conf: "0.97", gps: "28.6148°N, 77.2095°E" },
    { el: "Gantry Sign",              ra: "190.0",min: "250", st: "WARNING",       conf: "0.90", gps: "28.6150°N, 77.2097°E" },
  ];

  const stColors = { "COMPLIANT": "155724", "WARNING": "856404", "NON-COMPLIANT": "721c24" };
  const stBg     = { "COMPLIANT": "D4EDDA", "WARNING": "FFF3CD", "NON-COMPLIANT": "F8D7DA" };

  const header = [
    { text: "Element Type", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
    { text: "RA Score", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
    { text: "IRC Min", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
    { text: "Status", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
    { text: "Conf.", options: { bold: true, color: C.white, fill: { color: C.navyDark } } },
  ];

  const rows = [header, ...detections.map(d => [
    d.el,
    { text: d.ra, options: { bold: true } },
    d.min,
    { text: d.st, options: { bold: true, color: stColors[d.st], fill: { color: stBg[d.st] } } },
    d.conf,
  ])];

  s.addTable(rows, {
    x: 0.3, y: 1.42, w: 9.4,
    border: { pt: 1, color: "C0D0E0" },
    fontSize: 11.5, fontFace: "Calibri",
    rowH: 0.44,
    colW: [3.2, 1.3, 1.2, 2.0, 0.9],
  });

  // Summary badges
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3,  y: 4.25, w: 2.8, h: 0.8, fill: { color: "D4EDDA" } });
  s.addText("✅ 2 Compliant",     { x: 0.3,  y: 4.3,  w: 2.8, h: 0.65, fontSize: 14, bold: true, color: "155724", align: "center", fontFace: "Calibri" });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.4,  y: 4.25, w: 3.0, h: 0.8, fill: { color: "FFF3CD" } });
  s.addText("⚠️ 2 Warning",        { x: 3.4,  y: 4.3,  w: 3.0, h: 0.65, fontSize: 14, bold: true, color: "856404", align: "center", fontFace: "Calibri" });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.7,  y: 4.25, w: 3.0, h: 0.8, fill: { color: "F8D7DA" } });
  s.addText("❌ 1 Non-Compliant",  { x: 6.7,  y: 4.3,  w: 3.0, h: 0.65, fontSize: 14, bold: true, color: "721c24", align: "center", fontFace: "Calibri" });
}

// ════════════════════════════════════════════════════════════
// SLIDE 10 — IMPACT & ROI
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navyDark };
  addTitleBar(s, "Impact & ROI", "ReflectAI vs Traditional Survey Methods");

  const cols = [
    { title: "Traditional Method", items: ["₹8,000+ per km", "3 hours per km", "Lane closures required", "Inspector subjectivity", "Quarterly surveys at best", "Paper-based reports"], color: "A83200" },
    { title: "ReflectAI", items: ["~₹200 per km", "Highway speed (100 km/hr)", "No disruption to traffic", "Objective AI measurement", "Continuous monitoring", "Automated work orders"], color: C.green },
  ];

  cols.forEach((col, i) => {
    const x = 0.4 + i * 4.8;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.35, w: 4.3, h: 0.5, fill: { color: col.color } });
    s.addText(col.title, { x, y: 1.38, w: 4.3, h: 0.44, fontSize: 16, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0 });
    col.items.forEach((item, j) => {
      const bg = j % 2 === 0 ? "1A3050" : "162840";
      s.addShape(pres.shapes.RECTANGLE, { x, y: 1.9 + j * 0.46, w: 4.3, h: 0.44, fill: { color: bg } });
      const icon = i === 1 ? "✓ " : "✗ ";
      s.addText(`${icon}${item}`, {
        x: x + 0.15, y: 1.95 + j * 0.46, w: 4.0, h: 0.32,
        fontSize: 12, color: i === 1 ? "90EE90" : "FF9999", fontFace: "Calibri", margin: 0,
      });
    });
  });

  // Big numbers
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 4.72, w: 9.4, h: 0.83, fill: { color: C.navy } });
  s.addText("40× faster   ·   97% cost reduction   ·   24/7 operation   ·   Zero lane closures", {
    x: 0.3, y: 4.82, w: 9.4, h: 0.52,
    fontSize: 16, bold: true, color: C.yellow, align: "center", fontFace: "Calibri",
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 11 — IMPLEMENTATION GUIDE
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  addTitleBar(s, "Quick-Start Implementation", "From zero to running demo in 5 commands");

  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.35, w: 9.4, h: 3.55, fill: { color: "0D1B2A" } });

  const lines = [
    { t: "# 1. Install all dependencies", c: "6A9153" },
    { t: "pip install -r requirements.txt", c: "9CDCFE" },
    { t: "", c: "FFFFFF" },
    { t: "# 2. Get your free Grok API key at console.groq.com", c: "6A9153" },
    { t: "export GROQ_API_KEY=gsk_your_key-here", c: "9CDCFE" },
    { t: "", c: "FFFFFF" },
    { t: "# 3. Run the Streamlit application", c: "6A9153" },
    { t: "streamlit run reflectai_demo_grok.py", c: "DCDCAA" },
    { t: "", c: "FFFFFF" },
    { t: "# 4. Open browser → http://localhost:8501", c: "6A9153" },
    { t: "# 5. Upload road image → detect → generate work order", c: "6A9153" },
  ];

  lines.forEach((l, i) => {
    s.addText(l.t, {
      x: 0.55, y: 1.48 + i * 0.28, w: 8.9, h: 0.27,
      fontSize: 11.5, color: l.c, fontFace: "Consolas", margin: 0,
    });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 5.07, w: 9.4, h: 0.48, fill: { color: C.grayLight } });
  s.addText("YOLOv8 weights (yolov8n.pt) download automatically on first run  ·  All dependencies in requirements.txt", {
    x: 0.4, y: 5.12, w: 9.2, h: 0.35,
    fontSize: 11, color: C.navyDark, align: "center", fontFace: "Calibri",
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 12 — THANK YOU
// ════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navyDark };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.6, w: 10, h: 2.65, fill: { color: C.navy } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.6, w: 0.2, h: 2.65, fill: { color: C.yellow } });

  s.addText("🛣️ ReflectAI", {
    x: 0.5, y: 0.4, w: 9, h: 0.9,
    fontSize: 40, bold: true, color: C.white, align: "center", fontFace: "Calibri",
  });
  s.addText("Thank You!", {
    x: 0.5, y: 1.7, w: 9, h: 0.65,
    fontSize: 34, bold: true, color: C.yellow, align: "center", fontFace: "Calibri",
  });
  s.addText("AI-Powered Retroreflectivity — Making Indian Highways Safer at Night", {
    x: 0.5, y: 2.45, w: 9, h: 0.45,
    fontSize: 15, color: C.lightBlue, align: "center", fontFace: "Calibri",
  });
  s.addText("YOLOv8 + Groq LLaMA + OpenCV + IRC 67 / IRC 35", {
    x: 0.5, y: 2.95, w: 9, h: 0.35,
    fontSize: 13, color: "AECBF5", align: "center", fontFace: "Calibri",
  });

  const contacts = [
    "📦  github.com/your-team/reflectai",
    "🔑  console.groq.com  (Grok API key)",
    "📘  docs.ultralytics.com  (YOLOv8)",
    "📋  6th NHAI Innovation Hackathon  2025",
  ];
  contacts.forEach((c, i) => {
    s.addText(c, {
      x: 2.5, y: 3.55 + i * 0.35, w: 6.5, h: 0.32,
      fontSize: 12, color: "AECBF5", fontFace: "Calibri", align: "center",
    });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.2, w: 10, h: 0.425, fill: { color: "061428" } });
  s.addText("Safer highways · Smarter maintenance · AI-driven compliance", {
    x: 0.3, y: 5.27, w: 9.4, h: 0.3,
    fontSize: 11, color: C.grayMid, align: "center", fontFace: "Calibri",
  });
}

// ── Write file ───────────────────────────────────────────────
pres.writeFile({ fileName: "/home/claude/reflectai_groq/outputs/ReflectAI_NHAI_Presentation.pptx" })
  .then(() => console.log("✅ Presentation saved"))
  .catch(e => { console.error(e); process.exit(1); });
