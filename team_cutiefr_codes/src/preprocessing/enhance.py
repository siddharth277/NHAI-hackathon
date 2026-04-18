# ============================================================
# src/preprocessing/enhance.py
# ReflectAI Preprocessing Pipeline
# CLAHE + Gamma Correction + Dark Channel Prior Dehazing
# ============================================================

import cv2
import numpy as np
from dataclasses import dataclass
from enum import Enum


class Condition(Enum):
    DAY = "Day"
    NIGHT = "Night"


class Weather(Enum):
    DRY = "Dry"
    WET = "Wet"


class FogState(Enum):
    CLEAR = "No Fog"
    FOGGY = "Fog"


@dataclass
class EnvironmentConfig:
    """Environmental conditions for preprocessing adaptation."""
    time_of_day: str = "Day"
    road_condition: str = "Dry"
    street_light: str = "On"
    fog: str = "No Fog"

    @property
    def is_night(self): return self.time_of_day == "Night"
    @property
    def is_foggy(self): return self.fog == "Fog"
    @property
    def is_wet(self): return self.road_condition == "Wet"


class ReflectAIPreprocessor:
    """
    Multi-stage adaptive preprocessing pipeline for retroreflectivity imagery.
    
    Pipeline stages:
      1. CLAHE (Contrast-Limited Adaptive Histogram Equalization)
      2. Gamma Correction (night/low-light boost)
      3. Dark Channel Prior Dehazing (fog/haze removal)
      4. Wet Road Glare Suppression (specular highlight attenuation)
      5. Gaussian Smoothing (sensor noise removal)
    """

    def __init__(self,
                 clahe_clip_limit: float = 2.0,
                 clahe_grid_size: tuple = (8, 8),
                 night_gamma: float = 1.6,
                 fog_atm_light_percentile: float = 99.0,
                 fog_omega: float = 0.95,
                 fog_min_transmission: float = 0.1):
        """
        Args:
            clahe_clip_limit: CLAHE clip limit (higher = more contrast)
            clahe_grid_size: CLAHE tile grid size
            night_gamma: Gamma value for night footage (>1 = brighten)
            fog_atm_light_percentile: Percentile for atmospheric light estimation
            fog_omega: Dehazing strength (0–1, higher = more aggressive)
            fog_min_transmission: Minimum transmission value to prevent artifacts
        """
        self.clahe = cv2.createCLAHE(
            clipLimit=clahe_clip_limit,
            tileGridSize=clahe_grid_size
        )
        self.night_gamma = night_gamma
        self.fog_atm_light_percentile = fog_atm_light_percentile
        self.fog_omega = fog_omega
        self.fog_min_transmission = fog_min_transmission

        # Precompute gamma lookup tables
        self._gamma_tables = {}

    def _get_gamma_table(self, gamma: float) -> np.ndarray:
        """Precompute and cache gamma correction lookup table."""
        key = round(gamma, 2)
        if key not in self._gamma_tables:
            inv = 1.0 / gamma
            table = np.array(
                [((i / 255.0) ** inv) * 255 for i in range(256)],
                dtype=np.uint8
            )
            self._gamma_tables[key] = table
        return self._gamma_tables[key]

    # ----------------------------------------------------------------
    # STAGE 1: CLAHE
    # ----------------------------------------------------------------
    def apply_clahe(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE on the L channel of LAB colour space.
        Enhances local contrast without blowing out highlights.
        
        Args:
            img_bgr: BGR image array (H, W, 3)
        Returns:
            Contrast-enhanced BGR image
        """
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_eq = self.clahe.apply(l)
        lab_eq = cv2.merge([l_eq, a, b])
        return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)

    # ----------------------------------------------------------------
    # STAGE 2: Gamma Correction
    # ----------------------------------------------------------------
    def apply_gamma(self, img_bgr: np.ndarray, gamma: float) -> np.ndarray:
        """
        Apply gamma correction using precomputed lookup table.
        gamma > 1.0: brightens image (useful for night footage)
        gamma < 1.0: darkens image
        
        Args:
            img_bgr: BGR image
            gamma: Gamma value
        Returns:
            Gamma-corrected BGR image
        """
        table = self._get_gamma_table(gamma)
        return cv2.LUT(img_bgr, table)

    # ----------------------------------------------------------------
    # STAGE 3: Dark Channel Prior Dehazing
    # ----------------------------------------------------------------
    def _dark_channel(self, img: np.ndarray, patch_size: int = 15) -> np.ndarray:
        """
        Compute dark channel of an image.
        Dark channel = minimum pixel value across all channels in a local patch.
        
        Args:
            img: Float image (H, W, 3) in range [0, 1]
            patch_size: Erosion kernel size (larger = more global haze estimate)
        Returns:
            Dark channel map (H, W)
        """
        # Minimum across colour channels
        min_channel = np.min(img, axis=2)
        # Minimum filter (morphological erosion)
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (patch_size, patch_size)
        )
        dark = cv2.erode(min_channel, kernel)
        return dark

    def _estimate_atmospheric_light(self, img: np.ndarray,
                                     dark_channel: np.ndarray) -> np.ndarray:
        """
        Estimate atmospheric light from brightest pixels in dark channel.
        
        Args:
            img: Float image (H, W, 3)
            dark_channel: Dark channel map (H, W)
        Returns:
            Atmospheric light vector (3,) in range [0, 1]
        """
        h, w = dark_channel.shape
        n_pixels = h * w
        # Select top percentile pixels by dark channel intensity
        n_bright = max(1, int(n_pixels * 0.001))  # 0.1% of pixels
        flat_dc = dark_channel.flatten()
        flat_img = img.reshape(-1, 3)
        # Indices of brightest dark channel pixels
        idx = np.argpartition(flat_dc, -n_bright)[-n_bright:]
        # Atmospheric light = average of corresponding original pixels
        atm = np.mean(flat_img[idx], axis=0)
        return np.clip(atm, 0.1, 1.0)

    def apply_dehazing(self, img_bgr: np.ndarray,
                       patch_size: int = 15) -> np.ndarray:
        """
        Apply Dark Channel Prior dehazing (He et al., 2011).
        
        Recovers scene radiance from hazy image using the observation that
        outdoor haze-free images have very dark pixels in at least one channel.
        
        Args:
            img_bgr: BGR image (H, W, 3) uint8
            patch_size: Local patch size for dark channel computation
        Returns:
            Dehazed BGR image
        """
        # Normalise to float [0, 1]
        img_f = img_bgr.astype(np.float64) / 255.0

        # Compute dark channel
        dc = self._dark_channel(img_f, patch_size)

        # Estimate atmospheric light
        atm = self._estimate_atmospheric_light(img_f, dc)

        # Estimate transmission map
        # t(x) = 1 - omega * min_c(min_y(I_c(y) / A_c))
        transmission = np.zeros_like(dc)
        for c in range(3):
            if atm[c] > 1e-6:
                transmission = np.maximum(
                    transmission,
                    self._dark_channel(img_f[:, :, c:c+1] / atm[c], patch_size)
                )
        transmission = 1.0 - self.fog_omega * transmission

        # Soft-matting refinement (guided filter — simplified for speed)
        # In production: replace with cv2.ximgproc.guidedFilter
        transmission = cv2.blur(
            transmission.astype(np.float32), (patch_size, patch_size)
        )
        transmission = np.clip(transmission, self.fog_min_transmission, 1.0)

        # Recover scene radiance: J = (I - A) / t + A
        recovered = np.zeros_like(img_f)
        for c in range(3):
            recovered[:, :, c] = (
                (img_f[:, :, c] - atm[c]) / transmission + atm[c]
            )

        # Clip and convert back to uint8
        recovered = np.clip(recovered, 0, 1)
        return (recovered * 255).astype(np.uint8)

    # ----------------------------------------------------------------
    # STAGE 4: Wet Road Glare Suppression
    # ----------------------------------------------------------------
    def suppress_wet_glare(self, img_bgr: np.ndarray,
                            threshold: int = 240) -> np.ndarray:
        """
        Attenuate specular highlights caused by wet road surfaces.
        
        Wet roads cause mirror-like specular reflections that can overwhelm
        retroreflective signals. This stage reduces extreme highlight regions.
        
        Args:
            img_bgr: BGR image
            threshold: Brightness threshold above which pixels are suppressed
        Returns:
            Glare-suppressed BGR image
        """
        # Find specular highlight mask
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        # Dilate mask slightly to include highlight halos
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask_dilated = cv2.dilate(mask, kernel)

        # Inpaint using neighbourhood interpolation
        result = cv2.inpaint(img_bgr, mask_dilated, 5, cv2.INPAINT_TELEA)
        return result

    # ----------------------------------------------------------------
    # STAGE 5: Gaussian Smoothing
    # ----------------------------------------------------------------
    def apply_smoothing(self, img_bgr: np.ndarray,
                         kernel_size: tuple = (3, 3)) -> np.ndarray:
        """Suppress sensor noise with gentle Gaussian blur."""
        return cv2.GaussianBlur(img_bgr, kernel_size, 0)

    # ----------------------------------------------------------------
    # MAIN PIPELINE
    # ----------------------------------------------------------------
    def process(self, img_bgr: np.ndarray,
                env: EnvironmentConfig = None) -> np.ndarray:
        """
        Run the full adaptive preprocessing pipeline.
        
        Stages applied depend on environmental conditions:
        - CLAHE: always applied
        - Gamma: applied when night-time
        - Dehazing: applied when foggy
        - Glare suppression: applied when wet road
        - Gaussian smoothing: always applied
        
        Args:
            img_bgr: Input BGR image (H, W, 3) uint8
            env: Environmental configuration (defaults to Day/Dry/Clear)
        Returns:
            Preprocessed BGR image
        """
        if env is None:
            env = EnvironmentConfig()

        result = img_bgr.copy()

        # Stage 1: CLAHE (always)
        result = self.apply_clahe(result)

        # Stage 2: Gamma correction for night/low-light
        if env.is_night:
            gamma = self.night_gamma
            # If no street lighting, boost more aggressively
            if env.street_light == "Off":
                gamma = min(self.night_gamma * 1.2, 2.5)
            result = self.apply_gamma(result, gamma)

        # Stage 3: Dehazing for foggy conditions
        if env.is_foggy:
            result = self.apply_dehazing(result)

        # Stage 4: Glare suppression for wet conditions
        if env.is_wet:
            result = self.suppress_wet_glare(result)

        # Stage 5: Gaussian smoothing (always)
        result = self.apply_smoothing(result)

        return result

    def process_batch(self, images: list,
                       env: EnvironmentConfig = None) -> list:
        """Process a list of images through the pipeline."""
        return [self.process(img, env) for img in images]


# ----------------------------------------------------------------
# CLI usage
# ----------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 3:
        print("Usage: python enhance.py <input_image> <output_image> [--night] [--fog] [--wet]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    env = EnvironmentConfig(
        time_of_day="Night" if "--night" in sys.argv else "Day",
        fog="Fog" if "--fog" in sys.argv else "No Fog",
        road_condition="Wet" if "--wet" in sys.argv else "Dry",
        street_light="Off" if "--no-light" in sys.argv else "On"
    )

    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Could not read {input_path}")
        sys.exit(1)

    preprocessor = ReflectAIPreprocessor()
    result = preprocessor.process(img, env)

    cv2.imwrite(output_path, result)
    print(f"Preprocessed image saved to {output_path}")
    print(f"Conditions: {env.time_of_day}, {env.road_condition}, fog={env.fog}")
