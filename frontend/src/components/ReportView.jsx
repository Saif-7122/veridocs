import React, { useState, useEffect } from 'react';
import { getReport } from '../api';

const ReportView = ({ sessionId }) => {
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (sessionId) {
      fetchReport();
    }
  }, [sessionId]);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const reportText = await getReport(sessionId);
      setReport(reportText);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!report) return;
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `veridocs_report_${sessionId || 'local'}.md`;
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
          disabled={loading || !report}
          style={{
            backgroundColor: '#CC4125', color: '#FFFFFF', padding: '10px 24px', 
            border: 'none', borderRadius: '4px', fontFamily: 'inherit', fontSize: '14px',
            cursor: (loading || !report) ? 'not-allowed' : 'pointer',
            opacity: (loading || !report) ? 0.7 : 1
          }}>
          Download .md
        </button>
      </div>
      
      {error && <div style={{ color: '#CC4125', marginBottom: '16px' }}>{error}</div>}

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
        {loading ? 'Generating report...' : (report || 'No report available.')}
      </div>
    </div>
  );
};
export default ReportView;
