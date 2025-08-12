#!/usr/bin/env python3
"""
运动视频智能剪辑平台 - 后端启动脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app

def main():
    """主函数"""
    print("🎬 运动视频智能剪辑平台 - 后端服务")
    print("=" * 50)
    
    # 创建应用实例
    app = create_app('development')
    
    # 获取配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 启动后端服务...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"🌐 API文档: http://{host}:{port}/api/videos")
    print(f"🏥 健康检查: http://{host}:{port}/health")
    print("=" * 50)
    
    try:
        # 启动Flask应用
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n⚠️ 服务被用户中断")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
