import React, { useCallback, useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export default function ProofGraph({ nodes: initialNodes, connections: initialEdges, onNodeClick }) {
  // Convert initial nodes and edges to React Flow format
  const initialFlowNodes = Array.from(initialNodes.values()).map(node => ({
    id: node.id,
    position: { x: node.x, y: node.y },
    data: { 
      label: node.statement,
      isElementary: node.isElementary,
      explanation: node.explanation,
      proofText: node.proofText
    },
    style: {
      background: node.isElementary ? '#4CAF50' : '#2196F3',
      color: 'white',
      border: '1px solid #ccc',
      borderRadius: '5px',
      padding: '10px',
      width: 200,
      textAlign: 'center'
    }
  }));

  const initialFlowEdges = initialEdges.map(edge => ({
    id: edge.id,
    source: edge.from,
    target: edge.to,
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#999' }
  }));

  const [nodes, setNodes, onNodesChange] = useNodesState(initialFlowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialFlowEdges);

  // Update nodes and edges when initial data changes
  useEffect(() => {
    setNodes(initialFlowNodes);
    setEdges(initialFlowEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const onNodeClickHandler = useCallback((event, node) => {
    onNodeClick({
      id: node.id,
      statement: node.data.label,
      isElementary: node.data.isElementary,
      explanation: node.data.explanation,
      proofText: node.data.proofText
    });
  }, [onNodeClick]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClickHandler}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
} 