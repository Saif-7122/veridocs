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
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 66px)', maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#999', marginTop: '40px' }}>
            No messages yet. Ask a question about your documents!
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ 
            marginBottom: '24px', 
            display: 'flex', 
            justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' 
          }}>
            <div style={{
              backgroundColor: m.role === 'user' ? '#111111' : (m.isError ? '#ffebeb' : '#FFFFFF'),
              color: m.role === 'user' ? '#FFFFFF' : '#111111',
              padding: '16px 20px',
              borderRadius: '4px',
              maxWidth: '75%',
              border: m.role === 'assistant' ? (m.isError ? '1px solid #ffcccc' : '1px solid #e0e0e0') : 'none',
              boxShadow: m.role === 'assistant' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none'
            }}>
              <div style={{ lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>{m.content}</div>
              {m.citations && m.citations.length > 0 && (
                <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {m.citations.map((cit, idx) => (
                    <span key={idx} style={{
                      backgroundColor: '#CC4125',
                      color: '#FFFFFF',
                      fontSize: '12px',
                      padding: '4px 8px',
                      borderRadius: '4px'
                    }}>
                      {cit.source} (p. {cit.page})
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ color: '#666666', fontStyle: 'italic', padding: '16px' }}>Thinking...</div>
        )}
      </div>
      <div style={{ padding: '24px', borderTop: '1px solid #e0e0e0', backgroundColor: '#F5F5F5' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '16px' }}>
          <input 
            type="text" 
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            style={{
              flex: 1,
              padding: '16px',
              fontFamily: 'inherit',
              border: '1px solid #cccccc',
              borderRadius: '4px',
              outline: 'none',
              fontSize: '16px'
            }}
          />
          <button type="submit" disabled={loading} style={{
            backgroundColor: '#CC4125',
            color: '#FFFFFF',
            padding: '0 32px',
            border: 'none',
            borderRadius: '4px',
            fontFamily: 'inherit',
            fontSize: '16px',
            cursor: loading ? 'wait' : 'pointer',
            opacity: loading ? 0.7 : 1
          }}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
export default ChatView;
