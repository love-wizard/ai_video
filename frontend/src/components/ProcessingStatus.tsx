import React, { useState, useEffect } from 'react';

interface ProcessingStatusProps {}

const ProcessingStatus: React.FC<ProcessingStatusProps> = () => {
  const [currentStatus, setCurrentStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('等待开始...');
  const [currentStep, setCurrentStep] = useState('');

  const processingSteps = [
    '分析视频内容...',
    '识别运动类型...',
    '理解剪辑需求...',
    '检测精彩瞬间...',
    '生成剪辑时间轴...',
    '执行视频剪辑...',
    '合成最终视频...',
    '完成！'
  ];

  useEffect(() => {
    if (currentStatus === 'processing') {
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            setCurrentStatus('completed');
            setStatusMessage('剪辑完成！');
            return 100;
          }
          return prev + 10;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [currentStatus]);

  useEffect(() => {
    if (currentStatus === 'processing' && progress < 100) {
      const stepIndex = Math.floor((progress / 100) * (processingSteps.length - 1));
      setCurrentStep(processingSteps[stepIndex]);
    }
  }, [progress, currentStatus]);

  const startProcessing = () => {
    setCurrentStatus('processing');
    setProgress(0);
    setStatusMessage('开始处理...');
  };

  const resetStatus = () => {
    setCurrentStatus('idle');
    setProgress(0);
    setStatusMessage('等待开始...');
    setCurrentStep('');
  };

  return (
    <div className="component-container">
      <h2 className="component-title">处理状态</h2>
      
      {currentStatus === 'idle' && (
        <div style={{ textAlign: 'center' }}>
          <p>{statusMessage}</p>
          <button className="button" onClick={startProcessing}>
            开始处理
          </button>
        </div>
      )}

      {currentStatus === 'processing' && (
        <div>
          <div style={{ marginBottom: '1rem' }}>
            <p><span className={`status-indicator status-processing`}></span>处理中...</p>
            <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>{currentStep}</p>
          </div>
          
          <div style={{ width: '100%', backgroundColor: 'rgba(255,255,255,0.3)', borderRadius: '10px', margin: '1rem 0' }}>
            <div 
              style={{ 
                width: `${progress}%`, 
                height: '20px', 
                backgroundColor: '#2196F3', 
                borderRadius: '10px',
                transition: 'width 0.5s ease'
              }}
            />
          </div>
          <p>{progress}%</p>
        </div>
      )}

      {currentStatus === 'completed' && (
        <div style={{ textAlign: 'center' }}>
          <p><span className={`status-indicator status-completed`}></span>✅ {statusMessage}</p>
          <div style={{ margin: '1rem 0' }}>
            <button className="button" style={{ backgroundColor: '#4CAF50' }}>
              下载剪辑结果
            </button>
            <button className="button" onClick={resetStatus}>
              重新开始
            </button>
          </div>
        </div>
      )}

      {currentStatus === 'error' && (
        <div style={{ textAlign: 'center' }}>
          <p><span className={`status-indicator status-error`}></span>❌ 处理失败</p>
          <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>请检查视频格式和网络连接</p>
          <button className="button" onClick={resetStatus}>
            重试
          </button>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;
