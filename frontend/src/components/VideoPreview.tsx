import React, { useState, useRef, useEffect } from 'react';

interface VideoPreviewProps {
  videoFile?: File | null;
  videoUrl?: string;
  onVideoSelected?: (file: File) => void;
}

const VideoPreview: React.FC<VideoPreviewProps> = ({ 
  videoFile, 
  videoUrl, 
  onVideoSelected 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const controlsTimeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => setCurrentTime(video.currentTime);
    const handleLoadedMetadata = () => setDuration(video.duration);
    const handleVolumeChange = () => setVolume(video.volume);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement);

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('volumechange', handleVolumeChange);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('volumechange', handleVolumeChange);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  useEffect(() => {
    if (showControls) {
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current);
      }
      controlsTimeoutRef.current = setTimeout(() => {
        setShowControls(false);
      }, 3000);
    }

    return () => {
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current);
      }
    };
  }, [showControls]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const newTime = parseFloat(e.target.value);
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = parseFloat(e.target.value);
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isMuted) {
      video.volume = volume || 1;
      setIsMuted(false);
    } else {
      video.volume = 0;
      setIsMuted(true);
    }
  };

  const changePlaybackRate = (rate: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.playbackRate = rate;
    setPlaybackRate(rate);
  };

  const toggleFullscreen = () => {
    const video = videoRef.current;
    if (!video) return;

    if (!isFullscreen) {
      if (video.requestFullscreen) {
        video.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleMouseMove = () => {
    setShowControls(true);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onVideoSelected) {
      onVideoSelected(file);
    }
  };

  if (!videoFile && !videoUrl) {
    return (
      <div className="component-container">
        <h2 className="component-title">🎬 视频预览</h2>
        <div className="video-placeholder">
          <div className="placeholder-icon">📹</div>
          <p className="placeholder-text">请先上传视频文件</p>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="file-input"
            id="video-file-input"
          />
          <label htmlFor="video-file-input" className="button secondary">
            📁 选择视频文件
          </label>
        </div>
      </div>
    );
  }

  return (
    <div className="component-container">
      <h2 className="component-title">🎬 视频预览</h2>
      
      <div className="video-container">
        <video
          ref={videoRef}
          className="video-player"
          src={videoUrl || (videoFile ? URL.createObjectURL(videoFile) : '')}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setShowControls(false)}
        />
        
        {showControls && (
          <div className="video-controls">
            <div className="controls-top">
              <div className="playback-controls">
                <button 
                  className="control-button"
                  onClick={togglePlay}
                  title={isPlaying ? '暂停' : '播放'}
                >
                  {isPlaying ? '⏸️' : '▶️'}
                </button>
                
                <div className="time-display">
                  <span>{formatTime(currentTime)}</span>
                  <span>/</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>
              
              <div className="right-controls">
                <select
                  className="playback-rate-select"
                  value={playbackRate}
                  onChange={(e) => changePlaybackRate(parseFloat(e.target.value))}
                >
                  <option value={0.5}>0.5x</option>
                  <option value={0.75}>0.75x</option>
                  <option value={1}>1x</option>
                  <option value={1.25}>1.25x</option>
                  <option value={1.5}>1.5x</option>
                  <option value={2}>2x</option>
                </select>
                
                <button 
                  className="control-button"
                  onClick={toggleMute}
                  title={isMuted ? '取消静音' : '静音'}
                >
                  {isMuted ? '🔇' : '🔊'}
                </button>
                
                <button 
                  className="control-button"
                  onClick={toggleFullscreen}
                  title={isFullscreen ? '退出全屏' : '全屏'}
                >
                  {isFullscreen ? '⏹️' : '⛶'}
                </button>
              </div>
            </div>
            
            <div className="progress-section">
              <input
                type="range"
                className="seek-slider"
                min={0}
                max={duration || 0}
                value={currentTime}
                onChange={handleSeek}
                step={0.1}
              />
            </div>
            
            <div className="volume-section">
              <input
                type="range"
                className="volume-slider"
                min={0}
                max={1}
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                step={0.1}
              />
            </div>
          </div>
        )}
      </div>
      
      {videoFile && (
        <div className="video-info">
          <p><strong>文件名：</strong>{videoFile.name}</p>
          <p><strong>文件大小：</strong>{(videoFile.size / (1024 * 1024)).toFixed(2)} MB</p>
          <p><strong>文件类型：</strong>{videoFile.type}</p>
        </div>
      )}
    </div>
  );
};

export default VideoPreview;
