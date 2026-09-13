---
name: skin-disease-classifier
description: >
  Educational multi-class skin lesion image classification pipeline using
  PyTorch (ResNet-18), SQLite history, and an extensible disease list.
  Use this skill to train a skin disease classifier from a labeled image
  dataset, run inference on individual images, or launch a Tkinter desktop
  application that stores prediction history in SQLite. NOT for clinical use.
---

# Skin Disease Image Classifier Skill

> **âš ï¸ Disclaimer:** This project is for educational purposes only. Model
> outputs are not clinically validated and must never be used as medical
> advice or as a substitute for a qualified dermatologist.

## Overview

This skill provides a complete end-to-end pipeline for:

1. **Training** a ResNet-18 image classifier on a custom skin lesion dataset
2. **Running inference** on individual images from the command line
3. **Launching a Tkinter desktop app** that loads the trained checkpoint and
   logs prediction history to a local SQLite database (`skin_disease.db`)

## Repository Structure

```
skin-disease-/
â”œâ”€â”€ train.py                  # Transfer-learning trainer (ResNet-18)
â”œâ”€â”€ detection.py              # CLI inference script
â”œâ”€â”€ data_loader.py            # Dataset validation & class-folder loader
â”œâ”€â”€ university_skin_system.py # Tkinter desktop app + SQLite history
â”œâ”€â”€ app.py                    # (Optional) Flask/web entry point
â”œâ”€â”€ diseases_list.txt         # Example class vocabulary (not ground truth)
â”œâ”€â”€ requirements.txt          # Core Python dependencies (PyTorch, torchvision)
â”œâ”€â”€ requirements-web.txt      # Extra deps for the web app variant
â”œâ”€â”€ skin_disease.db           # SQLite prediction history database
â”œâ”€â”€ templates/                # HTML templates for the web variant
â”œâ”€â”€ DATASET.md                # Dataset acquisition & folder structure guide
â”œâ”€â”€ SETUP.md                  # Environment setup instructions
â”œâ”€â”€ SECURITY.md               # Security policy
â””â”€â”€ TEST_VERIFICATION_GUIDE.md
```

## Prerequisites

- Python 3.9+
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Prepare your dataset

Arrange your images into labelled class sub-folders as described in
`DATASET.md`. Example layout:

```
data/
â”œâ”€â”€ melanoma/
â”‚   â”œâ”€â”€ img001.jpg
â”‚   â””â”€â”€ ...
â”œâ”€â”€ nevus/
â”‚   â””â”€â”€ ...
â””â”€â”€ seborrheic_keratosis/
    â””â”€â”€ ...
```

Recommended public datasets: [HAM10000](https://doi.org/10.1038/sdata.2018.161)
and the [ISIC Archive](https://www.isic-archive.com/).
Always follow each source's licensing, attribution, and privacy terms.

### 2. Train the model

```bash
python train.py --data-dir data --epochs 10 --batch-size 16
```

Key options (run `python train.py --help` for the full list):

| Flag | Default | Description |
|------|---------|-------------|
| `--data-dir` | `data` | Root folder containing class sub-directories |
| `--epochs` | `10` | Number of training epochs |
| `--batch-size` | `16` | Mini-batch size |
| `--lr` | `1e-4` | Learning rate |

Outputs saved to:
- `models/best_model.pt` â€” best validation checkpoint
- `models/last_model.pt` â€” final epoch checkpoint

Each checkpoint embeds the class mapping and preprocessing settings required
by inference.

### 3. Run inference (CLI)

```bash
python detection.py path/to/image.jpg --model models/best_model.pt --top-k 3
```

Returns the top-k predicted disease classes with confidence scores.

### 4. Launch the desktop application

```bash
python university_skin_system.py
```

Or point to a different checkpoint:

```bash
SKIN_DISEASE_MODEL=models/last_model.pt python university_skin_system.py
```

The app loads the checkpoint, lets you upload/select an image, displays the
top predictions, and records each session in `skin_disease.db`.

### 5. (Optional) Launch the web application

```bash
pip install -r requirements-web.txt
python app.py
```

## Agent Instructions

When this skill is triggered, follow these steps:

1. **Confirm prerequisites** â€” check that Python and pip are available.
2. **Install dependencies** â€” run `pip install -r requirements.txt` in the
   project directory.
3. **Guide dataset preparation** â€” refer the user to `DATASET.md` and help
   them organise their image folders.
4. **Train** â€” run `train.py` with appropriate flags; monitor validation
   accuracy and report results.
5. **Evaluate** â€” run `detection.py` on a sample image to verify the
   checkpoint loaded correctly.
6. **Launch** â€” start `university_skin_system.py` or `app.py` as requested.
7. **Safety reminder** â€” always reiterate that outputs are for educational
   purposes only and are not a substitute for professional medical diagnosis.
