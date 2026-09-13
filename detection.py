"""Run inference using a checkpoint produced by train.py."""

import argparse
from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms


DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "best_model.pt"


class SkinDiseasePredictor:
    def __init__(self, model_path=DEFAULT_MODEL_PATH, device=None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        checkpoint_path = Path(model_path)
        if not checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Trained model not found: {checkpoint_path}. Run train.py first."
            )

        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
        required = {"model_state_dict", "classes", "image_size", "normalization"}
        missing = required.difference(checkpoint)
        if missing:
            raise ValueError(
                f"Unsupported checkpoint {checkpoint_path}; missing: {', '.join(sorted(missing))}"
            )
        if checkpoint.get("architecture", "resnet18") != "resnet18":
            raise ValueError("Only resnet18 checkpoints are currently supported")

        self.classes = checkpoint["classes"]
        model = models.resnet18(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, len(self.classes))
        model.load_state_dict(checkpoint["model_state_dict"])
        self.model = model.to(self.device).eval()

        normalization = checkpoint["normalization"]
        self.transform = transforms.Compose(
            [
                transforms.Resize((checkpoint["image_size"], checkpoint["image_size"])),
                transforms.ToTensor(),
                transforms.Normalize(normalization["mean"], normalization["std"]),
            ]
        )

    def predict(self, image_path, top_k=1):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        with Image.open(image_path) as image:
            tensor = self.transform(image.convert("RGB")).unsqueeze(0).to(self.device)

        with torch.no_grad():
            probabilities = torch.softmax(self.model(tensor), dim=1)[0]
        count = min(top_k, len(self.classes))
        scores, indices = probabilities.topk(count)
        return [
            {"label": self.classes[index], "confidence": float(score)}
            for score, index in zip(scores.cpu().tolist(), indices.cpu().tolist())
        ]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Path to the image to classify")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--top-k", type=int, default=3)
    return parser.parse_args()


def main():
    args = parse_args()
    predictions = SkinDiseasePredictor(args.model).predict(args.image, args.top_k)
    for prediction in predictions:
        print(f"{prediction['label']}: {prediction['confidence']:.2%}")


if __name__ == "__main__":
    main()
