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
                              output_path: str, target_duration: int = 60, 
                              audio_suggestions: List[str] = None) -> bool:
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
            
            # 根据audio_suggestions调整音频
            if audio_suggestions:
                adjusted_clips = self._apply_audio_suggestions(adjusted_clips, audio_suggestions)
                print(f"应用音频建议: {audio_suggestions}")
            
            final_video = concatenate_videoclips(adjusted_clips, method="compose")
            
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            video.close()
            final_video.close()
            for clip in clips:
                clip.close()
            
            # 验证生成的文件
            if self._verify_video_file(output_path):
                return True
            else:
                print(f"生成的视频文件验证失败: {output_path}")
                return False
            
        except Exception as e:
            print(f"创建精彩瞬间视频失败: {e}")
            return False

    def _verify_video_file(self, file_path: str) -> bool:
        """验证生成的视频文件是否完整可播放"""
        try:
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # 小于1KB的文件可能有问题
                print(f"文件太小: {file_size} bytes")
                return False
            
            # 尝试用OpenCV打开文件
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                print(f"无法打开视频文件: {file_path}")
                return False
            
            # 检查视频属性
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps if fps > 0 else 0
            
            cap.release()
            
            if frame_count <= 0 or fps <= 0 or duration <= 0:
                print(f"视频属性无效: frames={frame_count}, fps={fps}, duration={duration}")
                return False
            
            print(f"视频文件验证成功: {file_path}, size={file_size}, frames={frame_count}, fps={fps}, duration={duration:.2f}s")
            return True
            
        except Exception as e:
            print(f"文件验证失败: {e}")
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
    
    def detect_highlight_moments(self, video_path: str, sport_type: str = None, 
                                clip_target: str = 'highlights', focus_moments: List[str] = None,
                                clip_style: str = '标准剪辑', audio_suggestions: List[str] = None,
                                duration_distribution: Dict[str, float] = None) -> List[Tuple[float, float]]:
        """检测视频中的精彩瞬间"""
        try:
            print(f"开始检测精彩瞬间 - 目标: {clip_target}, 重点: {focus_moments}")
            
            frames = self._extract_key_frames(video_path, num_frames=100)
            motion_scores = self._analyze_motion_intensity(frames)
            
            if sport_type:
                motion_scores = self._apply_sport_specific_detection(motion_scores, sport_type)
            
            # 根据AI分析结果调整检测策略
            if clip_target == 'scoring':
                # 如果是得分目标，增强得分相关的瞬间
                motion_scores = self._enhance_scoring_moments(motion_scores)
            elif clip_target == 'defense':
                # 如果是防守目标，增强防守相关的瞬间
                motion_scores = self._enhance_defense_moments(motion_scores)
            elif clip_target == 'teamwork':
                # 如果是团队配合目标，增强团队相关的瞬间
                motion_scores = self._enhance_teamwork_moments(motion_scores)
            
            # 根据focus_moments进一步调整检测策略
            if focus_moments:
                motion_scores = self._enhance_focus_moments(motion_scores, focus_moments, sport_type)
            
            highlight_segments = self._find_highlight_segments(
                motion_scores, video_path, clip_target, focus_moments, 
                clip_style, duration_distribution
            )
            return highlight_segments
            
        except Exception as e:
            print(f"检测精彩瞬间失败: {e}")
            return []
    
    def _enhance_scoring_moments(self, motion_scores: List[float]) -> List[float]:
        """增强得分相关的瞬间"""
        enhanced_scores = motion_scores.copy()
        for i in range(1, len(motion_scores) - 1):
            # 寻找突然的高运动强度（可能是得分瞬间）
            if (motion_scores[i] > 0.7 and 
                motion_scores[i-1] < 0.4 and 
                motion_scores[i+1] < 0.4):
                enhanced_scores[i] *= 1.8  # 大幅增强
        return enhanced_scores
    
    def _enhance_defense_moments(self, motion_scores: List[float]) -> List[float]:
        """增强防守相关的瞬间"""
        enhanced_scores = motion_scores.copy()
        for i in range(2, len(motion_scores) - 2):
            # 寻找持续的高运动强度（可能是防守动作）
            if all(motion_scores[j] > 0.6 for j in range(i-1, i+2)):
                enhanced_scores[i] *= 1.5
        return enhanced_scores
    
    def _enhance_teamwork_moments(self, motion_scores: List[float]) -> List[float]:
        """增强团队配合相关的瞬间"""
        enhanced_scores = motion_scores.copy()
        for i in range(1, len(motion_scores) - 1):
            # 寻找中等但稳定的运动强度（可能是团队配合）
            if (0.4 < motion_scores[i] < 0.7 and 
                abs(motion_scores[i] - motion_scores[i-1]) < 0.2):
                enhanced_scores[i] *= 1.3
        return enhanced_scores
    
    def _enhance_focus_moments(self, motion_scores: List[float], focus_moments: List[str], sport_type: str = None) -> List[float]:
        """根据focus_moments增强相关瞬间"""
        enhanced_scores = motion_scores.copy()
        
        for focus in focus_moments:
            focus_lower = focus.lower()
            
            # 根据不同的重点瞬间类型进行增强
            if any(word in focus_lower for word in ['投篮', '扣篮', '射门', '进球', '得分']):
                # 增强得分相关瞬间
                for i in range(1, len(motion_scores) - 1):
                    if (motion_scores[i] > 0.6 and 
                        motion_scores[i-1] < 0.3 and 
                        motion_scores[i+1] < 0.3):
                        enhanced_scores[i] *= 1.6
                        print(f"增强得分瞬间: 位置{i}, 分数{motion_scores[i]:.3f} -> {enhanced_scores[i]:.3f}")
            
            elif any(word in focus_lower for word in ['抢断', '盖帽', '防守', '解围']):
                # 增强防守相关瞬间
                for i in range(2, len(motion_scores) - 2):
                    if all(motion_scores[j] > 0.5 for j in range(i-1, i+2)):
                        enhanced_scores[i] *= 1.4
                        print(f"增强防守瞬间: 位置{i}, 分数{motion_scores[i]:.3f} -> {enhanced_scores[i]:.3f}")
            
            elif any(word in focus_lower for word in ['助攻', '传球', '配合', '团队']):
                # 增强团队配合瞬间
                for i in range(1, len(motion_scores) - 1):
                    if (0.3 < motion_scores[i] < 0.6 and 
                        abs(motion_scores[i] - motion_scores[i-1]) < 0.15):
                        enhanced_scores[i] *= 1.3
                        print(f"增强团队配合瞬间: 位置{i}, 分数{motion_scores[i]:.3f} -> {enhanced_scores[i]:.3f}")
            
            elif any(word in focus_lower for word in ['技术', '动作', '技巧']):
                # 增强技术动作瞬间
                for i in range(1, len(motion_scores) - 1):
                    if (motion_scores[i] > 0.5 and 
                        motion_scores[i-1] < motion_scores[i] and 
                        motion_scores[i+1] < motion_scores[i]):
                        enhanced_scores[i] *= 1.2
                        print(f"增强技术动作瞬间: 位置{i}, 分数{motion_scores[i]:.3f} -> {enhanced_scores[i]:.3f}")
            
            elif any(word in focus_lower for word in ['精彩', '亮点', '高亮']):
                # 增强一般精彩瞬间
                for i in range(1, len(motion_scores) - 1):
                    if motion_scores[i] > 0.6:
                        enhanced_scores[i] *= 1.1
                        print(f"增强精彩瞬间: 位置{i}, 分数{motion_scores[i]:.3f} -> {enhanced_scores[i]:.3f}")
        
        return enhanced_scores
    
    def _calculate_focus_threshold_adjustment(self, focus_moments: List[str]) -> float:
        """计算根据focus_moments的阈值调整系数"""
        adjustment = 1.0
        
        for focus in focus_moments:
            focus_lower = focus.lower()
            
            # 根据不同的重点瞬间类型调整阈值
            if any(word in focus_lower for word in ['投篮', '扣篮', '射门', '进球', '得分']):
                adjustment *= 0.9  # 降低阈值，更容易检测到得分瞬间
            elif any(word in focus_lower for word in ['抢断', '盖帽', '防守', '解围']):
                adjustment *= 0.95  # 稍微降低阈值，包含更多防守动作
            elif any(word in focus_lower for word in ['助攻', '传球', '配合', '团队']):
                adjustment *= 0.85  # 大幅降低阈值，包含更多团队配合
            elif any(word in focus_lower for word in ['技术', '动作', '技巧']):
                adjustment *= 0.9  # 降低阈值，包含更多技术动作
            elif any(word in focus_lower for word in ['精彩', '亮点', '高亮']):
                adjustment *= 0.95  # 稍微降低阈值，包含更多精彩瞬间
        
        return max(0.7, adjustment)  # 确保调整系数不会太低
    
    def _adjust_threshold_by_style(self, threshold: float, clip_style: str) -> float:
        """根据clip_style调整检测阈值"""
        style_lower = clip_style.lower()
        
        if any(word in style_lower for word in ['快速', '快节奏', '紧凑']):
            # 快速剪辑风格：提高阈值，只选择最精彩的瞬间
            threshold *= 1.2
            print(f"快速剪辑风格：提高阈值至 {threshold:.3f}")
        elif any(word in style_lower for word in ['慢速', '慢节奏', '舒缓']):
            # 慢速剪辑风格：降低阈值，包含更多内容
            threshold *= 0.8
            print(f"慢速剪辑风格：降低阈值至 {threshold:.3f}")
        elif any(word in style_lower for word in ['戏剧', '紧张', '激烈']):
            # 戏剧性剪辑：中等阈值，平衡精彩和连贯性
            threshold *= 1.1
            print(f"戏剧性剪辑风格：调整阈值至 {threshold:.3f}")
        elif any(word in style_lower for word in ['轻松', '休闲', '自然']):
            # 轻松剪辑：大幅降低阈值，包含更多自然内容
            threshold *= 0.7
            print(f"轻松剪辑风格：降低阈值至 {threshold:.3f}")
        elif any(word in style_lower for word in ['专业', '技术', '精确']):
            # 专业剪辑：提高阈值，追求精确性
            threshold *= 1.15
            print(f"专业剪辑风格：提高阈值至 {threshold:.3f}")
        
        return max(0.5, min(1.5, threshold))  # 限制阈值范围
    
    def _adjust_segment_by_duration_distribution(self, start: float, end: float, duration: float, 
                                                video_duration: float, duration_distribution: Dict[str, float]) -> Tuple[float, float]:
        """根据duration_distribution调整片段时长"""
        center = (start + end) / 2
        
        # 根据分布调整目标时长
        if 'short' in duration_distribution and duration_distribution['short'] > 0.5:
            # 偏好短片段
            target_duration = min(3.0, duration)
            print(f"偏好短片段：调整至 {target_duration:.1f}秒")
        elif 'medium' in duration_distribution and duration_distribution['medium'] > 0.5:
            # 偏好中等片段
            target_duration = min(6.0, max(3.0, duration))
            print(f"偏好中等片段：调整至 {target_duration:.1f}秒")
        elif 'long' in duration_distribution and duration_distribution['long'] > 0.5:
            # 偏好长片段
            target_duration = min(10.0, max(6.0, duration))
            print(f"偏好长片段：调整至 {target_duration:.1f}秒")
        else:
            # 默认调整
            target_duration = duration
        
        # 计算新的起止时间
        half_duration = target_duration / 2
        new_start = max(0, center - half_duration)
        new_end = min(video_duration, center + half_duration)
        
        return new_start, new_end
    
    def _apply_audio_suggestions(self, clips: List[VideoFileClip], audio_suggestions: List[str]) -> List[VideoFileClip]:
        """根据audio_suggestions调整音频效果"""
        adjusted_clips = []
        
        for clip in clips:
            adjusted_clip = clip
            
            for suggestion in audio_suggestions:
                suggestion_lower = suggestion.lower()
                
                if any(word in suggestion_lower for word in ['静音', '无声', '关闭音频']):
                    # 静音处理
                    adjusted_clip = adjusted_clip.without_audio()
                    print(f"应用静音建议: {suggestion}")
                
                elif any(word in suggestion_lower for word in ['降低音量', '减小音量', '音量降低']):
                    # 降低音量
                    adjusted_clip = adjusted_clip.volumex(0.3)
                    print(f"应用降低音量建议: {suggestion}")
                
                elif any(word in suggestion_lower for word in ['提高音量', '增大音量', '音量提高']):
                    # 提高音量
                    adjusted_clip = adjusted_clip.volumex(1.5)
                    print(f"应用提高音量建议: {suggestion}")
                
                elif any(word in suggestion_lower for word in ['慢动作', '慢速', '减速']):
                    # 慢动作效果
                    adjusted_clip = adjusted_clip.speedx(0.5)
                    print(f"应用慢动作建议: {suggestion}")
                
                elif any(word in suggestion_lower for word in ['快动作', '快速', '加速']):
                    # 快动作效果
                    adjusted_clip = adjusted_clip.speedx(2.0)
                    print(f"应用快动作建议: {suggestion}")
                
                elif any(word in suggestion_lower for word in ['淡入', '渐入']):
                    # 淡入效果
                    adjusted_clip = adjusted_clip.fadein(1.0)
                    print(f"应用淡入建议: {suggestion}")
                
                elif any(word in suggestion_lower for word in ['淡出', '渐出']):
                    # 淡出效果
                    adjusted_clip = adjusted_clip.fadeout(1.0)
                    print(f"应用淡出建议: {suggestion}")
            
            adjusted_clips.append(adjusted_clip)
        
        return adjusted_clips
    
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
    
    def _find_highlight_segments(self, motion_scores: List[float], video_path: str, clip_target: str = 'highlights', 
                                focus_moments: List[str] = None, clip_style: str = '标准剪辑', 
                                duration_distribution: Dict[str, float] = None) -> List[Tuple[float, float]]:
        """找出精彩瞬间时间段"""
        try:
            video = VideoFileClip(video_path)
            video_duration = video.duration
            video.close()
            
            time_interval = video_duration / len(motion_scores)
            
            # 根据剪辑目标调整阈值
            if clip_target == 'scoring':
                threshold = np.percentile(motion_scores, 85)  # 更严格的阈值，只选择最精彩的瞬间
            elif clip_target == 'defense':
                threshold = np.percentile(motion_scores, 75)  # 稍宽松的阈值，包含更多防守动作
            elif clip_target == 'teamwork':
                threshold = np.percentile(motion_scores, 70)  # 更宽松的阈值，包含更多团队配合
            else:
                threshold = np.percentile(motion_scores, 80)  # 默认阈值
            
            # 根据focus_moments进一步调整阈值
            if focus_moments:
                focus_threshold_adjustment = self._calculate_focus_threshold_adjustment(focus_moments)
                threshold *= focus_threshold_adjustment
                print(f"根据focus_moments调整阈值: {threshold:.3f} (调整系数: {focus_threshold_adjustment:.2f})")
            
            # 根据clip_style调整检测策略
            if clip_style:
                threshold = self._adjust_threshold_by_style(threshold, clip_style)
                print(f"根据clip_style调整阈值: {threshold:.3f} (风格: {clip_style})")
            
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
                
                # 根据duration_distribution调整片段时长
                if duration_distribution:
                    start, end = self._adjust_segment_by_duration_distribution(
                        start, end, duration, video_duration, duration_distribution
                    )
                else:
                    # 默认调整逻辑
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
