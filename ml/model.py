import streamlit as st
import os

# Set Legacy Keras for compatibility with TF 2.16+
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import tensorflow as tf
import keras
from PIL import Image
import numpy as np
import os
import json

# ---------------- CONSTANTS ---------------- #
CLASSES = ["CNV", "DME", "Drusen", "Normal"]
IMG_SIZE = (224, 224)


# ---------------- LOAD MODEL ---------------- #
@st.cache_resource
def load_model():
    """Load trained model safely."""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    model_paths = [
        os.path.join(base_dir, "mobilenetv3_oct.h5"),
        os.path.join(base_dir, "model", "mobilenetv3_oct.h5"),
        os.path.join(base_dir, "model", "eye_disease_model (2).keras")
    ]

    for path in model_paths:
        if os.path.exists(path):
            try:
                model = keras.models.load_model(path)
                print(f"Model loaded from: {path}")
                return model
            except Exception as e:
                print(f"Error loading model from {path}: {e}")

    st.error("❌ Model file not found.")
    return None


# ---------------- IMAGE PREPROCESS ---------------- #
def process_image(image: Image.Image):
    """Prepare image for model."""

    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.resize(IMG_SIZE)

    img_array = np.array(image)

    # MobileNetV3 preprocessing
    img_array = keras.applications.mobilenet_v3.preprocess_input(img_array)

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


# ---------------- PREDICTION ---------------- #
def predict(image: Image.Image, model):
    """Run prediction safely (NO ERRORS)."""

    if model is None:
        return None, 0.0, "{}"

    # Preprocess
    img_array = process_image(image)

    # Predict
    predictions = model.predict(img_array)

    # 🔥 CRITICAL FIX: Flatten output safely
    probs = np.array(predictions)
    probs = np.squeeze(probs)      # remove extra dimensions
    probs = probs.flatten()        # ensure 1D

    # Safety check all 4 parameters run
    if len(probs) != len(CLASSES):
        st.error(f"⚠️ Model output mismatch: got {len(probs)} values")
        return None, 0.0, "{}"

    # Get prediction
    predicted_idx = int(np.argmax(probs))
    predicted_class = CLASSES[predicted_idx]

    # Confidence
    confidence = float(probs[predicted_idx])

    # Full probabilities
    probs_dict = {
        CLASSES[i]: float(probs[i]) for i in range(len(CLASSES))
    }

    return predicted_class, confidence, json.dumps(probs_dict)