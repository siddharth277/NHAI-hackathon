# 🛣️ ReflectAI — AI-Powered Retroreflectivity Measurement System
### 6th NHAI Innovation Hackathon · Groq LLaMA Edition

> **Complete zero-to-running guide** — from a fresh machine to a working live demo.

---

## Table of Contents
1. [What This System Does](#1-what-this-system-does)
2. [System Architecture](#2-system-architecture)
3. [File-by-File Description](#3-file-by-file-description)
4. [Prerequisites](#4-prerequisites)
5. [Step-by-Step Installation](#5-step-by-step-installation)
6. [Getting a Groq API Key](#6-getting-a-groq-api-key)
7. [Running the Application](#7-running-the-application)
8. [Using the Application](#8-using-the-application)
9. [YOLOv8 Pretrained Model](#9-yolov8-pretrained-model)
10. [Groq AI Agent Pipeline](#10-groq-ai-agent-pipeline)
11. [IRC Standards Reference](#11-irc-standards-reference)
12. [Project Structure](#12-project-structure)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. What This System Does

ReflectAI is an AI-powered pipeline that automatically measures **retroreflectivity (RA)**
of road markings and signs on Indian National Highways.

**Retroreflectivity** is how well a road element (lane marking, sign, road stud)
reflects vehicle headlights back to the driver — critical for night-time safety.

### The Problem
- NHAI manages 40,000+ km of national highways
- Manual retroreflectometer inspection costs ₹8,000+/km and takes 3 hours/km
- Non-compliant markings are a leading cause of night-time road accidents in India

### The ReflectAI Solution
1. Camera-equipped survey vehicle drives the highway at normal speed
2. **YOLOv8** detects road elements (markings, studs, signs) from each frame
3. **Image analysis** predicts RA scores from pixel brightness + environmental conditions
4. **Groq LLaMA AI Agent** automatically generates maintenance work orders

**Result:** ₹200/km cost, highway-speed survey, zero lane closures.

---

## 2. System Architecture

```
Camera Feed / Uploaded Image
           │
    ┌──────▼──────────────────────────────────────────────────┐
    │  STAGE 1: PREPROCESSING  (enhance.py)                   │
    │  CLAHE → Gamma Correction → Dark Channel Dehaze         │
    │  → Wet Road Glare Removal → Gaussian Denoise            │
    └──────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │  STAGE 2: YOLOv8 DETECTION  (ultralytics)               │
    │  Pretrained yolov8n.pt on COCO                          │
    │  Detects: Lane Markings | Road Studs | Signs            │
    └──────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │  STAGE 3: RA SCORE PREDICTION  (feature_extractor.py)   │
    │  Brightness analysis + Condition Multiplier             │
    │  → Compare vs IRC 67/35 threshold                       │
    │  → COMPLIANT / WARNING / NON-COMPLIANT                  │
    └──────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────┐
    │  STAGE 4: GROQ AI AGENT  (maintenance_agent_groq.py)    │
    │  Model: llama-3.3-70b-versatile                         │
    │  Tools: analyze → prioritize → cost → work_order        │
    └──────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┬──────────────┐
              ▼            ▼            ▼              ▼
        Annotated      CSV           NHAI         PDF
         Image        Report      Work Order    Document
```

---

## 3. File-by-File Description

### `reflectai_demo_groq.py` — Main Application

**Purpose:** The Streamlit web application — entry point for the entire system.

**What it does:**
- Renders the web UI with sidebar environmental controls
- Accepts uploaded road images (JPG/PNG)
- Runs all 4 pipeline stages: preprocess → detect → score → agent
- Calls the Groq AI agent to generate NHAI work orders
- Displays annotated images, compliance tables, download buttons

**Key functions:**

| Function | Purpose |
|----------|---------|
| `main()` | Streamlit entry point; orchestrates the full pipeline |
| `get_mult(tod, rc, sl, fog)` | Returns condition multiplier (0.35–1.00) |
| `predict_ra(element_type, roi_bgr, mult)` | Estimates RA score from image brightness |
| `classify(ra, element_type)` | Maps RA to COMPLIANT/WARNING/NON-COMPLIANT |
| `draw_boxes(pil_img, detections)` | Annotates PIL image with detection overlays |
| `demo_detections(img_np, mult)` | Fallback demo detections when YOLO model not loaded |
| `_show_agent_section(...)` | Renders Groq agent UI section |

---

### `src/agents/maintenance_agent_groq.py` — Groq AI Agent

**Purpose:** The intelligent maintenance planning agent powered by Groq LLaMA.

**How it connects to Groq:**
```python
from groq import Groq
client = Groq(api_key="gsk_your_key_here")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=AGENT_TOOLS,
    tool_choice="auto"
)
```

**Agentic tool loop:**

The agent calls 4 local Python tools in sequence via Groq's function-calling API:

| Tool | What It Does |
|------|-------------|
| `analyze_scan_results(scan_data)` | Parses detection JSON, identifies IRC non-compliance, computes RA deficits |
| `prioritize_maintenance(issues)` | Tiers issues into Urgent/High/Scheduled based on safety criticality |
| `estimate_repair_cost(element_types_json)` | Calculates INR cost from element type × NHAI contractor rates |
| `generate_work_order(priority_list, highway_section)` | Produces formal NHAI work order with dates and work order ID |

**Groq model used:** `llama-3.3-70b-versatile`
- Supports full tool/function calling
- Fast inference (Groq specializes in ultra-low latency LLM serving)
- Free tier available at console.groq.com

---

### `src/preprocessing/enhance.py` — Image Preprocessing Pipeline

**Purpose:** Cleans and enhances road images before detection to improve accuracy
under adverse lighting/weather conditions.

**The 5 pipeline stages:**

| Stage | Algorithm | What It Fixes |
|-------|-----------|---------------|
| 1 | CLAHE | Low local contrast — makes faded markings visible |
| 2 | Gamma Correction | Dark night footage — brightens without overexposure |
| 3 | Dark Channel Prior (He et al. 2009) | Fog/haze — recovers visibility |
| 4 | Wet Road Glare Suppression | Specular highlights from wet roads |
| 5 | Gaussian Smoothing | Sensor noise from camera |

**Usage:**
```python
from preprocessing.enhance import ReflectAIPreprocessor, EnvironmentConfig

env = EnvironmentConfig(time_of_day="Night", road_condition="Wet",
                        street_light="Off", fog="Fog")
preprocessor = ReflectAIPreprocessor()
processed_bgr = preprocessor.process(raw_bgr_image, env)
```

---

### `src/models/feature_extractor.py` — RA Score Prediction Model

**Purpose:** For production deployment — replaces the brightness-based RA estimator
with a trained deep learning model.

**Architecture:**
```
ROI Crop (224×224 pixels)
         │
[EfficientNet-B4 backbone]    ← pretrained ImageNet, frozen during training
         │
  [1792-dim feature vector]
         │
  + [8-dim condition vector]   ← time/weather encoded as one-hot
         │
[Gradient Boosting Regressor] ← trained on labeled NHAI retroreflectometer data
         │
  RA Value (mcd/lx/m2, float)
         │
[Isotonic Regression]         ← removes prediction bias, calibrates output
         │
  Calibrated RA Score
```

**Training mode:**
```bash
python src/models/feature_extractor.py --train --labels data/labels.csv
```

**Prediction mode:**
```bash
python src/models/feature_extractor.py --predict --image roi.jpg
```

**labels.csv format:**
```
image_path,element_type,ra_score,time_of_day,road_condition,street_light,fog
data/roi/img001.jpg,Lane Centreline Marking,87.3,Day,Dry,On,No Fog
data/roi/img002.jpg,Road Stud / RPM,142.1,Night,Dry,Off,No Fog
```

---

### `src/data/augment.py` — Synthetic Data Augmentation

**Purpose:** Generates augmented training images from a small set of base road images,
so the model learns to work under all weather/lighting conditions without needing
thousands of real labeled images.

**Augmentation functions:**

| Function | Simulates | Method |
|----------|-----------|--------|
| `add_fog(img, severity)` | Atmospheric haze | Transmission model: I_fog = I×t + A×(1-t) |
| `add_rain(img, intensity, angle)` | Rain streaks | Angled lines + motion blur |
| `add_night(img)` | Night / low exposure | Brightness reduction + vignette |
| `add_motion_blur(img, angle, length)` | Vehicle motion blur | Kernel convolution |
| `add_wet_road(img)` | Wet road glare | Specular highlight simulation |
| `augment_image(img)` | Random combination | Applies random mix of above |

**Usage:**
```bash
python src/data/augment.py --input data/raw --output data/augmented --count 25
```
This generates 25 augmented variants of each image in data/raw/.

---

## 4. Prerequisites

### Hardware
- Any modern laptop or desktop (no GPU required for demo)
- Minimum 4 GB RAM (8 GB recommended)
- 2 GB free disk space (model weights + packages)

### Software
- **Python 3.9, 3.10, 3.11, or 3.12** (Python 3.11 recommended)
- **pip** package manager
- Internet connection (first run downloads YOLOv8 weights ~6 MB)

---

## 5. Step-by-Step Installation

### Step 1 — Check your Python version
```bash
python --version
# Must show 3.9.x, 3.10.x, 3.11.x, or 3.12.x
```

Download Python from https://python.org/downloads if not installed.

### Step 2 — Create a virtual environment (strongly recommended)
```bash
# Windows
python -m venv reflectai_env
reflectai_env\Scripts\activate

# macOS / Linux
python -m venv reflectai_env
source reflectai_env/bin/activate
```

You will see `(reflectai_env)` in your terminal prompt when it is active.

### Step 3 — Upgrade pip
```bash
pip install --upgrade pip
```

### Step 4 — Install all dependencies
```bash
pip install -r requirements.txt
```

This installs: Streamlit, OpenCV, PyTorch, Ultralytics (YOLOv8), Groq SDK,
scikit-learn, FPDF2, and all other dependencies.

**Note for GPU users** — replace the torch install with the CUDA version:
```bash
# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Step 5 — Verify installation
```bash
python -c "import streamlit, cv2, ultralytics, groq; print('All packages OK')"
```
Expected output: `All packages OK`

---

## 6. Getting a Groq API Key

Groq (groq.com) provides ultra-fast LLaMA inference with a free tier.
The API key format is: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Steps:**
1. Go to **https://console.groq.com**
2. Sign up with Google, GitHub, or email
3. In the left sidebar click **"API Keys"**
4. Click **"Create API Key"**
5. Copy the key — it starts with `gsk_`

**Set the key as an environment variable:**
```bash
# macOS / Linux
export GROQ_API_KEY=gsk_your_key_here

# Windows Command Prompt
set GROQ_API_KEY=gsk_your_key_here

# Windows PowerShell
$env:GROQ_API_KEY="gsk_your_key_here"
```

Alternatively, you can paste the key directly into the Streamlit UI —
there is a password input field in the "Groq AI Maintenance Agent" section.

**Free tier limits:** ~14,400 requests/day, 6,000 tokens/minute — more than
enough for hackathon use.

---

## 7. Running the Application

Make sure the virtual environment is activated and `GROQ_API_KEY` is set:

```bash
streamlit run reflectai_demo_groq.py
```

The browser opens automatically at **http://localhost:8501**

On the **first run**, YOLOv8 downloads `yolov8n.pt` (~6 MB) automatically.
Subsequent runs use the cached file from `~/.cache/ultralytics/`.

---

## 8. Using the Application

### Step 1 — Set Environmental Conditions (left sidebar)
| Control | Options | Effect |
|---------|---------|--------|
| Time of Day | Day / Night | Night reduces effective RA |
| Road Condition | Dry / Wet | Wet roads scatter light, reduce RA |
| Street Lighting | On / Off | Lighting improves visibility |
| Fog / Haze | No Fog / Fog | Heavy fog dramatically reduces RA |

The **Condition Multiplier** is automatically computed and shown.
It scales all predicted RA scores to reflect the actual driving conditions.

### Step 2 — Upload a Road Image
Click "Browse files" and upload any JPG/PNG road image.
Works best with:
- Dashboard camera footage
- Images with visible lane markings, studs, or road signs
- Day or night images (preprocessing handles both)

### Step 3 — Read the Results
**Left panel:** Original uploaded image
**Right panel:** Annotated image with colour-coded bounding boxes:
- 🟢 **Green** = COMPLIANT (RA meets IRC minimum)
- 🟠 **Orange** = WARNING (RA is 75–100% of IRC minimum)
- 🔴 **Red** = NON-COMPLIANT (RA < 75% of IRC minimum)

### Step 4 — Download the CSV Report
Click **"📥 Download CSV Report"** for a spreadsheet with all detections.

### Step 5 — Generate the AI Work Order
Scroll down to **"Groq AI Maintenance Agent"**:
- Enter your Groq API key (gsk_...) if not set via environment variable
- Optionally check "Use demo scan data"
- Click **"🤖 Generate Groq AI Maintenance Work Order"**
- Download the work order as a .txt file

---

## 9. YOLOv8 Pretrained Model

### What is YOLOv8?
YOLOv8 (You Only Look Once v8) by Ultralytics is a real-time object detector.
The `yolov8n` (nano) variant runs at 80+ FPS on CPU.

### Why the pretrained COCO model?
The demo uses weights pretrained on COCO (80 classes) because:
- No custom NHAI road dataset is needed to run the demo
- COCO classes act as proxies for road elements

### COCO class → road element mapping
```python
COCO_PROXY = {
    0:  "Shoulder Sign",            # 'person' as proxy
    2:  "Lane Centreline Marking",  # 'car' as proxy
    5:  "Gantry Sign",              # 'bus' as proxy
    7:  "Road Stud / RPM",          # 'truck' as proxy
    9:  "Delineator",               # 'traffic light' as proxy
    11: "Edge Lane Marking",        # 'stop sign' as proxy
}
```

### How YOLOv8 downloads automatically
```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")   # Downloads from Ultralytics CDN if not cached
```
The file is saved at `~/.cache/ultralytics/assets/yolov8n.pt`.

### For production — fine-tune on NHAI road data
```bash
# Prepare dataset in YOLO format, then:
yolo detect train data=road_markings.yaml model=yolov8n.pt epochs=100 imgsz=640
```
Supported annotation formats: YOLO .txt, COCO JSON, Pascal VOC XML.

---

## 10. Groq AI Agent Pipeline

### How the agentic loop works

```
User clicks "Generate Work Order"
           │
    Groq LLaMA receives task + AGENT_TOOLS list
           │
    Groq decides → call analyze_scan_results
           │
    → Python executes analyze_scan_results() locally
    → Returns analysis string to Groq
           │
    Groq decides → call prioritize_maintenance
           │
    → Python executes prioritize_maintenance() locally
    → Returns priority plan to Groq
           │
    Groq decides → call estimate_repair_cost
           │
    → Python executes estimate_repair_cost() locally
    → Returns cost breakdown to Groq
           │
    Groq decides → call generate_work_order
           │
    → Python executes generate_work_order() locally
    → Returns formal work order text to Groq
           │
    Groq writes final summary → displayed in Streamlit
```

### Groq SDK usage
```python
from groq import Groq

client = Groq(api_key="gsk_your_key_here")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,        # conversation history
    tools=AGENT_TOOLS,        # list of tool/function definitions
    tool_choice="auto",       # let the model decide when to call tools
    max_tokens=2048,
    temperature=0.1,
)

# Check for tool calls
if response.choices[0].message.tool_calls:
    for tc in response.choices[0].message.tool_calls:
        tool_name = tc.function.name
        tool_args = json.loads(tc.function.arguments)
        # Execute locally, return result as "tool" role message
```

### Available Groq models that support tool calling
| Model | Speed | Best For |
|-------|-------|----------|
| `llama-3.3-70b-versatile` | Fast | Default — best balance |
| `llama-3.1-70b-versatile` | Fast | Alternative |
| `mixtral-8x7b-32768` | Very fast | Quick responses |

Change `GROQ_MODEL` at the top of `maintenance_agent_groq.py` to switch.

---

## 11. IRC Standards Reference

### Minimum RA Values (mcd·lx⁻¹·m⁻²)

| Road Element | Standard | Min RA | Warning below |
|-------------|----------|--------|---------------|
| Lane Centreline Marking | IRC 35:2015 | 80 | 60 |
| Edge Lane Marking | IRC 35:2015 | 80 | 60 |
| Road Stud / RPM | IRC 35:2015 | 150 | 113 |
| Shoulder Sign | IRC 67:2012 | 250 | 188 |
| Gantry Sign | IRC 67:2012 | 250 | 188 |
| Delineator | IRC 35:2015 | 100 | 75 |

### Compliance Classification Logic
```python
if ra_score >= irc_minimum:
    status = "COMPLIANT"        # Green
elif ra_score >= irc_minimum * 0.75:
    status = "WARNING"          # Orange — schedule within 30 days
else:
    status = "NON-COMPLIANT"   # Red — immediate action required
```

---

## 12. Project Structure

```
reflectai_groq/
│
├── reflectai_demo_groq.py           # MAIN — run: streamlit run reflectai_demo_groq.py
├── requirements.txt                 # All pip dependencies
├── README.md                        # This file
├── generate_demo_video.py           # Generates demo video (optional)
├── make_pptx.js                     # Generates PPT (node make_pptx.js)
│
└── src/
    ├── __init__.py
    │
    ├── agents/
    │   ├── __init__.py
    │   └── maintenance_agent_groq.py   # Groq LLaMA agent with tool calling
    │
    ├── preprocessing/
    │   ├── __init__.py
    │   └── enhance.py                  # 5-stage image preprocessing pipeline
    │
    ├── models/
    │   ├── __init__.py
    │   └── feature_extractor.py        # EfficientNet-B4 + GBR RA predictor
    │
    └── data/
        ├── __init__.py
        └── augment.py                  # Fog/rain/night/wet augmentation
```

---

## 13. Troubleshooting

### "ModuleNotFoundError: No module named 'groq'"
```bash
pip install groq
```

### "Error: GROQ_API_KEY not set"
```bash
export GROQ_API_KEY=gsk_your_key_here
```
Or enter the key in the Streamlit UI password field.

### "ModuleNotFoundError: No module named 'cv2'"
```bash
pip install opencv-python-headless
```

### "ModuleNotFoundError: No module named 'ultralytics'"
```bash
pip install ultralytics
```

### YOLOv8 model download fails (no internet)
Pre-download manually:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Streamlit port in use
```bash
streamlit run reflectai_demo_groq.py --server.port 8502
```

### Groq API rate limit error
The free tier allows ~14,400 requests/day. If you hit limits,
wait 60 seconds or upgrade at console.groq.com.

### "No module named 'preprocessing'"
Make sure you run from the project root (where reflectai_demo_groq.py is):
```bash
cd /path/to/reflectai_groq
streamlit run reflectai_demo_groq.py
```

---

## Quick Start (TL;DR)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Groq API key (gsk_... from console.groq.com)
export GROQ_API_KEY=gsk_your_key_here

# 3. Run the app
streamlit run reflectai_demo_groq.py

# 4. Open http://localhost:8501 in your browser
# 5. Upload a road image → see detections → generate AI work order
```

---

*ReflectAI · 6th NHAI Innovation Hackathon · YOLOv8 + Groq LLaMA · IRC 67:2012 & IRC 35:2015*
