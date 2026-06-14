from pathlib import Path
import base64
import io
import time

from flask import Flask, jsonify, render_template, request, url_for
from PIL import Image
from werkzeug.utils import secure_filename

from utils.labels import MODEL_LABELS
from utils.predict import load_model, predict_image


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

models = {}
model_error = ""


def load_models():
    loaded_models = {}

    for model_key in ["mobilenetv2", "simple_cnn"]:
        loaded_models[model_key] = load_model(model_key)

    return loaded_models


try:
    models = load_models()
except Exception as error:
    model_error = str(error)


def allowed_file(filename):
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def build_prediction_results(image_path):
    mobilenet_result = predict_image(models["mobilenetv2"], image_path, "mobilenetv2")
    simple_cnn_result = predict_image(models["simple_cnn"], image_path, "simple_cnn")
    return mobilenet_result, simple_cnn_result


@app.route("/")
def index():
    return render_template(
        "index.html",
        message=request.args.get("message", ""),
        model_error=model_error,
        model_labels=MODEL_LABELS,
    )


@app.route("/camera")
def camera():
    return render_template(
        "camera.html",
        model_error=model_error,
        model_labels=MODEL_LABELS,
    )


@app.route("/model-performance")
def model_performance():
    return render_template(
        "model_performance.html",
        model_labels=MODEL_LABELS,
    )


@app.route("/predict", methods=["POST"])
def predict():
    if model_error:
        return render_template(
            "index.html",
            message="Models are not ready.",
            model_error=model_error,
            model_labels=MODEL_LABELS,
        )

    if "image" not in request.files:
        return render_template(
            "index.html",
            message="Please choose an image first.",
            model_error=model_error,
            model_labels=MODEL_LABELS,
        )

    image_file = request.files["image"]

    if image_file.filename == "":
        return render_template(
            "index.html",
            message="Please choose an image first.",
            model_error=model_error,
            model_labels=MODEL_LABELS,
        )

    if not allowed_file(image_file.filename):
        return render_template(
            "index.html",
            message="Only png, jpg, jpeg, and webp files are supported.",
            model_error=model_error,
            model_labels=MODEL_LABELS,
        )

    filename = secure_filename(image_file.filename)
    saved_name = f"{int(time.time())}_{filename}"
    saved_path = UPLOAD_DIR / saved_name
    image_file.save(saved_path)

    try:
        mobilenet_result, simple_cnn_result = build_prediction_results(saved_path)
    except Exception as error:
        return render_template(
            "index.html",
            message=f"Prediction failed: {error}",
            model_error=model_error,
            model_labels=MODEL_LABELS,
        )

    image_url = url_for("static", filename=f"uploads/{saved_name}")

    return render_template(
        "result.html",
        image_url=image_url,
        mobilenet_result=mobilenet_result,
        simple_cnn_result=simple_cnn_result,
    )


@app.route("/camera-predict", methods=["POST"])
def camera_predict():
    if model_error:
        return jsonify({"error": "Models are not ready.", "details": model_error}), 400

    data = request.get_json()

    if not data or "image_data" not in data:
        return jsonify({"error": "No camera image received."}), 400

    image_data = data["image_data"]

    if "," not in image_data:
        return jsonify({"error": "Invalid image data."}), 400

    try:
        image_bytes = base64.b64decode(image_data.split(",", 1)[1])
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return jsonify({"error": "Could not read the camera image."}), 400

    saved_name = f"{int(time.time())}_camera.png"
    saved_path = UPLOAD_DIR / saved_name
    image.save(saved_path)

    try:
        mobilenet_result, simple_cnn_result = build_prediction_results(saved_path)
    except Exception as error:
        return jsonify({"error": f"Prediction failed: {error}"}), 500

    image_url = url_for("static", filename=f"uploads/{saved_name}")

    return jsonify(
        {
            "image_url": image_url,
            "mobilenet_result": mobilenet_result,
            "simple_cnn_result": simple_cnn_result,
        }
    )


if __name__ == "__main__":
    app.run(debug=False)
