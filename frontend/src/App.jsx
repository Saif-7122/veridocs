import React, { useState } from 'react';
import Nav from './components/Nav';
import UploadView from './components/UploadView';
import ChatView from './components/ChatView';
import CompareView from './components/CompareView';
import ReportView from './components/ReportView';

function App() {
  const [view, setView] = useState('upload');
  const [hasSession, setHasSession] = useState(false);

  const handleUploadComplete = () => {
    setHasSession(true);
    setView('chat');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Nav currentView={view} onViewChange={setView} hasSession={hasSession} />
      
      <div style={{ flex: 1 }}>
        {view === 'upload' && <UploadView onComplete={handleUploadComplete} />}
        {view === 'chat' && <ChatView />}
        {view === 'compare' && <CompareView />}
        {view === 'report' && <ReportView />}
      </div>
    </div>
  );
}

export default App;
