import React from 'react';
import './App.css';
import VideoUploader from './components/VideoUploader';
import TextInput from './components/TextInput';
import ProcessingStatus from './components/ProcessingStatus';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>运动视频智能剪辑平台</h1>
        <p>上传视频，输入需求，AI自动剪辑精彩瞬间</p>
      </header>
      <main className="App-main">
        <VideoUploader />
        <TextInput />
        <ProcessingStatus />
      </main>
    </div>
  );
}

export default App;
