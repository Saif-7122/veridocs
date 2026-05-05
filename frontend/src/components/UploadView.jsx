import React, { useState, useRef } from 'react';
import { uploadFiles } from '../api';

const UploadView = ({ onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await uploadFiles(files);
      onComplete(result.session_id, result.files);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      setFiles(prev => [...prev, ...droppedFiles]);
    }
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div style={{ padding: '60px', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
      <h1 style={{ marginBottom: '16px', color: '#111111' }}>Document Ingestion</h1>
      <p style={{ color: '#666666', marginBottom: '40px' }}>Upload your PDFs and DOCX files to begin analysis.</p>
      
      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleFileClick}
        style={{ 
          border: `2px dashed ${isDragging ? '#CC4125' : '#cccccc'}`, 
          padding: '60px', 
          backgroundColor: isDragging ? '#fdf8f7' : '#FFFFFF',
          borderRadius: '4px',
          marginBottom: '40px',
          cursor: 'pointer',
          transition: 'all 0.2s ease-in-out'
        }}
      >
        <p style={{ color: '#CC4125', fontWeight: 'bold', marginBottom: '8px' }}>
          {isDragging ? 'Drop files now' : 'Drag & Drop files here'}
        </p>
        <p style={{ color: '#999999', fontSize: '14px' }}>or click to browse</p>
        <input 
          type="file" 
          multiple 
          ref={fileInputRef} 
          onChange={handleFileInputChange} 
          style={{ display: 'none' }} 
        />
      </div>

      <div style={{ textAlign: 'left', marginBottom: '40px', backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '4px', border: '1px solid #e0e0e0' }}>
        <h3 style={{ marginBottom: '16px', fontSize: '16px', borderBottom: '1px solid #eee', paddingBottom: '8px' }}>Queue ({files.length})</h3>
        {files.map((f, i) => (
          <div key={i} style={{ padding: '8px 0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <span style={{ color: '#CC4125', marginRight: '8px' }}>📄</span>
              {f.name}
            </div>
            <button 
              onClick={() => removeFile(i)}
              style={{ background: 'none', border: 'none', color: '#999', cursor: 'pointer', fontSize: '16px', padding: '4px 8px' }}
              title="Remove file"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {error && <div style={{ color: '#CC4125', marginBottom: '16px' }}>{error}</div>}

      <button
        onClick={handleAnalyze}
        disabled={loading || files.length === 0}
        style={{
          backgroundColor: '#CC4125',
          color: '#FFFFFF',
          padding: '12px 32px',
          border: 'none',
          borderRadius: '4px',
          fontFamily: 'inherit',
          fontSize: '16px',
          cursor: (loading || files.length === 0) ? 'not-allowed' : 'pointer',
          opacity: (loading || files.length === 0) ? 0.7 : 1
        }}
      >
        {loading ? 'Processing Documents...' : 'Analyse Documents'}
      </button>
    </div>
  );
};
export default UploadView;
