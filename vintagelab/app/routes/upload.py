import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..services.file_utils import allowed_file, get_file_type, convert_heic_to_jpg

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if not allowed_file(filename, current_app.config):
        return jsonify({'error': f'File type .{ext} not supported'}), 400

    file_id = str(uuid.uuid4())
    save_name = f"{file_id}.{ext}"
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], save_name)
    file.save(save_path)

    file_type = get_file_type(ext, current_app.config)

    # Convert HEIC to JPG for web preview
    if ext in ('heic', 'heif'):
        converted_path, converted_name = convert_heic_to_jpg(save_path, file_id, current_app.config['UPLOAD_FOLDER'])
        if converted_path:
            save_name = converted_name
            ext = 'jpg'
        else:
            return jsonify({'error': 'Failed to convert HEIC image'}), 500

    return jsonify({
        'file_id': file_id,
        'filename': save_name,
        'original_name': filename,
        'file_type': file_type,
        'extension': ext,
        'size': os.path.getsize(os.path.join(current_app.config['UPLOAD_FOLDER'], save_name))
    })
