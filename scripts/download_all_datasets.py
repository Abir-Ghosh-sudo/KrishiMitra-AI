#!/usr/bin/env python3
"""Download agricultural datasets from Kaggle, HuggingFace, and direct URLs."""

import os
import sys
import json
import zipfile
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data" / "raw"
KAGGLE_DIR = ROOT / ".kaggle"

# Create directories
for subdir in ["plant_disease", "pest", "weed", "satellite", "yield", "weather", "soil", "market", "rag"]:
    (DATA_RAW / subdir).mkdir(parents=True, exist_ok=True)

def download_file(url, dest, desc=None):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[SKIP] {dest.name} already exists")
        return
    try:
        resp = requests.get(url, stream=True, headers={"User-Agent": "KrishiMitra-AI/1.0"})
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        with open(dest, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True, desc=desc or dest.name) as pbar:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))
        print(f"[OK] Downloaded {dest}")
    except Exception as e:
        print(f"[ERR] Failed to download {url}: {e}")

def download_kaggle(dataset, target_dir, unzip=True):
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        import kaggle
        print(f"[KAGGLE] Downloading {dataset} -> {target_dir}")
        kaggle.api.dataset_download_files(dataset, path=str(target_dir), unzip=unzip)
        print(f"[OK] {dataset}")
    except Exception as e:
        print(f"[ERR] Kaggle {dataset}: {e}")
        print("Make sure kaggle.json is in ~/.kaggle/ or ./.kaggle/")

def download_hf(dataset, target_dir, repo_type="dataset"):
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import snapshot_download
        print(f"[HF] Downloading {dataset} -> {target_dir}")
        snapshot_download(repo_id=dataset, repo_type=repo_type, local_dir=str(target_dir))
        print(f"[OK] {dataset}")
    except Exception as e:
        print(f"[ERR] HuggingFace {dataset}: {e}")

def main():
    print("=" * 60)
    print("KrishiMitra-AI Dataset Downloader")
    print("=" * 60)
    
    # Plant Disease - Kaggle
    print("\n### Plant Disease Datasets ###")
    download_kaggle("abdallahalidev/plantvillage-dataset", DATA_RAW / "plant_disease" / "plantvillage")
    download_kaggle("emmarex/plantdisease", DATA_RAW / "plant_disease" / "plantdisease_alt")
    download_kaggle("vipoooool/new-plant-diseases-dataset", DATA_RAW / "plant_disease" / "new_plant_diseases")
    download_kaggle("abdulhasibuddin/plant-doc-dataset", DATA_RAW / "plant_disease" / "plantdoc")
    download_kaggle("nirmalsankalana/cassava-leaf-disease-classification", DATA_RAW / "plant_disease" / "cassava")
    download_kaggle("rizwan123456789/rice-leaf-diseases-dataset", DATA_RAW / "plant_disease" / "rice")
    
    # Pest
    print("\n### Pest Datasets ###")
    download_kaggle("rtlmhjbn/ip02-dataset", DATA_RAW / "pest" / "ip102")
    
    # Weed
    print("\n### Weed Datasets ###")
    download_kaggle("aleemaparakatta/weed-detection-in-soybean-crops", DATA_RAW / "weed" / "deepweeds")
    
    # HuggingFace
    print("\n### HuggingFace Datasets ###")
    download_hf("linkanjarad/plant-disease-classification-dataset", DATA_RAW / "plant_disease" / "hf_plant")
    download_hf("yassiracharki/Crop-Disease-Detection-PlantVillage", DATA_RAW / "plant_disease" / "hf_plantvillage")
    
    print("\n" + "=" * 60)
    print("Download complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
