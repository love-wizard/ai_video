#!/usr/bin/env python3
"""
核心功能测试脚本
测试AI服务、视频处理和API功能
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_services():
    """测试AI服务"""
    print("🧠 测试AI服务...")
    
    try:
        from app.ai_services import SportsClassifier, TextAnalyzer
        
        # 测试运动类型识别器
        print("  - 测试运动类型识别器...")
        classifier = SportsClassifier()
        print(f"    ✓ 运动类型识别器创建成功")
        
        # 测试文本分析器
        print("  - 测试文本分析器...")
        analyzer = TextAnalyzer()
        print(f"    ✓ 文本分析器创建成功")
        
        # 测试文本分析
        test_text = "帮我剪出高亮瞬间并合成视频，总长度在1分钟内"
        result = analyzer.analyze_clip_request(test_text, 'basketball')
        print(f"    ✓ 文本分析测试成功: {result['clip_target']}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ AI服务测试失败: {e}")
        return False

def test_video_processing():
    """测试视频处理模块"""
    print("🎬 测试视频处理模块...")
    
    try:
        from app.video_processing import FFmpegWrapper, MoviePyEditor
        
        # 测试FFmpeg包装器
        print("  - 测试FFmpeg包装器...")
        try:
            ffmpeg = FFmpegWrapper()
            print(f"    ✓ FFmpeg包装器创建成功: {ffmpeg.ffmpeg_path}")
        except RuntimeError as e:
            print(f"    ⚠️ FFmpeg未安装: {e}")
            print("    请安装FFmpeg以启用完整功能")
        
        # 测试MoviePy编辑器
        print("  - 测试MoviePy编辑器...")
        editor = MoviePyEditor()
        print(f"    ✓ MoviePy编辑器创建成功")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 视频处理模块测试失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    print("🗄️ 测试数据库连接...")
    
    try:
        from app import create_app, db
        from app.models import Video, ClipRequest
        
        # 创建测试应用
        app = create_app('testing')
        
        with app.app_context():
            # 测试数据库表创建
            db.create_all()
            print("    ✓ 数据库表创建成功")
            
            # 测试模型
            video = Video(
                filename='test.mp4',
                filepath='/tmp/test.mp4',
                status='test'
            )
            db.session.add(video)
            db.session.commit()
            print("    ✓ 数据库写入测试成功")
            
            # 清理测试数据
            db.session.delete(video)
            db.session.commit()
            print("    ✓ 数据库清理测试成功")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 数据库测试失败: {e}")
        return False

def test_api_routes():
    """测试API路由"""
    print("🌐 测试API路由...")
    
    try:
        from app import create_app
        from app.api import videos_bp
        
        # 创建测试应用
        app = create_app('testing')
        
        # 测试蓝图注册
        if videos_bp in app.blueprints.values():
            print("    ✓ API蓝图注册成功")
        else:
            print("    ❌ API蓝图注册失败")
            return False
        
        # 测试路由
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('videos.'):
                routes.append(f"{rule.methods} {rule.rule}")
        
        print(f"    ✓ 发现 {len(routes)} 个API路由")
        for route in routes:
            print(f"      - {route}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ API路由测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试运动视频智能剪辑平台核心功能")
    print("=" * 60)
    
    tests = [
        ("AI服务", test_ai_services),
        ("视频处理模块", test_video_processing),
        ("数据库", test_database),
        ("API路由", test_api_routes)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        
        duration = end_time - start_time
        status = "✅ 通过" if success else "❌ 失败"
        
        print(f"    ⏱️ 耗时: {duration:.2f}秒")
        print(f"    📊 状态: {status}")
        
        results.append((test_name, success, duration))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, duration in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name:<20} {duration:>8.2f}s")
    
    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！核心功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
