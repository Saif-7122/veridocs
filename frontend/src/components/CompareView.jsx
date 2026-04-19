import React, { useState } from 'react';
import { MOCK_COMPARE, MOCK_INSIGHTS } from '../mockData';

const CompareView = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const runComparison = () => {
    setLoading(true);
    setTimeout(() => {
      setData({ compare: MOCK_COMPARE, insights: MOCK_INSIGHTS });
      setLoading(false);
    }, 1600);
  };

  if (!data) {
    return (
      <div style={{ padding: '60px', textAlign: 'center' }}>
        <h2 style={{ marginBottom: '24px' }}>Document Comparison</h2>
        <p style={{ color: '#666', marginBottom: '32px' }}>Analyze overlapping themes, agreements, and contradictions.</p>
        <button 
          onClick={runComparison}
          disabled={loading}
          style={{
            backgroundColor: '#111111', color: '#FFFFFF', padding: '12px 32px', 
            border: 'none', borderRadius: '4px', fontFamily: 'inherit', fontSize: '16px',
            cursor: loading ? 'wait' : 'pointer', opacity: loading ? 0.7 : 1
          }}>
          {loading ? 'Running Matrix Analysis...' : 'Run Comparison'}
        </button>
      </div>
    );
  }

  const { compare, insights } = data;

  const Card = ({ title, children, color = '#111111' }) => (
    <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #e0e0e0', borderRadius: '4px', padding: '24px' }}>
      <h3 style={{ color, borderBottom: '1px solid #eee', paddingBottom: '12px', marginBottom: '16px', fontSize: '18px' }}>
        {title}
      </h3>
      {children}
    </div>
  );

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px', backgroundColor: '#FFFFFF', padding: '24px', borderLeft: '4px solid #CC4125', borderRadius: '4px' }}>
        <h3 style={{ marginBottom: '8px' }}>Executive Summary</h3>
        <p style={{ lineHeight: '1.6', color: '#444' }}>{compare.summary}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
        <Card title="Agreements" color="#2c7a2c">
          <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
            {compare.agreements.map((item, i) => <li key={i} style={{ marginBottom: '8px' }}>{item}</li>)}
          </ul>
        </Card>

        <Card title="Contradictions" color="#CC4125">
          <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
            {compare.contradictions.map((item, i) => <li key={i} style={{ marginBottom: '8px' }}>{item}</li>)}
          </ul>
        </Card>

        <Card title="Unique Content">
          {Object.entries(compare.unique_to).map(([doc, points]) => (
            <div key={doc} style={{ marginBottom: '16px' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px', color: '#666' }}>{doc}</div>
              <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
                {points.map((p, i) => <li key={i} style={{ marginBottom: '4px' }}>{p}</li>)}
              </ul>
            </div>
          ))}
        </Card>

        <Card title="Document Themes">
          {Object.entries(insights).map(([doc, themes]) => (
            <div key={doc} style={{ marginBottom: '16px' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px', color: '#666' }}>{doc}</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {themes.map((t, i) => (
                  <span key={i} style={{ backgroundColor: '#F5F5F5', border: '1px solid #ddd', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
};
export default CompareView;
