# Skin Disease Image Classification

An educational PyTorch project for training a ResNet-18 image classifier on real skin lesion images and using its predictions in both a **Flask web app** and a **Tkinter desktop app**.

> ⚠️ **Disclaimer:** This software and its model outputs are not clinically validated and must **not** be used as medical advice or as a substitute for a qualified dermatologist.

---

## Quick Start (4 steps)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Download the dataset

**Option A — Real HAM10000 data (recommended):**
```bash
# First: get your Kaggle API key from https://www.kaggle.com/settings/account
# Save it to  ~/.kaggle/kaggle.json
python setup_dataset.py
```

**Option B — Synthetic demo data (no Kaggle needed):**
```bash
python setup_dataset.py --demo --demo-size 100
```

This creates `data/` with 7 class folders:

| Folder | Disease |
|--------|---------|
| `Melanoma` | Melanoma |
| `Melanocytic_Nevi` | Common mole |
| `Basal_Cell_Carcinoma` | Most common skin cancer |
| `Actinic_Keratosis` | Pre-cancerous lesion |
| `Benign_Keratosis` | Seborrheic keratosis |
| `Dermatofibroma` | Benign nodule |
| `Vascular_Lesion` | Blood vessel lesion |

### 3. Train the model

```bash
python train.py --data-dir data --epochs 15 --batch-size 32
```

Key options:

| Flag | Default | Description |
|------|---------|-------------|
| `--data-dir` | `data` | Folder with class sub-directories |
| `--epochs` | `15` | Max training epochs |
| `--batch-size` | `32` | Mini-batch size |
| `--learning-rate` | `1e-4` | Initial learning rate |
| `--patience` | `5` | Early-stopping patience |
| `--no-pretrained` | — | Skip ImageNet weights |

Training outputs saved to `models/`:
- `best_model.pt` — checkpoint with best validation accuracy
- `last_model.pt` — final epoch checkpoint
- `training_curves.png` — loss & accuracy plots
- `confusion_matrix.png` — per-class confusion matrix

### 4. Run the app

**Flask web app (browser):**
```bash
python app.py
# Open http://localhost:5000
```

**Tkinter desktop app:**
```bash
python university_skin_system.py
```

---

## CLI inference

```bash
# Top-3 predictions
python detection.py path/to/image.jpg --top-k 3

# With Grad-CAM heatmap
python detection.py path/to/image.jpg --gradcam
```

---

## Project structure

```
skin-disease-/
├── train.py                   # Transfer-learning trainer (ResNet-18)
├── detection.py               # CLI inference + Grad-CAM
├── data_loader.py             # Dataset loader with augmentation
├── setup_dataset.py           # Download HAM10000 or create demo data
├── app.py                     # Flask web application
├── university_skin_system.py  # Tkinter desktop application
├── requirements.txt
├── models/                    # Created after training
│   ├── best_model.pt
│   ├── training_curves.png
│   └── confusion_matrix.png
├── data/                      # Created by setup_dataset.py
│   ├── Melanoma/
│   ├── Melanocytic_Nevi/
│   └── ...
└── templates/                 # Flask HTML templates
```

---

## Dataset

The recommended dataset is **HAM10000** (Human Against Machine with 10000 training images):
- [HAM10000 paper](https://doi.org/10.1038/sdata.2018.161)
- [ISIC Archive](https://www.isic-archive.com/)

Always follow the source's licensing, attribution, and privacy requirements.

---

## License & safety

This project is for **educational purposes only**. The model outputs must not be used for clinical decision-making. Always consult a qualified dermatologist.
