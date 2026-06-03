import os
import threading
from flask import Flask
from .services.cleanup import start_cleanup_scheduler


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vintagelab-dev-secret-change-me')
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['PROCESSED_FOLDER'] = os.path.join(os.path.dirname(__file__), 'processed')
    app.config['ALLOWED_PHOTO_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'heic', 'heif', 'webp'}
    app.config['ALLOWED_VIDEO_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv'}

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

    from .routes.main import main_bp
    from .routes.upload import upload_bp
    from .routes.process import process_bp
    from .routes.download import download_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(process_bp, url_prefix='/api')
    app.register_blueprint(download_bp, url_prefix='/api')

    start_cleanup_scheduler(app)

    return app
