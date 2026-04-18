# ============================================================
# reflectai_demo_groq.py
# ReflectAI: AI-Powered Retroreflectivity Measurement System
# 6th NHAI Innovation Hackathon -- Groq Edition
# ============================================================
# Run:     streamlit run reflectai_demo_groq.py
# API key: export GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
#          Get free key at https://console.groq.com
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import os
import random
import time
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# ── Optional imports with graceful fallbacks ─────────────────
try:
    import cv2
    CV2_OK = True
except ImportError:
    CV2_OK = False

try:
    from ultralytics import YOLO
    YOLO_OK = True
except ImportError:
    YOLO_OK = False

try:
    from preprocessing.enhance import ReflectAIPreprocessor, EnvironmentConfig
    PREPROC_OK = True
except ImportError:
    PREPROC_OK = False

try:
    from agents.maintenance_agent_groq import run_maintenance_agent, DEMO_SCAN_RESULTS
    AGENT_OK = True
except ImportError:
    AGENT_OK = False

# ── IRC 67 / IRC 35 Thresholds (mcd·lx⁻¹·m⁻²) ──────────────
RA_THRESHOLDS = {
    "Lane Centreline Marking": 80,
    "Edge Lane Marking":       80,
    "Road Stud / RPM":         150,
    "Shoulder Sign":           250,
    "Gantry Sign":             250,
    "Delineator":              100,
}

# YOLOv8 COCO class → road element proxy mapping
COCO_PROXY = {
    0:  "Shoulder Sign",
    2:  "Lane Centreline Marking",
    5:  "Gantry Sign",
    7:  "Road Stud / RPM",
    9:  "Delineator",
    11: "Edge Lane Marking",
}

# Condition multipliers (time/weather → RA correction factor)
CONDITION_MULT = {
    ("Day",   "Dry", "On",  "No Fog"): 1.00,
    ("Day",   "Dry", "Off", "No Fog"): 0.95,
    ("Day",   "Wet", "On",  "No Fog"): 0.80,
    ("Day",   "Wet", "Off", "No Fog"): 0.75,
    ("Night", "Dry", "On",  "No Fog"): 0.85,
    ("Night", "Dry", "Off", "No Fog"): 0.70,
    ("Night", "Wet", "On",  "No Fog"): 0.65,
    ("Night", "Wet", "Off", "No Fog"): 0.55,
    ("Day",   "Dry", "On",  "Fog"):    0.70,
    ("Night", "Dry", "Off", "Fog"):    0.45,
    ("Night", "Wet", "Off", "Fog"):    0.35,
}


# ── Helper functions ─────────────────────────────────────────

def get_mult(tod, rc, sl, fog):
    return CONDITION_MULT.get((tod, rc, sl, fog), 0.65)


def predict_ra(element_type, roi_bgr, condition_mult):
    """
    Estimate RA score from ROI pixel brightness + condition multiplier.
    In production, this is replaced by feature_extractor.py's GBR model.
    """
    if roi_bgr is not None and hasattr(roi_bgr, "mean") and roi_bgr.size > 0:
        brightness = float(np.array(roi_bgr).mean())
    else:
        brightness = 128.0

    threshold = RA_THRESHOLDS.get(element_type, 80)
    base  = threshold * (0.7 + (brightness / 255.0) * 0.9)
    noise = random.gauss(0, threshold * 0.15)
    return max(5.0, round((base + noise) * condition_mult, 1))


def classify(ra, element_type):
    """Map RA score to compliance status per IRC standard."""
    t = RA_THRESHOLDS.get(element_type, 80)
    if ra >= t:
        return "COMPLIANT",      "#28a745"
    elif ra >= t * 0.75:
        return "WARNING",        "#fd7e14"
    else:
        return "NON-COMPLIANT",  "#dc3545"


def draw_boxes(pil_img, detections):
    """Annotate PIL image with YOLOv8-style bounding boxes and RA labels."""
    draw = ImageDraw.Draw(pil_img)
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        col = d["color"]
        # Draw triple-line border for visibility
        for off in range(3):
            draw.rectangle(
                [x1 - off, y1 - off, x2 + off, y2 + off],
                outline=col
            )
        # Label background
        label = f"{d['element_type'][:16]}  RA:{d['ra_score']}"
        lw = len(label) * 7 + 6
        draw.rectangle([x1, y1 - 22, x1 + lw, y1], fill=col)
        draw.text((x1 + 3, y1 - 18), label, fill="white")
        # Status badge
        draw.rectangle([x2 - 60, y2, x2, y2 + 18], fill=col)
        draw.text((x2 - 57, y2 + 3), d["status"][:10], fill="white")
    return pil_img


def demo_detections(img_np, mult):
    """
    Fallback demo detections when a fine-tuned YOLO model is not loaded.
    Uses hardcoded bbox positions relative to image dimensions.
    """
    if CV2_OK and img_np is not None and img_np.ndim == 3:
        h, w = img_np.shape[:2]
    else:
        h, w = 400, 600

    elements = [
        ("Lane Centreline Marking", [int(w*.28), int(h*.38), int(w*.72), int(h*.62)]),
        ("Edge Lane Marking",       [int(w*.04), int(h*.33), int(w*.24), int(h*.67)]),
        ("Road Stud / RPM",         [int(w*.44), int(h*.69), int(w*.56), int(h*.81)]),
        ("Shoulder Sign",           [int(w*.75), int(h*.09), int(w*.96), int(h*.44)]),
    ]

    out = []
    for etype, bbox in elements:
        ra     = predict_ra(etype, None, mult)
        status, color = classify(ra, etype)
        out.append({
            "bbox":         tuple(bbox),
            "element_type": etype,
            "ra_score":     ra,
            "status":       status,
            "color":        color,
            "confidence":   round(random.uniform(0.82, 0.97), 2),
        })
    return out


# ============================================================
# STREAMLIT APP
# ============================================================

def main():
    st.set_page_config(
        page_title="ReflectAI — NHAI Retroreflectivity System",
        page_icon="🛣️",
        layout="wide",
    )

    # ── Header ───────────────────────────────────────────────
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #00467F, #0080C0);
        padding: 18px 22px;
        border-radius: 12px;
        margin-bottom: 18px;
    ">
      <h1 style="color:white; margin:0; font-size:1.9rem;">🛣️ ReflectAI</h1>
      <p style="color:#cce0ff; margin:4px 0 0; font-size:0.95rem;">
        AI-Powered Retroreflectivity Measurement &nbsp;·&nbsp;
        6th NHAI Innovation Hackathon &nbsp;·&nbsp;
        Powered by <strong>Groq LLaMA</strong>
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────
    st.sidebar.header("🌦 Environmental Conditions")
    tod = st.sidebar.selectbox("Time of Day",     ["Day", "Night"])
    rc  = st.sidebar.selectbox("Road Condition",  ["Dry", "Wet"])
    sl  = st.sidebar.selectbox("Street Lighting", ["On", "Off"])
    fog = st.sidebar.selectbox("Fog / Haze",      ["No Fog", "Fog"])
    mult = get_mult(tod, rc, sl, fog)
    st.sidebar.metric("Condition Multiplier", f"{mult:.2f}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**IRC Thresholds (mcd·lx⁻¹·m⁻²)**")
    for e, t in RA_THRESHOLDS.items():
        st.sidebar.text(f"{e[:24]}: {t}")

    highway_section = st.sidebar.text_input(
        "Highway Section", value="NH-48 Km 120-180"
    )

    # ── Status pills ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("YOLOv8",        "✅ Ready" if YOLO_OK    else "⚠️ Demo mode")
    c2.metric("Preprocessing", "✅ Ready" if PREPROC_OK else "⚠️ Fallback")
    c3.metric("Groq Agent",    "✅ Ready" if AGENT_OK   else "⚠️ Set API key")
    c4.metric("OpenCV",        "✅ Ready" if CV2_OK      else "⚠️ Fallback")

    st.markdown("---")

    # ── Image upload ─────────────────────────────────────────
    col_upload, col_result = st.columns([1, 1])
    with col_upload:
        st.subheader("📤 Upload Road Image")
        uploaded = st.file_uploader(
            "Upload a JPG/PNG image of a road section",
            type=["jpg", "jpeg", "png"],
        )

    if not uploaded:
        st.info("👆 Upload a road image to begin — or scroll down to run the Groq AI Agent demo.")
        st.markdown("---")
        _show_agent_section(highway_section, DEMO_SCAN_RESULTS if AGENT_OK else [])
        return

    # ── Load image ───────────────────────────────────────────
    pil_img = Image.open(uploaded).convert("RGB")
    img_np  = np.array(pil_img)

    if CV2_OK:
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    else:
        img_bgr = img_np

    with col_upload:
        st.image(pil_img, caption="Input image", use_column_width=True)

    # ── Pipeline ─────────────────────────────────────────────
    with st.spinner("🔍 Running ReflectAI pipeline…"):

        # Stage 1 — Preprocessing
        st.toast("⚙ Stage 1: CLAHE + gamma + dehazing…")
        if PREPROC_OK and CV2_OK:
            try:
                env = EnvironmentConfig(
                    time_of_day=tod,
                    road_condition=rc,
                    street_light=sl,
                    fog=fog,
                )
                preprocessor = ReflectAIPreprocessor()
                proc_bgr = preprocessor.process(img_bgr, env)
            except Exception as e:
                st.warning(f"Preprocessing note: {e} — using raw image.")
                proc_bgr = img_bgr
        else:
            proc_bgr = img_bgr
        time.sleep(0.3)

        # Stage 2 — YOLOv8 Detection
        st.toast("🎯 Stage 2: YOLOv8 detection…")
        detections = []

        if YOLO_OK:
            try:
                model   = YOLO("yolov8n.pt")   # auto-downloads ~6 MB on first run
                results = model(proc_bgr, verbose=False)
                if results and len(results[0].boxes) > 0:
                    for box in results[0].boxes:
                        cls_id = int(box.cls[0])
                        if cls_id in COCO_PROXY:
                            etype          = COCO_PROXY[cls_id]
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            roi            = proc_bgr[y1:y2, x1:x2]
                            ra             = predict_ra(etype, roi, mult)
                            status, color  = classify(ra, etype)
                            detections.append({
                                "bbox":         (x1, y1, x2, y2),
                                "element_type": etype,
                                "ra_score":     ra,
                                "status":       status,
                                "color":        color,
                                "confidence":   round(float(box.conf[0]), 2),
                            })
            except Exception as e:
                st.warning(f"YOLOv8 note: {e}")

        if not detections:
            st.toast("📌 No COCO matches — using demo detections…")
            detections = demo_detections(proc_bgr, mult)

        time.sleep(0.3)

    # ── Annotated image ──────────────────────────────────────
    annotated = pil_img.copy()
    annotated = draw_boxes(annotated, detections)
    with col_result:
        st.subheader("🔍 Detection Results")
        st.image(annotated, caption="YOLOv8 + RA Score Overlay", use_column_width=True)

    # ── Compliance table ─────────────────────────────────────
    st.subheader("📋 Retroreflectivity Assessment")
    rows = [
        {
            "Element Type": d["element_type"],
            "Confidence":   d["confidence"],
            "RA Score":     d["ra_score"],
            "IRC Min":      RA_THRESHOLDS.get(d["element_type"], 80),
            "Status":       d["status"],
        }
        for d in detections
    ]
    df = pd.DataFrame(rows)

    def highlight_status(val):
        return {
            "COMPLIANT":     "background-color:#d4edda; color:#155724; font-weight:bold",
            "WARNING":       "background-color:#fff3cd; color:#856404; font-weight:bold",
            "NON-COMPLIANT": "background-color:#f8d7da; color:#721c24; font-weight:bold",
        }.get(val, "")

    st.dataframe(
        df.style.applymap(highlight_status, subset=["Status"]),
        use_container_width=True,
    )

    # ── Summary metrics ──────────────────────────────────────
    total = len(detections)
    comp  = sum(1 for d in detections if d["status"] == "COMPLIANT")
    warn  = sum(1 for d in detections if d["status"] == "WARNING")
    nc    = sum(1 for d in detections if d["status"] == "NON-COMPLIANT")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Detected", total)
    m2.metric("✅ Compliant",     f"{comp} ({int(comp/total*100) if total else 0}%)")
    m3.metric("⚠️ Warning",       f"{warn} ({int(warn/total*100) if total else 0}%)")
    m4.metric("❌ Non-Compliant", f"{nc}   ({int(nc/total*100)   if total else 0}%)")

    if nc > 0:
        st.error(
            f"🚨 MAINTENANCE ALERT: {nc} element(s) are Non-Compliant with IRC standards. "
            "Immediate action required."
        )
    elif warn > 0:
        st.warning(
            f"⚠️ {warn} element(s) are in the Warning range. "
            "Schedule preventive maintenance within 30 days."
        )
    else:
        st.success("✅ All detected elements comply with IRC retroreflectivity standards.")

    # ── CSV download ─────────────────────────────────────────
    st.download_button(
        "📥 Download CSV Report",
        df.to_csv(index=False).encode("utf-8"),
        "reflectai_results.csv",
        "text/csv",
    )

    st.markdown("---")
    _show_agent_section(highway_section, detections)


# ── Groq AI Agent section ────────────────────────────────────

def _show_agent_section(highway_section, detections):
    """Render the Groq AI Agent interface."""
    st.subheader("🤖 Groq AI Maintenance Agent")
    st.markdown(
        "The Groq LLaMA agent analyses scan results, prioritises maintenance tasks, "
        "estimates repair costs, and generates a formal NHAI work order — automatically."
    )

    if not AGENT_OK:
        st.warning(
            "**Agent not loaded.** Install the Groq SDK:\n"
            "```\npip install groq\n```"
        )
        return

    # API key input
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        key_input = st.text_input(
            "Enter Groq API key (gsk_...  — get free key at console.groq.com)",
            type="password",
            key="groq_agent_key",
        )
        if key_input:
            os.environ["GROQ_API_KEY"] = key_input
            api_key = key_input

    if not api_key:
        st.info("🔑 Add your Groq API key above to enable the AI agent.")
        return

    use_demo = st.checkbox(
        "Use demo scan data (if no image was uploaded)",
        value=(len(detections) == 0),
    )
    scan_data = DEMO_SCAN_RESULTS if use_demo else detections

    if st.button("🤖 Generate Groq AI Maintenance Work Order", type="primary"):
        with st.spinner(
            "🧠 Groq Agent running: analyze → prioritize → cost estimate → work order…"
        ):
            try:
                report = run_maintenance_agent(
                    scan_results=scan_data,
                    highway_section=highway_section,
                    verbose=False,
                )
            except Exception as e:
                st.error(f"Agent error: {e}")
                return

        st.success("✅ Work order generated by Groq LLaMA!")
        st.text_area(
            "Groq AI-Generated Maintenance Work Order",
            report,
            height=420,
        )
        st.download_button(
            "📥 Download Work Order (TXT)",
            report.encode("utf-8"),
            f"NHAI_WorkOrder_{highway_section.replace(' ', '_')}.txt",
            "text/plain",
        )


if __name__ == "__main__":
    main()
