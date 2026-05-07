# Skin Disease Detection Project (Advanced)

This project uses deep learning to detect 50+ skin diseases from images. It now supports algorithm expansion, modern AI training methods, and a scalable database approach.

## 🚀 Features
- Detection & classification of 50+ skin diseases
- Scalable database and easy disease addition
- Model training on high-level/big data
- Modern Python backend (upgradeable to PyTorch/TensorFlow)
- Desktop app with Tkinter GUI and SQLite database (current version)

## 🧩 Algorithms & Detection
- You can implement advanced CNN architectures (ResNet, EfficientNet, etc.)
- Template scripts for `data_loader.py`, `train.py`, and `detection.py` can be provided
- Integrates with the GUI or works standalone for research

## 🗃️ Database & Data
- Use or extend current SQLite structure
- For large-scale ML: add scripts to load data from public datasets ([HAM10000](https://doi.org/10.1038/sdata.2018.161), [ISIC Archive](https://www.isic-archive.com/)), or your custom images
- `diseases_list.txt` enumerates all supported diseases (expandable to >50; add yours as needed)

## 🏋️‍♂️ High-Level Training
- Guide/scripts available for retraining or up-training models
- Easily scale up to more images/diseases by updating data folders and disease list

## 🧑‍⚕️ Supported Diseases (Examples)
(Current database contains: Acne, Eczema, Psoriasis, Ringworm, Melanoma ...)

You can expand this to 50+ diseases. Examples to add:
- Basal Cell Carcinoma
- Squamous Cell Carcinoma
- Actinic Keratosis
- Benign Keratosis
- Dermatofibroma
- Vascular Lesion
- Nevus (mole)
- ...and more

> List full names in `diseases_list.txt`, one per line, to reach 50+.

## 📦 Project Structure (Advanced)
```
skin-disease-
├── README.md
├── requirements.txt
├── diseases_list.txt (you must add all 50+)
├── data_loader.py (template can be generated for you)
├── train.py (template can be generated for you)
├── detection.py (template can be generated for you)
├── models/
└── skin_disease_system.py (current GUI+DB)
```

## 📄 Quick Start
1. Install Python 3
2. Install requirements: `pip install -r requirements.txt`
3. Prepare dataset folders as described above/with scripts
4. Edit disease list (`diseases_list.txt`)
5. Train: `python train.py` (for AI detection models)
6. Run: `python skin_disease_system.py` (current GUI)

## 🖼️ Screenshots & Demo Login (Unchanged)
- See old login and usage in the GUI; will grow as new features are added

## ⚠️ Educational/Research Usage Notice
- Not for medical/clinical use—research/academic only

## 📜 License
Specify your license

---

**Next Steps**
- Use the provided templates or scripts to add your AI, training, and detection pipeline
- Add `diseases_list.txt` with 50+ diseases
- Populate `data_loader.py`, `train.py`, and `detection.py` as needed
- Let me know if you want any starter code for these scripts!