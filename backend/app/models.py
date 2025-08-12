from datetime import datetime
from app import db
import uuid

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    sport_type = db.Column(db.String(50))
    duration = db.Column(db.Float)
    status = db.Column(db.String(20), default='uploading')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Video {self.filename}>'

class ClipRequest(db.Model):
    __tablename__ = 'clip_requests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = db.Column(db.String(36), db.ForeignKey('videos.id'), nullable=False)
    text_input = db.Column(db.Text, nullable=False)
    target_duration = db.Column(db.Integer, default=60)
    status = db.Column(db.String(20), default='pending')
    result_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    video = db.relationship('Video', backref=db.backref('clip_requests', lazy=True))
    
    def __repr__(self):
        return f'<ClipRequest {self.id}>'

