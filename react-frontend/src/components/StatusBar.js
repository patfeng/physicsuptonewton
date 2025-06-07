import React from 'react';

const StatusBar = ({ statusText, progress }) => {
  return (
    <div className="status-bar">
      <span className="status-text">{statusText}</span>
      <div className="progress-container">
        <div 
          className="progress-bar" 
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default StatusBar; 