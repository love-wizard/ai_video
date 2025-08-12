import os
import uuid
from flask import request, jsonify, current_app, Blueprint
from werkzeug.utils import secure_filename
from . import videos_bp
from ..models import Video, ClipRequest
from .. import db
from ..ai_services import SportsClassifier, TextAnalyzer
from ..video_processing import FFmpegWrapper, MoviePyEditor
import threading
import time

# 创建健康检查蓝图
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'sports-video-editing-platform'
    })

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
        
        # 启动后台任务：运动类型识别和视频分析
        def analyze_video_background():
            try:
                # 运动类型识别
                classifier = SportsClassifier()
                sport_scores = classifier.classify_sport(filepath)
                dominant_sport, confidence = classifier.get_dominant_sport(sport_scores)
                
                # 获取视频信息
                try:
                    ffmpeg = FFmpegWrapper()
                    video_info = ffmpeg.get_video_info(filepath)
                    duration = video_info.get('duration', 0)
                except Exception as e:
                    print(f"FFmpeg获取视频信息失败: {e}")
                    duration = 0
                
                # 更新数据库 - 使用全局变量避免上下文问题
                try:
                    from app import create_app
                    app = create_app('development')
                    with app.app_context():
                        # 重新查询视频对象
                        video_obj = Video.query.get(video_id)
                        if video_obj:
                            video_obj.sport_type = dominant_sport
                            video_obj.duration = duration
                            video_obj.status = 'analyzed'
                            db.session.commit()
                            print(f"视频分析完成: {dominant_sport}, 时长: {duration}秒")
                except Exception as e:
                    print(f"数据库更新失败: {e}")
                    
            except Exception as e:
                print(f"视频分析失败: {e}")
                try:
                    from app import create_app
                    app = create_app('development')
                    with app.app_context():
                        video_obj = Video.query.get(video_id)
                        if video_obj:
                            video_obj.status = 'error'
                            db.session.commit()
                except Exception as db_error:
                    print(f"数据库错误状态更新失败: {db_error}")
        
        # 启动后台线程
        thread = threading.Thread(target=analyze_video_background)
        thread.daemon = True
        thread.start()
        
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
    
    # 启动后台剪辑任务
    def process_clip_background():
        try:
            # 更新状态为处理中
            try:
                from app import create_app
                app = create_app('development')
                with app.app_context():
                    clip_obj = ClipRequest.query.get(clip_request.id)
                    if clip_obj:
                        clip_obj.status = 'processing'
                        db.session.commit()
                        print(f"剪辑请求 {clip_request.id} 开始处理")
            except Exception as e:
                print(f"更新剪辑状态失败: {e}")
            
            # 在后台线程中重新查询视频对象
            try:
                with app.app_context():
                    video_obj = Video.query.get(video_id)
                    if not video_obj:
                        print(f"视频 {video_id} 不存在")
                        return
                    
                    # 文本分析
                    text_analyzer = TextAnalyzer()
                    analysis_result = text_analyzer.analyze_clip_request(
                        data['text'], 
                        video_obj.sport_type
                    )
                    
                    print(f"AI分析结果: {analysis_result}")
                    
                    # 根据AI分析结果调整剪辑策略
                    clip_target = analysis_result.get('clip_target', 'highlights')
                    focus_moments = analysis_result.get('focus_moments', [])
                    clip_style = analysis_result.get('clip_style', '标准剪辑')
                    
                    # 精彩瞬间检测 - 使用AI分析结果指导
                    moviepy_editor = MoviePyEditor()
                    highlight_segments = moviepy_editor.detect_highlight_moments(
                        video_obj.filepath, 
                        video_obj.sport_type,
                        clip_target=clip_target,
                        focus_moments=focus_moments
                    )
            except Exception as e:
                print(f"查询视频对象失败: {e}")
                return
            
            if not highlight_segments:
                # 如果没有检测到精彩瞬间，使用均匀分布
                video_duration = video_obj.duration or 60
                segment_count = 5
                segment_duration = min(8, video_duration / segment_count)
                highlight_segments = []
                for i in range(segment_count):
                    start = i * segment_duration
                    end = start + segment_duration
                    highlight_segments.append((start, end))
            
            # 创建输出目录
            output_dir = os.path.join(os.getcwd(), 'storage', 'results')
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成输出文件名
            output_filename = f"clip_{clip_request.id}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            # 执行视频剪辑
            success = moviepy_editor.create_highlight_video(
                video_obj.filepath,
                highlight_segments,
                output_path,
                clip_request.target_duration
            )
            
            if success:
                # 更新状态为完成
                try:
                    with app.app_context():
                        clip_obj = ClipRequest.query.get(clip_request.id)
                        if clip_obj:
                            clip_obj.status = 'completed'
                            clip_obj.result_path = output_path
                            db.session.commit()
                            print(f"剪辑请求 {clip_request.id} 完成")
                except Exception as e:
                    print(f"更新剪辑完成状态失败: {e}")
            else:
                # 更新状态为失败
                try:
                    with app.app_context():
                        clip_obj = ClipRequest.query.get(clip_request.id)
                        if clip_obj:
                            clip_obj.status = 'error'
                            db.session.commit()
                            print(f"剪辑请求 {clip_request.id} 失败")
                except Exception as e:
                    print(f"更新剪辑失败状态失败: {e}")
                    
        except Exception as e:
            print(f"视频剪辑失败: {e}")
            try:
                with app.app_context():
                    clip_obj = ClipRequest.query.get(clip_request.id)
                    if clip_obj:
                        clip_obj.status = 'error'
                        db.session.commit()
            except Exception as db_error:
                print(f"数据库错误状态更新失败: {db_error}")
    
    # 启动后台线程
    thread = threading.Thread(target=process_clip_background)
    thread.daemon = True
    thread.start()
    
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

@videos_bp.route('/<video_id>/clip/<clip_id>/download', methods=['GET'])
def download_clip(video_id, clip_id):
    """下载剪辑结果"""
    clip_request = ClipRequest.query.get(clip_id)
    if not clip_request or clip_request.video_id != video_id:
        return jsonify({'error': '剪辑请求不存在'}), 404
    
    if clip_request.status != 'completed':
        return jsonify({'error': '剪辑尚未完成'}), 400
    
    if not clip_request.result_path or not os.path.exists(clip_request.result_path):
        return jsonify({'error': '文件不存在'}), 404
    
    # 返回文件下载链接
    return jsonify({
        'downloadUrl': f'/api/videos/{video_id}/clip/{clip_id}/file',
        'filename': os.path.basename(clip_request.result_path)
    })

@videos_bp.route('/<video_id>/clip/<clip_id>/file', methods=['GET'])
def serve_clip_file(video_id, clip_id):
    """提供剪辑文件下载"""
    from flask import send_file
    
    clip_request = ClipRequest.query.get(clip_id)
    if not clip_request or clip_request.video_id != video_id:
        return jsonify({'error': '剪辑请求不存在'}), 404
    
    if clip_request.status != 'completed':
        return jsonify({'error': '剪辑尚未完成'}), 400
    
    if not clip_request.result_path or not os.path.exists(clip_request.result_path):
        return jsonify({'error': '文件不存在'}), 404
    
    return send_file(
        clip_request.result_path,
        as_attachment=True,
        download_name=os.path.basename(clip_request.result_path)
    )
