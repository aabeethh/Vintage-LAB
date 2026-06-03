"""File validation and utility functions."""

import os


def allowed_file(filename: str, config: dict) -> bool:
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    all_allowed = config['ALLOWED_PHOTO_EXTENSIONS'] | config['ALLOWED_VIDEO_EXTENSIONS']
    return ext in all_allowed


def get_file_type(ext: str, config: dict) -> str:
    if ext in config['ALLOWED_PHOTO_EXTENSIONS']:
        return 'photo'
    if ext in config['ALLOWED_VIDEO_EXTENSIONS']:
        return 'video'
    return 'unknown'


def convert_heic_to_jpg(heic_path: str, file_id: str, upload_dir: str):
    """Convert HEIC to JPG using pillow-heif if available."""
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
        from PIL import Image
        img = Image.open(heic_path).convert('RGB')
        jpg_name = f"{file_id}.jpg"
        jpg_path = os.path.join(upload_dir, jpg_name)
        img.save(jpg_path, 'JPEG', quality=95)
        return jpg_path, jpg_name
    except ImportError:
        # Try imagemagick fallback
        import subprocess
        jpg_name = f"{file_id}.jpg"
        jpg_path = os.path.join(upload_dir, jpg_name)
        try:
            subprocess.run(['convert', heic_path, jpg_path], capture_output=True, check=True)
            return jpg_path, jpg_name
        except Exception:
            return None, None
    except Exception:
        return None, None
