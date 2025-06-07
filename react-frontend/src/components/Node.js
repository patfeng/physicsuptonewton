import React from 'react';

const Node = ({ node, onClick }) => {
  const getNodeClasses = () => {
    let classes = 'node';
    
    if (node.level === 0) {
      classes += ' root';
    }
    
    if (node.isElementary) {
      classes += ' elementary';
    } else if (node.level > 0) {
      classes += ' analyzing';
    }
    
    if (node.appearing) {
      classes += ' appearing';
    }
    
    return classes;
  };

  const getDisplayText = () => {
    return node.statement.length > 80 
      ? node.statement.substring(0, 77) + '...'
      : node.statement;
  };

  const getNodeStyle = () => ({
    left: `${node.x - 60}px`,
    top: `${node.y - 60}px`,
  });

  return (
    <div
      className={getNodeClasses()}
      style={getNodeStyle()}
      onClick={onClick}
      data-node-id={node.id}
    >
      {getDisplayText()}
    </div>
  );
};

export default Node; 