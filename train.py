"""Train a ResNet-18 classifier on a real folder-based image dataset."""

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
IMAGENET_STD = [0.229, 0.224, 0.225]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data", help="Root containing one folder per class")
    parser.add_argument(
        "--classes-file",
        help="Optional ordered list of classes; by default class folders are discovered",
    )
    parser.add_argument(
        "--output-dir",
        default=Path(__file__).resolve().parent / "models",
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--no-pretrained",
        action="store_true",
        help="Do not initialize with ImageNet weights (useful for offline smoke tests)",
    )
    return parser.parse_args()


def stratified_split(targets, validation_split, seed):
    if not 0 < validation_split < 1:
        raise ValueError("--validation-split must be greater than 0 and less than 1")

    by_class = defaultdict(list)
    for index, label in enumerate(targets):
        by_class[label].append(index)

    rng = random.Random(seed)
    train_indices, validation_indices = [], []
    for label, indices in sorted(by_class.items()):
        if len(indices) < 2:
            raise ValueError(
                f"Class index {label} has only one image; at least two are required "
                "for training and validation"
            )
        rng.shuffle(indices)
        validation_count = min(len(indices) - 1, max(1, round(len(indices) * validation_split)))
        validation_indices.extend(indices[:validation_count])
        train_indices.extend(indices[validation_count:])

    rng.shuffle(train_indices)
    rng.shuffle(validation_indices)
    return train_indices, validation_indices


def make_transforms(image_size):
    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
    validation_transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
    return train_transform, validation_transform


def evaluate(model, loader, criterion, device):
    model.eval()
    loss_total, loss_weight, correct, sample_count = 0.0, 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            batch_weight = (
                criterion.weight[labels].sum().item()
                if criterion.weight is not None
                else labels.numel()
            )
            loss_total += loss.item() * batch_weight
            loss_weight += batch_weight
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            sample_count += images.size(0)
    return loss_total / loss_weight, correct / sample_count


def save_checkpoint(path, model, classes, image_size, epoch, validation_accuracy):
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "classes": classes,
            "image_size": image_size,
            "normalization": {"mean": IMAGENET_MEAN, "std": IMAGENET_STD},
            "epoch": epoch,
            "validation_accuracy": validation_accuracy,
            "architecture": "resnet18",
        },
        path,
    )


def main():
    args = parse_args()
    if (
        args.epochs < 1
        or args.batch_size < 1
        or args.image_size < 1
        or args.learning_rate <= 0
    ):
        raise ValueError(
            "Epochs, batch size, image size, and learning rate must all be positive"
        )

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    dataset = SkinDiseaseDataset(args.data_dir, args.classes_file)
    train_indices, validation_indices = stratified_split(
        dataset.targets, args.validation_split, args.seed
    )
    train_transform, validation_transform = make_transforms(args.image_size)
    train_dataset = Subset(dataset.with_transform(train_transform), train_indices)
    validation_dataset = Subset(dataset.with_transform(validation_transform), validation_indices)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pin_memory = device.type == "cuda"
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.workers,
        pin_memory=pin_memory,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.workers,
        pin_memory=pin_memory,
    )

    weights = None if args.no_pretrained else models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, len(dataset.classes))
    model = model.to(device)

    train_counts = Counter(dataset.targets[index] for index in train_indices)
    class_weights = torch.tensor(
        [
            len(train_indices) / (len(dataset.classes) * train_counts[index])
            for index in range(len(dataset.classes))
        ],
        dtype=torch.float32,
        device=device,
    )
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    best_accuracy = -1.0
    print(
        f"Training {len(dataset.classes)} classes from {len(train_indices)} images; "
        f"validating on {len(validation_indices)} images using {device}."
    )

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        running_weight = 0.0
        loop = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}")
        for images, labels in loop:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            batch_weight = criterion.weight[labels].sum().item()
            running_loss += loss.item() * batch_weight
            running_weight += batch_weight
            loop.set_postfix(loss=f"{loss.item():.4f}")

        train_loss = running_loss / running_weight
        validation_loss, validation_accuracy = evaluate(
            model, validation_loader, criterion, device
        )
        print(
            f"Epoch {epoch}: train_loss={train_loss:.4f}, "
            f"val_loss={validation_loss:.4f}, val_accuracy={validation_accuracy:.2%}"
        )
        save_checkpoint(
            output_dir / "last_model.pt",
            model,
            dataset.classes,
            args.image_size,
            epoch,
            validation_accuracy,
        )
        if validation_accuracy > best_accuracy:
            best_accuracy = validation_accuracy
            save_checkpoint(
                output_dir / "best_model.pt",
                model,
                dataset.classes,
                args.image_size,
                epoch,
                validation_accuracy,
            )

    print(f"Training complete. Best validation accuracy: {best_accuracy:.2%}")
    print(f"Best checkpoint: {output_dir / 'best_model.pt'}")


if __name__ == "__main__":
    main()
