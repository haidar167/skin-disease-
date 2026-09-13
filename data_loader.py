"""Dataset utilities for folder-based skin image datasets."""

from copy import copy
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from torch.utils.data import Dataset


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


class SkinDiseaseDataset(Dataset):
    """Load images stored as ``data_root/class_name/image.jpg``.

    Class names are discovered from folders that are actually present. An
    optional classes file can enforce a stable, explicit class order.
    """

    def __init__(self, data_root, classes_file=None, transform=None):
        self.data_root = Path(data_root).expanduser().resolve()
        if not self.data_root.is_dir():
            raise FileNotFoundError(f"Dataset directory does not exist: {self.data_root}")

        present_classes = sorted(path.name for path in self.data_root.iterdir() if path.is_dir())
        if classes_file:
            classes_path = Path(classes_file).expanduser()
            with classes_path.open(encoding="utf-8") as handle:
                classes = [line.strip() for line in handle if line.strip()]
            if len(classes) != len(set(classes)):
                raise ValueError(f"Duplicate class names found in {classes_path}")
            missing = [name for name in classes if name not in present_classes]
            if missing:
                raise ValueError(
                    "Classes listed without matching dataset folders: " + ", ".join(missing)
                )
            extra = [name for name in present_classes if name not in classes]
            if extra:
                raise ValueError(
                    "Dataset folders missing from the classes file: " + ", ".join(extra)
                )
            self.classes = classes
        else:
            self.classes = present_classes

        if len(self.classes) < 2:
            raise ValueError("A classification dataset must contain at least two class folders")

        self.class_to_idx = {name: index for index, name in enumerate(self.classes)}
        self.samples = []
        class_counts = {name: 0 for name in self.classes}
        for class_name in self.classes:
            class_dir = self.data_root / class_name
            for image_path in sorted(class_dir.rglob("*")):
                if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
                    self.samples.append((image_path, self.class_to_idx[class_name]))
                    class_counts[class_name] += 1

        if not self.samples:
            raise ValueError(f"No supported images found below {self.data_root}")
        undersized = [name for name, count in class_counts.items() if count < 2]
        if undersized:
            raise ValueError(
                "Each class needs at least two supported images; check: "
                + ", ".join(undersized)
            )

        self.targets = [label for _, label in self.samples]
        self.transform = transform

    def with_transform(self, transform):
        """Return a lightweight dataset view with a different transform."""
        dataset = copy(self)
        dataset.transform = transform
        return dataset

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, label = self.samples[index]
        try:
            with Image.open(image_path) as image:
                image = image.convert("RGB")
        except (OSError, UnidentifiedImageError) as exc:
            raise RuntimeError(f"Unable to read image: {image_path}") from exc

        if self.transform:
            image = self.transform(image)
        return image, label
