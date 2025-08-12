#!/usr/bin/env python3
"""
性能监控脚本
监控系统资源使用和性能指标
"""

import os
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, log_file="performance.log"):
        self.log_file = log_file
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval=5):
        """开始监控"""
        if self.monitoring:
            print("⚠️ 监控已在运行中")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print(f"🚀 性能监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("⏹️ 性能监控已停止")
    
    def _monitor_loop(self, interval):
        """监控循环"""
        while self.monitoring:
            try:
                self._collect_metrics()
                time.sleep(interval)
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self):
        """收集性能指标"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used / (1024**3)  # GB
        memory_total = memory.total / (1024**3)  # GB
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = disk.used / (1024**3)  # GB
        disk_total = disk.total / (1024**3)  # GB
        
        # 网络I/O
        network = psutil.net_io_counters()
        bytes_sent = network.bytes_sent / (1024**2)  # MB
        bytes_recv = network.bytes_recv / (1024**2)  # MB
        
        # 进程信息
        process = psutil.Process()
        process_cpu = process.cpu_percent()
        process_memory = process.memory_info().rss / (1024**2)  # MB
        
        # 构建日志条目
        log_entry = (
            f"[{timestamp}] "
            f"CPU: {cpu_percent:.1f}% "
            f"Memory: {memory_percent:.1f}% ({memory_used:.1f}GB/{memory_total:.1f}GB) "
            f"Disk: {disk_percent:.1f}% ({disk_used:.1f}GB/{disk_total:.1f}GB) "
            f"Network: ↑{bytes_sent:.1f}MB ↓{bytes_recv:.1f}MB "
            f"Process: CPU={process_cpu:.1f}% Memory={process_memory:.1f}MB"
        )
        
        # 写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
        
        # 控制台输出
        print(log_entry)
    
    def get_system_info(self):
        """获取系统信息"""
        print("🖥️ 系统信息:")
        print(f"  操作系统: {os.name}")
        print(f"  平台: {os.sys.platform}")
        print(f"  Python版本: {os.sys.version}")
        print(f"  CPU核心数: {psutil.cpu_count()}")
        print(f"  内存总量: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"  磁盘总量: {psutil.disk_usage('/').total / (1024**3):.1f} GB")
    
    def get_process_info(self):
        """获取进程信息"""
        process = psutil.Process()
        print("📊 进程信息:")
        print(f"  进程ID: {process.pid}")
        print(f"  进程名称: {process.name()}")
        print(f"  CPU使用率: {process.cpu_percent()}%")
        print(f"  内存使用: {process.memory_info().rss / (1024**2):.1f} MB")
        print(f"  创建时间: {datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数"""
    print("📊 运动视频智能剪辑平台 - 性能监控")
    print("=" * 50)
    
    monitor = PerformanceMonitor()
    
    try:
        # 显示系统信息
        monitor.get_system_info()
        print()
        monitor.get_process_info()
        print()
        
        # 开始监控
        monitor.start_monitoring(interval=10)
        
        print("按 Ctrl+C 停止监控...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断监控")
    except Exception as e:
        print(f"\n❌ 监控异常: {e}")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
