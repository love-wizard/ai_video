import React, { useState } from 'react';

interface TextInputProps {}

const TextInput: React.FC<TextInputProps> = () => {
  const [text, setText] = useState('');
  const [sportType, setSportType] = useState('auto');
  const [targetDuration, setTargetDuration] = useState(60);

  const presetTemplates = [
    '帮我剪出高亮瞬间并合成视频，总长度在1分钟内',
    '提取最精彩的进球/得分瞬间',
    '剪辑出最激动人心的比赛片段',
    '制作一个精彩集锦视频',
    '突出显示技术动作和精彩配合'
  ];

  const handleSubmit = async () => {
    if (!text.trim()) {
      alert('请输入剪辑需求描述');
      return;
    }

    // TODO: 发送剪辑请求到后端
    console.log('发送剪辑请求:', {
      text,
      sportType,
      targetDuration
    });
  };

  const handleTemplateSelect = (template: string) => {
    setText(template);
  };

  return (
    <div className="component-container">
      <h2 className="component-title">剪辑需求描述</h2>
      
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', textAlign: 'left' }}>
          运动类型：
        </label>
        <select 
          value={sportType} 
          onChange={(e) => setSportType(e.target.value)}
          style={{
            width: '100%',
            padding: '0.5rem',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            color: '#333'
          }}
        >
          <option value="auto">自动识别</option>
          <option value="basketball">篮球</option>
          <option value="football">足球</option>
          <option value="tennis">网球</option>
          <option value="swimming">游泳</option>
          <option value="athletics">田径</option>
        </select>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', textAlign: 'left' }}>
          目标时长（秒）：
        </label>
        <input
          type="number"
          value={targetDuration}
          onChange={(e) => setTargetDuration(Number(e.target.value))}
          min="10"
          max="300"
          style={{
            width: '100%',
            padding: '0.5rem',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            color: '#333'
          }}
        />
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', textAlign: 'left' }}>
          剪辑需求描述：
        </label>
        <textarea
          className="text-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="请描述您希望如何剪辑这个视频..."
        />
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <p style={{ marginBottom: '0.5rem', textAlign: 'left' }}>快速模板：</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {presetTemplates.map((template, index) => (
            <button
              key={index}
              onClick={() => handleTemplateSelect(template)}
              style={{
                padding: '0.5rem 1rem',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '20px',
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              {template}
            </button>
          ))}
        </div>
      </div>

      <button 
        className="button" 
        onClick={handleSubmit}
        disabled={!text.trim()}
      >
        开始剪辑
      </button>
    </div>
  );
};

export default TextInput;
