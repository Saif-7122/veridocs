import React, { useState } from 'react';
import { MOCK_SESSION } from '../mockData';

const UploadView = ({ onComplete }) => {
  const [loading, setLoading] = useState(false);

  const handleAnalyze = () => {
    setLoading(true);
    setTimeout(() => {
      onComplete(MOCK_SESSION);
    }, 1800);
  };

  return (
    <div style={{ padding: '60px', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
      <h1 style={{ marginBottom: '16px', color: '#111111' }}>Document Ingestion</h1>
      <p style={{ color: '#666666', marginBottom: '40px' }}>Upload your PDFs and DOCX files to begin analysis.</p>
      
      <div style={{ 
        border: '2px dashed #cccccc', 
        padding: '60px', 
        backgroundColor: '#FFFFFF',
        borderRadius: '4px',
        marginBottom: '40px',
        cursor: 'pointer'
      }}>
        <p style={{ color: '#CC4125', fontWeight: 'bold', marginBottom: '8px' }}>Drag & Drop files here</p>
        <p style={{ color: '#999999', fontSize: '14px' }}>or click to browse</p>
      </div>

      <div style={{ textAlign: 'left', marginBottom: '40px', backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '4px', border: '1px solid #e0e0e0' }}>
        <h3 style={{ marginBottom: '16px', fontSize: '16px', borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Queue ({MOCK_SESSION.length})</h3>
        {MOCK_SESSION.map(f => (
          <div key={f} style={{ padding: '8px 0', display: 'flex', alignItems: 'center' }}>
            <span style={{ color: '#CC4125', marginRight: '8px' }}>📄</span>
            {f}
          </div>
        ))}
      </div>

      <button
        onClick={handleAnalyze}
        disabled={loading}
        style={{
          backgroundColor: '#CC4125',
          color: '#FFFFFF',
          padding: '12px 32px',
          border: 'none',
          borderRadius: '4px',
          fontFamily: 'inherit',
          fontSize: '16px',
          cursor: loading ? 'wait' : 'pointer',
          opacity: loading ? 0.7 : 1
        }}
      >
        {loading ? 'Processing Documents...' : 'Analyse Documents'}
      </button>
    </div>
  );
};
export default UploadView;
