import React, { useState, useEffect } from 'react';

interface ProcessingStatusProps {
  isProcessing?: boolean;
  onStartProcessing?: () => void;
  onReset?: () => void;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ 
  isProcessing = false, 
  onStartProcessing, 
  onReset 
}) => {
  const [currentStatus, setCurrentStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('等待开始...');
  const [currentStep, setCurrentStep] = useState('');
  const [estimatedTime, setEstimatedTime] = useState(0);

  const processingSteps = [
    '🔍 分析视频内容...',
    '🏃 识别运动类型...',
    '📝 理解剪辑需求...',
    '🎯 检测精彩瞬间...',
    '⏱️ 生成剪辑时间轴...',
    '✂️ 执行视频剪辑...',
    '🎬 合成最终视频...',
    '✅ 完成！'
  ];

  useEffect(() => {
    if (isProcessing && currentStatus === 'idle') {
      setCurrentStatus('processing');
      setProgress(0);
      setStatusMessage('开始处理...');
      setEstimatedTime(60); // 预估60秒
    }
  }, [isProcessing, currentStatus]);

  useEffect(() => {
    if (currentStatus === 'processing') {
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            setCurrentStatus('completed');
            setStatusMessage('剪辑完成！');
            setCurrentStep(processingSteps[processingSteps.length - 1]);
            return 100;
          }
          return prev + Math.random() * 8 + 2; // 2-10%的随机进度
        });
      }, 1500);

      return () => clearInterval(interval);
    }
  }, [currentStatus, processingSteps]);

  useEffect(() => {
    if (currentStatus === 'processing' && progress < 100) {
      const stepIndex = Math.floor((progress / 100) * (processingSteps.length - 1));
      setCurrentStep(processingSteps[stepIndex]);
      
      // 更新预估时间
      const remainingProgress = 100 - progress;
      const timePerPercent = estimatedTime / 100;
      const remainingTime = Math.ceil(remainingProgress * timePerPercent);
      setEstimatedTime(remainingTime);
    }
  }, [progress, currentStatus, processingSteps, estimatedTime]);

  const startProcessing = () => {
    if (onStartProcessing) {
      onStartProcessing();
    } else {
      setCurrentStatus('processing');
      setProgress(0);
      setStatusMessage('开始处理...');
      setEstimatedTime(60);
    }
  };

  const resetStatus = () => {
    if (onReset) {
      onReset();
    } else {
      setCurrentStatus('idle');
      setProgress(0);
      setStatusMessage('等待开始...');
      setCurrentStep('');
      setEstimatedTime(0);
    }
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds}秒`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}分${remainingSeconds}秒`;
  };

  return (
    <div className="component-container">
      <h2 className="component-title">📊 处理状态</h2>
      
      {currentStatus === 'idle' && (
        <div className="status-idle">
          <div className="status-icon">⏸️</div>
          <p className="status-text">{statusMessage}</p>
          <button className="button" onClick={startProcessing}>
            🚀 开始处理
          </button>
        </div>
      )}

      {currentStatus === 'processing' && (
        <div className="status-processing">
          <div className="status-header">
            <div className="status-icon">⚡</div>
            <div className="status-info">
              <p className="status-text">处理中...</p>
              <p className="status-step">{currentStep}</p>
              <p className="status-time">预估剩余时间：{formatTime(estimatedTime)}</p>
            </div>
          </div>
          
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill processing"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="progress-details">
              <span className="progress-percentage">{Math.round(progress)}%</span>
              <span className="progress-time">{formatTime(estimatedTime)}</span>
            </div>
          </div>
        </div>
      )}

      {currentStatus === 'completed' && (
        <div className="status-completed">
          <div className="status-icon">🎉</div>
          <p className="status-text">{statusMessage}</p>
          <div className="completion-actions">
            <button className="button success">
              📥 下载剪辑结果
            </button>
            <button className="button secondary" onClick={resetStatus}>
              🔄 重新开始
            </button>
          </div>
        </div>
      )}

      {currentStatus === 'error' && (
        <div className="status-error">
          <div className="status-icon">❌</div>
          <p className="status-text">处理失败</p>
          <p className="error-details">请检查视频格式和网络连接</p>
          <button className="button secondary" onClick={resetStatus}>
            🔄 重试
          </button>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;
