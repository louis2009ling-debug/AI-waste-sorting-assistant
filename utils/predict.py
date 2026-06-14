from pathlib import Path

import numpy as np
from tensorflow import keras

from utils.labels import CLASS_NAMES, MODEL_LABELS, get_suggestion
from utils.preprocess import preprocess_for_model


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATHS = {
    "mobilenetv2": BASE_DIR / "models" / "mobilenetv2_trashnet.keras",
    "simple_cnn": BASE_DIR / "models" / "simple_cnn_trashnet.keras",
}


def load_model(model_type):
    model_path = MODEL_PATHS[model_type]
    return keras.models.load_model(model_path, compile=False)


def format_confidence(score):
    return round(float(score) * 100, 1)


def format_recognition_score(score):
    return int(round(float(score) * 100))


def format_top_predictions(scores, top_k=3):
    top_indexes = np.argsort(scores)[::-1][:top_k]
    results = []

    for index in top_indexes:
        results.append(
            {
                "label": CLASS_NAMES[index],
                "score": round(float(scores[index]) * 100, 1),
            }
        )

    return results


def predict_image(model, image_path, model_type):
    image_array = preprocess_for_model(image_path, model_type)
    scores = model.predict(image_array, verbose=0)[0]

    best_index = int(np.argmax(scores))
    best_label = CLASS_NAMES[best_index]
    best_score = float(scores[best_index])

    return {
        "model_key": model_type,
        "model_name": MODEL_LABELS[model_type],
        "predicted_class": best_label,
        "confidence": format_confidence(best_score),
        "recognition_score": format_recognition_score(best_score),
        "top_predictions": format_top_predictions(scores, top_k=3),
        "suggestion": get_suggestion(best_label),
    }
