from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from config import config

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from .api import videos_bp
    from .api.routes import health_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
