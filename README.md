# 运动视频智能剪辑平台

一个基于AI的运动视频智能剪辑平台，允许用户上传运动视频并输入文字描述，系统会自动识别运动类型并剪辑出精彩瞬间。

## 功能特性

- 🎥 支持多种视频格式上传（MP4, AVI, MOV, MKV）
- 🏀 自动识别运动类型（篮球、足球、网球、游泳、田径等）
- 📝 智能文本理解，支持自然语言描述剪辑需求
- ✂️ AI驱动的视频精彩瞬间检测和剪辑
- 🎬 输出1分钟内的精彩集锦视频

## 技术架构

### 前端
- React 18 + TypeScript
- Tailwind CSS 样式框架
- React Dropzone 文件上传
- 响应式设计，支持移动端

### 后端
- Python Flask API
- SQLite 数据库
- OpenAI GPT-4 集成
- OpenCV + MoviePy 视频处理
- FFmpeg 视频编码

### AI服务
- 运动类型识别模型
- 精彩瞬间检测算法
- 自然语言理解处理

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- FFmpeg
- Conda（推荐）

### 后端设置

1. 激活conda环境：
```bash
conda activate video-editing
```

2. 安装Python依赖：
```bash
cd backend
pip install -r requirements.txt
```

3. 设置环境变量：
```bash
# 创建.env文件
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "SECRET_KEY=your_secret_key_here" >> .env
```

4. 启动Flask后端：
```bash
python run.py
```

后端将在 http://localhost:5000 运行

### 前端设置

1. 安装Node.js依赖：
```bash
cd frontend
npm install
```

2. 启动React开发服务器：
```bash
npm start
```

前端将在 http://localhost:3000 运行

## 使用流程

1. **上传视频**：拖拽或选择运动视频文件
2. **输入需求**：描述您希望如何剪辑视频
3. **AI分析**：系统自动识别运动类型和精彩瞬间
4. **智能剪辑**：根据需求生成剪辑时间轴
5. **下载结果**：获取1分钟内的精彩集锦

## 项目结构

```
video/
├── frontend/                 # React前端应用
├── backend/                  # Flask后端API
├── ai_models/               # AI模型和算法
├── video_processing/        # 视频处理模块
├── storage/                 # 文件存储
├── tests/                   # 测试文件
└── docs/                    # 文档
```

## 开发计划

- [x] 第一阶段：环境搭建和基础架构
- [x] 第二阶段：核心功能开发
- [ ] 第三阶段：用户界面和体验优化
- [ ] 第四阶段：测试和优化

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

