"""Photo processing service using OpenCV + Pillow."""

import os
import cv2
import numpy as np
from PIL import Image
from ..filters.registry import FILTER_REGISTRY


def process_photo(input_path: str, filter_id: str, output_dir: str) -> str:
    """
    Apply filter to photo. Returns output filename.
    """
    if filter_id not in FILTER_REGISTRY:
        raise ValueError(f"Unknown filter: {filter_id}")

    filter_fn = FILTER_REGISTRY[filter_id]['fn']

    # Read image
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        # Try via PIL (HEIC fallback, etc.)
        pil_img = Image.open(input_path).convert('RGB')
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    if img is None:
        raise RuntimeError(f"Could not read image: {input_path}")

    # Resize very large images for performance (max 4000px on long edge)
    h, w = img.shape[:2]
    max_dim = 4000
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    # Apply filter
    result = filter_fn(img)

    # Build output filename
    base = os.path.splitext(os.path.basename(input_path))[0]
    ext = os.path.splitext(input_path)[1].lower()
    if ext in ('.heic', '.heif'):
        ext = '.jpg'
    output_filename = f"{base}_{filter_id}{ext}"
    output_path = os.path.join(output_dir, output_filename)

    # Save with high quality
    if ext in ('.jpg', '.jpeg'):
        cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
    elif ext == '.png':
        cv2.imwrite(output_path, result, [cv2.IMWRITE_PNG_COMPRESSION, 1])
    elif ext == '.webp':
        cv2.imwrite(output_path, result, [cv2.IMWRITE_WEBP_QUALITY, 95])
    else:
        cv2.imwrite(output_path, result)

    return output_filename
