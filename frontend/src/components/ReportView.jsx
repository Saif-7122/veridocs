import React from 'react';
import { MOCK_REPORT } from '../mockData';

const ReportView = () => {
  const handleDownload = () => {
    const blob = new Blob([MOCK_REPORT], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'veridocs_report.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h2>Session Report</h2>
        <button 
          onClick={handleDownload}
          style={{
            backgroundColor: '#CC4125', color: '#FFFFFF', padding: '10px 24px', 
            border: 'none', borderRadius: '4px', fontFamily: 'inherit', fontSize: '14px',
            cursor: 'pointer'
          }}>
          Download .md
        </button>
      </div>
      
      <div style={{ 
        backgroundColor: '#FFFFFF', 
        padding: '40px', 
        borderRadius: '4px', 
        border: '1px solid #e0e0e0',
        whiteSpace: 'pre-wrap',
        fontFamily: 'monospace',
        fontSize: '14px',
        lineHeight: '1.6',
        color: '#333'
      }}>
        {MOCK_REPORT}
      </div>
    </div>
  );
};
export default ReportView;
