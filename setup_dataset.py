"""
setup_dataset.py — Download and organise the HAM10000 dataset for training.

Usage:
    python setup_dataset.py              # Download real HAM10000 via Kaggle API
    python setup_dataset.py --demo       # Create a small synthetic demo dataset
    python setup_dataset.py --demo --demo-size 100
"""

import argparse
import csv
import os
import random
import shutil
from pathlib import Path

DATA_DIR = Path("data")

# Mapping: HAM10000 dx code → folder name
HAM10000_CLASSES = {
    "akiec": "Actinic_Keratosis",
    "bcc":   "Basal_Cell_Carcinoma",
    "bkl":   "Benign_Keratosis",
    "df":    "Dermatofibroma",
    "mel":   "Melanoma",
    "nv":    "Melanocytic_Nevi",
    "vasc":  "Vascular_Lesion",
}


# ── Kaggle download ────────────────────────────────────────────────────────────

def download_ham10000():
    """Download HAM10000 from Kaggle and organise into class folders."""
    # Check kaggle package
    try:
        import kaggle  # noqa: F401
    except ImportError:
        raise SystemExit(
            "❌  'kaggle' package not found.\n"
            "    pip install kaggle\n"
            "    Then place your API key at  ~/.kaggle/kaggle.json\n"
            "    (Kaggle → Settings → Account → API → Create New Token)"
        )

    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        raise SystemExit(
            "❌  Kaggle API key not found at ~/.kaggle/kaggle.json\n"
            "    Get it from  https://www.kaggle.com/settings/account"
            "  →  API  →  Create New Token"
        )

    raw = Path("ham10000_raw")
    raw.mkdir(exist_ok=True)

    print("📥  Downloading HAM10000 from Kaggle (~3 GB) …")
    ret = os.system(
        f'kaggle datasets download '
        f'-d kmader/skin-cancer-mnist-ham10000 '
        f'-p "{raw}" --unzip'
    )
    if ret != 0:
        raise SystemExit("❌  Kaggle download failed. Check your API key and internet connection.")

    print("\n📂  Organising images into class folders …")
    _organise(raw)

    print("🧹  Removing raw download …")
    shutil.rmtree(raw, ignore_errors=True)
    print("✅  Done! Dataset is ready in  ./data/")


def _organise(raw_dir: Path):
    """Move images from the raw HAM10000 download into data/<ClassName>/ folders."""
    # Find metadata CSV
    csv_files = sorted(raw_dir.rglob("HAM10000_metadata.csv"))
    if not csv_files:
        csv_files = sorted(raw_dir.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("Could not locate metadata CSV in the downloaded files.")

    meta_path = csv_files[0]
    print(f"   Metadata: {meta_path}")

    # Index all images by stem
    all_images: dict[str, Path] = {}
    for ext in (".jpg", ".jpeg", ".png"):
        for p in raw_dir.rglob(f"*{ext}"):
            all_images[p.stem] = p

    DATA_DIR.mkdir(exist_ok=True)
    moved, skipped = 0, 0

    with meta_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            image_id   = row.get("image_id", "").strip()
            dx         = row.get("dx", "").strip().lower()
            class_name = HAM10000_CLASSES.get(dx)
            src        = all_images.get(image_id)

            if not class_name or not src:
                skipped += 1
                continue

            dest = DATA_DIR / class_name
            dest.mkdir(exist_ok=True)
            shutil.copy2(src, dest / src.name)
            moved += 1

    print(f"   ✅  {moved} images organised into {len(HAM10000_CLASSES)} classes "
          f"({skipped} skipped / unknown class)")


# ── Synthetic demo dataset ─────────────────────────────────────────────────────

def create_demo(images_per_class: int = 50):
    """Create a tiny synthetic dataset — good for verifying the pipeline."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit("pip install Pillow")

    print(f"🎨  Creating synthetic demo dataset "
          f"({images_per_class} images × {len(HAM10000_CLASSES)} classes) …")

    base_colors = [
        (220, 150, 130), (180, 100, 80), (200, 170, 140),
        (160, 90,  70),  (240, 200, 180), (190, 130, 110), (210, 160, 120),
    ]
    rng = random.Random(42)

    for (short, name), color in zip(HAM10000_CLASSES.items(), base_colors):
        cls_dir = DATA_DIR / name
        cls_dir.mkdir(parents=True, exist_ok=True)
        for i in range(images_per_class):
            img  = Image.new("RGB", (224, 224), color)
            draw = ImageDraw.Draw(img)
            for _ in range(rng.randint(4, 15)):
                x, y = rng.randint(0, 224), rng.randint(0, 224)
                r    = rng.randint(5, 45)
                shade = tuple(max(0, min(255, c + rng.randint(-50, 50))) for c in color)
                draw.ellipse([x - r, y - r, x + r, y + r], fill=shade)
            img.save(cls_dir / f"{short}_{i:04d}.jpg", quality=85)
        print(f"   ✅  {name:<35}  {images_per_class} images")

    print("\n✅  Demo dataset ready in  ./data/")
    print("   ⚠️  Synthetic images only — the trained model will NOT be clinically useful.")
    print("      Use  --kaggle  or add real images for meaningful results.\n")


# ── Stats ──────────────────────────────────────────────────────────────────────

def print_stats():
    if not DATA_DIR.exists():
        print("⚠️  No data/ directory found.")
        return
    print("\n📊  Dataset statistics:")
    total = 0
    for d in sorted(DATA_DIR.iterdir()):
        if d.is_dir():
            n = sum(1 for f in d.iterdir() if f.suffix.lower() in
                    {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"})
            total += n
            print(f"   {d.name:<35}  {n:>5} images")
    print(f"   {'TOTAL':<35}  {total:>5} images")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--kaggle", action="store_true", default=True,
                      help="Download real HAM10000 via Kaggle API (default)")
    mode.add_argument("--demo",   action="store_true",
                      help="Create a small synthetic demo dataset instead")
    parser.add_argument("--demo-size", type=int, default=50,
                        help="Images per class for --demo (default: 50)")
    args = parser.parse_args()

    if args.demo:
        create_demo(args.demo_size)
    else:
        download_ham10000()

    print_stats()
    print("\n🚀  Next step:")
    print("    python train.py --data-dir data --epochs 15 --batch-size 32\n")


if __name__ == "__main__":
    main()
