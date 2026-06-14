# EcoSort

EcoSort is a student-friendly AI waste sorting assistant built for a hackathon project. It helps users decide how to sort trash by using image classification, camera capture, and a simple text-based helper.

The project compares two machine learning models on the same task:

- `MobileNetV2 Transfer Learning`
- `Simple CNN`

This makes EcoSort both a useful demo app and a learning project about computer vision.

## Why We Built It

Many people want to recycle correctly, but they are not always sure where an item belongs. EcoSort was created to make waste sorting easier and more educational.

Instead of only giving one answer, the app also shows:

- the predicted category
- the confidence score
- the top 3 predictions
- a short recycling tip
- a comparison between two different AI models

## Main Features

- Upload an image of a waste item and get predictions from two models
- Use the browser camera to capture a waste item and classify it
- View confidence scores and top-3 prediction results
- Read simple recycling suggestions for each category
- Compare training curves and confusion matrices on a model performance page
- Type an item name into the text helper for a quick keyword-based sorting suggestion

## Waste Categories

EcoSort uses 6 categories from the TrashNet-style dataset:

- `cardboard`
- `glass`
- `metal`
- `paper`
- `plastic`
- `trash`

## Tech Stack

- Python
- Flask
- TensorFlow / Keras
- NumPy
- Pillow
- Matplotlib
- scikit-learn
- HTML / CSS / JavaScript

## Project Structure

```text
.
├── app.py
├── train_mobilenetv2.py
├── train_cnn.py
├── evaluate_mobilenetv2.py
├── evaluate_cnn.py
├── test_predict.py
├── check_dataset.py
├── requirements.txt
├── templates/
├── static/
│   ├── ecosort.js
│   ├── camera.js
│   ├── style.css
│   └── results/
└── utils/
    ├── labels.py
    ├── predict.py
    └── preprocess.py
```

## How It Works

### 1. Web App

`app.py` starts a Flask website with three main pages:

- Home page for image upload
- Camera page for live capture
- Model performance page for charts and comparison

When a user uploads or captures an image, the app runs both models and shows their results side by side.

### 2. Models

`MobileNetV2` uses transfer learning from ImageNet, so it starts with strong visual features and usually performs better.

`Simple CNN` is a smaller model trained from scratch. It is easier to understand and is great for learning the basics of convolutional neural networks.

### 3. Text Helper

The text helper is not a large language model. It uses keyword matching in `static/ecosort.js` to give a fast category suggestion for common item names.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare local folders

This repository currently expects two local resources that are not included here:

- `dataset/trashnet/` for training and evaluation
- `models/` for saved `.keras` model files

Expected model files:

- `models/mobilenetv2_trashnet.keras`
- `models/simple_cnn_trashnet.keras`

Expected dataset structure:

```text
dataset/
└── trashnet/
    ├── cardboard/
    ├── glass/
    ├── metal/
    ├── paper/
    ├── plastic/
    └── trash/
```

### 3. Run the app

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Training

Train the transfer learning model:

```bash
python train_mobilenetv2.py
```

Train the simple CNN:

```bash
python train_cnn.py
```

Training outputs include:

- saved model files in `models/`
- accuracy charts in `static/results/`
- loss charts in `static/results/`

## Evaluation

Evaluate the MobileNetV2 model:

```bash
python evaluate_mobilenetv2.py
```

Evaluate the Simple CNN:

```bash
python evaluate_cnn.py
```

These scripts generate confusion matrix images and print classification reports in the terminal.

## Quick Prediction Test

You can test one image from the command line:

```bash
python test_predict.py path/to/image.jpg mobilenetv2
```

Or:

```bash
python test_predict.py path/to/image.jpg simple_cnn
```

## Dataset Check

To verify that the dataset folders are correct:

```bash
python check_dataset.py
```

## Why This Project Is Good For a High School Hackathon

- It solves a real environmental problem
- It combines AI with a simple web app
- It is easy to demo live with image upload and camera capture
- It teaches the difference between transfer learning and a custom CNN
- It includes both technical results and a clear social impact story

## Future Ideas

- Add more waste categories
- Support local recycling rules by city
- Improve the text helper with a smarter backend
- Save prediction history for users
- Add multilingual support
- Deploy the project online

## License

This project includes a `LICENSE` file in the repository.
