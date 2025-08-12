import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface VideoUploaderProps {
  onVideoUploaded?: (videoId: string, filename: string, file: File) => void;
}

const VideoUploader: React.FC<VideoUploaderProps> = ({ onVideoUploaded }) => {
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedVideo, setUploadedVideo] = useState<{id: string, filename: string} | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // 验证文件大小（最大100MB）
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      setErrorMessage('文件大小不能超过100MB');
      setUploadStatus('error');
      return;
    }

    setUploadStatus('uploading');
    setUploadProgress(0);
    setErrorMessage('');

    try {
      const formData = new FormData();
      formData.append('video', file);

      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 15;
        });
      }, 200);

      const response = await fetch('/api/videos/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (response.ok) {
        const result = await response.json();
        setUploadedVideo({ id: result.videoId, filename: file.name });
        setUploadStatus('success');
        setUploadProgress(100);
        
        // 通知父组件
        if (onVideoUploaded) {
          onVideoUploaded(result.videoId, file.name, file);
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || '上传失败');
      }
    } catch (error) {
      console.error('上传错误:', error);
      setErrorMessage(error instanceof Error ? error.message : '上传失败');
      setUploadStatus('error');
    }
  }, [onVideoUploaded]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadProgress(0);
    setUploadedVideo(null);
    setErrorMessage('');
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="component-container">
      <h2 className="component-title">🎥 视频上传</h2>
      
      {uploadStatus === 'idle' && (
        <div
          {...getRootProps()}
          className={`upload-area ${isDragActive ? 'dragover' : ''} ${isDragReject ? 'dragreject' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="upload-icon">📁</div>
          <p className="upload-text">拖拽视频文件到这里，或者点击选择文件</p>
          <p className="upload-hint">支持格式：MP4, AVI, MOV, MKV</p>
          <p className="upload-hint">最大文件大小：100MB</p>
          {isDragReject && (
            <p className="upload-error">❌ 不支持的文件格式</p>
          )}
        </div>
      )}

      {uploadStatus === 'uploading' && (
        <div className="upload-area">
          <div className="upload-icon">⏳</div>
          <p className="upload-text">正在上传...</p>
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="progress-text">{Math.round(uploadProgress)}%</p>
          </div>
          <p className="upload-hint">请稍候，不要关闭页面</p>
        </div>
      )}

      {uploadStatus === 'success' && uploadedVideo && (
        <div className="upload-area success">
          <div className="upload-icon">✅</div>
          <p className="upload-text">上传成功！</p>
          <div className="video-info">
            <p><strong>文件名：</strong>{uploadedVideo.filename}</p>
            <p><strong>视频ID：</strong>{uploadedVideo.id}</p>
          </div>
          <button className="button secondary" onClick={resetUpload}>
            重新上传
          </button>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="upload-area error">
          <div className="upload-icon">❌</div>
          <p className="upload-text">上传失败</p>
          {errorMessage && (
            <p className="error-message">{errorMessage}</p>
          )}
          <button className="button secondary" onClick={resetUpload}>
            重试
          </button>
        </div>
      )}
    </div>
  );
};

export default VideoUploader;
