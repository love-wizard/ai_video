#!/usr/bin/env python3
"""
调试视频剪辑问题的脚本
"""

import os
import sys
import traceback

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_moviepy_import():
    """测试MoviePy导入"""
    print("🧪 测试MoviePy导入...")
    try:
        from moviepy.editor import VideoFileClip
        print("✅ MoviePy导入成功")
        return True
    except ImportError as e:
        print(f"❌ MoviePy导入失败: {e}")
        return False

def test_opencv_import():
    """测试OpenCV导入"""
    print("\n🧪 测试OpenCV导入...")
    try:
        import cv2
        print("✅ OpenCV导入成功")
        return True
    except ImportError as e:
        print(f"❌ OpenCV导入失败: {e}")
        return False

def test_video_file_access():
    """测试视频文件访问"""
    print("\n🧪 测试视频文件访问...")
    
    # 检查上传目录
    upload_dir = os.path.join(os.getcwd(), 'storage', 'uploads')
    if os.path.exists(upload_dir):
        video_files = [f for f in os.listdir(upload_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        print(f"📁 上传目录: {upload_dir}")
        print(f"🎬 找到 {len(video_files)} 个视频文件")
        
        for file in video_files:
            file_path = os.path.join(upload_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  - {file}: {file_size} bytes")
            
            # 测试文件是否可读
            try:
                with open(file_path, 'rb') as f:
                    f.read(1024)  # 读取1KB
                print(f"    ✅ 文件可读")
            except Exception as e:
                print(f"    ❌ 文件读取失败: {e}")
    else:
        print("❌ 上传目录不存在")
        return False
    
    return True

def test_moviepy_editor():
    """测试MoviePy编辑器"""
    print("\n🧪 测试MoviePy编辑器...")
    try:
        from app.video_processing.moviepy_editor import MoviePyEditor
        
        editor = MoviePyEditor()
        print("✅ MoviePy编辑器初始化成功")
        
        # 测试支持格式
        print(f"📹 支持格式: {editor.supported_formats}")
        
        return True
    except Exception as e:
        print(f"❌ MoviePy编辑器初始化失败: {e}")
        traceback.print_exc()
        return False

def test_ffmpeg_wrapper():
    """测试FFmpeg包装器"""
    print("\n🧪 测试FFmpeg包装器...")
    try:
        from app.video_processing.ffmpeg_wrapper import FFmpegWrapper
        
        ffmpeg = FFmpegWrapper()
        print("✅ FFmpeg包装器初始化成功")
        
        return True
    except Exception as e:
        print(f"❌ FFmpeg包装器初始化失败: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n🧪 测试数据库连接...")
    try:
        from app import create_app, db
        
        app = create_app('development')
        with app.app_context():
            # 测试数据库连接
            db.engine.execute("SELECT 1")
            print("✅ 数据库连接成功")
            
            # 检查表是否存在
            from app.models import Video, ClipRequest
            print("✅ 数据模型导入成功")
            
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        traceback.print_exc()
        return False

def test_storage_directories():
    """测试存储目录"""
    print("\n🧪 测试存储目录...")
    
    directories = [
        os.path.join(os.getcwd(), 'storage', 'uploads'),
        os.path.join(os.getcwd(), 'storage', 'results'),
        os.path.join(os.getcwd(), 'storage', 'temp')
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ 目录存在: {directory}")
            
            # 测试写入权限
            try:
                test_file = os.path.join(directory, 'test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"    ✅ 目录可写")
            except Exception as e:
                print(f"    ❌ 目录不可写: {e}")
        else:
            print(f"❌ 目录不存在: {directory}")
            
            # 尝试创建目录
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"    ✅ 目录创建成功")
            except Exception as e:
                print(f"    ❌ 目录创建失败: {e}")
    
    return True

def main():
    """主函数"""
    print("🔍 开始诊断视频剪辑问题...\n")
    
    tests = [
        test_moviepy_import,
        test_opencv_import,
        test_video_file_access,
        test_moviepy_editor,
        test_ffmpeg_wrapper,
        test_database_connection,
        test_storage_directories
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            traceback.print_exc()
            results.append(False)
    
    print("\n📊 诊断结果汇总:")
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {i+1}. {test.__name__}: {status}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过，系统配置正常")
    else:
        print("⚠️ 发现问题，请检查上述失败的测试项")

if __name__ == "__main__":
    main()
