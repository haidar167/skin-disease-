"""Run inference using a checkpoint produced by train.py.

Usage:
    python detection.py path/to/image.jpg
    python detection.py path/to/image.jpg --top-k 5
    python detection.py path/to/image.jpg --gradcam
"""

import argparse
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "best_model.pt"


class SkinDiseasePredictor:
    """Load a checkpoint and run inference on skin lesion images."""

    def __init__(self, model_path=DEFAULT_MODEL_PATH, device=None):
        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        ckpt_path = Path(model_path)
        if not ckpt_path.is_file():
            raise FileNotFoundError(
                f"Model checkpoint not found: {ckpt_path}\n"
                "Run  python train.py --data-dir data  first."
            )

        ckpt = torch.load(ckpt_path, map_location=self.device, weights_only=True)
        required = {"model_state_dict", "classes", "image_size", "normalization"}
        missing  = required.difference(ckpt)
        if missing:
            raise ValueError(f"Checkpoint missing keys: {', '.join(sorted(missing))}")
        if ckpt.get("architecture", "resnet18") != "resnet18":
            raise ValueError("Only resnet18 checkpoints are supported.")

        self.classes   = ckpt["classes"]
        image_size     = ckpt["image_size"]
        norm           = ckpt["normalization"]

        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(norm["mean"], norm["std"]),
        ])

        self.model = models.resnet18(weights=None)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, len(self.classes))
        self.model.load_state_dict(ckpt["model_state_dict"])
        self.model.to(self.device).eval()

        # Grad-CAM hooks on the last residual block
        self._activations: torch.Tensor | None = None
        self._gradients:   torch.Tensor | None = None
        self.model.layer4.register_forward_hook(self._fwd_hook)
        self.model.layer4.register_full_backward_hook(self._bwd_hook)

    def _fwd_hook(self, _module, _inp, output):
        self._activations = output.detach()

    def _bwd_hook(self, _module, _grad_in, grad_out):
        self._gradients = grad_out[0].detach()

    # ── Core inference ─────────────────────────────────────────────────────────

    def predict(self, image_path, top_k: int = 3):
        """Return list of (class_name, confidence_pct) sorted by confidence."""
        img    = Image.open(image_path).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            probs = F.softmax(self.model(tensor), dim=1)[0]
        k = min(top_k, len(self.classes))
        vals, idxs = probs.topk(k)
        return [(self.classes[i.item()], round(v.item() * 100, 2))
                for v, i in zip(vals, idxs)]

    # ── Grad-CAM ───────────────────────────────────────────────────────────────

    def predict_with_gradcam(self, image_path, top_k: int = 3):
        """Run inference and save a Grad-CAM overlay next to the image."""
        image_path = Path(image_path)
        img    = Image.open(image_path).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        tensor.requires_grad_(True)

        logits = self.model(tensor)
        probs  = F.softmax(logits, dim=1)[0]
        top_class = probs.argmax().item()

        self.model.zero_grad()
        logits[0, top_class].backward()

        try:
            import cv2
            import numpy as np

            grads  = self._gradients[0]       # [C, H, W]
            acts   = self._activations[0]     # [C, H, W]
            w      = grads.mean(dim=(1, 2))   # [C]
            cam    = torch.clamp((w[:, None, None] * acts).sum(0), min=0).cpu().numpy()
            if cam.max() > 0:
                cam = (cam - cam.min()) / (cam.max() - cam.min())

            ow, oh = img.size
            cam_up  = cv2.resize(cam, (ow, oh))
            heatmap = cv2.applyColorMap((cam_up * 255).astype("uint8"), cv2.COLORMAP_JET)
            orig    = np.array(img)[..., ::-1]          # RGB → BGR
            overlay = cv2.addWeighted(orig, 0.55, heatmap, 0.45, 0)
            out     = image_path.with_name(image_path.stem + "_heatmap.png")
            cv2.imwrite(str(out), overlay)
            print(f"  🔥 Grad-CAM heatmap saved → {out}")
        except ImportError:
            print("  ⚠️  opencv-python not installed — skipping Grad-CAM.")
            print("      pip install opencv-python-headless")

        k = min(top_k, len(self.classes))
        vals, idxs = probs.detach().topk(k)
        return [(self.classes[i.item()], round(v.item() * 100, 2))
                for v, i in zip(vals, idxs)]


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image",     help="Path to the input image")
    parser.add_argument("--model",   default=DEFAULT_MODEL_PATH,
                        help="Path to checkpoint (default: models/best_model.pt)")
    parser.add_argument("--top-k",   type=int, default=3)
    parser.add_argument("--gradcam", action="store_true",
                        help="Generate and save a Grad-CAM heatmap")
    args = parser.parse_args()

    predictor = SkinDiseasePredictor(model_path=args.model)
    print(f"\n🔬 Analysing: {args.image}\n")

    if args.gradcam:
        results = predictor.predict_with_gradcam(args.image, top_k=args.top_k)
    else:
        results = predictor.predict(args.image, top_k=args.top_k)

    print("Top predictions:")
    print("─" * 55)
    for rank, (name, conf) in enumerate(results, 1):
        filled = int(conf / 5)
        bar    = "█" * filled + "░" * (20 - filled)
        print(f"  {rank}. {name:<30} {bar} {conf:5.1f}%")
    print("─" * 55)
    print("\n⚠️  For educational purposes only — not medical advice.")


if __name__ == "__main__":
    main()
