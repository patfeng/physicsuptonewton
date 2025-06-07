import React from 'react';

const Connection = ({ from, to }) => {
  const getConnectionStyle = () => {
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    return {
      left: `${from.x}px`,
      top: `${from.y}px`,
      width: `${length}px`,
      transform: `rotate(${angle}deg)`,
    };
  };

  return (
    <div
      className="connection"
      style={getConnectionStyle()}
    />
  );
};

export default Connection; 