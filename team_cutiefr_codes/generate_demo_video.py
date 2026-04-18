"""
generate_demo_video.py
ReflectAI — NHAI Hackathon Demo Video Generator

Creates a realistic demo video showing:
  - A moving highway perspective (scrolling road with lane markings)
  - YOLOv8-style bounding boxes appearing on detected elements
  - RA score overlays with COMPLIANT / WARNING / NON-COMPLIANT status
  - Dashboard HUD (speed, GPS, condition multiplier)
  - Grok AI agent work-order generation animation
  - Title cards and section transitions
"""

import cv2
import numpy as np
import math
import os

# ── Output ───────────────────────────────────────────────────
OUT_PATH = "/home/claude/reflectai_groq/outputs/ReflectAI_Demo.mp4"
W, H     = 1280, 720
FPS      = 30

# ── Colors (BGR) ─────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
NAVY        = (127, 70,   0)    # BGR of #00467F
BLUE        = (192, 128,  0)    # BGR of #0080C0
LIGHT_BLUE  = (255, 184, 77)
GREEN       = (69, 167,  40)
ORANGE      = (20, 126, 253)
RED         = (69,  53, 220)
YELLOW      = (0, 193, 255)
GRAY_DARK   = (40,  45,  50)
GRAY_LIGHT  = (210, 220, 230)
ASPHALT     = (55,  55,  58)
ASPHALT2    = (45,  47,  50)

writer = cv2.VideoWriter(OUT_PATH, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))


# ════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════

def fill(frame, color):
    frame[:] = color

def rect(frame, x1, y1, x2, y2, color, thick=-1, alpha=1.0):
    if alpha < 1.0:
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, thick)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    else:
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thick)

def text(frame, msg, x, y, scale=0.6, color=WHITE, thick=1, font=cv2.FONT_HERSHEY_SIMPLEX):
    cv2.putText(frame, msg, (x, y), font, scale, color, thick, cv2.LINE_AA)

def text_bold(frame, msg, x, y, scale=0.7, color=WHITE):
    text(frame, msg, x, y, scale, color, 2)

def gradient_rect(frame, x1, y1, x2, y2, c1, c2, vertical=True):
    """Draw a gradient rectangle."""
    if vertical:
        for i in range(y2 - y1):
            t = i / max(1, y2 - y1 - 1)
            col = tuple(int(c1[j] * (1-t) + c2[j] * t) for j in range(3))
            cv2.line(frame, (x1, y1 + i), (x2, y1 + i), col, 1)
    else:
        for i in range(x2 - x1):
            t = i / max(1, x2 - x1 - 1)
            col = tuple(int(c1[j] * (1-t) + c2[j] * t) for j in range(3))
            cv2.line(frame, (x1 + i, y1), (x1 + i, y2), col, 1)

def draw_rounded_rect(frame, x1, y1, x2, y2, r, color, thick=-1, alpha=1.0):
    overlay = frame.copy() if alpha < 1.0 else frame
    cv2.rectangle(overlay, (x1 + r, y1), (x2 - r, y2), color, thick)
    cv2.rectangle(overlay, (x1, y1 + r), (x2, y2 - r), color, thick)
    for cx, cy in [(x1+r, y1+r), (x2-r, y1+r), (x1+r, y2-r), (x2-r, y2-r)]:
        cv2.circle(overlay, (cx, cy), r, color, thick)
    if alpha < 1.0:
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def fade_in(frame, t, duration=0.5):
    """Apply fade-in alpha to a frame (t=0..1 within the scene)."""
    if t < duration:
        alpha = t / duration
        black = np.zeros_like(frame)
        cv2.addWeighted(frame, alpha, black, 1-alpha, 0, frame)

def draw_text_box(frame, lines, x, y, w, bg_color, text_color=WHITE,
                  scale=0.55, padding=10, line_h=26, alpha=0.85):
    """Draw a semi-transparent text box."""
    h = padding * 2 + len(lines) * line_h
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    for i, line in enumerate(lines):
        cv2.putText(frame, line, (x + padding, y + padding + (i+1) * line_h - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, text_color, 1, cv2.LINE_AA)


# ════════════════════════════════════════════════════════════
# ROAD DRAWING
# ════════════════════════════════════════════════════════════

def draw_road(frame, scroll_y, time_of_day="night"):
    """Draw a perspective highway with scrolling lane markings."""
    # Sky gradient
    sky_top = (20, 10, 5) if time_of_day == "night" else (200, 150, 80)
    sky_bot = (45, 25, 15) if time_of_day == "night" else (230, 200, 130)
    horizon_y = H // 2 - 40
    gradient_rect(frame, 0, 0, W, horizon_y, sky_top, sky_bot)

    # Road surface
    gradient_rect(frame, 0, horizon_y, W, H, (48, 50, 52), (62, 64, 66))

    # Horizon glow (night headlights)
    if time_of_day == "night":
        for gy in range(30):
            alpha = 0.15 * (1 - gy / 30)
            color = (int(80 * alpha), int(100 * alpha), int(130 * alpha))
            cv2.line(frame, (0, horizon_y - gy), (W, horizon_y - gy), color, 1)

    # Perspective vanishing point
    vp_x, vp_y = W // 2, horizon_y

    # Road edges (perspective lines)
    road_left_bot  = (W // 2 - 420, H)
    road_right_bot = (W // 2 + 420, H)
    road_left_top  = (W // 2 - 60, horizon_y + 2)
    road_right_top = (W // 2 + 60, horizon_y + 2)

    pts = np.array([road_left_top, road_right_top, road_right_bot, road_left_bot], np.int32)
    cv2.fillPoly(frame, [pts], (55, 57, 60))

    # Road edge white lines
    cv2.line(frame, road_left_top,  road_left_bot,  (180, 180, 180), 3)
    cv2.line(frame, road_right_top, road_right_bot, (180, 180, 180), 3)

    # Dashed centre line (scrolling)
    n_dashes = 18
    for i in range(n_dashes):
        # Perspective interpolation
        t1 = (i     + (scroll_y % 1.0)) / n_dashes
        t2 = (i + 0.45 + (scroll_y % 1.0)) / n_dashes
        t1 = min(t1, 1.0); t2 = min(t2, 1.0)

        def lerp_pt(t):
            x = int(vp_x + (W // 2 - vp_x) * 0 * (1-t))
            y = int(horizon_y + (H - horizon_y) * t)
            w = int(20 + 380 * t)
            return x, y, w

        x1, y1, _ = lerp_pt(t1)
        x2, y2, _ = lerp_pt(t2)
        lw = max(1, int(3 * t1))
        if y2 > horizon_y + 5:
            cv2.line(frame, (x1, y1), (x2, y2), (220, 220, 180), lw)

    # Road studs (reflective dots)
    for i in range(8):
        t = ((i + scroll_y * 0.5) % 8) / 8
        if t > 0.05:
            x = int(vp_x)
            y = int(horizon_y + (H - horizon_y) * t)
            r = max(2, int(5 * t))
            brightness = 200 + int(55 * math.sin(t * 10))
            cv2.circle(frame, (x, y), r, (brightness, brightness, brightness), -1)
            # Glow
            cv2.circle(frame, (x, y), r + 2, (100, 100, 80), 1)

    # Trees / roadside elements
    for i in range(6):
        tx = 20 + i * 95 if i < 3 else W - 200 + (i-3) * 95
        ty = horizon_y + 15 + (i * 7 % 30)
        cv2.line(frame, (tx, ty), (tx, ty + 60), (30, 60, 30), 2)
        cv2.circle(frame, (tx, ty), 20, (20, 50, 20), -1)

    return frame


def draw_detection_box(frame, x1, y1, x2, y2, label, ra_score, status, conf, alpha=1.0):
    """Draw YOLOv8-style bounding box with RA overlay."""
    color = GREEN if status == "COMPLIANT" else (ORANGE if status == "WARNING" else RED)

    # Draw box with alpha
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
    # Corner brackets
    cl = 18
    for cx, cy, dx, dy in [(x1,y1,1,1),(x2,y1,-1,1),(x1,y2,1,-1),(x2,y2,-1,-1)]:
        cv2.line(overlay, (cx, cy), (cx + dx*cl, cy), color, 3)
        cv2.line(overlay, (cx, cy), (cx, cy + dy*cl), color, 3)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Label background
    lbl = f"{label[:18]}  RA:{ra_score:.0f}"
    lw = len(lbl) * 8 + 10
    rect(frame, x1, y1 - 22, x1 + lw, y1, color)
    text(frame, lbl, x1 + 4, y1 - 6, 0.42, BLACK, 1)

    # Status badge
    badges = {"COMPLIANT": "✓ OK", "WARNING": "⚠ WARN", "NON-COMPLIANT": "✗ FAIL"}
    badge = badges.get(status, "?")
    bw = len(badge) * 9 + 10
    rect(frame, x2 - bw, y2, x2, y2 + 20, color)
    text(frame, badge, x2 - bw + 4, y2 + 15, 0.4, BLACK, 1)


# ════════════════════════════════════════════════════════════
# HUD (Heads-Up Display)
# ════════════════════════════════════════════════════════════

def draw_hud(frame, speed_kmh, gps, condition, frame_idx):
    """Draw dashboard HUD at top of frame."""
    # Top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (W, 50), (15, 20, 30), -1)
    cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

    # Logo
    text_bold(frame, "ReflectAI", 12, 32, 0.75, LIGHT_BLUE)
    cv2.line(frame, (130, 8), (130, 42), (80, 100, 150), 1)

    # Speed
    text_bold(frame, f"{speed_kmh:.0f} km/h", 148, 32, 0.7, WHITE)

    # GPS
    cv2.line(frame, (280, 8), (280, 42), (80, 100, 150), 1)
    text(frame, f"GPS: {gps}", 292, 32, 0.48, GRAY_LIGHT, 1)

    # Condition
    cv2.line(frame, (560, 8), (560, 42), (80, 100, 150), 1)
    text(frame, f"Cond: {condition}", 572, 32, 0.48, YELLOW, 1)

    # Time
    cv2.line(frame, (760, 8), (760, 42), (80, 100, 150), 1)
    secs = frame_idx // FPS
    text(frame, f"00:{secs:02d}", 775, 32, 0.55, GRAY_LIGHT, 1)

    # NHAI badge
    rect(frame, W - 145, 6, W - 5, 44, (127, 70, 0))
    text_bold(frame, "NHAI SURVEY", W - 138, 31, 0.45, WHITE)


def draw_sidebar(frame, detections_so_far):
    """Draw right sidebar with running detection count."""
    overlay = frame.copy()
    cv2.rectangle(overlay, (W - 220, 55), (W, H), (10, 15, 25), -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)
    cv2.line(frame, (W - 220, 55), (W - 220, H), (60, 80, 120), 1)

    text_bold(frame, "DETECTIONS", W - 210, 82, 0.55, LIGHT_BLUE)
    cv2.line(frame, (W - 215, 90), (W - 10, 90), (60, 80, 120), 1)

    for i, d in enumerate(detections_so_far[:8]):
        y = 112 + i * 72
        color = GREEN if d["status"]=="COMPLIANT" else (ORANGE if d["status"]=="WARNING" else RED)
        rect(frame, W - 215, y, W - 15, y + 62, (20, 25, 35))
        cv2.rectangle(frame, (W - 215, y), (W - 15, y + 62), color, 1)
        text(frame, d["label"][:20], W - 208, y + 16, 0.36, GRAY_LIGHT, 1)
        text_bold(frame, f"RA: {d['ra']:.0f}", W - 208, y + 34, 0.45, WHITE)
        st_col = GREEN if d["status"]=="COMPLIANT" else (ORANGE if d["status"]=="WARNING" else RED)
        text(frame, d["status"], W - 208, y + 52, 0.36, st_col, 1)


# ════════════════════════════════════════════════════════════
# TITLE CARD
# ════════════════════════════════════════════════════════════

def make_title_card(title, subtitle, n_frames, color1=(0,50,90), color2=(0,30,60)):
    frames = []
    for fi in range(n_frames):
        f = np.zeros((H, W, 3), dtype=np.uint8)
        t = fi / n_frames
        gradient_rect(f, 0, 0, W, H, color1, color2, vertical=True)

        # Animated accent line
        lw = int(W * min(t * 3, 1.0))
        cv2.line(f, (0, H//2 - 60), (lw, H//2 - 60), BLUE, 3)

        # Fade in text
        alpha = min(1.0, t * 4)
        overlay = f.copy()
        scale = 1.4
        (tw, th), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, scale, 3)
        tx = (W - tw) // 2
        cv2.putText(overlay, title, (tx, H//2 - 20), cv2.FONT_HERSHEY_SIMPLEX, scale, WHITE, 3, cv2.LINE_AA)
        (sw, sh), _ = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 1)
        sx = (W - sw) // 2
        cv2.putText(overlay, subtitle, (sx, H//2 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, LIGHT_BLUE, 1, cv2.LINE_AA)

        # NHAI badge
        rect(overlay, W//2 - 180, H//2 + 60, W//2 + 180, H//2 + 100, (127, 70, 0))
        (bw, _), _ = cv2.getTextSize("6th NHAI Innovation Hackathon", cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.putText(overlay, "6th NHAI Innovation Hackathon",
                    ((W - bw)//2, H//2 + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, YELLOW, 1, cv2.LINE_AA)

        cv2.addWeighted(overlay, alpha, f, 1 - alpha, 0, f)

        # Fade in / out
        if fi < FPS // 2:
            fa = fi / (FPS // 2)
            f = (f * fa).astype(np.uint8)
        if fi > n_frames - FPS // 2:
            fa = (n_frames - fi) / (FPS // 2)
            f = (f * fa).astype(np.uint8)

        frames.append(f)
    return frames


# ════════════════════════════════════════════════════════════
# GROK AGENT ANIMATION
# ════════════════════════════════════════════════════════════

def make_agent_scene(n_frames):
    tools = [
        ("analyze_scan_results()", "Scanning 5 road elements..."),
        ("prioritize_maintenance()", "Tier 1: Road Stud RPM — URGENT"),
        ("estimate_repair_cost()", "Total cost: INR 12,400"),
        ("generate_work_order()", "Work Order NHAI-WO-20250418-4872"),
    ]
    frames = []
    for fi in range(n_frames):
        f = np.zeros((H, W, 3), dtype=np.uint8)
        gradient_rect(f, 0, 0, W, H, (8, 12, 22), (15, 22, 38))

        # Title
        rect(f, 0, 0, W, 58, (10, 18, 35))
        text_bold(f, "Groq AI Maintenance Agent", 20, 38, 0.9, LIGHT_BLUE)
        text(f, "Groq LLaMA  |  OpenAI-compatible  |  Function Calling", W - 450, 35, 0.45, (150, 170, 200), 1)

        # Tool steps
        t_norm = fi / n_frames
        for i, (tool, result) in enumerate(tools):
            activated = t_norm > i / len(tools)
            done      = t_norm > (i + 0.8) / len(tools)
            y = 110 + i * 140

            # Tool box
            bg = (20, 35, 55) if activated else (15, 20, 30)
            border = BLUE if activated else (40, 55, 80)
            rect(f, 60, y, W - 60, y + 110, bg)
            cv2.rectangle(f, (60, y), (W - 60, y + 110), border, 2 if activated else 1)

            # Step number
            step_col = GREEN if done else (BLUE if activated else (60, 80, 100))
            cv2.circle(f, (100, y + 55), 22, step_col, -1)
            text_bold(f, str(i+1), 93 if i < 9 else 89, y + 63, 0.75, BLACK)

            # Tool name
            text_bold(f, tool, 140, y + 38, 0.65, YELLOW if activated else (80, 100, 130))

            # Result (show with typing animation)
            if done:
                chars = int((t_norm - (i + 0.8) / len(tools)) * len(result) * 8)
                chars = min(chars, len(result))
                text(f, f"  → {result[:chars]}", 140, y + 75, 0.52, (100, 220, 100), 1)
            elif activated:
                dots = "." * (1 + int(t_norm * 12) % 3)
                text(f, f"  Running{dots}", 140, y + 75, 0.52, GRAY_LIGHT, 1)

            # Progress bar
            if activated:
                prog = min(1.0, (t_norm - i/len(tools)) * len(tools))
                cv2.rectangle(f, (60, y + 108), (int(60 + (W-120) * prog), y + 112), BLUE, -1)

        # Final output
        if t_norm > 0.92:
            alpha = min(1.0, (t_norm - 0.92) / 0.08)
            overlay = f.copy()
            rect(overlay, 60, H - 95, W - 60, H - 12, (0, 60, 20))
            cv2.rectangle(overlay, (60, H - 95), (W - 60, H - 12), GREEN, 2)
            text_bold(overlay, "✓  NHAI Work Order Generated  —  NHAI-WO-20250418-4872",
                      80, H - 55, 0.7, WHITE)
            text(overlay, "Tier 1 Urgent: Road Stud/RPM repairs  |  Est. Cost: INR 12,400  |  Due: 7 days",
                 80, H - 28, 0.5, (180, 255, 180), 1)
            cv2.addWeighted(overlay, alpha, f, 1 - alpha, 0, f)

        frames.append(f)
    return frames


# ════════════════════════════════════════════════════════════
# MAIN VIDEO GENERATION
# ════════════════════════════════════════════════════════════

print("🎬 Generating ReflectAI Demo Video...")

# ── Scene 1: Title Card (3s) ─────────────────────────────────
print("  Scene 1: Title card...")
for f in make_title_card("🛣️  ReflectAI", "AI-Powered Retroreflectivity Measurement  |  NHAI Hackathon", FPS * 3):
    writer.write(f)

# ── Scene 2: Moving car on night highway — preprocessing (4s) ─
print("  Scene 2: Night highway / preprocessing...")
detections_so_far = []
for fi in range(FPS * 4):
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    scroll = fi * 0.06
    draw_road(frame, scroll, "night")
    draw_hud(frame, 98 + math.sin(fi * 0.1) * 2, "28.6139°N 77.2090°E", "Night/Wet ×0.65", fi)

    # Preprocessing label
    t = fi / (FPS * 4)
    stages = ["CLAHE Contrast", "Gamma Correction", "Dehaze Filter", "Noise Removal"]
    visible = int(t * len(stages) * 1.5)
    for si, stage in enumerate(stages):
        if si < visible:
            alpha = min(1.0, (visible - si) * 0.4)
            oy = 80 + si * 30
            rect(frame, 10, oy, 260, oy + 24, (20, 35, 60), alpha=0.8)
            text(frame, f"✓ {stage}", 18, oy + 17, 0.48, (100, 200, 255), 1)

    # Title "STAGE 1: PREPROCESSING"
    draw_text_box(frame, ["STAGE 1: PREPROCESSING",
                          "CLAHE + Gamma + Dehaze + Denoise"],
                  10, 58, 320, (10, 20, 50), LIGHT_BLUE, 0.5, 8, 24, 0.85)
    writer.write(frame)

# ── Scene 3: YOLOv8 detection with boxes appearing (6s) ──────
print("  Scene 3: YOLOv8 detection...")
elements = [
    {"label": "Lane Centreline", "ra": 85.0,  "status": "COMPLIANT",
     "bbox": (350, 370, 720, 470), "gps": "28.6139°N, 77.2090°E"},
    {"label": "Edge Lane Mark",  "ra": 55.0,  "status": "WARNING",
     "bbox": (60,  310, 240, 540), "gps": "28.6142°N, 77.2091°E"},
    {"label": "Road Stud/RPM",   "ra": 32.0,  "status": "NON-COMPLIANT",
     "bbox": (475, 510, 580, 590), "gps": "28.6145°N, 77.2093°E"},
    {"label": "Shoulder Sign",   "ra": 320.0, "status": "COMPLIANT",
     "bbox": (840, 70,  1050, 380), "gps": "28.6148°N, 77.2095°E"},
    {"label": "Gantry Sign",     "ra": 190.0, "status": "WARNING",
     "bbox": (150, 60,  650, 160), "gps": "28.6150°N, 77.2097°E"},
]

for fi in range(FPS * 6):
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    scroll = fi * 0.04 + FPS * 4 * 0.06
    draw_road(frame, scroll, "night")

    t = fi / (FPS * 6)
    n_visible = int(t * (len(elements) + 1))

    for ei, el in enumerate(elements[:n_visible]):
        x1, y1, x2, y2 = el["bbox"]
        appear_t = min(1.0, (t * (len(elements)+1) - ei) * 2)
        draw_detection_box(frame, x1, y1, x2, y2,
                           el["label"], el["ra"], el["status"], 0.91, appear_t)
        if ei <= len(detections_so_far) - 1:
            pass
        elif appear_t > 0.5:
            detections_so_far.append({
                "label": el["label"], "ra": el["ra"], "status": el["status"]
            })

    draw_hud(frame, 95, "28.6142°N 77.2091°E", "Night/Wet ×0.65", fi + FPS*4)

    # Stage 2 label
    draw_text_box(frame, ["STAGE 2: YOLOv8 DETECTION",
                          f"Detected: {min(n_visible, len(elements))} / {len(elements)} elements"],
                  10, 58, 340, (10, 20, 50), LIGHT_BLUE, 0.5, 8, 24)

    draw_sidebar(frame, detections_so_far)
    writer.write(frame)

# ── Scene 4: RA score closeup + compliance table (4s) ────────
print("  Scene 4: Compliance assessment...")
for fi in range(FPS * 4):
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    gradient_rect(frame, 0, 0, W, H, (8, 12, 22), (15, 22, 38))

    # Header
    rect(frame, 0, 0, W, 58, (10, 18, 35))
    text_bold(frame, "STAGE 3: IRC COMPLIANCE ASSESSMENT", 20, 38, 0.8, LIGHT_BLUE)
    text(frame, "IRC 67:2012 & IRC 35:2015 Standards", W - 360, 35, 0.5, GRAY_LIGHT)

    t = fi / (FPS * 4)
    rows = [
        ("Element Type",        "RA Score", "IRC Min", "Status",        WHITE,      (30, 45, 70)),
        ("Lane Centreline",     "85.0",     "80",      "COMPLIANT",     GREEN,      (18, 35, 18)),
        ("Edge Lane Marking",   "55.0",     "80",      "WARNING",       ORANGE,     (35, 30, 10)),
        ("Road Stud / RPM",     "32.0",     "150",     "NON-COMPLIANT", RED,        (35, 15, 15)),
        ("Shoulder Sign",       "320.0",    "250",     "COMPLIANT",     GREEN,      (18, 35, 18)),
        ("Gantry Sign",         "190.0",    "250",     "WARNING",       ORANGE,     (35, 30, 10)),
    ]
    cols = [320, 180, 150, 240]
    xs = [80, 420, 610, 770]

    for ri, row in enumerate(rows):
        if ri > int(t * (len(rows) + 1)):
            continue
        y = 85 + ri * 82
        appear = min(1.0, (t * (len(rows)+1) - ri) * 3)
        bg = row[5]
        rect(frame, 70, y, W - 70, y + 70, bg, alpha=appear)
        cv2.rectangle(frame, (70, y), (W - 70, y + 70), row[4], 1)
        for ci, (val, colw) in enumerate(zip(row[:4], cols)):
            bld = 2 if ri == 0 else 1
            col = row[4] if ci == 3 and ri > 0 else WHITE
            text(frame, val, xs[ci], y + 42, 0.55 if ri > 0 else 0.6, col, bld)

    # Summary bar
    if t > 0.7:
        rect(frame, 70, H - 85, W - 70, H - 15, (15, 22, 38))
        text_bold(frame, "2 COMPLIANT", 100,       H - 42, 0.7, GREEN)
        text_bold(frame, "2 WARNING",   420,       H - 42, 0.7, ORANGE)
        text_bold(frame, "1 NON-COMPLIANT", 700,  H - 42, 0.7, RED)
    writer.write(frame)

# ── Scene 5: Grok Agent (5s) ─────────────────────────────────
print("  Scene 5: Grok AI Agent...")
for f in make_agent_scene(FPS * 5):
    writer.write(f)

# ── Scene 6: Title card outro (2s) ───────────────────────────
print("  Scene 6: Outro...")
for f in make_title_card(
    "ReflectAI  ×  Grok",
    "Automated Retroreflectivity  |  Zero Manual Inspection  |  Real-Time Work Orders",
    FPS * 2,
    color1=(0, 40, 80), color2=(0, 15, 35)
):
    writer.write(f)

writer.release()
print(f"✅ Video saved: {OUT_PATH}")
print(f"   Duration: ~{(FPS*3 + FPS*4 + FPS*6 + FPS*4 + FPS*5 + FPS*2)//FPS}s  |  Resolution: {W}×{H}  |  FPS: {FPS}")
