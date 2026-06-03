import os
from flask import Blueprint, send_file, jsonify, current_app

download_bp = Blueprint('download', __name__)


@download_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Security: sanitize
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400

    processed_dir = current_app.config['PROCESSED_FOLDER']
    file_path = os.path.join(processed_dir, filename)

    real_dir = os.path.realpath(processed_dir)
    real_path = os.path.realpath(file_path)
    if not real_path.startswith(real_dir):
        return jsonify({'error': 'Access denied'}), 403

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True, download_name=filename)


@download_bp.route('/preview/<filename>', methods=['GET'])
def preview_file(filename):
    """Serve processed file for inline preview (not as attachment)."""
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400

    processed_dir = current_app.config['PROCESSED_FOLDER']
    file_path = os.path.join(processed_dir, filename)

    real_dir = os.path.realpath(processed_dir)
    real_path = os.path.realpath(file_path)
    if not real_path.startswith(real_dir):
        return jsonify({'error': 'Access denied'}), 403

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path)


@download_bp.route('/preview/upload/<filename>', methods=['GET'])
def preview_upload(filename):
    """Serve uploaded file for inline preview."""
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400

    upload_dir = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_dir, filename)

    real_dir = os.path.realpath(upload_dir)
    real_path = os.path.realpath(file_path)
    if not real_path.startswith(real_dir):
        return jsonify({'error': 'Access denied'}), 403

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path)
