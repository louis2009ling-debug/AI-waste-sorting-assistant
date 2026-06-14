from pathlib import Path


CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def count_images(folder):
    total = 0
    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            total += 1
    return total


def main():
    dataset_dir = Path("dataset") / "trashnet"

    if not dataset_dir.exists():
        print("Dataset folder not found:", dataset_dir)
        return

    if not dataset_dir.is_dir():
        print("Dataset path is not a folder:", dataset_dir)
        return

    found_folders = sorted(
        folder.name for folder in dataset_dir.iterdir() if folder.is_dir()
    )

    expected_folders = sorted(CLASS_NAMES)

    if found_folders != expected_folders:
        print("Dataset folders do not match the expected class list.")
        print("Expected:", ", ".join(expected_folders))
        print("Found:", ", ".join(found_folders))
        return

    print("Dataset structure looks correct.")
    print()

    for class_name in CLASS_NAMES:
        class_folder = dataset_dir / class_name
        image_count = count_images(class_folder)
        print(f"{class_name}: {image_count} images")


if __name__ == "__main__":
    main()
