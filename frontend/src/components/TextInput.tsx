import React, { useState } from 'react';

interface TextInputProps {
  onClipRequest?: (text: string, sportType: string, targetDuration: number) => void;
  disabled?: boolean;
}

const TextInput: React.FC<TextInputProps> = ({ onClipRequest, disabled = false }) => {
  const [text, setText] = useState('');
  const [sportType, setSportType] = useState('auto');
  const [targetDuration, setTargetDuration] = useState(60);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const presetTemplates = [
    '帮我剪出高亮瞬间并合成视频，总长度在1分钟内',
    '提取最精彩的进球/得分瞬间',
    '剪辑出最激动人心的比赛片段',
    '制作一个精彩集锦视频',
    '突出显示技术动作和精彩配合'
  ];

  const handleSubmit = async () => {
    if (!text.trim()) {
      setErrorMessage('请输入剪辑需求描述');
      return;
    }

    if (text.length < 10) {
      setErrorMessage('描述至少需要10个字符');
      return;
    }

    setErrorMessage('');
    setIsSubmitting(true);

    try {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onClipRequest) {
        onClipRequest(text, sportType, targetDuration);
      }
      
      // 清空表单
      setText('');
      setSportType('auto');
      setTargetDuration(60);
      
    } catch (error) {
      setErrorMessage('提交失败，请重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTemplateSelect = (template: string) => {
    setText(template);
    setErrorMessage('');
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    if (errorMessage) {
      setErrorMessage('');
    }
  };

  const characterCount = text.length;
  const isTextValid = text.length >= 10;

  return (
    <div className="component-container">
      <h2 className="component-title">✂️ 剪辑需求描述</h2>
      
      <div className="form-group">
        <label className="form-label">
          🏃 运动类型：
        </label>
        <select 
          value={sportType} 
          onChange={(e) => setSportType(e.target.value)}
          className="form-select"
          disabled={disabled}
        >
          <option value="auto">🤖 自动识别</option>
          <option value="basketball">🏀 篮球</option>
          <option value="football">⚽ 足球</option>
          <option value="tennis">🎾 网球</option>
          <option value="swimming">🏊 游泳</option>
          <option value="athletics">🏃 田径</option>
        </select>
      </div>

      <div className="form-group">
        <label className="form-label">
          ⏱️ 目标时长（秒）：
        </label>
        <input
          type="number"
          value={targetDuration}
          onChange={(e) => setTargetDuration(Number(e.target.value))}
          min="10"
          max="300"
          className="form-input"
          disabled={disabled}
        />
        <small className="form-hint">建议时长：10-300秒</small>
      </div>

      <div className="form-group">
        <label className="form-label">
          📝 剪辑需求描述：
        </label>
        <textarea
          className={`form-textarea ${!isTextValid && text.length > 0 ? 'error' : ''}`}
          value={text}
          onChange={handleTextChange}
          placeholder="请详细描述您希望如何剪辑这个视频..."
          disabled={disabled}
          rows={4}
        />
        <div className="character-count">
          <span className={isTextValid ? 'valid' : 'invalid'}>
            {characterCount}/10
          </span>
          {!isTextValid && text.length > 0 && (
            <span className="validation-message">描述至少需要10个字符</span>
          )}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">🚀 快速模板：</label>
        <div className="template-buttons">
          {presetTemplates.map((template, index) => (
            <button
              key={index}
              type="button"
              onClick={() => handleTemplateSelect(template)}
              className="template-button"
              disabled={disabled}
            >
              {template}
            </button>
          ))}
        </div>
      </div>

      {errorMessage && (
        <div className="error-message">
          ❌ {errorMessage}
        </div>
      )}

      <button 
        className="button" 
        onClick={handleSubmit}
        disabled={!text.trim() || !isTextValid || isSubmitting || disabled}
      >
        {isSubmitting ? '⏳ 提交中...' : '🎬 开始剪辑'}
      </button>
    </div>
  );
};

export default TextInput;
