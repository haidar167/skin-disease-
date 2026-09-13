"""Dataset utilities for folder-based skin image datasets."""

from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from torch.utils.data import Dataset


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


class SkinDiseaseDataset(Dataset):
    """Load images stored as ``data_root/class_name/image.ext``.

    Class names are discovered automatically from sub-folders that are
    present, or can be fixed with an optional classes file.
    """

    def __init__(self, data_root, classes_file=None, transform=None):
        self.data_root = Path(data_root).expanduser().resolve()
        if not self.data_root.is_dir():
            raise FileNotFoundError(f"Dataset directory not found: {self.data_root}")

        present = sorted(p.name for p in self.data_root.iterdir() if p.is_dir())

        if classes_file:
            cp = Path(classes_file).expanduser()
            with cp.open(encoding="utf-8") as fh:
                classes = [ln.strip() for ln in fh if ln.strip()]
            if len(classes) != len(set(classes)):
                raise ValueError(f"Duplicate class names in {cp}")
            missing = [c for c in classes if c not in present]
            if missing:
                raise ValueError(
                    f"Classes in {cp} not found in {self.data_root}: {', '.join(missing)}"
                )
            extra = [c for c in present if c not in classes]
            if extra:
                print(f"  ℹ️  Ignoring unlisted folders: {', '.join(extra)}")
        else:
            classes = present

        if not classes:
            raise ValueError(f"No class sub-directories found in {self.data_root}")

        self.classes      = classes
        self.class_to_idx = {name: idx for idx, name in enumerate(classes)}
        self.transform    = transform
        self.samples      = self._collect()

    def _collect(self):
        samples = []
        for cls in self.classes:
            cls_dir = self.data_root / cls
            idx     = self.class_to_idx[cls]
            found   = 0
            for p in sorted(cls_dir.iterdir()):
                if p.suffix.lower() in IMAGE_EXTENSIONS:
                    samples.append((p, idx))
                    found += 1
            if found == 0:
                print(f"  ⚠️  No images in class folder: {cls}")
        return samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        path, label = self.samples[index]
        try:
            img = Image.open(path).convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise RuntimeError(f"Cannot read {path}: {exc}") from exc
        if self.transform:
            img = self.transform(img)
        return img, label

    def class_counts(self):
        """Return {class_name: image_count} dict."""
        cnt = Counter(label for _, label in self.samples)
        return {self.classes[i]: cnt[i] for i in range(len(self.classes))}
