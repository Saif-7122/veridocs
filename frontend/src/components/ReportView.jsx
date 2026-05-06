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

  const renderMarkdown = (text) => {
    if (!text) return null;
    return text.split('\n').map((line, i) => {
      // Bold
      let content = line;
      if (line.startsWith('# ')) return <h1 key={i}>{line.substring(2)}</h1>;
      if (line.startsWith('## ')) return <h2 key={i} style={{ marginTop: '24px' }}>{line.substring(3)}</h2>;
      if (line.startsWith('### ')) return <h3 key={i} style={{ marginTop: '16px' }}>{line.substring(4)}</h3>;
      if (line.startsWith('- ')) return <li key={i} style={{ marginLeft: '20px' }}>{line.substring(2)}</li>;
      
      // Basic bold/italic parsing could go here but let's keep it simple
      return <p key={i} style={{ marginBottom: '12px' }}>{content}</p>;
    });
  };

  return (
    <div className="view-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h2>Session Summary Report</h2>
        <button 
          onClick={handleDownload}
          disabled={loading || !report}
          className="btn btn-primary"
        >
          Download .md
        </button>
      </div>
      
      {error && <div style={{ color: 'var(--primary)', marginBottom: '16px' }}>{error}</div>}

      <div className="card" style={{ minHeight: '500px' }}>
        {loading ? (
          <div className="empty-state">
            <div className="spinner" style={{ marginBottom: '16px' }}></div>
            <p>Compiling document intelligence report...</p>
          </div>
        ) : (
          report ? renderMarkdown(report) : <div className="empty-state">No report data generated yet.</div>
        )}
      </div>
    </div>
  );
};
export default ReportView;
