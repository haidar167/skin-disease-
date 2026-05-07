import os
from PIL import Image
from torch.utils.data import Dataset

class SkinDiseaseDataset(Dataset):
    def __init__(self, img_dir, diseases_list_file, transform=None):
        self.img_dir = img_dir
        with open(diseases_list_file) as f:
            self.diseases = [line.strip() for line in f.readlines() if line.strip()]
        self.img_paths = []
        self.labels = []
        for idx, disease in enumerate(self.diseases):
            disease_folder = os.path.join(img_dir, disease)
            if not os.path.isdir(disease_folder):
                continue
            for fname in os.listdir(disease_folder):
                if fname.lower().endswith(('jpg','jpeg','png')):
                    self.img_paths.append(os.path.join(disease_folder, fname))
                    self.labels.append(idx)
        self.transform = transform

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        img = Image.open(self.img_paths[idx]).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            img = self.transform(img)
        return img, label
