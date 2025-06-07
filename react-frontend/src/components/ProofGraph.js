import React, { useEffect, useRef, useState, useCallback } from 'react';
import Node from './Node';
import Connection from './Connection';

const ProofGraph = ({ nodes, connections, onNodeClick }) => {
  const graphRef = useRef(null);
  const contentRef = useRef(null);
  const [centerX, setCenterX] = useState(window.innerWidth / 2);
  const [centerY, setCenterY] = useState(window.innerHeight / 2);
  
  // Pan and zoom state
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [lastPan, setLastPan] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const updateCenterPosition = () => {
      if (graphRef.current) {
        const rect = graphRef.current.getBoundingClientRect();
        setCenterX(rect.width / 2);
        setCenterY(rect.height / 2);
      }
    };

    updateCenterPosition();
    window.addEventListener('resize', updateCenterPosition);
    
    return () => {
      window.removeEventListener('resize', updateCenterPosition);
    };
  }, []);

  // Update node positions when center changes
  useEffect(() => {
    nodes.forEach(node => {
      if (node.level === 0) {
        node.x = centerX;
        node.y = centerY;
      } else {
        const radius = [0, 200, 300, 400, 500, 600][Math.min(node.level, 5)];
        const dx = node.x - (window.innerWidth / 2); // Use screen center as reference
        const dy = node.y - (window.innerHeight / 2); // Use screen center as reference
        const angle = Math.atan2(dy, dx);
        node.x = centerX + radius * Math.cos(angle);
        node.y = centerY + radius * Math.sin(angle);
      }
    });
  }, [centerX, centerY, nodes]);

  // Mouse wheel zoom
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const rect = graphRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newZoom = Math.max(0.1, Math.min(5, zoom * delta));
    
    // Calculate new pan to zoom towards mouse position
    const zoomFactor = newZoom / zoom;
    const newPanX = mouseX - (mouseX - panX) * zoomFactor;
    const newPanY = mouseY - (mouseY - panY) * zoomFactor;
    
    setZoom(newZoom);
    setPanX(newPanX);
    setPanY(newPanY);
  }, [zoom, panX, panY]);

  // Mouse drag start
  const handleMouseDown = useCallback((e) => {
    if (e.target === graphRef.current || e.target === contentRef.current) {
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
      setLastPan({ x: panX, y: panY });
      e.preventDefault();
    }
  }, [panX, panY]);

  // Mouse drag move
  const handleMouseMove = useCallback((e) => {
    if (isDragging) {
      const deltaX = e.clientX - dragStart.x;
      const deltaY = e.clientY - dragStart.y;
      setPanX(lastPan.x + deltaX);
      setPanY(lastPan.y + deltaY);
    }
  }, [isDragging, dragStart, lastPan]);

  // Mouse drag end
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Touch events for mobile
  const handleTouchStart = useCallback((e) => {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      setIsDragging(true);
      setDragStart({ x: touch.clientX, y: touch.clientY });
      setLastPan({ x: panX, y: panY });
    }
  }, [panX, panY]);

  const handleTouchMove = useCallback((e) => {
    e.preventDefault();
    if (e.touches.length === 1 && isDragging) {
      const touch = e.touches[0];
      const deltaX = touch.clientX - dragStart.x;
      const deltaY = touch.clientY - dragStart.y;
      setPanX(lastPan.x + deltaX);
      setPanY(lastPan.y + deltaY);
    }
  }, [isDragging, dragStart, lastPan]);

  const handleTouchEnd = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Add event listeners
  useEffect(() => {
    const graph = graphRef.current;
    if (!graph) return;

    graph.addEventListener('wheel', handleWheel, { passive: false });
    graph.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    graph.addEventListener('touchstart', handleTouchStart, { passive: false });
    graph.addEventListener('touchmove', handleTouchMove, { passive: false });
    graph.addEventListener('touchend', handleTouchEnd);

    return () => {
      graph.removeEventListener('wheel', handleWheel);
      graph.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      graph.removeEventListener('touchstart', handleTouchStart);
      graph.removeEventListener('touchmove', handleTouchMove);
      graph.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleWheel, handleMouseDown, handleMouseMove, handleMouseUp, handleTouchStart, handleTouchMove, handleTouchEnd]);

  // Zoom controls
  const zoomIn = () => {
    const newZoom = Math.min(5, zoom * 1.2);
    setZoom(newZoom);
  };

  const zoomOut = () => {
    const newZoom = Math.max(0.1, zoom * 0.8);
    setZoom(newZoom);
  };

  const resetView = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  };

  const showInstructions = nodes.size === 0;

  const renderInstructions = () => (
    <div className="instructions">
      <div className="instructions-content">
        <h3>How it works:</h3>
        <ul>
          <li>Enter a statement that could be proven before Newton's time (1727)</li>
          <li>The AI will break it down into simpler dependencies</li>
          <li>Dependencies appear as connected nodes radiating outward</li>
          <li>Click nodes to see detailed explanations</li>
          <li>Green nodes are elementary (5th grade level)</li>
          <li>Use mouse wheel to zoom, drag to pan</li>
        </ul>
      </div>
    </div>
  );

  const renderZoomControls = () => (
    <div className="zoom-controls">
      <button className="zoom-btn" onClick={zoomIn} title="Zoom In">+</button>
      <button className="zoom-btn" onClick={zoomOut} title="Zoom Out">−</button>
      <button className="reset-btn" onClick={resetView} title="Reset View">Reset</button>
    </div>
  );

  const renderConnections = () => {
    return connections.map(connection => {
      const fromNode = nodes.get(connection.from);
      const toNode = nodes.get(connection.to);
      
      if (!fromNode || !toNode) return null;
      
      return (
        <Connection
          key={connection.id}
          from={fromNode}
          to={toNode}
        />
      );
    });
  };

  const renderNodes = () => {
    return Array.from(nodes.values()).map(node => (
      <Node
        key={node.id}
        node={node}
        onClick={() => onNodeClick(node)}
      />
    ));
  };

  const contentStyle = {
    transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
  };

  return (
    <div 
      ref={graphRef} 
      className={`proof-graph ${isDragging ? 'dragging' : ''}`}
    >
      {showInstructions && renderInstructions()}
      {!showInstructions && renderZoomControls()}
      
      <div 
        ref={contentRef}
        className="graph-content" 
        style={contentStyle}
      >
        {renderConnections()}
        {renderNodes()}
      </div>
    </div>
  );
};

export default ProofGraph; 