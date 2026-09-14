"""Train a ResNet-18 classifier on a real folder-based image dataset.

Optimised for: AMD Ryzen 5 7430U (6 cores / 12 threads, ~7.4 GB RAM, CPU-only).

Usage:
    python train.py --data-dir data --epochs 30 --batch-size 8
    python train.py --help
"""

import argparse
import random
from collections import Counter, defaultdict
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import models, transforms
from tqdm import tqdm

from data_loader import SkinDiseaseDataset

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir",         default="data",
                        help="Root containing one sub-folder per class (default: data)")
    parser.add_argument("--classes-file",
                        help="Optional ordered list of classes; default = auto-discover folders")
    parser.add_argument("--output-dir",       default=Path(__file__).resolve().parent / "models")
    parser.add_argument("--epochs",           type=int,   default=30,
                        help="Number of training epochs (default: 30)")
    parser.add_argument("--batch-size",       type=int,   default=8,
                        help="Batch size — keep at 8 for 7.4 GB RAM (default: 8)")
    parser.add_argument("--learning-rate",    type=float, default=1e-4)
    parser.add_argument("--image-size",       type=int,   default=224)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--workers",          type=int,   default=4,
                        help="DataLoader workers — 4 for Ryzen 5 7430U (default: 4)")
    parser.add_argument("--seed",             type=int,   default=42)
    parser.add_argument("--num-threads",      type=int,   default=10,
                        help="PyTorch CPU threads — 10 of 12 available (default: 10)")
    parser.add_argument("--patience",         type=int,   default=7,
                        help="Early-stopping patience in epochs (default: 7)")
    parser.add_argument("--no-pretrained",    action="store_true",
                        help="Skip ImageNet pre-training (useful for offline smoke tests)")
    return parser.parse_args()


# ── Data split ─────────────────────────────────────────────────────────────────

def stratified_split(targets, validation_split, seed):
    if not 0 < validation_split < 1:
        raise ValueError("--validation-split must be between 0 and 1")
    by_class = defaultdict(list)
    for idx, label in enumerate(targets):
        by_class[label].append(idx)
    rng = random.Random(seed)
    train_idx, val_idx = [], []
    for label, indices in sorted(by_class.items()):
        if len(indices) < 2:
            raise ValueError(f"Class {label} has only {len(indices)} image — need ≥ 2.")
        rng.shuffle(indices)
        n_val = min(len(indices) - 1, max(1, round(len(indices) * validation_split)))
        val_idx.extend(indices[:n_val])
        train_idx.extend(indices[n_val:])
    rng.shuffle(train_idx)
    rng.shuffle(val_idx)
    return train_idx, val_idx


# ── Transforms ─────────────────────────────────────────────────────────────────

def make_transforms(image_size):
    train_tf = transforms.Compose([
        transforms.Resize((image_size + 32, image_size + 32)),
        transforms.RandomCrop(image_size),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        transforms.RandomErasing(p=0.2),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    return train_tf, val_tf


# ── Model ──────────────────────────────────────────────────────────────────────

def build_model(num_classes, pretrained):
    weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model   = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def compute_class_weights(targets, num_classes, device):
    counts  = Counter(targets)
    total   = len(targets)
    weights = [total / (num_classes * max(counts.get(i, 1), 1))
               for i in range(num_classes)]
    return torch.tensor(weights, dtype=torch.float32, device=device)


# ── Training loop ──────────────────────────────────────────────────────────────

def run_epoch(model, loader, criterion, optimizer, device, training):
    model.train() if training else model.eval()
    total_loss, correct, total = 0.0, 0, 0
    label = "Training" if training else "Validating"
    ctx   = torch.enable_grad() if training else torch.no_grad()
    with ctx:
        for images, labels in tqdm(loader, desc=f"  {label}", leave=False, ncols=80):
            images, labels = images.to(device), labels.to(device)
            if training:
                optimizer.zero_grad()
            outputs = model(images)
            loss    = criterion(outputs, labels)
            if training:
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * images.size(0)
            correct    += (outputs.argmax(1) == labels).sum().item()
            total      += images.size(0)
    return total_loss / total, correct / total


# ── Visualisations ─────────────────────────────────────────────────────────────

def save_plots(train_losses, val_losses, train_accs, val_accs, output_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        epochs = range(1, len(train_losses) + 1)
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        axes[0].plot(epochs, train_losses, "b-o", label="Train",      linewidth=2)
        axes[0].plot(epochs, val_losses,   "r-o", label="Validation", linewidth=2)
        axes[0].set_title("Loss",     fontsize=14, fontweight="bold")
        axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Cross-Entropy Loss")
        axes[0].legend(); axes[0].grid(True, alpha=0.3)

        axes[1].plot(epochs, [a * 100 for a in train_accs], "b-o", label="Train",      linewidth=2)
        axes[1].plot(epochs, [a * 100 for a in val_accs],   "r-o", label="Validation", linewidth=2)
        axes[1].set_title("Accuracy", fontsize=14, fontweight="bold")
        axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Accuracy (%)")
        axes[1].legend(); axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        out = Path(output_dir) / "training_curves.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  📊 Training curves  → {out}")
    except Exception as exc:
        print(f"  ⚠️  Could not save plots: {exc}")


def save_confusion_matrix(model, val_loader, classes, device, output_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for images, labels in val_loader:
                preds = model(images.to(device)).argmax(1).cpu()
                all_preds.extend(preds.numpy())
                all_labels.extend(labels.numpy())

        n  = len(classes)
        cm = np.zeros((n, n), dtype=int)
        for t, p in zip(all_labels, all_preds):
            cm[t][p] += 1

        fig, ax = plt.subplots(figsize=(max(8, n), max(6, n)))
        im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
        plt.colorbar(im, ax=ax)
        ax.set(xticks=range(n), yticks=range(n),
               xticklabels=classes, yticklabels=classes,
               title="Confusion Matrix",
               xlabel="Predicted", ylabel="True")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
        for i in range(n):
            for j in range(n):
                color = "white" if cm[i, j] > cm.max() / 2 else "black"
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color=color, fontsize=9)
        plt.tight_layout()
        out = Path(output_dir) / "confusion_matrix.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  📊 Confusion matrix → {out}")
    except Exception as exc:
        print(f"  ⚠️  Could not save confusion matrix: {exc}")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    torch.manual_seed(args.seed)

    # ── CPU optimisation for AMD Ryzen 5 7430U ──────────────────────────────
    torch.set_num_threads(args.num_threads)
    torch.set_num_interop_threads(2)   # 2 threads for inter-op parallelism

    device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🖥️  Device      : {device}")
    print(f"🧵  CPU threads : {torch.get_num_threads()} / {args.num_threads} allocated")
    print(f"📦  Batch size  : {args.batch_size}")
    print(f"👷  Workers     : {args.workers}")

    train_tf, val_tf = make_transforms(args.image_size)

    full_ds  = SkinDiseaseDataset(args.data_dir, args.classes_file, transform=train_tf)
    classes  = full_ds.classes
    targets  = [full_ds[i][1] for i in range(len(full_ds))]

    print(f"📂 Classes ({len(classes)}): {', '.join(classes)}")
    print(f"📷 Total images : {len(full_ds)}")
    for cls, cnt in full_ds.class_counts().items():
        print(f"   {cls:<35} {cnt:>5} images")

    train_idx, val_idx = stratified_split(targets, args.validation_split, args.seed)
    print(f"\n📊 Split  →  train={len(train_idx)}  val={len(val_idx)}")

    val_ds = SkinDiseaseDataset(args.data_dir, args.classes_file, transform=val_tf)

    train_loader = DataLoader(Subset(full_ds, train_idx),
                              batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers,
                              pin_memory=False,        # CPU-only: pin_memory wastes RAM
                              persistent_workers=(args.workers > 0))
    val_loader   = DataLoader(Subset(val_ds, val_idx),
                              batch_size=args.batch_size, shuffle=False,
                              num_workers=args.workers,
                              pin_memory=False,
                              persistent_workers=(args.workers > 0))

    model     = build_model(len(classes), pretrained=not args.no_pretrained).to(device)
    weights   = compute_class_weights([targets[i] for i in train_idx], len(classes), device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    best_model_path = output_dir / "best_model.pt"
    best_val_acc = 0.0
    if best_model_path.exists():
        try:
            existing_best = torch.load(best_model_path, map_location="cpu")
            best_val_acc = float(existing_best.get("val_acc", 0.0))
            print(f"📌 Existing best model checkpoint loaded (Epoch {existing_best.get('epoch', '?')} | Val Acc: {best_val_acc*100:.2f}%)")
        except Exception:
            best_val_acc = 0.0

    patience_counter = 0
    train_losses, val_losses, train_accs, val_accs = [], [], [], []

    print(f"\n🚀 Training for up to {args.epochs} epochs  (early-stop patience={args.patience})\n")

    for epoch in range(1, args.epochs + 1):
        lr = scheduler.get_last_lr()[0]
        print(f"Epoch {epoch:3d}/{args.epochs}   LR={lr:.2e}")

        tr_loss, tr_acc = run_epoch(model, train_loader, criterion, optimizer, device, training=True)
        va_loss, va_acc = run_epoch(model, val_loader,   criterion, optimizer, device, training=False)
        scheduler.step()

        train_losses.append(tr_loss); val_losses.append(va_loss)
        train_accs.append(tr_acc);    val_accs.append(va_acc)

        print(f"  Train  loss={tr_loss:.4f}  acc={tr_acc*100:.1f}%")
        print(f"  Val    loss={va_loss:.4f}  acc={va_acc*100:.1f}%")

        ckpt = dict(model_state_dict=model.state_dict(), classes=classes,
                    image_size=args.image_size,
                    normalization=dict(mean=IMAGENET_MEAN, std=IMAGENET_STD),
                    architecture="resnet18", epoch=epoch, val_acc=va_acc)
        torch.save(ckpt, output_dir / "last_model.pt")

        if va_acc > best_val_acc:
            best_val_acc    = va_acc
            patience_counter = 0
            torch.save(ckpt, output_dir / "best_model.pt")
            print(f"  ✅ New best saved!  val_acc={va_acc*100:.1f}%")
        else:
            patience_counter += 1
            print(f"  ⏳ No improvement  ({patience_counter}/{args.patience})")
            if patience_counter >= args.patience:
                print(f"\n⛔ Early stopping at epoch {epoch}")
                break
        print()

    print(f"🏁 Done.  Best val accuracy: {best_val_acc*100:.2f}%")
    save_plots(train_losses, val_losses, train_accs, val_accs, output_dir)
    save_confusion_matrix(model, val_loader, classes, device, output_dir)
    print(f"\n📁 Saved to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
