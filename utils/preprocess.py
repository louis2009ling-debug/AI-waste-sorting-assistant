import numpy as np
from PIL import Image
from tensorflow import keras


def load_image_array(image_path, image_size=(160, 160)):
    image = Image.open(image_path).convert("RGB")
    image = image.resize(image_size)
    array = np.array(image, dtype="float32")
    array = np.expand_dims(array, axis=0)
    return array


def preprocess_for_model(image_path, model_type, image_size=(160, 160)):
    array = load_image_array(image_path, image_size=image_size)

    if model_type == "mobilenetv2":
        return keras.applications.mobilenet_v2.preprocess_input(array)

    return array
