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
    <div className="view-container">
      <div className="empty-state" style={{ paddingBottom: '20px' }}>
        <h1 style={{ marginBottom: '16px' }}>Document Ingestion</h1>
        <p>Upload your PDFs or Word documents to begin the AI analysis.</p>
      </div>
      
      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleFileClick}
        className="card"
        style={{ 
          border: `2px dashed ${isDragging ? 'var(--primary)' : '#ccc'}`, 
          padding: '60px', 
          backgroundColor: isDragging ? '#fdf8f7' : '#FFFFFF',
          textAlign: 'center',
          cursor: 'pointer',
          marginBottom: '32px'
        }}
      >
        <p style={{ color: 'var(--primary)', fontWeight: 'bold', marginBottom: '8px', fontSize: '18px' }}>
          {isDragging ? 'Drop files now' : 'Drag & Drop files here'}
        </p>
        <p style={{ color: '#999', fontSize: '14px' }}>Supports .pdf, .docx, .doc</p>
        <input 
          type="file" 
          multiple 
          ref={fileInputRef} 
          onChange={handleFileInputChange} 
          style={{ display: 'none' }} 
        />
      </div>

      {files.length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: '16px', fontSize: '16px', borderBottom: '1px solid #eee', paddingBottom: '8px' }}>
            Queue ({files.length} files)
          </h3>
          {files.map((f, i) => (
            <div key={i} style={{ padding: '8px 0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ color: 'var(--primary)', marginRight: '12px' }}>📄</span>
                {f.name}
              </div>
              <button 
                onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                style={{ background: 'none', border: 'none', color: '#999', cursor: 'pointer', fontSize: '14px' }}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {loading && (
        <div style={{ textAlign: 'center', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
          <div className="spinner"></div>
          <span style={{ color: 'var(--text-muted)' }}>Processing documents...</span>
        </div>
      )}

      {error && <div style={{ color: 'var(--primary)', marginBottom: '24px', textAlign: 'center' }}>{error}</div>}

      <div style={{ textAlign: 'center' }}>
        <button
          onClick={handleAnalyze}
          disabled={loading || files.length === 0}
          className="btn btn-primary"
          style={{ width: '100%', maxWidth: '300px' }}
        >
          Analyse Documents
        </button>
      </div>
    </div>
  );
};
export default UploadView;
