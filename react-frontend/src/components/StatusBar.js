import React from 'react';

const StatusBar = ({ statusText, progress }) => {
  const isComplete = progress === 100;
  
  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="status-bar">
      <span className="status-text">{statusText}</span>
      <div className="status-controls">
        <div className="progress-container">
          <div 
            className="progress-bar" 
            style={{ width: `${progress}%` }}
          />
        </div>
        {isComplete && (
          <button 
            className="refresh-btn"
            onClick={handleRefresh}
            title="Start new analysis"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M23 4v6h-6M1 20v-6h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default StatusBar; 