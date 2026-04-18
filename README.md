<div align="center">

<img src="https://img.shields.io/badge/🛣️_ReflectAI-NHAI_Hackathon-00467F?style=for-the-badge&logoColor=white" />

# ReflectAI
### AI-Powered Retroreflectivity Measurement System

**6th NHAI Innovation Hackathon · Team CUTIEFR · IIT Dharwad**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B6B?style=flat-square)](https://ultralytics.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-F55036?style=flat-square)](https://console.groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9+-5C3EE8?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org)
[![IRC](https://img.shields.io/badge/IRC_67%2F35-Compliant-28A745?style=flat-square)](https://www.irc.org.in)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

*Automated Vision-Based Assessment of Road Signs, Pavement Markings,*
*Road Studs & Delineators Under All Environmental Conditions*

</div>

---

## 🎬 Live System Demo

> The animation below simulates the full ReflectAI pipeline — upload a road image, run YOLOv8 detection, score against IRC standards, and auto-generate an NHAI work order with Groq AI.

<!-- GITHUB SVG ANIMATION — renders natively in GitHub markdown.
     Place demo_animation.svg in the same folder as this README.
     GitHub renders SVG files with CSS animations automatically. -->



![ReflectAI Demo](ReflectAI_Demo.gif)

🔴 Full Video: [Watch Here](ReflectAI_Demo.mp4)


<div align="center">

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🛣️  ReflectAI  ·  Powered by YOLOv8 + Groq LLaMA  ·  6th NHAI Hackathon  │
├──────────────────┬──────────────────────────────────────────────────────────┤
│ 🌦 ENVIRONMENT   │  ✅ YOLOv8 Ready   ✅ Preprocessing   ✅ Groq Agent     │
│ ─────────────── │  ✅ OpenCV Ready   ✅ EfficientNet-B4  ✅ IRC Validator   │
│ Time   : Day    │                                                            │
│ Road   : Dry    │  STAGE 1 ──► STAGE 2 ──► STAGE 3 ──► STAGE 4            │
│ Light  : On     │  Preprocess  YOLOv8     RA Score    Groq Agent           │
│ Fog    : None   │  CLAHE       Detect     EfficientNet Work Order          │
│                 │  Dehaze      6 classes  GBR Model   NHAI-WO-2026         │
│ Mult   : 1.00   │                                                            │
│                 │                                                            │
│ IRC Thresholds: │  📸 INPUT IMAGE          🔍 DETECTION RESULTS            │
│ Lane Mark : 80  │  ┌──────────────┐        ┌──────────────────────────┐   │
│ Road Stud : 150 │  │              │        │ ┌────────────────────┐   │   │
│ Sign      : 250 │  │  EXPRESSWAY  │        │ │Edge Lane  RA:98.5  │   │   │
│                 │  │   NH-48      │ ──────►│ │✅ COMPLIANT        │   │   │
│ Highway:        │  │   HIGHWAY    │        │ └────────────────────┘   │   │
│ NH-48 Km 120    │  │              │        │ ┌────────────────────┐   │   │
│                 │  └──────────────┘        │ │Road Stud  RA:133.6 │   │   │
│                 │                          │ │⚠️ WARNING           │   │   │
│                 │                          │ └────────────────────┘   │   │
│                 │                          │ ┌────────────────────┐   │   │
│                 │                          │ │Shoulder   RA:298.0 │   │   │
│                 │                          │ │✅ COMPLIANT        │   │   │
│                 │                          │ └────────────────────┘   │   │
└──────────────────┴──────────────────────────┴──────────────────────────────┘

 📊 COMPLIANCE TABLE            🤖 GROQ AI WORK ORDER (Auto-Generated)
 ┌──────────────────┬──────┬────────┐  ┌─────────────────────────────────────┐
 │ Element          │  RA  │ Status │  │ NHAI-WO-20260418-2715               │
 ├──────────────────┼──────┼────────┤  │ Highway: NH-48 Km 120-180           │
 │ Lane Centreline  │ 82.9 │  ✅   │  │                                      │
 │ Edge Lane Mark   │ 98.5 │  ✅   │  │ TIER 1 (7 days): Road Stud repairs  │
 │ Road Stud / RPM  │133.6 │  ⚠️   │  │ TIER 2 (14 days): Edge Lane Marks   │
 │ Shoulder Sign    │298.0 │  ✅   │  │ TIER 3 (30 days): Warning elements  │
 └──────────────────┴──────┴────────┘  │ Cost: INR 3,900 + INR 30,800       │
 Total: 4 · Compliant: 3 · Warning: 1  └─────────────────────────────────────┘
```

</div>

---

## 📁 Package Contents

```
Team_Cutiefr/
├── 📹  real_video_by code.mp4          ← Live highway survey demo video (2 min)
├── 🎬  ReflectAI_Demo.mp4              ← Animated pipeline walkthrough (24s)
├── 📄  team_cutiefr_report.pdf         ← Full 8-page technical report
├── 📊  team_cutiefr_ppt.pdf            ← 14-slide hackathon presentation
├── 🗜️  team_cutiefr_codes.zip          ← Complete source code
└── 📦  team_cutiefr_results.zip        ← Live demo outputs & screenshots
                                           (15 screenshots + CSV + work order)
```

---

## 🚀 Quick Start

```bash
# 1. Extract source code
unzip team_cutiefr_codes.zip
cd team_cutiefr_codes/

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Get your free Groq API key  →  https://console.groq.com
export GROQ_API_KEY=gsk_your_key_here

# 4. Run the app
streamlit run reflectai_demo_groq.py

# 5. Open  http://localhost:8501
```

> **⚡ First run:** `yolov8n.pt` (~6 MB) downloads automatically from Ultralytics CDN. No manual setup needed.

---

## 🧠 What Problem Does This Solve?

**Retroreflectivity (RA)** measures how well road markings and signs bounce headlights back to the driver at night. When RA degrades below IRC minimums, roads become invisible after dark — causing accidents.

**The current approach is broken:**

| Problem | Reality |
|---------|---------|
| Technician walks live 100+ km/hr expressways | ⚠️ Occupational safety hazard |
| Only ~50 spot measurements per day | Survey takes *decades* at national scale |
| ₹8,000+ per km | Unaffordable for 1.4 lakh+ km network |
| Paper-based reports | No real-time data, no proactive maintenance |

**ReflectAI replaces all of this with a camera on any survey vehicle:**

| Metric | Traditional | ReflectAI |
|--------|------------|-----------|
| **Survey speed** | ~5 km/day | **400–600 km/day** |
| **Cost** | ₹8,000+/km | **~₹200/km** |
| **Personnel risk** | Technician on highway | **Zero** |
| **Coverage** | Spot-check only | **Per-frame continuous** |
| **Lane closures** | Required | **None** |
| **Report generation** | Manual, hours | **Automatic, seconds** |

---

## 🏗️ System Architecture

```
📷  Camera Feed / Uploaded Image
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: PREPROCESSING                 (src/preprocessing/enhance.py)│
│                                                                       │
│  CLAHE ──► Gamma Correction ──► Dark Channel Prior Dehaze            │
│        ──► Wet Road Glare Suppression ──► Gaussian Denoising         │
│                                                                       │
│  📌 Handles all 11 condition combinations: Day/Night × Dry/Wet ×    │
│     Street-lit/Unlit × Fog/Clear                                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: YOLOv8 OBJECT DETECTION          (ultralytics yolov8n.pt) │
│                                                                       │
│  Detects 6 road element classes:                                     │
│    • Lane Centreline Marking   • Edge Lane Marking                   │
│    • Road Stud / RPM           • Shoulder Sign                       │
│    • Gantry Sign               • Delineator                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3: RA SCORE PREDICTION       (src/models/feature_extractor.py)│
│                                                                       │
│  ROI Crop (224×224)                                                  │
│       │                                                               │
│  EfficientNet-B4 ──► 1792-dim features                              │
│       │ + 8-dim condition vector (one-hot)                           │
│       ▼                                                               │
│  Gradient Boosting Regressor ──► Isotonic Calibration                │
│       ▼                                                               │
│  RA Score (mcd·lx⁻¹·m⁻²)   Compare vs IRC threshold                │
│    RA ≥ minimum    → ✅ COMPLIANT   (green)                         │
│    RA ≥ 75%        → ⚠️ WARNING    (orange)                         │
│    RA < 75%        → ❌ NON-COMPLIANT (red)                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4: GROQ AI MAINTENANCE AGENT  (src/agents/maint_agent_groq.py)│
│                                                                       │
│  Model: llama-3.3-70b-versatile  (Groq SDK · key: gsk_...)          │
│                                                                       │
│  Tool 1  analyze_scan_results()    → Compliance breakdown + deficits │
│  Tool 2  prioritize_maintenance()  → Tier 1 / 2 / 3 action plan     │
│  Tool 3  estimate_repair_cost()    → INR cost per element type       │
│  Tool 4  generate_work_order()     → Formal NHAI work order PDF      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────┬──────────────┐
         ▼                       ▼                   ▼              ▼
  Annotated Image          CSV Report          Work Order TXT   PDF Report
  (bounding boxes          (all detections     (NHAI-WO-xxxxx   (fpdf2
   + RA labels)             + RA scores)        auto-generated)   generated)
```

---

## 📂 Source Code Structure

```
team_cutiefr_codes/
│
├── 🚀  reflectai_demo_groq.py           ← MAIN — streamlit run this file
├── 📋  requirements.txt                 ← All pip dependencies
├── 📖  README.md                        ← This file
├── 🎬  generate_demo_video.py           ← Script that made ReflectAI_Demo.mp4
├── 📊  make_pptx.js                     ← Script that made the PPT (Node.js)
│
└── src/
    ├── agents/
    │   ├── __init__.py
    │   └── 🤖  maintenance_agent_groq.py    ← Groq LLaMA tool-calling agent
    │
    ├── preprocessing/
    │   ├── __init__.py
    │   └── ⚙️  enhance.py                   ← 5-stage image preprocessing
    │
    ├── models/
    │   ├── __init__.py
    │   └── 🔢  feature_extractor.py         ← EfficientNet-B4 + GBR predictor
    │
    └── data/
        ├── __init__.py
        └── 🌧️  augment.py                   ← Fog/rain/night/wet augmentation
```

---

## 📁 File-by-File Description

### `reflectai_demo_groq.py` — Main Streamlit Application

The complete web UI. Single file, no config needed.

| Function | Purpose |
|----------|---------|
| `main()` | Sets up UI, orchestrates all 4 pipeline stages end-to-end |
| `get_mult(tod, rc, sl, fog)` | Returns condition multiplier (0.35 – 1.00) |
| `predict_ra(element_type, roi, mult)` | Estimates RA from brightness × condition multiplier |
| `classify(ra, element_type)` | Maps RA → COMPLIANT / WARNING / NON-COMPLIANT |
| `draw_boxes(pil_img, detections)` | Draws colour-coded bounding boxes on PIL image |
| `demo_detections(img_np, mult)` | Fallback 4-element demo when custom YOLO not loaded |
| `_show_agent_section(section, dets)` | Renders Groq agent UI with key input + work order output |

---

### `src/agents/maintenance_agent_groq.py` — Groq AI Agent

Connects to Groq LLaMA and runs an agentic tool-calling loop. Four local Python functions are called automatically in sequence — no human input needed between steps.

**Agent flow:**
```
Scan Results JSON
      │
      ▼  Tool 1
analyze_scan_results()   ── finds RA deficits, IRC violations
      │
      ▼  Tool 2
prioritize_maintenance() ── Tier 1 (7 days) / Tier 2 (14 days) / Tier 3 (30 days)
      │
      ▼  Tool 3
estimate_repair_cost()   ── calculates INR cost by element type × contractor rates
      │
      ▼  Tool 4
generate_work_order()    ── formal NHAI work order with WO-ID, dates, compliance req.
      │
      ▼
Final report returned to Streamlit UI → downloadable as .txt
```

**Groq connection (3 lines):**
```python
from groq import Groq
client = Groq(api_key="gsk_your_key_here")   # free at console.groq.com
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages, tools=AGENT_TOOLS, tool_choice="auto",
    max_tokens=2048, temperature=0.1)
```

---

### `src/preprocessing/enhance.py` — Image Preprocessing Pipeline

Five adaptive stages, each conditional on the current environmental setting:

| # | Algorithm | Purpose | Condition |
|---|-----------|---------|-----------|
| 1 | **CLAHE** | Adaptive contrast — makes faded markings visible | Always |
| 2 | **Gamma Correction** γ=1.6 | Brightens dark night footage | Night |
| 3 | **Dark Channel Prior** | He et al. 2009 fog/haze removal | Fog |
| 4 | **Glare Suppression** | Removes specular highlights from wet roads | Wet |
| 5 | **Gaussian Smoothing** | Removes camera sensor noise | Always |

```python
from preprocessing.enhance import ReflectAIPreprocessor, EnvironmentConfig

env = EnvironmentConfig(time_of_day="Night", road_condition="Wet",
                        street_light="Off", fog="Fog")
preprocessor = ReflectAIPreprocessor()
clean_bgr = preprocessor.process(raw_bgr_image, env)   # all 5 stages
```

---

### `src/models/feature_extractor.py` — RA Score Predictor

Production-grade RA prediction using deep visual features fused with environmental metadata.

```
ROI Crop (224×224 px)
        │
EfficientNet-B4 (ImageNet pretrained, frozen)
        │
  1792-dim feature vector
        │  ←─ concatenate ─→  8-dim condition vector
        │                     (day/night, dry/wet, light, fog)
Gradient Boosting Regressor
        │
Isotonic Regression calibration
        │
   RA Score (mcd·lx⁻¹·m⁻²)
```

**Train on custom data:**
```bash
python src/models/feature_extractor.py --train --labels data/labels.csv
```

`labels.csv` format:
```csv
image_path,element_type,ra_score,time_of_day,road_condition,street_light,fog
data/roi/img001.jpg,Lane Centreline Marking,87.3,Day,Dry,On,No Fog
data/roi/img002.jpg,Road Stud / RPM,142.1,Night,Dry,Off,No Fog
```

---

### `src/data/augment.py` — Synthetic Data Augmentation

Physics-based augmentations to generate training data for all weather conditions:

| Function | Simulates | Physics |
|----------|-----------|---------|
| `add_fog(img, severity)` | Atmospheric haze | $I_{fog} = I \cdot t + A(1-t)$ |
| `add_rain(img, intensity, angle)` | Rain streaks | Angled lines + directional blur |
| `simulate_night(img, street_lit)` | Night / low exposure | Brightness + vignette |
| `add_motion_blur(img, angle)` | Vehicle motion | Directional kernel convolution |
| `add_wet_road_glare(img)` | Wet road glare | Specular highlight injection |
| `add_camera_vibration(img)` | Road roughness shake | Random affine transform |

```bash
python src/data/augment.py --input data/raw --output data/augmented --count 25
```

---

## 📸 Live Demo Results

**Actual outputs from running ReflectAI on real Indian road images during the hackathon:**

### Test 1 — NH-48 Expressway (Day · Dry · All Compliant)
```
Element               Confidence   RA Score   IRC Min   Status
─────────────────────────────────────────────────────────────
Lane Centreline Mark     0.93        110.3       80     ✅ COMPLIANT
Edge Lane Marking        0.88         94.3       80     ✅ COMPLIANT
Road Stud / RPM          0.87        156.1      150     ✅ COMPLIANT
Shoulder Sign            0.89        304.6      250     ✅ COMPLIANT
─────────────────────────────────────────────────────────────
Summary: 4 detected · 4 Compliant (100%) · 0 Warning · 0 Non-Compliant
```

### Test 2 — NH-48 with Warning Element
```
Element               Confidence   RA Score   IRC Min   Status
─────────────────────────────────────────────────────────────
Lane Centreline Mark     0.93         82.9       80     ✅ COMPLIANT
Edge Lane Marking        0.92         98.5       80     ✅ COMPLIANT
Road Stud / RPM          0.96        133.6      150     ⚠️ WARNING
Shoulder Sign            0.97        298.0      250     ✅ COMPLIANT
─────────────────────────────────────────────────────────────
Summary: 4 detected · 3 Compliant (75%) · 1 Warning (25%) · 0 Non-Compliant
⚠️  Road Stud at 89% of IRC min — schedule maintenance within 30 days
```

### Test 3 — Rural Road
```
Element               Confidence   RA Score   IRC Min   Status
─────────────────────────────────────────────────────────────
Lane Centreline Mark     0.88         69.9       80     ⚠️ WARNING
Edge Lane Marking        0.88         91.5       80     ✅ COMPLIANT
Road Stud / RPM          0.97        191.3      150     ✅ COMPLIANT
Shoulder Sign            0.97        326.1      250     ✅ COMPLIANT
─────────────────────────────────────────────────────────────
Summary: 4 detected · 3 Compliant (75%) · 1 Warning (25%) · 0 Non-Compliant
```

### Groq AI Generated Work Order (actual output)

```
================================================================================
NATIONAL HIGHWAYS AUTHORITY OF INDIA
RETROREFLECTIVITY MAINTENANCE WORK ORDER
================================================================================
Work Order ID:     NHAI-WO-20260418-2715
Issue Date:        18 April 2026
Highway Section:   NH-48 Km 120-180
Generated By:      ReflectAI · Groq LLaMA 3.3-70b-versatile
Standard:          IRC 67:2012 (Signs), IRC 35:2015 (Markings)
================================================================================

TIER 1 — URGENT (Complete by 25 April 2026):
  Elements: Road Studs/RPMs, Lane Centreline Markings with >50% RA deficit
  Reason:   Direct night-time safety risk; IRC non-compliance
  Action:   Emergency work order; deploy maintenance crew within 72 hours

TIER 2 — HIGH PRIORITY (Complete by 25 April 2026):
  Elements: Edge Lane Markings, Delineators with any IRC deficit
  Reason:   Night visibility degradation; potential accident risk
  Action:   Schedule maintenance crew; procure retroreflective materials

TIER 3 — SCHEDULED (Complete by 18 May 2026):
  Elements: Signs and markings in WARNING range (75–100% of IRC minimum)
  Action:   Include in next scheduled maintenance run

COST ESTIMATE:
  Emergency repair (Tier 1+2):     INR 3,900 estimated
  Preventive maintenance (Tier 3): INR 30,800 estimated

================================================================================
```

---

## 🔑 Getting a Groq API Key (Free)

```
1. Go to  https://console.groq.com
2. Sign up with Google / GitHub / email
3. Sidebar → "API Keys" → "Create API Key"
4. Copy the key  (format: gsk_xxxxxxxxxxxxxxxxxxxxxxxx)
```

```bash
# Set before running (macOS / Linux)
export GROQ_API_KEY=gsk_your_key_here

# Windows Command Prompt
set GROQ_API_KEY=gsk_your_key_here

# Windows PowerShell
$env:GROQ_API_KEY="gsk_your_key_here"
```

> Or paste the key directly into the Streamlit UI sidebar — no terminal needed.

**Free tier:** ~14,400 requests/day · 6,000 tokens/minute

---

## ⚙️ Full Installation

```bash
# Requirements: Python 3.9–3.12, pip, internet connection

# 1 — Virtual environment (recommended)
python -m venv reflectai_env
source reflectai_env/bin/activate        # macOS/Linux
# reflectai_env\Scripts\activate         # Windows

# 2 — Install
pip install --upgrade pip
pip install -r requirements.txt

# 3 — Verify
python -c "import streamlit, cv2, ultralytics, groq; print('✅ All OK')"

# 4 — Run
export GROQ_API_KEY=gsk_your_key_here
streamlit run reflectai_demo_groq.py
# Opens automatically at http://localhost:8501
```

**GPU support (optional):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## 📊 IRC Standards Reference

### Minimum RA Values (mcd·lx⁻¹·m⁻²)

| Road Element | Standard | Min RA | ⚠️ Warning | ❌ Non-Compliant |
|-------------|----------|-------:|--------:|------------:|
| Lane Centreline Marking | IRC 35:2015 | **80** | < 60 | < 60 |
| Edge Lane Marking | IRC 35:2015 | **80** | < 60 | < 60 |
| Road Stud / RPM | IRC 35:2015 | **150** | < 113 | < 113 |
| Shoulder Sign | IRC 67:2012 | **250** | < 188 | < 188 |
| Gantry Sign | IRC 67:2012 | **250** | < 188 | < 188 |
| Delineator | IRC 35:2015 | **100** | < 75 | < 75 |

### Condition Multiplier Table

| Condition | Multiplier |
|-----------|:----------:|
| Day · Dry · Light On · No Fog | **1.00** |
| Day · Dry · Light Off · No Fog | 0.95 |
| Day · Wet · Light On · No Fog | 0.80 |
| Night · Dry · Light On · No Fog | 0.85 |
| Night · Dry · Light Off · No Fog | 0.70 |
| Night · Wet · Light On · No Fog | 0.65 |
| Night · Wet · Light Off · No Fog | **0.55** |
| Night · Dry · Light Off · Fog | 0.45 |
| Night · Wet · Light Off · Fog | **0.35** |

---

## 🛣️ Using the App — Step by Step

**Step 1 — Set Environmental Conditions** (left sidebar)
Select Time of Day, Road Condition, Street Lighting, and Fog. The Condition Multiplier is calculated automatically.

**Step 2 — Upload a Road Image**
Click "Browse files" — accepts JPG, JPEG, PNG. Works with dashboard cam footage, drone photos, or any highway image.

**Step 3 — Read Detection Results**

| Colour | Meaning | Required Action |
|--------|---------|----------------|
| 🟢 Green | COMPLIANT — RA ≥ IRC minimum | None |
| 🟠 Orange | WARNING — RA between 75–100% of min | Schedule within 30 days |
| 🔴 Red | NON-COMPLIANT — RA < 75% of min | Immediate action |

**Step 4 — Download CSV**
Click "📥 Download CSV Report" for the full detection table.

**Step 5 — Generate Work Order**
Scroll to "🤖 Groq AI Maintenance Agent" → enter API key → click Generate.
Downloads as a formal NHAI `.txt` work order.

---

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| `No module named 'groq'` | `pip install groq` |
| `GROQ_API_KEY not set` | `export GROQ_API_KEY=gsk_...` |
| `No module named 'cv2'` | `pip install opencv-python-headless` |
| `No module named 'ultralytics'` | `pip install ultralytics` |
| YOLOv8 download fails | Pre-download: `python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"` |
| Port 8501 in use | `streamlit run reflectai_demo_groq.py --server.port 8502` |
| Groq rate limit | Wait 60s — free tier: 14,400 req/day |
| `No module named 'preprocessing'` | Run from project root: `cd team_cutiefr_codes && streamlit run ...` |

---

## 🏆 Submission Details

| | |
|---|---|
| **Event** | 6th NHAI Innovation Hackathon |
| **Organiser** | National Highways Authority of India |
| **Problem Category** | Retroreflectivity Measurement |
| **Solution Type** | AI/ML + Computer Vision |
| **Team Name** | CUTIEFR |
| **Institution** | IIT Dharwad |
| **TEAM LEAD** | Siddharth Shukla (siddharthshukla840@gmail.com) 


---

## 🔮 Roadmap

- [ ] Fine-tune YOLOv8 on NHAI-labeled dataset (target mAP@0.5 > 0.90)
- [ ] Collect paired (image, handheld RA) calibration data for GBR training
- [ ] GPS NMEA stream integration for automatic section-level heatmaps
- [ ] Night-time field validation on reference panels
- [ ] TensorRT export for Jetson Nano real-time edge inference
- [ ] Drone/ArduPilot integration for gantry sign surveys
- [ ] FastAPI backend with NHAI AMS OAuth2 REST integration
- [ ] Expand Groq agent tools: contractor dispatch + post-repair verification

---

<div align="center">

**ReflectAI · 6th NHAI Innovation Hackathon · Team CUTIEFR · IIT Dharwad**

*YOLOv8 + Groq LLaMA 3.3-70b + EfficientNet-B4 + OpenCV · IRC 67:2012 & IRC 35:2015*

[![Safer Highways](https://img.shields.io/badge/Safer_Highways-Smarter_Maintenance-00467F?style=for-the-badge)](https://nhai.gov.in)

*Safer highways · Smarter maintenance · AI-driven compliance*

</div>
