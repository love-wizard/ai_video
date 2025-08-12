import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface VideoUploaderProps {}

const VideoUploader: React.FC<VideoUploaderProps> = () => {
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedVideo, setUploadedVideo] = useState<{id: string, filename: string} | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadStatus('uploading');
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('video', file);

      const response = await fetch('http://localhost:5000/api/videos/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadedVideo({ id: result.videoId, filename: file.name });
        setUploadStatus('success');
        setUploadProgress(100);
      } else {
        throw new Error('上传失败');
      }
    } catch (error) {
      console.error('上传错误:', error);
      setUploadStatus('error');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    multiple: false
  });

  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadProgress(0);
    setUploadedVideo(null);
  };

  return (
    <div className="component-container">
      <h2 className="component-title">视频上传</h2>
      
      {uploadStatus === 'idle' && (
        <div
          {...getRootProps()}
          className={`upload-area ${isDragActive ? 'dragover' : ''}`}
        >
          <input {...getInputProps()} />
          <p>拖拽视频文件到这里，或者点击选择文件</p>
          <p>支持格式：MP4, AVI, MOV, MKV</p>
        </div>
      )}

      {uploadStatus === 'uploading' && (
        <div className="upload-area">
          <p>正在上传...</p>
          <div style={{ width: '100%', backgroundColor: 'rgba(255,255,255,0.3)', borderRadius: '10px', margin: '1rem 0' }}>
            <div 
              style={{ 
                width: `${uploadProgress}%`, 
                height: '20px', 
                backgroundColor: '#4CAF50', 
                borderRadius: '10px',
                transition: 'width 0.3s ease'
              }}
            />
          </div>
          <p>{uploadProgress}%</p>
        </div>
      )}

      {uploadStatus === 'success' && uploadedVideo && (
        <div className="upload-area">
          <p>✅ 上传成功！</p>
          <p>文件名：{uploadedVideo.filename}</p>
          <p>视频ID：{uploadedVideo.id}</p>
          <button className="button" onClick={resetUpload}>
            重新上传
          </button>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="upload-area">
          <p>❌ 上传失败</p>
          <button className="button" onClick={resetUpload}>
            重试
          </button>
        </div>
      )}
    </div>
  );
};

export default VideoUploader;
