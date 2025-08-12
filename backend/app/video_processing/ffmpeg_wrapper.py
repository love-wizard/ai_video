import subprocess
import os
from typing import List, Tuple, Dict, Optional
import json

class FFmpegWrapper:
    """FFmpeg命令行工具包装器"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            print("⚠️ 未找到FFmpeg，视频时长检测功能将不可用")
            print("💡 请安装FFmpeg或将其复制到项目目录")
            self.ffmpeg_available = False
        else:
            self.ffmpeg_available = True
    
    def _find_ffmpeg(self) -> Optional[str]:
        """查找FFmpeg可执行文件"""
        # 检查常见路径
        common_paths = [
            'ffmpeg',
            'C:\\ffmpeg\\bin\\ffmpeg.exe',
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg'
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def get_video_info(self, video_path: str) -> Dict:
        """获取视频信息"""
        if not self.ffmpeg_available:
            print("⚠️ FFmpeg不可用，返回默认视频信息")
            return {
                'duration': 60.0,  # 默认60秒
                'fps': 30.0,
                'resolution': '1920x1080',
                'bitrate': 5000,
                'codec': 'h264',
                'size': 0
            }
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # 解析输出获取视频信息
            info = self._parse_video_info(result.stderr)
            
            # 获取文件大小
            if os.path.exists(video_path):
                info['size'] = os.path.getsize(video_path)
            
            return info
            
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return {
                'duration': 60.0,  # 默认60秒
                'fps': 30.0,
                'resolution': '1920x1080',
                'bitrate': 5000,
                'codec': 'h264',
                'size': 0
            }
    
    def _parse_video_info(self, ffmpeg_output: str) -> Dict:
        """解析FFmpeg输出获取视频信息"""
        info = {
            'duration': 0.0,
            'fps': 0.0,
            'resolution': '',
            'bitrate': 0,
            'codec': '',
            'size': 0
        }
        
        try:
            lines = ffmpeg_output.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # 解析时长
                if 'Duration:' in line:
                    duration_str = line.split('Duration:')[1].split(',')[0].strip()
                    info['duration'] = self._parse_duration(duration_str)
                
                # 解析帧率
                elif 'fps' in line and 'Video:' in line:
                    fps_match = line.split('fps')[0].split()[-1]
                    try:
                        info['fps'] = float(fps_match)
                    except ValueError:
                        pass
                
                # 解析分辨率
                elif 'Video:' in line and 'x' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'x' in part and part.replace('x', '').isdigit():
                            info['resolution'] = part
                            break
                
                # 解析比特率
                elif 'bitrate:' in line:
                    bitrate_str = line.split('bitrate:')[1].split()[0]
                    try:
                        info['bitrate'] = int(bitrate_str)
                    except ValueError:
                        pass
                
                # 解析编解码器
                elif 'Video:' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part in ['h264', 'h265', 'av1', 'vp9']:
                            info['codec'] = part
                            break
                
        except Exception as e:
            print(f"解析视频信息失败: {e}")
        
        return info
    
    def _parse_duration(self, duration_str: str) -> float:
        """解析时长字符串为秒数"""
        try:
            # 格式: HH:MM:SS.mm
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            pass
        return 0.0
    
    def extract_frames(self, video_path: str, output_dir: str, 
                      frame_rate: int = 1) -> List[str]:
        """提取视频帧"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')
            
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-vf', f'fps={frame_rate}',
                '-q:v', '2',
                output_pattern
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # 返回提取的帧文件列表
                frames = []
                for file in os.listdir(output_dir):
                    if file.startswith('frame_') and file.endswith('.jpg'):
                        frames.append(os.path.join(output_dir, file))
                return sorted(frames)
            else:
                print(f"提取帧失败: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"提取帧失败: {e}")
            return []
    
    def convert_format(self, input_path: str, output_path: str, 
                      output_format: str = 'mp4') -> bool:
        """转换视频格式"""
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"格式转换失败: {e}")
            return False
    
    def compress_video(self, input_path: str, output_path: str, 
                      target_size_mb: int = 50) -> bool:
        """压缩视频到指定大小"""
        try:
            # 获取输入视频信息
            info = self.get_video_info(input_path)
            if not info or info['duration'] == 0:
                return False
            
            # 计算目标比特率
            target_size_bits = target_size_mb * 8 * 1024 * 1024
            target_bitrate = int(target_size_bits / info['duration'])
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:v', f'{target_bitrate}',
                '-maxrate', f'{target_bitrate}',
                '-bufsize', f'{target_bitrate * 2}',
                '-preset', 'slow',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"视频压缩失败: {e}")
            return False
    
    def create_thumbnail(self, video_path: str, output_path: str, 
                        time_position: str = '00:00:05') -> bool:
        """创建视频缩略图"""
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-ss', time_position,
                '-vframes', '1',
                '-q:v', '2',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return False
    
    def merge_videos(self, video_paths: List[str], output_path: str) -> bool:
        """合并多个视频文件"""
        try:
            # 创建文件列表
            list_file = 'temp_video_list.txt'
            with open(list_file, 'w', encoding='utf-8') as f:
                for path in video_paths:
                    f.write(f"file '{path}'\n")
            
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # 清理临时文件
            if os.path.exists(list_file):
                os.remove(list_file)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"合并视频失败: {e}")
            return False
    
    def add_watermark(self, input_path: str, output_path: str, 
                      watermark_path: str, position: str = 'bottomright') -> bool:
        """添加水印"""
        try:
            # 计算水印位置
            position_map = {
                'topleft': '10:10',
                'topright': 'W-w-10:10',
                'bottomleft': '10:H-h-10',
                'bottomright': 'W-w-10:H-h-10',
                'center': '(W-w)/2:(H-h)/2'
            }
            
            pos = position_map.get(position, 'bottomright')
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-i', watermark_path,
                '-filter_complex', f'overlay={pos}',
                '-c:a', 'copy',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"添加水印失败: {e}")
            return False
