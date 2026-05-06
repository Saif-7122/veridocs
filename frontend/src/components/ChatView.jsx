import React, { useState } from 'react';
import { chatQuery } from '../api';

const ChatView = ({ sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !sessionId) return;
    
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    const currentInput = input;
    setInput('');
    setLoading(true);
    setError(null);
    
    try {
      const result = await chatQuery(sessionId, currentInput);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: result.answer,
        citations: result.citations,
        isError: result.error
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Error: " + err.message,
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view-container" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 72px)', maxWidth: '1000px' }}>
      <div style={{ flex: 1, padding: '20px 0', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {messages.length === 0 && (
          <div className="empty-state">
            <h2 style={{ marginBottom: '12px' }}>Consult your Documents</h2>
            <p>Ask specific questions about the uploaded files to get AI-powered insights.</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ 
            display: 'flex', 
            justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' 
          }}>
            <div style={{
              backgroundColor: m.role === 'user' ? 'var(--bg-dark)' : (m.isError ? '#fff5f5' : '#FFFFFF'),
              color: m.role === 'user' ? 'white' : 'var(--text-main)',
              padding: '20px 24px',
              borderRadius: '4px',
              maxWidth: '85%',
              border: m.role === 'assistant' ? '1px solid var(--border-light)' : 'none',
              boxShadow: m.role === 'assistant' ? 'var(--shadow-sm)' : 'none',
            }}>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7' }}>{m.content}</div>
              {m.role === 'assistant' && m.citations && m.citations.length > 0 && (
                <div style={{ marginTop: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {m.citations.map((cit, idx) => (
                    <span key={idx} className="pill" style={{ margin: 0 }}>
                      {cit.source} (p. {cit.page})
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-muted)' }}>
            <div className="spinner"></div>
            <span>Analyzing...</span>
          </div>
        )}
      </div>
      
      <div style={{ padding: '32px 0', borderTop: '1px solid var(--border-light)' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '16px' }}>
          <input 
            type="text" 
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask a question..."
            style={{
              flex: 1,
              padding: '16px',
              fontFamily: 'inherit',
              border: '1px solid #ccc',
              borderRadius: '4px',
              outline: 'none',
              fontSize: '16px'
            }}
          />
          <button type="submit" disabled={loading || !input.trim()} className="btn btn-primary">
            Send Query
          </button>
        </form>
      </div>
    </div>
  );
};
export default ChatView;
