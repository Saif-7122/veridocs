import React, { useState } from 'react';
import { getInsights, compareDocs } from '../api';

const CompareView = ({ sessionId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runComparison = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    setError(null);
    try {
      const [insightsData, compareData] = await Promise.all([
        getInsights(sessionId),
        compareDocs(sessionId)
      ]);
      setData({ compare: compareData, insights: insightsData.themes });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!data) {
    return (
      <div className="view-container">
        <div className="empty-state">
          <h1 style={{ marginBottom: '16px' }}>Document Matrix Analysis</h1>
          <p style={{ marginBottom: '32px' }}>Identify overlapping themes, legal agreements, and direct contradictions.</p>
          
          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', marginBottom: '24px' }}>
              <div className="spinner"></div>
              <span>Generating Matrix...</span>
            </div>
          )}
          
          {error && <div style={{ color: 'var(--primary)', marginBottom: '16px' }}>{error}</div>}
          
          <button 
            onClick={runComparison}
            disabled={loading || !sessionId}
            className="btn btn-dark"
          >
            {loading ? 'Processing...' : 'Run Comparison'}
          </button>
        </div>
      </div>
    );
  }

  const { compare, insights } = data;

  const Card = ({ title, children, color = 'var(--bg-dark)' }) => (
    <div className="card">
      <h3 style={{ color, borderBottom: '2px solid var(--border-light)', paddingBottom: '12px', marginBottom: '16px', fontSize: '18px' }}>
        {title}
      </h3>
      <div style={{ lineHeight: '1.7' }}>
        {children}
      </div>
    </div>
  );

  return (
    <div className="view-container">
      <div className="card" style={{ borderLeft: '4px solid var(--primary)' }}>
        <h2 style={{ marginBottom: '12px' }}>Executive Summary</h2>
        <p style={{ color: '#444' }}>{compare.summary}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <Card title="Agreements" color="#2c7a2c">
          <ul style={{ paddingLeft: '20px' }}>
            {compare.agreements && compare.agreements.length > 0 ? (
              compare.agreements.map((item, i) => <li key={i} style={{ marginBottom: '8px' }}>{item}</li>)
            ) : (
              <li style={{ color: '#999', listStyle: 'none', marginLeft: '-20px' }}>No specific agreements identified.</li>
            )}
          </ul>
        </Card>

        <Card title="Contradictions" color="var(--primary)">
          <ul style={{ paddingLeft: '20px' }}>
            {compare.contradictions && compare.contradictions.length > 0 ? (
              compare.contradictions.map((item, i) => <li key={i} style={{ marginBottom: '8px' }}>{item}</li>)
            ) : (
              <li style={{ color: '#999', listStyle: 'none', marginLeft: '-20px' }}>No direct contradictions found.</li>
            )}
          </ul>
        </Card>

        <Card title="Unique Content">
          {compare.unique_to && Object.keys(compare.unique_to).length > 0 ? (
            Object.entries(compare.unique_to).map(([doc, points]) => (
              <div key={doc} style={{ marginBottom: '16px' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px', color: '#666' }}>{doc}</div>
                <ul style={{ paddingLeft: '20px' }}>
                  {points && points.length > 0 ? (
                    points.map((p, i) => <li key={i} style={{ marginBottom: '4px' }}>{p}</li>)
                  ) : (
                    <li style={{ color: '#999', listStyle: 'none', marginLeft: '-20px' }}>None identified.</li>
                  )}
                </ul>
              </div>
            ))
          ) : (
            <div style={{ color: '#999' }}>No unique content mapped.</div>
          )}
        </Card>

        <Card title="Document Themes">
          {insights && Object.keys(insights).length > 0 ? (
            Object.entries(insights).map(([doc, themes]) => (
              <div key={doc} style={{ marginBottom: '16px' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px', color: '#666' }}>{doc}</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {themes && themes.length > 0 ? (
                    themes.map((t, i) => (
                      <span key={i} className="pill">
                        {t}
                      </span>
                    ))
                  ) : (
                    <span style={{ color: '#999', fontSize: '12px' }}>No themes extracted.</span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div style={{ color: '#999' }}>No themes available.</div>
          )}
        </Card>
      </div>
    </div>
  );
};
export default CompareView;
