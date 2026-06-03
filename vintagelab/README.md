# VintageLab

Mobile-first vintage camera effects app. Upload photos/videos, apply 40 film presets, download.

---

## Local Development

### 1. Install system deps

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

### 2. Python setup

```bash
cd vintagelab
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run

```bash
python run.py
```

Open: http://localhost:5000

---

## Render Deployment

### Option A — render.yaml (recommended)

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect repo → Render reads `render.yaml` automatically
4. Deploy

**Note:** render.yaml uses a disk for uploads. On the free plan, use ephemeral storage (remove the `disk:` section).

### Option B — Manual

1. New Web Service → connect repo
2. Build command:
   ```
   pip install -r requirements.txt
   ```
3. Start command:
   ```
   gunicorn run:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
   ```
4. Add env var: `SECRET_KEY` → any random string
5. FFmpeg: Render's Python environment includes FFmpeg. If not, add a shell build step:
   ```
   apt-get install -y ffmpeg
   ```

---

## Project Structure

```
vintagelab/
├── run.py                    # Entry point
├── requirements.txt
├── Procfile
├── render.yaml
└── app/
    ├── __init__.py           # App factory
    ├── uploads/              # Temp uploads
    ├── processed/            # Processed output
    ├── routes/
    │   ├── main.py           # Index page
    │   ├── upload.py         # POST /api/upload
    │   ├── process.py        # POST /api/process/photo|video
    │   └── download.py       # GET /api/download|preview
    ├── services/
    │   ├── photo_processor.py
    │   ├── video_processor.py
    │   ├── file_utils.py
    │   └── cleanup.py        # Auto-delete old files
    ├── filters/
    │   ├── effects.py        # 30+ reusable effect modules
    │   └── registry.py       # 40 presets + FILTER_REGISTRY
    ├── static/
    │   ├── css/main.css
    │   └── js/app.js
    └── templates/
        └── index.html
```

---

## Adding New Presets

In `app/filters/registry.py`:

```python
def f_my_filter(img):
    return _apply(img, [
        lambda i: adjust_temperature(i, 15),
        lambda i: add_grain_luminance(i, 18),
        lambda i: add_vignette(i, 0.3),
    ])

FILTER_REGISTRY['my_filter'] = {
    'fn': f_my_filter,
    'name': 'My Filter',
    'category': 'Film',   # Film | VHS | Disposable | Creative
}
```

---

## Environment Variables

| Key | Default | Notes |
|-----|---------|-------|
| `SECRET_KEY` | dev key | Change in production |
| `PORT` | 5000 | Set by Render automatically |

---

## HEIC Support

`pillow-heif` handles HEIC conversion. Installed via requirements.txt.
Falls back to ImageMagick `convert` if pillow-heif fails.
