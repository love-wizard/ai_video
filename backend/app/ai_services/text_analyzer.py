import openai
import os
from typing import Dict, List, Tuple
import json

class TextAnalyzer:
    """文本分析服务，使用OpenAI API理解用户需求"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        else:
            print("警告: 未设置OPENAI_API_KEY环境变量")
        
        # 预设的剪辑策略模板
        self.clip_strategies = {
            'basketball': {
                'highlights': '检测投篮、扣篮、助攻等精彩瞬间',
                'scoring': '突出得分瞬间和关键球',
                'defense': '展示抢断、盖帽等防守精彩表现',
                'teamwork': '强调团队配合和战术执行'
            },
            'football': {
                'goals': '突出进球瞬间和射门精彩表现',
                'skills': '展示盘带、传球等个人技术',
                'tactics': '强调战术配合和团队协作',
                'defense': '展示抢断、解围等防守表现'
            },
            'tennis': {
                'aces': '突出发球得分和精彩回球',
                'rallies': '展示多拍对攻和战术变化',
                'skills': '强调技术动作和击球质量',
                'clutch': '突出关键分和比赛转折点'
            },
            'swimming': {
                'starts': '突出起跳和转身技术',
                'finishes': '展示冲刺和到达终点',
                'technique': '强调泳姿和呼吸节奏',
                'competition': '突出竞争激烈的瞬间'
            },
            'athletics': {
                'sprints': '突出短跑起跑和冲刺',
                'jumps': '展示跳跃项目的腾空瞬间',
                'throws': '强调投掷项目的发力瞬间',
                'finishes': '突出到达终点的精彩瞬间'
            }
        }
    
    def analyze_clip_request(self, text: str, sport_type: str = None) -> Dict:
        """
        分析用户的剪辑需求
        
        Args:
            text: 用户输入的文本描述
            sport_type: 运动类型（可选）
            
        Returns:
            分析结果，包含剪辑策略和参数
        """
        try:
            if self.api_key:
                return self._analyze_with_openai(text, sport_type)
            else:
                return self._analyze_with_rules(text, sport_type)
        except Exception as e:
            print(f"文本分析错误: {e}")
            return self._get_default_strategy(sport_type)
    
    def _analyze_with_openai(self, text: str, sport_type: str = None) -> Dict:
        """使用OpenAI API分析文本"""
        try:
            prompt = self._build_analysis_prompt(text, sport_type)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的运动视频剪辑助手，能够理解用户的剪辑需求并制定相应的剪辑策略。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return self._parse_openai_response(result, sport_type)
            
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return self._analyze_with_rules(text, sport_type)
    
    def _build_analysis_prompt(self, text: str, sport_type: str = None) -> str:
        """构建分析提示词"""
        base_prompt = f"""
        请分析以下运动视频剪辑需求，并返回JSON格式的分析结果：
        
        用户需求：{text}
        运动类型：{sport_type if sport_type else '未知'}
        
        请分析以下方面：
        1. 剪辑目标（highlights/scoring/defense/teamwork等）
        2. 重点关注的瞬间类型
        3. 剪辑风格（快节奏/慢动作/对比等）
        4. 音乐和音效建议
        5. 时长分配建议
        
        返回格式：
        {{
            "clip_target": "剪辑目标",
            "focus_moments": ["重点瞬间1", "重点瞬间2"],
            "clip_style": "剪辑风格",
            "audio_suggestions": "音频建议",
            "duration_distribution": "时长分配",
            "confidence": 0.8
        }}
        """
        return base_prompt
    
    def _parse_openai_response(self, response: str, sport_type: str = None) -> Dict:
        """解析OpenAI API响应"""
        try:
            # 尝试提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # 验证必要字段
                required_fields = ['clip_target', 'focus_moments', 'clip_style']
                if all(field in result for field in required_fields):
                    return result
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析OpenAI响应失败: {e}")
        
        # 如果解析失败，使用规则分析
        return self._analyze_with_rules(response, sport_type)
    
    def _analyze_with_rules(self, text: str, sport_type: str = None) -> Dict:
        """使用规则分析文本"""
        text_lower = text.lower()
        
        # 检测剪辑目标
        clip_target = self._detect_clip_target(text_lower)
        
        # 检测重点瞬间
        focus_moments = self._detect_focus_moments(text_lower, sport_type)
        
        # 检测剪辑风格
        clip_style = self._detect_clip_style(text_lower)
        
        # 生成音频建议
        audio_suggestions = self._generate_audio_suggestions(clip_target, sport_type)
        
        return {
            "clip_target": clip_target,
            "focus_moments": focus_moments,
            "clip_style": clip_style,
            "audio_suggestions": audio_suggestions,
            "duration_distribution": "均匀分布精彩瞬间",
            "confidence": 0.7
        }
    
    def _detect_clip_target(self, text: str) -> str:
        """检测剪辑目标"""
        if any(word in text for word in ['高亮', '精彩', '亮点', 'highlight']):
            return 'highlights'
        elif any(word in text for word in ['得分', '进球', 'scoring', 'goal']):
            return 'scoring'
        elif any(word in text for word in ['防守', '抢断', 'defense', 'block']):
            return 'defense'
        elif any(word in text for word in ['配合', '团队', 'teamwork', 'assist']):
            return 'teamwork'
        else:
            return 'highlights'
    
    def _detect_focus_moments(self, text: str, sport_type: str = None) -> List[str]:
        """检测重点瞬间"""
        moments = []
        
        if sport_type and sport_type in self.clip_strategies:
            # 根据运动类型推荐重点瞬间
            strategies = self.clip_strategies[sport_type]
            for key, description in strategies.items():
                if any(word in text for word in description.split()):
                    moments.append(description)
        
        # 通用瞬间检测
        if any(word in text for word in ['瞬间', 'moment', '精彩']):
            moments.append('精彩瞬间')
        if any(word in text for word in ['技术', 'skill', '动作']):
            moments.append('技术动作')
        if any(word in text for word in ['配合', 'cooperation']):
            moments.append('团队配合')
        
        if not moments:
            moments = ['精彩瞬间', '技术动作']
        
        return moments
    
    def _detect_clip_style(self, text: str) -> str:
        """检测剪辑风格"""
        if any(word in text for word in ['快节奏', '快', 'fast']):
            return '快节奏'
        elif any(word in text for word in ['慢动作', '慢', 'slow']):
            return '慢动作'
        elif any(word in text for word in ['对比', '对比度', 'contrast']):
            return '对比剪辑'
        else:
            return '标准剪辑'
    
    def _generate_audio_suggestions(self, clip_target: str, sport_type: str = None) -> str:
        """生成音频建议"""
        if clip_target == 'highlights':
            return '使用激动人心的背景音乐，增强精彩瞬间的冲击力'
        elif clip_target == 'scoring':
            return '在得分瞬间添加音效，突出关键时刻'
        elif clip_target == 'defense':
            return '使用紧张刺激的音乐，营造防守的紧张氛围'
        else:
            return '根据运动类型选择合适的背景音乐，增强观看体验'
    
    def _get_default_strategy(self, sport_type: str = None) -> Dict:
        """获取默认剪辑策略"""
        return {
            "clip_target": "highlights",
            "focus_moments": ["精彩瞬间", "技术动作"],
            "clip_style": "标准剪辑",
            "audio_suggestions": "使用适合的背景音乐",
            "duration_distribution": "均匀分布精彩瞬间",
            "confidence": 0.5
        }
    
    def get_sport_specific_strategy(self, sport_type: str) -> Dict:
        """获取特定运动类型的剪辑策略"""
        if sport_type in self.clip_strategies:
            return self.clip_strategies[sport_type]
        else:
            return {"general": "通用剪辑策略"}
