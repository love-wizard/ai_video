import React, { useState, useCallback } from 'react';
import VideoUploader from './components/VideoUploader';
import VideoPreview from './components/VideoPreview';
import TextInput from './components/TextInput';
import ProcessingStatus from './components/ProcessingStatus';
import './App.css';

interface VideoData {
  id: string;
  filename: string;
  file: File;
}

interface ClipRequest {
  id: string;
  text: string;
  sportType: string;
  targetDuration: number;
  status: 'pending' | 'processing' | 'completed' | 'error';
}

const App: React.FC = () => {
  const [currentVideo, setCurrentVideo] = useState<VideoData | null>(null);
  const [clipRequests, setClipRequests] = useState<ClipRequest[]>([]);
  const [currentStep, setCurrentStep] = useState<'upload' | 'describe' | 'process' | 'complete'>('upload');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleVideoUploaded = useCallback((videoId: string, filename: string, file: File) => {
    const videoData: VideoData = { id: videoId, filename, file };
    setCurrentVideo(videoData);
    setCurrentStep('describe');
  }, []);

  const handleClipRequest = useCallback((text: string, sportType: string, targetDuration: number) => {
    const newRequest: ClipRequest = {
      id: Date.now().toString(),
      text,
      sportType,
      targetDuration,
      status: 'pending'
    };
    
    setClipRequests(prev => [...prev, newRequest]);
    setCurrentStep('process');
    setIsProcessing(true);
    
    // 模拟处理过程
    setTimeout(() => {
      setClipRequests(prev => 
        prev.map(req => 
          req.id === newRequest.id 
            ? { ...req, status: 'processing' }
            : req
        )
      );
      
      setTimeout(() => {
        setClipRequests(prev => 
          prev.map(req => 
            req.id === newRequest.id 
              ? { ...req, status: 'completed' }
              : req
          )
        );
        setIsProcessing(false);
        setCurrentStep('complete');
      }, 5000);
    }, 1000);
  }, []);

  const handleReset = useCallback(() => {
    setCurrentVideo(null);
    setClipRequests([]);
    setCurrentStep('upload');
    setIsProcessing(false);
  }, []);

  const handleNewVideo = useCallback(() => {
    setCurrentVideo(null);
    setClipRequests([]);
    setCurrentStep('upload');
    setIsProcessing(false);
  }, []);

  const getCurrentClipRequest = () => {
    return clipRequests[clipRequests.length - 1];
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'upload':
        return (
          <VideoUploader 
            onVideoUploaded={(videoId, filename, file) => 
              handleVideoUploaded(videoId, filename, file)
            }
          />
        );
      
      case 'describe':
        return (
          <>
            <VideoPreview 
              videoFile={currentVideo?.file}
              onVideoSelected={(file) => {
                const videoData: VideoData = { 
                  id: Date.now().toString(), 
                  filename: file.name, 
                  file 
                };
                setCurrentVideo(videoData);
              }}
            />
            <TextInput 
              onClipRequest={handleClipRequest}
              disabled={isProcessing}
            />
          </>
        );
      
      case 'process':
        return (
          <>
            <VideoPreview 
              videoFile={currentVideo?.file}
              onVideoSelected={(file) => {
                const videoData: VideoData = { 
                  id: Date.now().toString(), 
                  filename: file.name, 
                  file 
                };
                setCurrentVideo(videoData);
              }}
            />
            <ProcessingStatus 
              isProcessing={isProcessing}
              onReset={handleReset}
            />
          </>
        );
      
      case 'complete':
        const completedRequest = getCurrentClipRequest();
        return (
          <>
            <VideoPreview 
              videoFile={currentVideo?.file}
              onVideoSelected={(file) => {
                const videoData: VideoData = { 
                  id: Date.now().toString(), 
                  filename: file.name, 
                  file 
                };
                setCurrentVideo(videoData);
              }}
            />
            <div className="component-container">
              <h2 className="component-title">🎉 剪辑完成！</h2>
              <div className="completion-summary">
                <div className="summary-item">
                  <span className="summary-label">📹 视频文件：</span>
                  <span className="summary-value">{currentVideo?.filename}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">✂️ 剪辑需求：</span>
                  <span className="summary-value">{completedRequest?.text}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">⏱️ 目标时长：</span>
                  <span className="summary-value">{completedRequest?.targetDuration}秒</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">🏃 运动类型：</span>
                  <span className="summary-value">
                    {completedRequest?.sportType === 'auto' ? '自动识别' : completedRequest?.sportType}
                  </span>
                </div>
              </div>
              
              <div className="completion-actions">
                <button className="button success">
                  📥 下载剪辑结果
                </button>
                <button className="button secondary" onClick={handleNewVideo}>
                  🆕 处理新视频
                </button>
                <button className="button secondary" onClick={handleReset}>
                  🔄 重新开始
                </button>
              </div>
            </div>
          </>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 运动视频智能剪辑平台</h1>
        <p>上传运动视频，AI智能识别精彩瞬间，一键生成精彩集锦</p>
      </header>
      
      <main className="App-main">
        {/* 步骤指示器 */}
        <div className="step-indicator">
          <div className={`step ${currentStep === 'upload' ? 'active' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-text">上传视频</span>
          </div>
          <div className={`step ${currentStep === 'describe' ? 'active' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-text">描述需求</span>
          </div>
          <div className={`step ${currentStep === 'process' ? 'active' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-text">AI处理</span>
          </div>
          <div className={`step ${currentStep === 'complete' ? 'active' : ''}`}>
            <span className="step-number">4</span>
            <span className="step-text">完成下载</span>
          </div>
        </div>

        {/* 动态渲染当前步骤 */}
        {renderCurrentStep()}
      </main>
    </div>
  );
};

export default App;
