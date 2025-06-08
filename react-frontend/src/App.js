import React, { useState, useEffect, useRef, useCallback } from 'react';
import ProofGraph from './components/ProofGraph';
import Sidebar from './components/Sidebar';
import StatusBar from './components/StatusBar';

const EXAMPLE_STATEMENTS = [
  "The sum of angles in a triangle equals 180 degrees",
  "The area of a circle is π times the radius squared",
  "Objects fall at the same rate regardless of their weight",
  "The Pythagorean theorem: a² + b² = c²",
  "Parallel lines never meet"
];

export default function App() {
  const [nodes, setNodes] = useState(new Map());
  const [connections, setConnections] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [highlightedNodes, setHighlightedNodes] = useState(new Set());
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showInput, setShowInput] = useState(true);
  const [statusText, setStatusText] = useState('Ready to analyze statements');
  const [progress, setProgress] = useState(0);
  const [statementInput, setStatementInput] = useState('');
  const [placeholder, setPlaceholder] = useState('');
  
  const websocketRef = useRef(null);
  const placeholderIndexRef = useRef(0);
  const levelAnglesRef = useRef(new Map());

  // Placeholder cycling effect
  useEffect(() => {
    const interval = setInterval(() => {
      if (!statementInput) {
        setPlaceholder(`Try: "${EXAMPLE_STATEMENTS[placeholderIndexRef.current]}"`);
        placeholderIndexRef.current = (placeholderIndexRef.current + 1) % EXAMPLE_STATEMENTS.length;
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [statementInput]);

  const getXForNode = (level) => {
    if (!levelAnglesRef.current.has(level)) {
      levelAnglesRef.current.set(level, []);
    }
    
    const angles = levelAnglesRef.current.get(level);
    const numNodesAtLevel = angles.length;
    console.log("numNodesAtLevel", numNodesAtLevel);
    const position = numNodesAtLevel*250-(level*250);
    
    // const angleStep = (2 * Math.PI) /(numNodesAtLevel + 1);
    // const angle = numNodesAtLevel * angleStep;
    
    angles.push(position);
    return position;
  };

  const addNode = useCallback((nodeData) => {
    console.log('Adding node:', nodeData);
    const newNode = {
      id: nodeData.id,
      statement: nodeData.statement,
      level: nodeData.level,
      parentId: nodeData.parent_id,
      isElementary: nodeData.is_elementary,
      explanation: '',
      proofText: '',
      x: 0,
      y: 0,
      appearing: true
    };

    // Position the node
    if (newNode.level === 0) {
      newNode.x = window.innerWidth / 2; // Center X for fullscreen
      newNode.y = window.innerHeight / 2; // Center Y for fullscreen
    } else {
      // const radius = [0, 200, 400, 600, 800, 1000, 1200, 1400][Math.min(newNode.level, 7)]+Math.random()*50;
      const x = getXForNode(newNode.level) + Math.random()*10;
      newNode.x = (window.innerWidth / 2) + x;
      newNode.y = (window.innerHeight / 2) + (newNode.level*150)+Math.random()*50;
    }

    setNodes(prevNodes => {
      const updatedNodes = new Map(prevNodes);
      updatedNodes.set(newNode.id, newNode);
      return updatedNodes;
    });

    // Create connection if not root node
    if (newNode.parentId) {
      setConnections(prevConnections => [
        ...prevConnections,
        { id: `${newNode.parentId}-${newNode.id}`, from: newNode.parentId, to: newNode.id }
      ]);
    }

    setStatusText(`Analyzing dependencies... (${nodes.size + 1} nodes)`);
    setProgress(Math.min((nodes.size + 1) * 10, 90));

    // Remove appearing animation after delay
    setTimeout(() => {
      setNodes(prevNodes => {
        const updatedNodes = new Map(prevNodes);
        const node = updatedNodes.get(newNode.id);
        if (node) {
          node.appearing = false;
          updatedNodes.set(newNode.id, node);
        }
        return updatedNodes;
      });
    }, 800);
  }, [nodes.size]);

  const updateNode = useCallback((nodeData) => {
    console.log('Updating node:', nodeData);
    setNodes(prevNodes => {
      const updatedNodes = new Map(prevNodes);
      const node = updatedNodes.get(nodeData.id);
      if (node) {
        node.isElementary = nodeData.is_elementary;
        node.explanation = nodeData.explanation;
        node.proofText = nodeData.proof_text;
        updatedNodes.set(nodeData.id, node);
      }
      return updatedNodes;
    });
  }, []);

  const onAnalysisComplete = useCallback(() => {
    console.log('Analysis complete');
    setIsAnalyzing(false);
    setStatusText(`Analysis complete`);
    setProgress(100);
    
    setTimeout(() => {
      setProgress(0);
    }, 2000);
  }, [nodes.size]);

  const onError = useCallback((message) => {
    console.error('Analysis error:', message);
    setIsAnalyzing(false);
    setStatusText(`Error: ${message}`);
    setProgress(0);
  }, []);

  const clearVisualization = useCallback(() => {
    console.log('Clearing visualization');
    setNodes(new Map());
    setConnections([]);
    setSelectedNode(null);
    setHighlightedNodes(new Set());
    levelAnglesRef.current.clear();
  }, []);

  const handleMessage = useCallback((message) => {
    console.log('WebSocket message:', message);
    switch (message.type) {
      case 'node':
        addNode(message.data);
        break;
      case 'node_update':
        updateNode(message.data);
        break;
      case 'complete':
        onAnalysisComplete();
        break;
      case 'error':
        onError(message.data.message);
        break;
      default:
        break;
    }
  }, [addNode, updateNode, onAnalysisComplete, onError]);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    console.log('Connecting to WebSocket...');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host.split(':')[0]}:8000/ws/analyze`;
    
    console.log('WebSocket URL:', wsUrl);
    websocketRef.current = new WebSocket(wsUrl);
    
    websocketRef.current.onopen = () => {
      console.log('WebSocket connected');
      setStatusText('Connected to server');
    };
    
    websocketRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleMessage(message);
    };
    
    websocketRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      setStatusText('Disconnected from server');
      setIsAnalyzing(false);
    };
    
    websocketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatusText('Connection error');
      setIsAnalyzing(false);
    };
  }, [handleMessage]);

  const analyzeStatement = useCallback(async () => {
    console.log('Analyze button clicked, statement:', statementInput);
    console.log('Is analyzing:', isAnalyzing);
    
    if (isAnalyzing || !statementInput.trim()) {
      if (!statementInput.trim()) {
        alert('Please enter a statement to analyze');
      }
      return;
    }

    setIsAnalyzing(true);
    setShowInput(false);
    clearVisualization();

    // Connect to WebSocket if not connected
    if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
      console.log('WebSocket not connected, connecting...');
      connectWebSocket();
      
      // Wait for connection
      await new Promise((resolve) => {
        const checkConnection = () => {
          if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
            console.log('WebSocket connected, resolving...');
            resolve();
          } else {
            setTimeout(checkConnection, 100);
          }
        };
        checkConnection();
      });
    }

    // Send statement for analysis
    console.log('Sending statement to WebSocket:', statementInput);
    websocketRef.current.send(JSON.stringify({
      statement: statementInput
    }));

    setStatusText('Starting analysis...');
    setProgress(10);
  }, [isAnalyzing, statementInput, clearVisualization, connectWebSocket]);

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node);
    
    // Find all nodes that depend on this node (children)
    const dependentNodes = new Set();
    // Find all nodes this node depends on (parents)
    const dependencyNodes = new Set();
    
    // Helper function to recursively find all children
    const findChildren = (nodeId) => {
      connections.forEach(conn => {
        if (conn.from === nodeId) {
          dependentNodes.add(conn.to);
          findChildren(conn.to);
        }
      });
    };
    
    // Helper function to recursively find all parents
    const findParents = (nodeId) => {
      connections.forEach(conn => {
        if (conn.to === nodeId) {
          dependencyNodes.add(conn.from);
          findParents(conn.from);
        }
      });
    };
    
    findChildren(node.id);
    findParents(node.id);
    
    // Combine all nodes that should be highlighted
    const allHighlighted = new Set([...dependentNodes, ...dependencyNodes, node.id]);
    setHighlightedNodes(allHighlighted);
  }, [connections]);

  const handleVisualizationClick = useCallback((e) => {
    // Only hide sidebar if clicking directly on the visualization container
    // This prevents hiding when clicking on nodes (which have their own click handler)
    if (e.target === e.currentTarget) {
      setSelectedNode(null);
    }
  }, []);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      analyzeStatement();
    }
  };

  const handleAnalyzeClick = () => {
    console.log('Button clicked!');
    analyzeStatement();
  };

  return (
    <div className="container">
      <header className="header">
        {/* <h1>Proof</h1> */}
      </header>
      
      {showInput && (
        <div className="input-section">
          <div className="input-container">
            <textarea 
              className="statement-input"
              value={statementInput}
              onChange={(e) => setStatementInput(e.target.value)}
              placeholder={placeholder || "Enter a mathematical or physics statement that could be proven during Newton's time (e.g., 'The sum of angles in a triangle equals 180 degrees')"}
              rows="3"
              onKeyPress={handleKeyPress}
            />
            <button 
              className="analyze-btn"
              onClick={handleAnalyzeClick}
              disabled={isAnalyzing}
            >
              <span className="btn-text">Analyze Statement</span>
              {isAnalyzing && <span className="spinner"></span>}
            </button>
          </div>
        </div>
      )}
      
      <div className="visualization-container" onClick={handleVisualizationClick}>
        <ProofGraph 
          nodes={nodes}
          connections={connections}
          onNodeClick={handleNodeClick}
          highlightedNodes={highlightedNodes}
        />
      </div>
      
      <Sidebar selectedNode={selectedNode} />
      
      <StatusBar statusText={statusText} progress={progress} />
    </div>
  );
} 