import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///video_editing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'storage/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 1073741824))  # 1GB
    
    # 视频处理配置
    MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION', 3600))  # 最大视频时长（秒）
    TARGET_CLIP_DURATION = int(os.environ.get('TARGET_CLIP_DURATION', 60))  # 目标剪辑时长（秒）
    
    # OpenAI配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # 支持的文件格式
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv'}
    
    # 存储路径
    STORAGE_PATHS = {
        'uploads': 'storage/uploads',
        'results': 'storage/results',
        'temp': 'storage/temp',
        'thumbnails': 'storage/thumbnails'
    }
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的存储目录
        for path in Config.STORAGE_PATHS.values():
            os.makedirs(path, exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
