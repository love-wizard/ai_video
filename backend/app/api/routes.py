import os
import uuid
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from . import videos_bp
from ..models import Video, ClipRequest
from .. import db

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
UPLOAD_FOLDER = 'storage/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@videos_bp.route('/upload', methods=['POST'])
def upload_video():
    """视频上传接口"""
    if 'video' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        video_id = str(uuid.uuid4())
        filepath = os.path.join(UPLOAD_FOLDER, f"{video_id}_{filename}")
        
        # 确保上传目录存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # 保存文件
        file.save(filepath)
        
        # 创建数据库记录
        video = Video(
            id=video_id,
            filename=filename,
            filepath=filepath,
            status='uploaded'
        )
        db.session.add(video)
        db.session.commit()
        
        return jsonify({
            'videoId': video_id,
            'status': 'uploaded',
            'message': '视频上传成功'
        }), 201
    
    return jsonify({'error': '不支持的文件格式'}), 400

@videos_bp.route('/<video_id>/status', methods=['GET'])
def get_video_status(video_id):
    """获取视频处理状态"""
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': '视频不存在'}), 404
    
    return jsonify({
        'videoId': video.id,
        'status': video.status,
        'sportType': video.sport_type,
        'duration': video.duration
    })

@videos_bp.route('/<video_id>/clip', methods=['POST'])
def request_clip(video_id):
    """请求视频剪辑"""
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': '视频不存在'}), 404
    
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': '缺少文本输入'}), 400
    
    # 创建剪辑请求
    clip_request = ClipRequest(
        video_id=video_id,
        text_input=data['text'],
        target_duration=data.get('targetDuration', 60)
    )
    db.session.add(clip_request)
    db.session.commit()
    
    # TODO: 启动异步处理任务
    
    return jsonify({
        'clipId': clip_request.id,
        'status': 'pending',
        'message': '剪辑请求已提交'
    }), 201

@videos_bp.route('/<video_id>/clip/<clip_id>', methods=['GET'])
def get_clip_result(video_id, clip_id):
    """获取剪辑结果"""
    clip_request = ClipRequest.query.get(clip_id)
    if not clip_request or clip_request.video_id != video_id:
        return jsonify({'error': '剪辑请求不存在'}), 404
    
    if clip_request.status != 'completed':
        return jsonify({
            'clipId': clip_request.id,
            'status': clip_request.status,
            'message': '剪辑处理中'
        })
    
    return jsonify({
        'clipId': clip_request.id,
        'status': 'completed',
        'downloadUrl': f'/download/{clip_request.result_path}',
        'message': '剪辑完成'
    })

@videos_bp.route('/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    """删除视频"""
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': '视频不存在'}), 404
    
    # 删除文件
    if os.path.exists(video.filepath):
        os.remove(video.filepath)
    
    # 删除数据库记录
    db.session.delete(video)
    db.session.commit()
    
    return jsonify({'message': '视频删除成功'})
