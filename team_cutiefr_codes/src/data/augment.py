# ============================================================
# src/data/augment.py
# ReflectAI Synthetic Data Augmentation
# Generates fog, rain, night, motion blur, wet road conditions
# from a small set of base road images
# ============================================================
# Usage: python augment.py --input data/raw --output data/augmented --count 25
# ============================================================

import cv2
import numpy as np
import os
import argparse
import json
import random
from pathlib import Path
from typing import Tuple, List, Dict


# ----------------------------------------------------------------
# Individual augmentation functions
# ----------------------------------------------------------------

def add_fog(img: np.ndarray, severity: float = 0.5) -> np.ndarray:
    """
    Simulate fog by blending the image with a white haze layer.
    
    Physical model: I_fog = I * t + A * (1 - t)
    where t is transmission (inversely proportional to fog density).
    
    Args:
        img: BGR image uint8
        severity: 0.0 (light haze) to 1.0 (dense fog)
    Returns:
        Fogged BGR image
    """
    h, w = img.shape[:2]
    fog_density = 0.3 + severity * 0.5  # map to [0.3, 0.8]

    # Create depth-like gradient (simulate real fog depth attenuation)
    # Fog is typically denser at distance (top of road image)
    gradient = np.linspace(fog_density, fog_density * 0.4, h).reshape(-1, 1)
    gradient = np.tile(gradient, (1, w))

    fog_layer = np.ones_like(img, dtype=np.float32) * 255.0  # white atmospheric light
    img_f = img.astype(np.float32)

    for c in range(3):
        img_f[:, :, c] = img_f[:, :, c] * (1 - gradient) + fog_layer[:, :, c] * gradient

    # Add slight blur to simulate scattering
    blur_k = max(3, int(severity * 8) * 2 + 1)
    result = cv2.GaussianBlur(img_f.astype(np.uint8), (blur_k, blur_k), 0)
    return result


def add_rain(img: np.ndarray, intensity: float = 0.5,
             angle: int = -10, streak_length: int = 15) -> np.ndarray:
    """
    Simulate rain streaks on the image.
    
    Creates a separate rain layer with random line streaks, then
    blends with the original. Also darkens the image (wet roads absorb light).
    
    Args:
        img: BGR image
        intensity: 0.0 (light drizzle) to 1.0 (heavy rain)
        angle: Rain streak angle in degrees (negative = right-leaning)
        streak_length: Length of rain streak in pixels
    Returns:
        Rain-augmented BGR image
    """
    result = img.copy().astype(np.float32)
    h, w = img.shape[:2]

    # Number of rain streaks proportional to intensity and image area
    n_streaks = int(intensity * h * w * 0.0003)

    rain_layer = np.zeros_like(result)

    for _ in range(n_streaks):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        dx = int(streak_length * np.sin(np.radians(angle)))
        dy = int(streak_length * np.cos(np.radians(angle)))
        brightness = random.randint(160, 255)
        cv2.line(rain_layer, (x, y), (x + dx, y + dy),
                 (brightness, brightness, brightness), 1)

    # Slight blur on rain layer
    rain_blurred = cv2.GaussianBlur(rain_layer, (3, 3), 0)

    # Darken base image (wet roads are darker)
    darkening = 0.75 - intensity * 0.2
    result = result * darkening + rain_blurred * 0.3

    # Add slight blue tint (rain atmosphere)
    result[:, :, 0] = np.clip(result[:, :, 0] * 1.05, 0, 255)

    return np.clip(result, 0, 255).astype(np.uint8)


def simulate_night(img: np.ndarray, street_lit: bool = True,
                   gamma: float = 0.35) -> np.ndarray:
    """
    Simulate night-time appearance with optional headlamp illumination.
    
    Args:
        img: BGR daytime image
        street_lit: If True, add mild uniform lighting; if False, add headlamp cone
        gamma: Gamma to apply for base darkening (< 1 = darken)
    Returns:
        Night-simulated BGR image
    """
    h, w = img.shape[:2]

    # Step 1: Darken image with gamma
    dark_gamma = gamma
    inv = 1.0 / dark_gamma
    table = np.array([((i / 255.0) ** inv) * 255 for i in range(256)], dtype=np.uint8)
    darkened = cv2.LUT(img, table)

    # Step 2: Add blue-ish night tint
    tinted = darkened.copy().astype(np.float32)
    tinted[:, :, 0] = np.clip(tinted[:, :, 0] * 1.1, 0, 255)  # slight blue boost

    if not street_lit:
        # Step 3a: Add headlamp cone (without street lights)
        # Cone originates from bottom-center (camera position)
        cone_center_x = w // 2
        cone_center_y = h + h // 3  # below image (vehicle position)

        lamp_mask = np.zeros((h, w), dtype=np.float32)
        for y in range(h):
            for x in range(0, w, 2):  # sample every 2px for speed
                dist = np.sqrt((x - cone_center_x)**2 + (y - cone_center_y)**2)
                angle = abs(np.degrees(np.arctan2(
                    cone_center_y - y, x - cone_center_x)) - 90)
                if dist > 0 and angle < 30:  # 60-degree cone
                    intensity = max(0, 1.0 - dist / (h * 0.8)) * (1 - angle / 30)
                    lamp_mask[y, x] = intensity
                    lamp_mask[y, x + 1] = intensity

        lamp_mask = cv2.GaussianBlur(lamp_mask, (51, 51), 0)
        for c in range(3):
            tinted[:, :, c] = np.clip(
                tinted[:, :, c] + lamp_mask * 150, 0, 255
            )
    else:
        # Step 3b: Street lighting — uniform mild boost with sodium-lamp warm tint
        tinted[:, :, 2] = np.clip(tinted[:, :, 2] * 1.1, 0, 255)  # warm orange tint
        tinted = np.clip(tinted + 15, 0, 255)

    return np.clip(tinted, 0, 255).astype(np.uint8)


def add_motion_blur(img: np.ndarray, blur_amount: int = 9,
                    direction: str = "horizontal") -> np.ndarray:
    """
    Simulate motion blur from vehicle movement.
    
    Args:
        img: BGR image
        blur_amount: Kernel size (odd number, 3–21)
        direction: "horizontal" (forward motion) or "vertical" (camera shake)
    Returns:
        Motion-blurred BGR image
    """
    blur_amount = max(3, blur_amount)
    if blur_amount % 2 == 0:
        blur_amount += 1

    if direction == "horizontal":
        kernel = np.zeros((blur_amount, blur_amount))
        kernel[blur_amount // 2, :] = 1.0 / blur_amount
    else:
        kernel = np.zeros((blur_amount, blur_amount))
        kernel[:, blur_amount // 2] = 1.0 / blur_amount

    return cv2.filter2D(img, -1, kernel)


def add_wet_road_glare(img: np.ndarray, glare_strength: float = 0.4) -> np.ndarray:
    """
    Add specular glare patches simulating wet road reflections.
    
    Wet roads produce mirror-like reflections of overhead lights.
    These can mask retroreflective signals.
    
    Args:
        img: BGR image
        glare_strength: 0.0 to 1.0
    Returns:
        Wet-glare augmented image
    """
    h, w = img.shape[:2]
    result = img.copy().astype(np.float32)

    # Add 3–7 glare patches in the lower half (road area)
    n_patches = random.randint(3, 7)
    for _ in range(n_patches):
        # Glare patches occur on the road (lower half)
        cx = random.randint(w // 4, 3 * w // 4)
        cy = random.randint(h // 2, h - 1)
        radius_x = random.randint(15, 60)
        radius_y = random.randint(5, 20)
        brightness = random.randint(200, 255)

        # Create elliptical glare
        mask = np.zeros((h, w), dtype=np.float32)
        cv2.ellipse(mask, (cx, cy), (radius_x, radius_y), 0, 0, 360,
                    glare_strength * brightness / 255.0, -1)

        # Blur the glare for realism
        mask = cv2.GaussianBlur(mask, (31, 31), 0)

        for c in range(3):
            result[:, :, c] = np.clip(
                result[:, :, c] + mask * brightness, 0, 255
            )

    return result.astype(np.uint8)


def add_camera_vibration(img: np.ndarray,
                          max_shift: int = 3) -> np.ndarray:
    """
    Simulate small camera vibrations from road surface.
    
    Args:
        img: BGR image
        max_shift: Maximum pixel shift in any direction
    Returns:
        Slightly shifted image
    """
    dx = random.randint(-max_shift, max_shift)
    dy = random.randint(-max_shift, max_shift)
    h, w = img.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, M, (w, h))


def adjust_brightness_contrast(img: np.ndarray,
                                 brightness: int = 0,
                                 contrast: float = 1.0) -> np.ndarray:
    """
    Random brightness and contrast jitter for training robustness.
    
    Args:
        img: BGR image
        brightness: Additive brightness offset (-50 to +50)
        contrast: Multiplicative contrast factor (0.7 to 1.3)
    Returns:
        Adjusted image
    """
    result = img.astype(np.float32) * contrast + brightness
    return np.clip(result, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------
# Augmentation pipeline: applies combinations to one image
# ----------------------------------------------------------------

AUGMENTATION_CONFIGS = [
    # Each config is a dict of: name, condition_label, function_calls
    {"name": "fog_light",        "label": "Day_Dry_FogLight",
     "ops": [("fog", {"severity": 0.3})]},
    {"name": "fog_heavy",        "label": "Day_Dry_FogHeavy",
     "ops": [("fog", {"severity": 0.7})]},
    {"name": "rain_light",       "label": "Day_Wet_RainLight",
     "ops": [("rain", {"intensity": 0.3})]},
    {"name": "rain_heavy",       "label": "Day_Wet_RainHeavy",
     "ops": [("rain", {"intensity": 0.8})]},
    {"name": "night_lit",        "label": "Night_Dry_StreetLit",
     "ops": [("night", {"street_lit": True})]},
    {"name": "night_dark",       "label": "Night_Dry_NoLight",
     "ops": [("night", {"street_lit": False})]},
    {"name": "night_rain",       "label": "Night_Wet_NoLight",
     "ops": [("night", {"street_lit": False}), ("rain", {"intensity": 0.5})]},
    {"name": "night_fog",        "label": "Night_Dry_Fog",
     "ops": [("night", {"street_lit": False}), ("fog", {"severity": 0.5})]},
    {"name": "motion_blur_mild", "label": "Day_Dry_MotionBlur",
     "ops": [("motion_blur", {"blur_amount": 7})]},
    {"name": "motion_blur_hard", "label": "Day_Dry_MotionBlurHard",
     "ops": [("motion_blur", {"blur_amount": 15})]},
    {"name": "wet_glare",        "label": "Day_Wet_Glare",
     "ops": [("wet_glare", {"glare_strength": 0.5})]},
    {"name": "wet_glare_rain",   "label": "Day_Wet_GlareRain",
     "ops": [("rain", {"intensity": 0.4}), ("wet_glare", {"glare_strength": 0.4})]},
    {"name": "bright_jitter",    "label": "Day_Dry_BrightHigh",
     "ops": [("brightness", {"brightness": 40, "contrast": 1.1})]},
    {"name": "dark_jitter",      "label": "Day_Dry_BrightLow",
     "ops": [("brightness", {"brightness": -30, "contrast": 0.85})]},
    {"name": "vibration",        "label": "Day_Dry_Vibration",
     "ops": [("vibration", {"max_shift": 4})]},
]


def apply_ops(img: np.ndarray, ops: list) -> np.ndarray:
    """Apply a sequence of augmentation operations to an image."""
    result = img.copy()
    for op_name, kwargs in ops:
        if op_name == "fog":
            result = add_fog(result, **kwargs)
        elif op_name == "rain":
            result = add_rain(result, **kwargs)
        elif op_name == "night":
            result = simulate_night(result, **kwargs)
        elif op_name == "motion_blur":
            result = add_motion_blur(result, **kwargs)
        elif op_name == "wet_glare":
            result = add_wet_road_glare(result, **kwargs)
        elif op_name == "vibration":
            result = add_camera_vibration(result, **kwargs)
        elif op_name == "brightness":
            result = adjust_brightness_contrast(result, **kwargs)
    return result


def augment_dataset(input_dir: str, output_dir: str,
                     copies_per_image: int = 15,
                     seed: int = 42) -> dict:
    """
    Generate augmented dataset from base images.
    
    Args:
        input_dir: Directory containing base road images (JPG/PNG)
        output_dir: Directory to save augmented images
        copies_per_image: Number of augmented versions per base image
        seed: Random seed for reproducibility
    Returns:
        Dictionary mapping augmented filename → condition label
    """
    random.seed(seed)
    np.random.seed(seed)

    os.makedirs(output_dir, exist_ok=True)
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Find all base images
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    base_images = [f for f in input_path.iterdir()
                   if f.suffix.lower() in image_extensions]

    if not base_images:
        print(f"No images found in {input_dir}")
        return {}

    metadata = {}
    total_generated = 0

    print(f"Found {len(base_images)} base images")
    print(f"Generating {copies_per_image} augmented versions each...")

    for img_path in base_images:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Warning: Could not read {img_path}")
            continue

        stem = img_path.stem

        # Always save original
        orig_name = f"{stem}_orig.jpg"
        cv2.imwrite(str(output_path / orig_name), img)
        metadata[orig_name] = "Day_Dry_Original"

        # Apply augmentation configs
        configs_to_use = AUGMENTATION_CONFIGS[:copies_per_image]
        for cfg in configs_to_use:
            aug_img = apply_ops(img, cfg["ops"])
            out_name = f"{stem}_{cfg['name']}.jpg"
            cv2.imwrite(str(output_path / out_name), aug_img)
            metadata[out_name] = cfg["label"]
            total_generated += 1

    # Save metadata
    meta_path = output_path / "augmentation_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nGenerated {total_generated} augmented images")
    print(f"Total dataset size: {len(metadata)} images")
    print(f"Metadata saved to {meta_path}")

    return metadata


# ----------------------------------------------------------------
# CLI
# ----------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ReflectAI Data Augmentation")
    parser.add_argument("--input", default="data/raw",
                        help="Input directory with base road images")
    parser.add_argument("--output", default="data/augmented",
                        help="Output directory for augmented images")
    parser.add_argument("--count", type=int, default=15,
                        help="Augmented versions per base image (max 15)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    metadata = augment_dataset(
        args.input, args.output,
        copies_per_image=min(args.count, len(AUGMENTATION_CONFIGS)),
        seed=args.seed
    )
    print(f"\nDone. Dataset ready at: {args.output}")
