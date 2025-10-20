import os
import csv
import requests
import pandas as pd
from io import BytesIO
from PIL import Image

# SETTINGS
INPUT_CSV = "../data/data.csv"
OUTPUT_CSV = "images.csv"
IMAGES_DIR = "product_images"
FALLBACK_IMAGE_PATH = "SS-logo.png"

# CREATE OUTPUT DIR
os.makedirs(IMAGES_DIR, exist_ok=True)

# READ DATA
df = pd.read_csv(INPUT_CSV)

# Ensure there's an image_url column
if "image_url" not in df.columns:
    raise ValueError("CSV must have an 'image_url' column")


# FUNCTION TO DOWNLOAD IMAGE
def download_image(url, product_id):
    """Download image and return local path; use fallback on failure."""
    filename = f"{product_id}.jpg"
    local_path = os.path.join(IMAGES_DIR, filename)

    try:
        # try downloading
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content)).convert("RGB")
            image.save(local_path, "JPEG")
        else:
            # use fallback
            image = Image.open(FALLBACK_IMAGE_PATH).convert("RGB")
            image.save(local_path, "JPEG")
    except Exception:
        # on any error, use fallback image
        image = Image.open(FALLBACK_IMAGE_PATH).convert("RGB")
        image.save(local_path, "JPEG")

    return local_path


# MAIN LOOP
local_paths = []
for i, row in df.iterrows():
    url = row.get("image_url")
    pid = row.get("product_id", f"img_{i}")
    if pd.isna(url) or url.strip() == "":
        # no URL
        img_path = os.path.join(IMAGES_DIR, f"{pid}.jpg")
        Image.open(FALLBACK_IMAGE_PATH).convert("RGB").save(img_path, "JPEG")
        local_paths.append(img_path)
        print(f"[{i}] No URL -> Fallback used")
    else:
        img_path = download_image(url, pid)
        local_paths.append(img_path)
        print(f"[{i}] Downloaded -> {img_path}")

# SAVE UPDATED CSV
df["local_image_path"] = local_paths
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nDone! Images saved in '{IMAGES_DIR}' and new CSV saved as '{OUTPUT_CSV}'")
