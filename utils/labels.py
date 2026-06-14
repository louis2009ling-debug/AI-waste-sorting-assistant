CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

RECYCLING_SUGGESTIONS = {
    "cardboard": "Clean cardboard should be folded and placed in the recycling bin.",
    "glass": "Glass bottles and jars should usually go into the glass recycling bin.",
    "metal": "Metal cans should be emptied and placed in the recycling bin.",
    "paper": "Dry paper can usually be recycled.",
    "plastic": "Plastic containers should be cleaned before recycling.",
    "trash": "This item may belong in general waste if it cannot be recycled.",
}

MODEL_LABELS = {
    "mobilenetv2": "MobileNetV2 Transfer Learning",
    "simple_cnn": "Simple CNN",
}


def get_suggestion(label):
    return RECYCLING_SUGGESTIONS.get(label, "No suggestion available.")
