from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow import keras


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "trashnet"
MODEL_PATH = BASE_DIR / "models" / "mobilenetv2_trashnet.keras"
CONFUSION_MATRIX_PATH = BASE_DIR / "static" / "results" / "mobilenet_confusion_matrix.png"

CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
IMAGE_SIZE = (160, 160)
BATCH_SIZE = 16
VALIDATION_SPLIT = 0.2
SEED = 42


def load_validation_dataset():
    val_ds = keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=VALIDATION_SPLIT,
        subset="validation",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )

    if val_ds.class_names != CLASS_NAMES:
        raise ValueError(f"Class order does not match expected order: {val_ds.class_names}")

    return val_ds


def save_confusion_matrix(cm):
    plt.figure(figsize=(7, 6))
    plt.imshow(cm, cmap="Blues")
    plt.title("MobileNetV2 Confusion Matrix")
    plt.colorbar()

    tick_marks = np.arange(len(CLASS_NAMES))
    plt.xticks(tick_marks, CLASS_NAMES, rotation=45, ha="right")
    plt.yticks(tick_marks, CLASS_NAMES)

    for row in range(cm.shape[0]):
        for col in range(cm.shape[1]):
            plt.text(col, row, str(cm[row, col]), ha="center", va="center", color="black")

    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH)
    plt.close()


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    CONFUSION_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)

    val_ds = load_validation_dataset()
    model = keras.models.load_model(MODEL_PATH, compile=False)

    y_true = []
    y_pred = []

    for images, labels in val_ds:
        predictions = model.predict_on_batch(images)
        y_true.extend(labels.numpy())
        y_pred.extend(np.argmax(predictions, axis=1))

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    cm = confusion_matrix(y_true, y_pred)
    save_confusion_matrix(cm)

    print("Confusion matrix saved to:", CONFUSION_MATRIX_PATH)
    print()
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))


if __name__ == "__main__":
    main()
