# Using a real image dataset

This repository intentionally does not bundle patient images. Obtain a dataset
whose license permits your use, such as HAM10000 or an appropriate collection
from the ISIC Archive, and review its consent, attribution, and usage terms.
Do not commit patient images or identifying metadata.

Arrange the images into one directory per diagnosis:

```text
data/
├── melanoma/
│   ├── image_001.jpg
│   └── image_002.jpg
└── nevus/
    ├── image_003.jpg
    └── image_004.jpg
```

Folder names become the model's class labels. Each class needs at least two
readable images so that one can be reserved for validation. Nested image folders
are supported. JPG, JPEG, PNG, BMP, TIF, and TIFF files are accepted.

If a reproducible class order is required, create a text file containing exactly
the folder names, one per line, and pass it with `--classes-file`. The existing
`diseases_list.txt` is only an example vocabulary; it is no longer treated as the
classes in a dataset unless explicitly selected.

Keep subjects, rather than individual photos, isolated between training and
validation when multiple images of the same patient are available. The built-in
split is stratified by class but cannot detect patient identity. For publishable
or clinical research, independently audit labels, leakage, class balance,
demographic performance, calibration, and external validation.
