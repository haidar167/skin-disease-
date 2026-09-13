# Skin Disease Image Classification

An educational PyTorch project for training a ResNet-18 image classifier and
using its predictions in a Tkinter desktop application. The desktop application
now uses the trained checkpoint; it no longer generates random diagnoses.

> This software and its model outputs are not clinically validated and must not
> be used as medical advice or as a substitute for a qualified dermatologist.

## Train with real data

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Obtain properly licensed, de-identified images and arrange them into class
   folders as described in [DATASET.md](DATASET.md). Real images and checkpoints
   are excluded from Git.

3. Train and validate the model:

   ```bash
   python train.py --data-dir data --epochs 10 --batch-size 16
   ```

The trainer discovers labels from the folders that are present, creates a
class-stratified validation split, compensates for class imbalance in the loss,
and stores both `models/best_model.pt` and `models/last_model.pt`. Each checkpoint
contains the exact class mapping and preprocessing settings needed by inference.
Run `python train.py --help` for all options.

## Run inference

Classify one image directly:

```bash
python detection.py path/to/image.jpg --model models/best_model.pt --top-k 3
```

Or start the desktop application:

```bash
python university_skin_system.py
```

The application loads `models/best_model.pt` by default. To select another
checkpoint, set `SKIN_DISEASE_MODEL` to its path before starting the application.

## Dataset sources

Potential research datasets include
[HAM10000](https://doi.org/10.1038/sdata.2018.161) and the
[ISIC Archive](https://www.isic-archive.com/). Dataset availability does not
automatically grant permission for every use; follow the source's current terms,
attribution requirements, and privacy restrictions.

## Other files

- `data_loader.py` validates and loads class folders.
- `train.py` performs transfer learning and validation.
- `detection.py` restores checkpoint metadata and predicts labels.
- `university_skin_system.py` provides the desktop workflow and SQLite history.
- `diseases_list.txt` is an optional example class vocabulary, not ground truth.
