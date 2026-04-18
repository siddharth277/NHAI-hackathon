# ============================================================
# src/models/feature_extractor.py
# ReflectAI — EfficientNet-B4 Feature Extraction + GBR Regression
# Extracts visual features from ROI crops → predicts RA score
# ============================================================
# Train: python feature_extractor.py --train --labels data/labels.csv
# Predict: python feature_extractor.py --predict --image roi.jpg
# ============================================================

import numpy as np
import cv2
import torch
import torch.nn as nn
from torchvision import models, transforms
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.isotonic import IsotonicRegression
import pickle
import os
import json
import argparse
import pandas as pd
from pathlib import Path


# ----------------------------------------------------------------
# IRC 67 / IRC 35 RA thresholds (mcd·lx⁻¹·m⁻²)
# ----------------------------------------------------------------
RA_THRESHOLDS = {
    "Lane Centreline Marking": 80,
    "Edge Lane Marking":       80,
    "Road Stud / RPM":         150,
    "Shoulder Sign":           250,
    "Gantry Sign":             250,
    "Delineator":              100,
}

# Compliance classification thresholds (as fraction of IRC minimum)
COMPLIANCE_WARN_FRAC = 0.75   # Below 75% of minimum → Warning
# Below 75% → Warning; below 100% but above 75% → Warning; above 100% → Compliant

# ----------------------------------------------------------------
# Image transform for EfficientNet-B4 input
# ----------------------------------------------------------------
EFFICIENTNET_TRANSFORM = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Condition encoding (one-hot)
TIME_OF_DAY = {"Day": 0, "Night": 1}
ROAD_COND   = {"Dry": 0, "Wet": 1}
STREET_LIGHT = {"On": 0, "Off": 1}
FOG_STATE    = {"No Fog": 0, "Fog": 1}


def encode_condition(time_of_day: str, road_cond: str,
                     street_light: str, fog: str) -> np.ndarray:
    """
    Encode environmental conditions as 8-dimensional one-hot vector.
    
    Vector layout: [Day, Night, Dry, Wet, LightOn, LightOff, NoFog, Fog]
    
    Returns:
        numpy array (8,) float32
    """
    vec = np.zeros(8, dtype=np.float32)
    
    # Time of day: positions 0-1
    tod_idx = TIME_OF_DAY.get(time_of_day, 0)
    vec[tod_idx] = 1.0
    
    # Road condition: positions 2-3
    rc_idx = ROAD_COND.get(road_cond, 0)
    vec[2 + rc_idx] = 1.0
    
    # Street light: positions 4-5
    sl_idx = STREET_LIGHT.get(street_light, 0)
    vec[4 + sl_idx] = 1.0
    
    # Fog: positions 6-7
    fog_idx = FOG_STATE.get(fog, 0)
    vec[6 + fog_idx] = 1.0
    
    return vec


# ----------------------------------------------------------------
# EfficientNet-B4 Feature Extractor
# ----------------------------------------------------------------

class EfficientNetExtractor:
    """
    EfficientNet-B4 backbone for visual feature extraction.
    
    Loads pretrained ImageNet weights, removes the classification head,
    and outputs a 1792-dimensional feature vector per image crop.
    
    For production: fine-tune with RA-labeled patches from calibration survey.
    For hackathon demo: pretrained features work well with GBR regressor.
    """

    def __init__(self, device: str = None, fine_tuned_path: str = None):
        """
        Args:
            device: "cuda", "cpu", or None (auto-detect)
            fine_tuned_path: Path to fine-tuned EfficientNet weights (.pt file)
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"EfficientNetExtractor: using device={self.device}")

        # Load EfficientNet-B4
        self.model = models.efficientnet_b4(
            weights=models.EfficientNet_B4_Weights.IMAGENET1K_V1
        )

        # Remove classification head — keep feature extractor only
        # EfficientNet-B4 outputs 1792-dim vector after AdaptiveAvgPool
        self.model.classifier = nn.Identity()

        # Load fine-tuned weights if provided
        if fine_tuned_path and os.path.exists(fine_tuned_path):
            state = torch.load(fine_tuned_path, map_location=self.device)
            self.model.load_state_dict(state, strict=False)
            print(f"Loaded fine-tuned weights from {fine_tuned_path}")

        self.model = self.model.to(self.device)
        self.model.eval()

        self.feature_dim = 1792  # EfficientNet-B4 output dimension

    def extract(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Extract feature vector from a single BGR image crop.
        
        Args:
            img_bgr: BGR image array (H, W, 3) uint8
        Returns:
            Feature vector (1792,) float32
        """
        # BGR → RGB (torchvision expects RGB)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        tensor = EFFICIENTNET_TRANSFORM(img_rgb).unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.model(tensor)

        return features.cpu().numpy().squeeze()  # (1792,)

    def extract_batch(self, images_bgr: list) -> np.ndarray:
        """
        Extract features from a batch of images.
        
        Args:
            images_bgr: List of BGR images
        Returns:
            Feature matrix (N, 1792) float32
        """
        tensors = []
        for img in images_bgr:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            tensors.append(EFFICIENTNET_TRANSFORM(img_rgb))

        batch = torch.stack(tensors).to(self.device)
        with torch.no_grad():
            features = self.model(batch)
        return features.cpu().numpy()  # (N, 1792)


# ----------------------------------------------------------------
# Gradient Boosting Regression Model
# ----------------------------------------------------------------

class RAPredictor:
    """
    RA score prediction model.
    
    Architecture:
      Input: 1792-dim CNN features + 8-dim condition vector = 1800-dim
      Model: Gradient Boosting Regressor (scikit-learn)
      Output: RA score in mcd·lx⁻¹·m⁻²
      
    Post-processing:
      Isotonic regression calibration against handheld ground truth.
    """

    def __init__(self, n_estimators: int = 200,
                  max_depth: int = 5,
                  learning_rate: float = 0.05,
                  random_state: int = 42):
        self.regressor = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            loss="huber",          # Robust to RA measurement outliers
            subsample=0.8,         # Stochastic gradient boosting
            min_samples_leaf=5,
            random_state=random_state
        )
        self.calibrator = IsotonicRegression(out_of_bounds="clip")
        self.is_calibrated = False
        self.feature_dim = 1800   # 1792 (CNN) + 8 (condition)

    def build_feature_vector(self, cnn_features: np.ndarray,
                              condition_vec: np.ndarray) -> np.ndarray:
        """
        Concatenate CNN features and condition embedding.
        
        Args:
            cnn_features: (1792,) or (N, 1792)
            condition_vec: (8,) or (N, 8)
        Returns:
            Combined feature vector (1800,) or (N, 1800)
        """
        if cnn_features.ndim == 1:
            return np.concatenate([cnn_features, condition_vec])
        return np.hstack([cnn_features, condition_vec])

    def train(self, X: np.ndarray, y: np.ndarray,
              calibrate: bool = True,
              test_size: float = 0.2) -> dict:
        """
        Train the regressor on feature-RA pairs.
        
        Args:
            X: Feature matrix (N, 1800)
            y: RA score labels (N,) in mcd·lx⁻¹·m⁻²
            calibrate: Whether to fit isotonic regression calibration
            test_size: Fraction held out for evaluation
        Returns:
            Dictionary with training metrics
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        print(f"Training GBR on {len(X_train)} samples...")
        self.regressor.fit(X_train, y_train)

        # Evaluate
        y_pred_train = self.regressor.predict(X_train)
        y_pred_test  = self.regressor.predict(X_test)

        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae  = mean_absolute_error(y_test,  y_pred_test)

        print(f"Train MAE: {train_mae:.2f} mcd·lx⁻¹·m⁻²")
        print(f"Test  MAE: {test_mae:.2f} mcd·lx⁻¹·m⁻²")

        # Calibration using isotonic regression
        if calibrate:
            print("Fitting isotonic calibration...")
            self.calibrator.fit(y_pred_test, y_test)
            y_cal = self.calibrator.predict(y_pred_test)
            cal_mae = mean_absolute_error(y_test, y_cal)
            print(f"Calibrated Test MAE: {cal_mae:.2f} mcd·lx⁻¹·m⁻²")
            self.is_calibrated = True

        return {
            "train_mae": float(train_mae),
            "test_mae": float(test_mae),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "n_estimators": self.regressor.n_estimators
        }

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Predict RA score(s) from feature vector(s).
        
        Args:
            features: (1800,) single sample or (N, 1800) batch
        Returns:
            RA score(s) in mcd·lx⁻¹·m⁻²
        """
        if features.ndim == 1:
            features = features.reshape(1, -1)

        raw_pred = self.regressor.predict(features)

        if self.is_calibrated:
            return self.calibrator.predict(raw_pred)
        return raw_pred

    def predict_single(self, cnn_features: np.ndarray,
                        condition_vec: np.ndarray) -> float:
        """Predict RA score for a single ROI + condition."""
        fv = self.build_feature_vector(cnn_features, condition_vec)
        result = self.predict(fv)
        return max(0.0, float(result[0]))

    def save(self, path: str):
        """Save model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({
                "regressor": self.regressor,
                "calibrator": self.calibrator,
                "is_calibrated": self.is_calibrated
            }, f)
        print(f"Model saved to {path}")

    def load(self, path: str):
        """Load model from disk."""
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.regressor    = data["regressor"]
        self.calibrator   = data["calibrator"]
        self.is_calibrated = data["is_calibrated"]
        print(f"Model loaded from {path}")


# ----------------------------------------------------------------
# Compliance classifier
# ----------------------------------------------------------------

def classify_compliance(ra_score: float,
                         element_type: str) -> tuple:
    """
    Classify RA score against IRC 67/35 thresholds.
    
    Args:
        ra_score: Predicted RA score in mcd·lx⁻¹·m⁻²
        element_type: Road element class name
    Returns:
        Tuple of (status_string, color_hex)
          status: "COMPLIANT" | "WARNING" | "NON-COMPLIANT"
    """
    threshold = RA_THRESHOLDS.get(element_type, 80)
    warn_threshold = threshold * COMPLIANCE_WARN_FRAC

    if ra_score >= threshold:
        return "COMPLIANT", "#28a745"
    elif ra_score >= warn_threshold:
        return "WARNING", "#fd7e14"
    else:
        return "NON-COMPLIANT", "#dc3545"


# ----------------------------------------------------------------
# Synthetic label generator (for demo/hackathon without calibration survey)
# ----------------------------------------------------------------

def generate_synthetic_labels(image_dir: str,
                                metadata_path: str,
                                output_csv: str) -> pd.DataFrame:
    """
    Generate synthetic RA labels from image brightness for demo purposes.
    
    In production: replace with actual handheld retroreflectometer readings.
    
    The brightness of a road element's ROI is physically correlated with
    its retroreflective coefficient, so brightness-derived RA scores provide
    a reasonable proxy for initial model training.
    
    Args:
        image_dir: Directory of (augmented) images
        metadata_path: JSON mapping filename → condition_label
        output_csv: Path to save labeled dataset CSV
    Returns:
        DataFrame with columns: filename, condition, mean_brightness, ra_score
    """
    with open(metadata_path) as f:
        metadata = json.load(f)

    records = []
    for filename, condition_label in metadata.items():
        img_path = os.path.join(image_dir, filename)
        img = cv2.imread(img_path)
        if img is None:
            continue

        # Extract brightness from center crop (proxy for road marking ROI)
        h, w = img.shape[:2]
        y1, y2 = int(h * 0.3), int(h * 0.7)
        x1, x2 = int(w * 0.2), int(w * 0.8)
        roi = img[y1:y2, x1:x2]
        mean_brightness = float(roi.mean())

        # Parse condition from label
        parts = condition_label.split("_")
        is_night  = len(parts) > 0 and parts[0] == "Night"
        is_wet    = len(parts) > 1 and parts[1] == "Wet"
        is_foggy  = len(parts) > 2 and "Fog" in parts[2]

        # Condition multiplier (physics-inspired)
        mult = 1.0
        if is_night:  mult *= 0.7
        if is_wet:    mult *= 0.8
        if is_foggy:  mult *= 0.75

        # Synthetic RA score: brightness-based with condition scaling
        # A fully bright (255) marking in perfect conditions → 350 mcd·lx⁻¹·m⁻²
        base_ra = (mean_brightness / 255.0) * 350.0 * mult
        # Add realistic noise
        noise = np.random.normal(0, 15)
        ra_score = max(5.0, round(base_ra + noise, 1))

        records.append({
            "filename": filename,
            "condition": condition_label,
            "mean_brightness": round(mean_brightness, 2),
            "ra_score": ra_score
        })

    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    print(f"Generated {len(df)} synthetic labeled samples → {output_csv}")
    return df


# ----------------------------------------------------------------
# End-to-end inference function (used by Streamlit app)
# ----------------------------------------------------------------

_extractor = None
_predictor = None


def get_models(model_dir: str = "models"):
    """Lazy-load the extractor and predictor (singleton)."""
    global _extractor, _predictor
    if _extractor is None:
        _extractor = EfficientNetExtractor()
    if _predictor is None:
        model_path = os.path.join(model_dir, "ra_predictor.pkl")
        _predictor = RAPredictor()
        if os.path.exists(model_path):
            _predictor.load(model_path)
        else:
            print("Warning: No trained model found. Using untrained GBR (random predictions).")
    return _extractor, _predictor


def predict_ra_from_roi(roi_bgr: np.ndarray,
                         element_type: str,
                         time_of_day: str = "Day",
                         road_cond: str = "Dry",
                         street_light: str = "On",
                         fog: str = "No Fog",
                         model_dir: str = "models") -> dict:
    """
    Full inference pipeline: ROI image → RA score → compliance status.
    
    Args:
        roi_bgr: Cropped ROI BGR image
        element_type: Road element class name
        time_of_day, road_cond, street_light, fog: Environmental conditions
        model_dir: Directory containing trained model files
    Returns:
        Dictionary with ra_score, status, color, threshold
    """
    extractor, predictor = get_models(model_dir)

    # Extract CNN features
    features = extractor.extract(roi_bgr)

    # Encode conditions
    cond_vec = encode_condition(time_of_day, road_cond, street_light, fog)

    # Predict RA score
    ra_score = predictor.predict_single(features, cond_vec)

    # Classify compliance
    status, color = classify_compliance(ra_score, element_type)

    return {
        "ra_score": round(ra_score, 1),
        "status": status,
        "color": color,
        "threshold": RA_THRESHOLDS.get(element_type, 80),
        "element_type": element_type
    }


# ----------------------------------------------------------------
# CLI: train or predict
# ----------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ReflectAI Feature Extractor & RA Predictor")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--predict", action="store_true", help="Predict on a single image")
    parser.add_argument("--labels", default="data/labels.csv", help="CSV with filename,ra_score columns")
    parser.add_argument("--image_dir", default="data/augmented", help="Directory with images")
    parser.add_argument("--image", help="Single image path for prediction")
    parser.add_argument("--model_dir", default="models")
    args = parser.parse_args()

    os.makedirs(args.model_dir, exist_ok=True)

    if args.train:
        print("=== Training ReflectAI RA Predictor ===")
        extractor = EfficientNetExtractor()
        predictor = RAPredictor()

        df = pd.read_csv(args.labels)
        print(f"Loaded {len(df)} labeled samples")

        # Extract features for all images
        feature_list, label_list = [], []
        for _, row in df.iterrows():
            img_path = os.path.join(args.image_dir, row["filename"])
            img = cv2.imread(img_path)
            if img is None:
                continue

            # Extract features
            feats = extractor.extract(img)

            # Parse condition from filename or use default
            cond_label = row.get("condition", "Day_Dry_Original")
            parts = cond_label.split("_")
            tod = "Night" if len(parts) > 0 and parts[0] == "Night" else "Day"
            rc  = "Wet"   if len(parts) > 1 and parts[1] == "Wet"   else "Dry"
            cond_vec = encode_condition(tod, rc, "On", "No Fog")

            fv = predictor.build_feature_vector(feats, cond_vec)
            feature_list.append(fv)
            label_list.append(float(row["ra_score"]))

        X = np.array(feature_list)
        y = np.array(label_list)
        print(f"Feature matrix shape: {X.shape}")

        metrics = predictor.train(X, y, calibrate=True)
        predictor.save(os.path.join(args.model_dir, "ra_predictor.pkl"))

        with open(os.path.join(args.model_dir, "training_metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)
        print("\nTraining complete:", metrics)

    elif args.predict:
        if not args.image:
            print("Error: --image required for prediction")
        else:
            img = cv2.imread(args.image)
            result = predict_ra_from_roi(
                img, "Lane Centreline Marking",
                model_dir=args.model_dir
            )
            print(f"\nRA Score: {result['ra_score']} mcd·lx⁻¹·m⁻²")
            print(f"Status: {result['status']}")
            print(f"IRC Threshold: {result['threshold']}")
