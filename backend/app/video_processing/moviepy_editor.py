from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx import resize, crop, speedx
from moviepy.audio.fx import volumex
import numpy as np
import cv2
from typing import List, Tuple, Dict, Optional
import os

class MoviePyEditor:
    """MoviePy视频编辑器，负责视频剪辑和合成"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
        self.temp_dir = 'temp_clips'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def create_highlight_video(self, video_path: str, clip_segments: List[Tuple[float, float]], 
                              output_path: str, target_duration: int = 60) -> bool:
        """创建精彩瞬间视频"""
        try:
            video = VideoFileClip(video_path)
            clips = []
            
            for start_time, end_time in clip_segments:
                if start_time < end_time and end_time <= video.duration:
                    clip = video.subclip(start_time, end_time)
                    clips.append(clip)
            
            if not clips:
                return False
            
            adjusted_clips = self._adjust_clips_duration(clips, target_duration)
            final_video = concatenate_videoclips(adjusted_clips, method="compose")
            
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            video.close()
            final_video.close()
            for clip in clips:
                clip.close()
            
            return True
            
        except Exception as e:
            print(f"创建精彩瞬间视频失败: {e}")
            return False
    
    def _adjust_clips_duration(self, clips: List[VideoFileClip], target_duration: int) -> List[VideoFileClip]:
        """调整剪辑片段时长"""
        total_duration = sum(clip.duration for clip in clips)
        
        if total_duration <= target_duration:
            return clips
        
        ratio = target_duration / total_duration
        adjusted_clips = []
        
        for clip in clips:
            new_duration = clip.duration * ratio
            adjusted_clip = clip.subclip(0, new_duration)
            adjusted_clips.append(adjusted_clip)
        
        return adjusted_clips
    
    def detect_highlight_moments(self, video_path: str, sport_type: str = None) -> List[Tuple[float, float]]:
        """检测视频中的精彩瞬间"""
        try:
            frames = self._extract_key_frames(video_path, num_frames=100)
            motion_scores = self._analyze_motion_intensity(frames)
            
            if sport_type:
                motion_scores = self._apply_sport_specific_detection(motion_scores, sport_type)
            
            highlight_segments = self._find_highlight_segments(motion_scores, video_path)
            return highlight_segments
            
        except Exception as e:
            print(f"检测精彩瞬间失败: {e}")
            return []
    
    def _extract_key_frames(self, video_path: str, num_frames: int = 100) -> List[np.ndarray]:
        """提取关键帧"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return frames
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frames.append(gray)
        
        cap.release()
        return frames
    
    def _analyze_motion_intensity(self, frames: List[np.ndarray]) -> List[float]:
        """分析帧间运动强度"""
        if len(frames) < 2:
            return [0.0]
        
        motion_scores = [0.0]
        
        for i in range(1, len(frames)):
            diff = cv2.absdiff(frames[i], frames[i-1])
            motion_score = np.mean(diff)
            motion_score = min(motion_score / 255.0, 1.0)
            motion_scores.append(motion_score)
        
        return motion_scores
    
    def _apply_sport_specific_detection(self, motion_scores: List[float], sport_type: str) -> List[float]:
        """根据运动类型应用特定的检测策略"""
        if sport_type == 'basketball':
            return self._detect_basketball_moments(motion_scores)
        elif sport_type == 'football':
            return self._detect_football_moments(motion_scores)
        elif sport_type == 'tennis':
            return self._detect_tennis_moments(motion_scores)
        else:
            return motion_scores
    
    def _detect_basketball_moments(self, motion_scores: List[float]) -> List[float]:
        """检测篮球精彩瞬间"""
        enhanced_scores = motion_scores.copy()
        
        for i in range(1, len(motion_scores) - 1):
            if (motion_scores[i] > 0.6 and 
                motion_scores[i-1] < 0.3 and 
                motion_scores[i+1] < 0.3):
                enhanced_scores[i] *= 1.5
        
        return enhanced_scores
    
    def _detect_football_moments(self, motion_scores: List[float]) -> List[float]:
        """检测足球精彩瞬间"""
        enhanced_scores = motion_scores.copy()
        
        for i in range(2, len(motion_scores) - 2):
            if all(motion_scores[j] > 0.5 for j in range(i-2, i+3)):
                enhanced_scores[i] *= 1.3
        
        return enhanced_scores
    
    def _detect_tennis_moments(self, motion_scores: List[float]) -> List[float]:
        """检测网球精彩瞬间"""
        enhanced_scores = motion_scores.copy()
        
        for i in range(1, len(motion_scores) - 1):
            if (motion_scores[i] > 0.7 and 
                motion_scores[i-1] < 0.4):
                enhanced_scores[i] *= 1.4
        
        return enhanced_scores
    
    def _find_highlight_segments(self, motion_scores: List[float], video_path: str) -> List[Tuple[float, float]]:
        """找出精彩瞬间时间段"""
        try:
            video = VideoFileClip(video_path)
            video_duration = video.duration
            video.close()
            
            time_interval = video_duration / len(motion_scores)
            threshold = np.percentile(motion_scores, 80)
            
            highlight_times = []
            for i, score in enumerate(motion_scores):
                if score > threshold:
                    time_point = i * time_interval
                    highlight_times.append(time_point)
            
            segments = []
            if highlight_times:
                start_time = highlight_times[0]
                prev_time = start_time
                
                for time_point in highlight_times[1:]:
                    if time_point - prev_time > 2.0:
                        segments.append((start_time, prev_time + 1.0))
                        start_time = time_point
                    prev_time = time_point
                
                segments.append((start_time, prev_time + 1.0))
            
            adjusted_segments = []
            for start, end in segments:
                duration = end - start
                if duration < 3.0:
                    center = (start + end) / 2
                    start = max(0, center - 1.5)
                    end = min(video_duration, center + 1.5)
                elif duration > 8.0:
                    center = (start + end) / 2
                    start = center - 4.0
                    end = center + 4.0
                
                adjusted_segments.append((start, end))
            
            return adjusted_segments
            
        except Exception as e:
            print(f"查找精彩瞬间时间段失败: {e}")
            return []
    
    def add_transitions(self, clips: List[VideoFileClip], 
                       transition_type: str = 'fade') -> List[VideoFileClip]:
        """在剪辑片段之间添加转场效果"""
        if len(clips) < 2:
            return clips
        
        transition_duration = 0.5
        clips_with_transitions = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                # 第一个片段
                if transition_type == 'fade':
                    clip = clip.fadein(transition_duration)
                clips_with_transitions.append(clip)
            else:
                # 添加转场效果
                if transition_type == 'fade':
                    clip = clip.fadein(transition_duration).fadeout(transition_duration)
                clips_with_transitions.append(clip)
        
        return clips_with_transitions
    
    def add_text_overlay(self, clip: VideoFileClip, text: str, 
                         position: str = 'bottom') -> VideoFileClip:
        """添加文字覆盖层"""
        try:
            from moviepy.video.tools.drawing import color_gradient
            from moviepy.video.VideoClip import TextClip
            
            # 创建文字剪辑
            txt_clip = TextClip(text, fontsize=30, color='white', font='Arial-Bold')
            
            # 设置位置
            if position == 'bottom':
                txt_clip = txt_clip.set_position(('center', 'bottom'))
            elif position == 'top':
                txt_clip = txt_clip.set_position(('center', 'top'))
            elif position == 'center':
                txt_clip = txt_clip.set_position('center')
            
            # 设置持续时间
            txt_clip = txt_clip.set_duration(clip.duration)
            
            # 合成视频和文字
            final_clip = CompositeVideoClip([clip, txt_clip])
            
            return final_clip
            
        except ImportError:
            print("TextClip不可用，跳过文字覆盖")
            return clip
        except Exception as e:
            print(f"添加文字覆盖失败: {e}")
            return clip
    
    def create_slow_motion(self, clip: VideoFileClip, speed_factor: float = 0.5) -> VideoFileClip:
        """创建慢动作效果"""
        try:
            return clip.speedx(speed_factor)
        except Exception as e:
            print(f"创建慢动作失败: {e}")
            return clip
    
    def add_background_music(self, video_clip: VideoFileClip, 
                            music_path: str, volume: float = 0.3) -> VideoFileClip:
        """添加背景音乐"""
        try:
            from moviepy.audio.AudioClip import AudioFileClip
            
            # 加载音乐
            music = AudioFileClip(music_path)
            
            # 调整音乐时长匹配视频
            if music.duration > video_clip.duration:
                music = music.subclip(0, video_clip.duration)
            else:
                # 循环播放音乐
                music = music.loop(duration=video_clip.duration)
            
            # 调整音量
            music = music.volumex(volume)
            
            # 合成音频
            final_audio = CompositeVideoClip([video_clip, music.set_duration(video_clip.duration)])
            
            return final_audio
            
        except Exception as e:
            print(f"添加背景音乐失败: {e}")
            return video_clip
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)
        except Exception as e:
            print(f"清理临时文件失败: {e}")
