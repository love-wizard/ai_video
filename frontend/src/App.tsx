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
  resultPath?: string;
  downloadUrl?: string;
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

  const handleClipRequest = useCallback(async (text: string, sportType: string, targetDuration: number) => {
    if (!currentVideo) {
      alert('请先上传视频文件');
      return;
    }

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
    
    try {
      // 调用后端剪辑API
      const response = await fetch(`/api/videos/${currentVideo.id}/clip`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          sportType: sportType,
          targetDuration: targetDuration
        }),
      });

      if (!response.ok) {
        throw new Error(`剪辑请求失败: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('剪辑请求提交成功:', result);

      // 更新状态为处理中
      setClipRequests(prev => 
        prev.map(req => 
          req.id === newRequest.id 
            ? { ...req, status: 'processing', id: result.clipId }
            : req
        )
      );

      // 轮询检查剪辑状态
      const checkStatus = async () => {
        try {
          const statusResponse = await fetch(`/api/videos/${currentVideo.id}/clip/${result.clipId}`);
          if (statusResponse.ok) {
            const statusResult = await statusResponse.json();
            console.log('剪辑状态:', statusResult);

            if (statusResult.status === 'completed') {
              // 剪辑完成
              setClipRequests(prev => 
                prev.map(req => 
                  req.id === result.clipId 
                    ? { ...req, status: 'completed', resultPath: statusResult.downloadUrl }
                    : req
                )
              );
              setIsProcessing(false);
              setCurrentStep('complete');
              return;
            } else if (statusResult.status === 'error') {
              // 剪辑失败
              setClipRequests(prev => 
                prev.map(req => 
                  req.id === result.clipId 
                    ? { ...req, status: 'error' }
                    : req
                )
              );
              setIsProcessing(false);
              alert('视频剪辑失败，请重试');
              return;
            }

            // 继续轮询
            setTimeout(checkStatus, 2000);
          }
        } catch (error) {
          console.error('检查状态失败:', error);
          setTimeout(checkStatus, 2000);
        }
      };

      // 开始轮询
      setTimeout(checkStatus, 2000);

    } catch (error) {
      console.error('剪辑请求失败:', error);
      setClipRequests(prev => 
        prev.map(req => 
          req.id === newRequest.id 
            ? { ...req, status: 'error' }
            : req
        )
      );
      setIsProcessing(false);
      alert(`剪辑请求失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }, [currentVideo]);

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

  const handleDownloadClip = useCallback(async (clipRequest: ClipRequest) => {
    try {
      if (!currentVideo) {
        console.error('没有当前视频');
        return;
      }

      // 调用后端下载API
      const response = await fetch(`/api/videos/${currentVideo.id}/clip/${clipRequest.id}/file`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`下载失败: ${response.statusText}`);
      }

      // 检查内容类型
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('video/')) {
        console.warn('下载的内容不是视频文件:', contentType);
      }

      // 获取文件名
      const contentDisposition = response.headers.get('content-disposition');
      let filename = 'clipped_video.mp4';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // 创建下载链接
      const blob = await response.blob();
      
      // 验证文件大小
      if (blob.size < 1024) {
        throw new Error('下载的文件太小，可能有问题');
      }

      // 验证文件类型
      if (!blob.type.includes('video/') && !filename.endsWith('.mp4')) {
        console.warn('文件类型可能不正确:', blob.type);
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      console.log('下载成功:', filename, '大小:', blob.size, '类型:', blob.type);
      
      // 显示成功消息
      alert(`下载成功！\n文件名: ${filename}\n文件大小: ${(blob.size / 1024 / 1024).toFixed(2)} MB`);
      
    } catch (error) {
      console.error('下载失败:', error);
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      alert(`下载失败: ${errorMessage}\n请检查后端服务是否正常运行`);
    }
  }, [currentVideo]);

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
                <button 
                  className="button success"
                  onClick={() => handleDownloadClip(completedRequest)}
                  disabled={completedRequest?.status !== 'completed'}
                >
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
