"""Auto-cleanup of old temporary files."""

import os
import time
import threading


MAX_AGE_HOURS = 24
CHECK_INTERVAL_SECONDS = 3600  # every hour


def cleanup_old_files(folder: str, max_age_hours: int = MAX_AGE_HOURS):
    """Delete files older than max_age_hours from folder."""
    now = time.time()
    cutoff = now - max_age_hours * 3600
    deleted = 0
    if not os.path.exists(folder):
        return deleted
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        try:
            if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff:
                os.remove(fpath)
                deleted += 1
        except OSError:
            pass
    return deleted


def _cleanup_loop(upload_folder: str, processed_folder: str):
    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        cleanup_old_files(upload_folder)
        cleanup_old_files(processed_folder)


def start_cleanup_scheduler(app):
    """Start background cleanup thread."""
    t = threading.Thread(
        target=_cleanup_loop,
        args=(app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']),
        daemon=True
    )
    t.start()
