import os
import threading
from flask import Blueprint, request, jsonify, current_app
from ..services.photo_processor import process_photo
from ..services.video_processor import process_video
from ..filters.registry import FILTER_REGISTRY

process_bp = Blueprint('process', __name__)
video_jobs = {}


@process_bp.route('/filters', methods=['GET'])
def get_filters():
    filters = []
    for fid, meta in FILTER_REGISTRY.items():
        filters.append({
            'id': fid,
            'name': meta['name'],
            'category': meta['category'],
            'emoji': meta.get('emoji', '📷'),
            'desc': meta.get('desc', ''),
        })
    return jsonify({'filters': filters})


@process_bp.route('/process/photo', methods=['POST'])
def process_photo_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body'}), 400
    filename = data.get('filename')
    filter_id = data.get('filter_id')
    if not filename or not filter_id:
        return jsonify({'error': 'filename and filter_id required'}), 400
    if filter_id not in FILTER_REGISTRY:
        return jsonify({'error': f'Unknown filter: {filter_id}'}), 400
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(upload_path):
        return jsonify({'error': 'File not found'}), 404
    upload_dir = os.path.realpath(current_app.config['UPLOAD_FOLDER'])
    if not os.path.realpath(upload_path).startswith(upload_dir):
        return jsonify({'error': 'Invalid path'}), 400
    try:
        out = process_photo(upload_path, filter_id, current_app.config['PROCESSED_FOLDER'])
        return jsonify({'output_filename': out, 'status': 'done'})
    except Exception as e:
        current_app.logger.error(f'Photo processing error: {e}')
        return jsonify({'error': str(e)}), 500


@process_bp.route('/process/video', methods=['POST'])
def process_video_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body'}), 400
    filename = data.get('filename')
    filter_id = data.get('filter_id')
    if not filename or not filter_id:
        return jsonify({'error': 'filename and filter_id required'}), 400
    if filter_id not in FILTER_REGISTRY:
        return jsonify({'error': f'Unknown filter: {filter_id}'}), 400
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(upload_path):
        return jsonify({'error': 'File not found'}), 404
    upload_dir = os.path.realpath(current_app.config['UPLOAD_FOLDER'])
    if not os.path.realpath(upload_path).startswith(upload_dir):
        return jsonify({'error': 'Invalid path'}), 400
    job_id = filename.split('.')[0] + '_' + filter_id

    def run():
        try:
            video_jobs[job_id] = {'status': 'processing', 'progress': 0}
            out = process_video(
                upload_path, filter_id, current_app.config['PROCESSED_FOLDER'],
                progress_callback=lambda p: video_jobs.update({job_id: {'status': 'processing', 'progress': p}})
            )
            video_jobs[job_id] = {'status': 'done', 'output_filename': out, 'progress': 100}
        except Exception as e:
            video_jobs[job_id] = {'status': 'error', 'error': str(e), 'progress': 0}

    video_jobs[job_id] = {'status': 'queued', 'progress': 0}
    threading.Thread(target=run, daemon=True).start()
    return jsonify({'job_id': job_id, 'status': 'queued'})


@process_bp.route('/process/video/status/<job_id>', methods=['GET'])
def video_status(job_id):
    job = video_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)
