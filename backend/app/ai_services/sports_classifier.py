import cv2
import numpy as np
from typing import List, Tuple, Dict
import os

class SportsClassifier:
    """运动类型识别服务"""
    
    def __init__(self):
        self.sport_keywords = {
            'basketball': ['basketball', 'hoop', 'court', 'dribble', 'shoot'],
            'football': ['football', 'soccer', 'goal', 'field', 'kick'],
            'tennis': ['tennis', 'racket', 'court', 'serve', 'volley'],
            'swimming': ['swimming', 'pool', 'water', 'stroke', 'lane'],
            'athletics': ['running', 'track', 'jump', 'throw', 'sprint']
        }
        
        # 运动特征检测器
        self.feature_detectors = {
            'basketball': self._detect_basketball_features,
            'football': self._detect_football_features,
            'tennis': self._detect_tennis_features,
            'swimming': self._detect_swimming_features,
            'athletics': self._detect_athletics_features
        }
    
    def classify_sport(self, video_path: str) -> Dict[str, float]:
        """
        识别视频中的运动类型
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            运动类型及其置信度
        """
        try:
            # 提取视频帧进行分析
            frames = self._extract_key_frames(video_path, num_frames=10)
            
            # 分析每一帧
            sport_scores = {sport: 0.0 for sport in self.sport_keywords.keys()}
            
            for frame in frames:
                frame_scores = self._analyze_frame(frame)
                for sport, score in frame_scores.items():
                    sport_scores[sport] += score
            
            # 计算平均分数
            total_frames = len(frames)
            if total_frames > 0:
                for sport in sport_scores:
                    sport_scores[sport] /= total_frames
            
            # 归一化分数
            max_score = max(sport_scores.values())
            if max_score > 0:
                for sport in sport_scores:
                    sport_scores[sport] = sport_scores[sport] / max_score
            
            return sport_scores
            
        except Exception as e:
            print(f"运动类型识别错误: {e}")
            # 返回默认值
            return {'basketball': 0.2, 'football': 0.2, 'tennis': 0.2, 
                   'swimming': 0.2, 'athletics': 0.2}
    
    def _extract_key_frames(self, video_path: str, num_frames: int = 10) -> List[np.ndarray]:
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
                frames.append(frame)
        
        cap.release()
        return frames
    
    def _analyze_frame(self, frame: np.ndarray) -> Dict[str, float]:
        """分析单帧的运动特征"""
        scores = {sport: 0.0 for sport in self.sport_keywords.keys()}
        
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 检测边缘
        edges = cv2.Canny(gray, 50, 150)
        
        # 检测线条
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, 
                               minLineLength=50, maxLineGap=10)
        
        # 检测圆形
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                 param1=50, param2=30, minRadius=10, maxRadius=100)
        
        # 分析特征
        for sport, detector in self.feature_detectors.items():
            scores[sport] = detector(frame, gray, edges, lines, circles)
        
        return scores
    
    def _detect_basketball_features(self, frame, gray, edges, lines, circles) -> float:
        """检测篮球特征"""
        score = 0.0
        
        # 检测圆形（篮球）
        if circles is not None:
            score += 0.3
        
        # 检测矩形（球场边界）
        if lines is not None:
            horizontal_lines = sum(1 for line in lines if abs(line[0][1] - line[0][3]) < 10)
            vertical_lines = sum(1 for line in lines if abs(line[0][0] - line[0][2]) < 10)
            if horizontal_lines > 2 and vertical_lines > 2:
                score += 0.4
        
        # 检测橙色（篮球颜色）
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        orange_mask = cv2.inRange(hsv, (5, 50, 50), (15, 255, 255))
        orange_pixels = np.sum(orange_mask > 0)
        if orange_pixels > 1000:
            score += 0.3
        
        return min(score, 1.0)
    
    def _detect_football_features(self, frame, gray, edges, lines, circles) -> float:
        """检测足球特征"""
        score = 0.0
        
        # 检测圆形（足球）
        if circles is not None:
            score += 0.3
        
        # 检测绿色（草地）
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
        green_pixels = np.sum(green_mask > 0)
        if green_pixels > 5000:
            score += 0.4
        
        # 检测白色（球门线）
        white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
        white_pixels = np.sum(white_mask > 0)
        if white_pixels > 2000:
            score += 0.3
        
        return min(score, 1.0)
    
    def _detect_tennis_features(self, frame, gray, edges, lines, circles) -> float:
        """检测网球特征"""
        score = 0.0
        
        # 检测绿色（网球场）
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
        green_pixels = np.sum(green_mask > 0)
        if green_pixels > 3000:
            score += 0.4
        
        # 检测白色（网球场线）
        white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
        white_pixels = np.sum(white_mask > 0)
        if white_pixels > 1000:
            score += 0.3
        
        # 检测黄色（网球）
        yellow_mask = cv2.inRange(hsv, (20, 100, 100), (30, 255, 255))
        yellow_pixels = np.sum(yellow_mask > 0)
        if yellow_pixels > 500:
            score += 0.3
        
        return min(score, 1.0)
    
    def _detect_swimming_features(self, frame, gray, edges, lines, circles) -> float:
        """检测游泳特征"""
        score = 0.0
        
        # 检测蓝色（水）
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
        blue_pixels = np.sum(blue_mask > 0)
        if blue_pixels > 8000:
            score += 0.6
        
        # 检测白色（泳道线）
        white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
        white_pixels = np.sum(white_mask > 0)
        if white_pixels > 2000:
            score += 0.4
        
        return min(score, 1.0)
    
    def _detect_athletics_features(self, frame, gray, edges, lines, circles) -> float:
        """检测田径特征"""
        score = 0.0
        
        # 检测红色（跑道）
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        red_mask1 = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv, (170, 50, 50), (180, 255, 255))
        red_pixels = np.sum(red_mask1 > 0) + np.sum(red_mask2 > 0)
        if red_pixels > 3000:
            score += 0.5
        
        # 检测白色（跑道线）
        white_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
        white_pixels = np.sum(white_mask > 0)
        if white_pixels > 1000:
            score += 0.3
        
        # 检测绿色（草地）
        green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
        green_pixels = np.sum(green_mask > 0)
        if green_pixels > 2000:
            score += 0.2
        
        return min(score, 1.0)
    
    def get_dominant_sport(self, sport_scores: Dict[str, float]) -> Tuple[str, float]:
        """获取主导运动类型"""
        if not sport_scores:
            return 'unknown', 0.0
        
        dominant_sport = max(sport_scores.items(), key=lambda x: x[1])
        return dominant_sport
