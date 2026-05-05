import React, { useState } from 'react';
import Nav from './components/Nav';
import UploadView from './components/UploadView';
import ChatView from './components/ChatView';
import CompareView from './components/CompareView';
import ReportView from './components/ReportView';

function App() {
  const [view, setView] = useState('upload');
  const [hasSession, setHasSession] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleUploadComplete = (sid, fileNames) => {
    setSessionId(sid);
    setUploadedFiles(fileNames || []);
    setHasSession(true);
    setView('chat');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Nav currentView={view} onViewChange={setView} hasSession={hasSession} />
      
      <div style={{ flex: 1 }}>
        {view === 'upload' && <UploadView onComplete={handleUploadComplete} />}
        {view === 'chat' && <ChatView sessionId={sessionId} />}
        {view === 'compare' && <CompareView sessionId={sessionId} />}
        {view === 'report' && <ReportView sessionId={sessionId} />}
      </div>
    </div>
  );
}

export default App;
