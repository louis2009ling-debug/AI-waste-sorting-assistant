from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "trashnet"
MODEL_PATH = BASE_DIR / "models" / "mobilenetv2_trashnet.keras"
ACCURACY_PATH = BASE_DIR / "static" / "results" / "mobilenet_accuracy.png"
LOSS_PATH = BASE_DIR / "static" / "results" / "mobilenet_loss.png"

CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

IMAGE_SIZE = (160, 160)
BATCH_SIZE = 16
EPOCHS = 15
LEARNING_RATE = 0.0001
VALIDATION_SPLIT = 0.2
SEED = 42


def load_datasets():
    train_ds = keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=VALIDATION_SPLIT,
        subset="training",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )

    val_ds = keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=VALIDATION_SPLIT,
        subset="validation",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )

    class_names = train_ds.class_names

    if class_names != CLASS_NAMES:
        raise ValueError(f"Class order does not match expected order: {class_names}")

    return train_ds, val_ds, class_names


def build_model():
    data_augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
        ]
    )

    base_model = keras.applications.MobileNetV2(
        input_shape=IMAGE_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = keras.Input(shape=IMAGE_SIZE + (3,))
    x = data_augmentation(inputs)
    x = keras.applications.mobilenet_v2.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(len(CLASS_NAMES), activation="softmax")(x)

    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def save_curve(history, train_key, val_key, title, y_label, output_path):
    plt.figure(figsize=(6, 4))
    plt.plot(history.history[train_key], label=f"train {y_label.lower()}")
    plt.plot(history.history[val_key], label=f"val {y_label.lower()}")
    plt.title(title)
    plt.xlabel("Epoch")
    plt.ylabel(y_label)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main():
    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"Dataset folder not found: {DATASET_DIR}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACCURACY_PATH.parent.mkdir(parents=True, exist_ok=True)

    train_ds, val_ds, class_names = load_datasets()
    model = build_model()

    print("Class names:", class_names)
    print("Start training MobileNetV2...")

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
    )

    model.save(MODEL_PATH)
    save_curve(history, "accuracy", "val_accuracy", "MobileNetV2 Accuracy", "Accuracy", ACCURACY_PATH)
    save_curve(history, "loss", "val_loss", "MobileNetV2 Loss", "Loss", LOSS_PATH)

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Accuracy curve saved to: {ACCURACY_PATH}")
    print(f"Loss curve saved to: {LOSS_PATH}")


if __name__ == "__main__":
    main()
