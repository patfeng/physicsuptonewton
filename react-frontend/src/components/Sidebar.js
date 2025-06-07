import React from 'react';

const Sidebar = ({ selectedNode }) => {
  const renderNodeDetails = () => {
    if (!selectedNode) {
      return <p>Click on a node to see its proof details and explanation.</p>;
    }

    return (
      <div className="node-details">
        <h4>{selectedNode.statement}</h4>
        <p><strong>Level:</strong> {selectedNode.level}</p>
        <p><strong>Type:</strong> {selectedNode.isElementary ? 'Elementary (5th grade level)' : 'Complex statement'}</p>
        {selectedNode.explanation && (
          <p><strong>Explanation:</strong> {selectedNode.explanation}</p>
        )}
        {selectedNode.proofText && (
          <p><strong>Proof:</strong> {selectedNode.proofText}</p>
        )}
      </div>
    );
  };

  return (
    <div className={`sidebar ${selectedNode ? 'visible' : ''}`}>
      <div className="sidebar-content">
        <h3>Statement Details</h3>
        {renderNodeDetails()}
      </div>
    </div>
  );
};

export default Sidebar; 