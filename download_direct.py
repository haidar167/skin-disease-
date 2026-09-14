import os
import shutil
import zipfile
import requests
from pathlib import Path
from tqdm import tqdm
import csv
import time

import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

DATA_DIR = Path("data")

HAM10000_CLASSES = {
    "akiec": "Actinic_Keratosis",
    "bcc":   "Basal_Cell_Carcinoma",
    "bkl":   "Benign_Keratosis",
    "df":    "Dermatofibroma",
    "mel":   "Melanoma",
    "nv":    "Melanocytic_Nevi",
    "vasc":  "Vascular_Lesion",
}

def direct_download():
    """Directly download the HAM10000 dataset zip file bypassing Kaggle package."""
    raw = Path("ham10000_raw")
    raw.mkdir(exist_ok=True)
    
    zip_path = raw / "dataset.zip"
    url = "https://www.kaggle.com/api/v1/datasets/download/kmader/skin-cancer-mnist-ham10000"
    auth = ('haidarsmi', '29dc2dede112493456bcdbe03cf9e606')
    
    current_size = zip_path.stat().st_size if zip_path.exists() else 0
    headers = {}
    if current_size > 0:
        headers['Range'] = f'bytes={current_size}-'
        print(f"📥  Resuming download from {current_size} bytes...")
    else:
        print("📥  Starting direct download of HAM10000 (~5.5 GB) from Kaggle...")
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with requests.get(url, auth=auth, stream=True, verify=False, headers=headers, timeout=(10, 60)) as r:
                if r.status_code == 416: # Range not satisfiable (already downloaded)
                    print("✅ File already fully downloaded.")
                    break
                r.raise_for_status()
                
                # If server ignores Range header, it returns 200 instead of 206
                if current_size > 0 and r.status_code == 200:
                    print("⚠️ Server does not support resume. Restarting download...")
                    current_size = 0
                    mode = 'wb'
                else:
                    mode = 'ab' if current_size > 0 else 'wb'

                total_size = int(r.headers.get('content-length', 0)) + current_size
                
                with open(zip_path, mode) as f, tqdm(
                    desc="Downloading",
                    initial=current_size,
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
                            current_size += len(chunk)
            break # Success, exit retry loop
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            print(f"\n❌ Download interrupted: {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in 5 seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(5)
                headers['Range'] = f'bytes={current_size}-'
            else:
                print("❌ Max retries reached. Download failed.")
                return

    if not zipfile.is_zipfile(zip_path):
         print("❌ Error: Downloaded file is not a valid zip file or is incomplete.")
         return
                
    print(f"\n📦  Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(raw)
        
    print("🧹  Removing zip file...")
    zip_path.unlink()
    
    print("\n📂  Organising images into class folders ...")
    _organise(raw)
    
    print("🧹  Removing raw download ...")
    shutil.rmtree(raw, ignore_errors=True)
    print("✅  Done! Dataset is ready in  ./data/")


def _organise(raw_dir: Path):
    """Move images from the raw HAM10000 download into data/<ClassName>/ folders."""
    csv_files = sorted(raw_dir.rglob("HAM10000_metadata.csv"))
    if not csv_files:
        csv_files = sorted(raw_dir.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("Could not locate metadata CSV in the downloaded files.")

    meta_path = csv_files[0]
    print(f"   Metadata: {meta_path}")

    all_images = {}
    for ext in (".jpg", ".jpeg", ".png"):
        for p in raw_dir.rglob(f"*{ext}"):
            all_images[p.stem] = p

    DATA_DIR.mkdir(exist_ok=True)
    moved, skipped = 0, 0

    with meta_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            image_id   = row.get("image_id", "").strip()
            dx         = row.get("dx", "").strip().lower()
            class_name = HAM10000_CLASSES.get(dx)
            src        = all_images.get(image_id)

            if not class_name or not src:
                skipped += 1
                continue

            dest = DATA_DIR / class_name
            dest.mkdir(exist_ok=True)
            shutil.copy2(src, dest / src.name)
            moved += 1

    print(f"   ✅  {moved} images organised into {len(HAM10000_CLASSES)} classes "
          f"({skipped} skipped / unknown class)")


if __name__ == "__main__":
    direct_download()
