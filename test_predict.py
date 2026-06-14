import sys
from pathlib import Path

from utils.predict import load_model, predict_image


VALID_MODELS = {"mobilenetv2", "simple_cnn"}


def show_usage():
    print("Usage: python test_predict.py <image_path> [model_name]")
    print("model_name options: mobilenetv2, simple_cnn")


def show_result(model_name, image_path, result):
    print("Model:", model_name)
    print("Image:", image_path)
    print("Predicted class:", result["predicted_class"])
    print("Confidence:", f'{result["confidence"]}%')
    print("Recognition score:", result["recognition_score"], "/ 100")
    print("Top-3 predictions:")

    for index, item in enumerate(result["top_predictions"], start=1):
        print(f'{index}. {item["label"]} - {item["score"]}%')

    print("Suggestion:", result["suggestion"])


def main():
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)

    image_path = Path(sys.argv[1])
    selected_model = sys.argv[2].lower() if len(sys.argv) > 2 else "mobilenetv2"

    if selected_model not in VALID_MODELS:
        print("Unsupported model:", selected_model)
        show_usage()
        sys.exit(1)

    if not image_path.exists():
        print("Image file not found:", image_path)
        sys.exit(1)

    model = load_model(selected_model)
    result = predict_image(model, image_path, selected_model)
    show_result(selected_model, image_path, result)


if __name__ == "__main__":
    main()
