# FACIAL RECOGNITION 101 - SETUP
# Create a virtual environment first
# Install dependencies
# flask — runs the web server / API
# face-recognition — the core library that detects and compares faces
# opencv-python — handles webcam and image processing
# numpy — required for image data manipulation
# mediapipe — used for active liveness detection (blink detection)

# Creating the back bone
# Import libraries
import base64
import os
from datetime import datetime

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from flask import Flask, jsonify, request
from insightface.app import FaceAnalysis

# ── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)

# ── InsightFace Model ──────────────────────────────────────────────────────────
# ctx_id=-1 uses CPU; change to 0 if you have a CUDA GPU
face_app = FaceAnalysis(allowed_modules=["detection", "recognition"])
face_app.prepare(ctx_id=-1, det_size=(640, 640))

# ── Reference Face Storage ─────────────────────────────────────────────────────
reference_embeddings = []   # list of np.ndarray (512-dim each)
reference_names      = []   # list of str


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two embedding vectors (range: -1 … 1)."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-6))


def load_reference_faces(folder: str = None) -> None:
    if folder is None:
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_faces")
        
    if not os.path.isdir(folder):
        print(f"[WARN] Reference folder '{folder}' not found — skipping load.")
        return

    for filename in os.listdir(folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        path  = os.path.join(folder, filename)
        image = cv2.imread(path)
        if image is None:
            print(f"[WARN] Could not read image: {path}")
            continue

        faces = face_app.get(image)
        if not faces:
            print(f"[WARN] No face found in: {filename}")
            continue

        embedding = faces[0].embedding
        reference_embeddings.append(embedding)

        name = os.path.splitext(filename)[0].replace("_", " ").title()
        reference_names.append(name)
        print(f"[INFO] Loaded reference: {name}")


load_reference_faces()


# ── MediaPipe — Blink Detection (Tasks API for Python 3.12) ───────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "face_landmarker.task")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Missing '{MODEL_PATH}' — download it from:\n"
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    )

face_landmarker = mp_vision.FaceLandmarker.create_from_options(
    mp_vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mp_vision.RunningMode.IMAGE,
        num_faces=1,
    )
)

# Eye landmark indices (MediaPipe 478-point mesh)
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]


def eye_aspect_ratio(landmarks, eye_indices: list, frame_w: int, frame_h: int) -> float:
    """
    Eye Aspect Ratio (EAR):
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
    Low EAR (~< 0.20) = eye closed / blinking.
    """
    pts = [
        (int(landmarks[i].x * frame_w), int(landmarks[i].y * frame_h))
        for i in eye_indices
    ]
    v1 = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    v2 = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    h  = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    return (v1 + v2) / (2.0 * h + 1e-6)


def detect_blink(frame: np.ndarray) -> bool:
    """Return True if a blink is detected in `frame` (BGR)."""
    h, w = frame.shape[:2]
    rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # New Tasks API uses mp.Image instead of raw numpy
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result   = face_landmarker.detect(mp_image)

    if not result.face_landmarks:
        return False

    landmarks = result.face_landmarks[0]   # list of NormalizedLandmark
    left_ear  = eye_aspect_ratio(landmarks, LEFT_EYE,  w, h)
    right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
    avg_ear   = (left_ear + right_ear) / 2.0

    return avg_ear < 0.20


# ── Helper — Decode Base64 Frame ───────────────────────────────────────────────
def decode_frame(image_b64: str) -> np.ndarray | None:
    """Decode a base64-encoded JPEG/PNG string to a BGR numpy array."""
    try:
        image_bytes = base64.b64decode(image_b64)
        np_arr      = np.frombuffer(image_bytes, np.uint8)
        frame       = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"[ERROR] Frame decode failed: {e}")
        return None


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/verify", methods=["POST"])
def verify():
    """
    Expects JSON body:
        {
            "image":       "<base64-encoded image>",
            "blink_check": true | false   (optional, default false)
        }

    Blink-check mode  → returns {"blinked": true/false}
    Recognition mode  → returns verified/unverified result
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid or missing JSON body."}), 400

    image_b64      = data.get("image")
    is_blink_check = data.get("blink_check", False)

    if not image_b64:
        return jsonify({"status": "error", "message": "Missing 'image' field."}), 400

    frame = decode_frame(image_b64)
    if frame is None:
        return jsonify({"status": "error", "message": "Could not decode image."}), 400

    # ── Blink-check mode ────────────────────────────────────────────────────
    if is_blink_check:
        blinked = detect_blink(frame)
        return jsonify({"blinked": blinked})

    # ── Face recognition mode ───────────────────────────────────────────────
    faces = face_app.get(frame)

    if not faces:
        return jsonify({"status": "no_face", "message": "No face detected."})

    if not reference_embeddings:
        return jsonify({"status": "error", "message": "No reference faces loaded."}), 500

    for face in faces:
        embedding    = face.embedding
        similarities = [cosine_similarity(embedding, ref) for ref in reference_embeddings]
        best_idx     = int(np.argmax(similarities))
        best_score   = similarities[best_idx]

        if best_score >= 0.5:
            name = reference_names[best_idx]
            return jsonify({
                "status":     "verified",
                "name":       name,
                "confidence": round(best_score, 4),
                "time":       datetime.now().strftime("%I:%M %p"),
                "date":       datetime.now().strftime("%B %d, %Y"),
            })

    return jsonify({"status": "unverified", "message": "Face not recognized."})


@app.route("/health", methods=["GET"])
def health():
    """Quick health-check endpoint."""
    return jsonify({
        "status":            "ok",
        "references_loaded": len(reference_names),
        "names":             reference_names,
    })


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

    