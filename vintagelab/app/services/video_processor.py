"""
Video processing service.
Strategy: extract frames with FFmpeg, apply filter per frame via OpenCV,
reassemble with FFmpeg (preserving audio).
"""

import os
import subprocess
import tempfile
import shutil
import cv2
import numpy as np
from ..filters.registry import FILTER_REGISTRY


def _ffmpeg_available():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def process_video(
    input_path: str,
    filter_id: str,
    output_dir: str,
    progress_callback=None,
) -> str:
    """
    Apply filter to video. Returns output filename.
    """
    if filter_id not in FILTER_REGISTRY:
        raise ValueError(f"Unknown filter: {filter_id}")

    if not _ffmpeg_available():
        raise RuntimeError("FFmpeg not found. Install FFmpeg to process videos.")

    filter_fn = FILTER_REGISTRY[filter_id]['fn']

    base = os.path.splitext(os.path.basename(input_path))[0]
    ext = os.path.splitext(input_path)[1].lower()
    if ext == '.mov':
        out_ext = '.mp4'
    else:
        out_ext = ext if ext in ('.mp4', '.avi', '.mkv') else '.mp4'

    output_filename = f"{base}_{filter_id}{out_ext}"
    output_path = os.path.join(output_dir, output_filename)

    tmpdir = tempfile.mkdtemp(prefix='vintagelab_')
    frames_dir = os.path.join(tmpdir, 'frames')
    processed_dir = os.path.join(tmpdir, 'processed')
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    try:
        # --- Get video info ---
        probe = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_path],
            capture_output=True, text=True, check=True
        )
        import json
        probe_data = json.loads(probe.stdout)
        fps = '30'
        for stream in probe_data.get('streams', []):
            if stream.get('codec_type') == 'video':
                r_fps = stream.get('r_frame_rate', '30/1')
                if '/' in r_fps:
                    num, den = r_fps.split('/')
                    if int(den) > 0:
                        fps = str(round(int(num) / int(den), 2))
                break

        # Limit resolution for performance: max 1280px wide
        scale_filter = 'scale=min(1280\\,iw):-2'

        # --- Extract frames ---
        extract_cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', scale_filter,
            '-q:v', '2',
            os.path.join(frames_dir, 'frame_%06d.jpg'),
            '-y'
        ]
        subprocess.run(extract_cmd, capture_output=True, check=True)

        # --- Process frames ---
        frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg')])
        total = len(frame_files)
        if total == 0:
            raise RuntimeError("No frames extracted from video")

        for i, fname in enumerate(frame_files):
            frame_path = os.path.join(frames_dir, fname)
            img = cv2.imread(frame_path)
            if img is None:
                continue
            result = filter_fn(img)
            out_frame_path = os.path.join(processed_dir, fname)
            cv2.imwrite(out_frame_path, result, [cv2.IMWRITE_JPEG_QUALITY, 92])
            if progress_callback and i % 10 == 0:
                progress_callback(int((i / total) * 90))

        # --- Reassemble video with audio ---
        # Check if original has audio
        has_audio = any(
            s.get('codec_type') == 'audio'
            for s in probe_data.get('streams', [])
        )

        reassemble_cmd = [
            'ffmpeg',
            '-framerate', fps,
            '-i', os.path.join(processed_dir, 'frame_%06d.jpg'),
        ]
        if has_audio:
            reassemble_cmd += ['-i', input_path, '-map', '0:v', '-map', '1:a']
        reassemble_cmd += [
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
        ]
        if has_audio:
            reassemble_cmd += ['-c:a', 'aac', '-b:a', '128k', '-shortest']
        reassemble_cmd += [output_path, '-y']

        subprocess.run(reassemble_cmd, capture_output=True, check=True)

        if progress_callback:
            progress_callback(100)

        return output_filename

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ''
        raise RuntimeError(f"FFmpeg error: {stderr[:500]}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
