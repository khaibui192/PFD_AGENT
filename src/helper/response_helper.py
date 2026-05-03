import re
import json
from pathlib import Path

def safe_json(text):
    if not isinstance(text, str):
        return text

    text = text.strip()

    # extract object or array
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if not match:
        return None

    return json.loads(match.group(1))


VALID_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}


def collect_images(images, folder):
    paths = []

    # from --images
    if images:
        paths.extend(images)

    # from --folder
    if folder:
        folder_path = Path(folder)
        if not folder_path.exists():
            raise ValueError(f"Folder not found: {folder}")

        for file in folder_path.rglob("*"):
            if file.suffix.lower() in VALID_EXTS:
                paths.append(str(file))

    # remove duplicate
    paths = list(dict.fromkeys(paths))

    if not paths:
        raise ValueError("No valid images found")

    return paths