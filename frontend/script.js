class ProofVisualizer {
    constructor() {
        this.nodes = new Map();
        this.connections = [];
        this.websocket = null;
        this.isAnalyzing = false;
        this.graphContainer = document.getElementById('proofGraph');
        this.statusText = document.getElementById('statusText');
        this.progressBar = document.getElementById('progressBar');
        this.nodeDetails = document.getElementById('nodeDetails');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.spinner = document.getElementById('spinner');
        
        this.centerX = 0;
        this.centerY = 0;
        this.levelRadius = [0, 200, 300, 400, 500, 600]; // Radius for each level
        this.levelAngles = new Map(); // Track angle distribution per level
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        window.addEventListener('resize', () => this.updateCenterPosition());
        this.updateCenterPosition();
    }
    
    updateCenterPosition() {
        const rect = this.graphContainer.getBoundingClientRect();
        this.centerX = rect.width / 2;
        this.centerY = rect.height / 2;
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/analyze`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.updateStatus('Connected to server');
        };
        
        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateStatus('Disconnected from server');
            this.isAnalyzing = false;
            this.toggleAnalyzeButton(false);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('Connection error');
            this.isAnalyzing = false;
            this.toggleAnalyzeButton(false);
        };
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'node':
                this.addNode(message.data);
                break;
            case 'node_update':
                this.updateNode(message.data);
                break;
            case 'complete':
                this.onAnalysisComplete();
                break;
            case 'error':
                this.onError(message.data.message);
                break;
        }
    }
    
    addNode(nodeData) {
        const node = {
            id: nodeData.id,
            statement: nodeData.statement,
            level: nodeData.level,
            parentId: nodeData.parent_id,
            isElementary: nodeData.is_elementary,
            explanation: '',
            proofText: '',
            element: null,
            x: 0,
            y: 0
        };
        
        this.nodes.set(node.id, node);
        this.positionNode(node);
        this.createNodeElement(node);
        this.createConnection(node);
        
        this.updateStatus(`Analyzing dependencies... (${this.nodes.size} nodes)`);
        this.updateProgress(Math.min(this.nodes.size * 10, 90));
    }
    
    updateNode(nodeData) {
        const node = this.nodes.get(nodeData.id);
        if (node) {
            node.isElementary = nodeData.is_elementary;
            node.explanation = nodeData.explanation;
            node.proofText = nodeData.proof_text;
            
            // Update visual appearance
            if (node.element) {
                if (node.isElementary) {
                    node.element.classList.add('elementary');
                }
                node.element.classList.remove('analyzing');
            }
        }
    }
    
    positionNode(node) {
        if (node.level === 0) {
            // Root node at center
            node.x = this.centerX;
            node.y = this.centerY;
        } else {
            // Calculate position based on level and angle
            const radius = this.levelRadius[Math.min(node.level, this.levelRadius.length - 1)];
            const angle = this.getAngleForNode(node.level);
            
            node.x = this.centerX + radius * Math.cos(angle);
            node.y = this.centerY + radius * Math.sin(angle);
        }
    }
    
    getAngleForNode(level) {
        if (!this.levelAngles.has(level)) {
            this.levelAngles.set(level, []);
        }
        
        const angles = this.levelAngles.get(level);
        const numNodesAtLevel = angles.length;
        
        // Distribute nodes evenly around the circle
        const angleStep = (2 * Math.PI) / Math.max(8, numNodesAtLevel + 1);
        const angle = numNodesAtLevel * angleStep;
        
        angles.push(angle);
        return angle;
    }
    
    createNodeElement(node) {
        const nodeElement = document.createElement('div');
        nodeElement.className = 'node appearing';
        nodeElement.setAttribute('data-node-id', node.id);
        
        if (node.level === 0) {
            nodeElement.classList.add('root');
        } else {
            nodeElement.classList.add('analyzing');
        }
        
        nodeElement.style.left = `${node.x - 60}px`;
        nodeElement.style.top = `${node.y - 60}px`;
        
        // Truncate long statements for display
        const displayText = node.statement.length > 80 ? 
            node.statement.substring(0, 77) + '...' : 
            node.statement;
        nodeElement.textContent = displayText;
        
        nodeElement.addEventListener('click', () => this.showNodeDetails(node));
        
        this.graphContainer.appendChild(nodeElement);
        node.element = nodeElement;
        
        // Remove appearing animation class after animation completes
        setTimeout(() => {
            nodeElement.classList.remove('appearing');
        }, 800);
    }
    
    createConnection(node) {
        if (!node.parentId) return;
        
        const parentNode = this.nodes.get(node.parentId);
        if (!parentNode) return;
        
        const connection = document.createElement('div');
        connection.className = 'connection';
        
        // Calculate line position and rotation
        const dx = node.x - parentNode.x;
        const dy = node.y - parentNode.y;
        const length = Math.sqrt(dx * dx + dy * dy);
        const angle = Math.atan2(dy, dx) * 180 / Math.PI;
        
        connection.style.left = `${parentNode.x}px`;
        connection.style.top = `${parentNode.y}px`;
        connection.style.width = `${length}px`;
        connection.style.transform = `rotate(${angle}deg)`;
        
        this.graphContainer.appendChild(connection);
        this.connections.push(connection);
    }
    
    showNodeDetails(node) {
        const details = `
            <h4>${node.statement}</h4>
            <p><strong>Level:</strong> ${node.level}</p>
            <p><strong>Type:</strong> ${node.isElementary ? 'Elementary (5th grade level)' : 'Complex statement'}</p>
            ${node.explanation ? `<p><strong>Explanation:</strong> ${node.explanation}</p>` : ''}
            ${node.proofText ? `<p><strong>Proof:</strong> ${node.proofText}</p>` : ''}
        `;
        
        this.nodeDetails.innerHTML = details;
    }
    
    clearVisualization() {
        // Clear instructions
        const instructions = this.graphContainer.querySelector('.instructions');
        if (instructions) {
            instructions.remove();
        }
        
        // Clear existing nodes and connections
        this.nodes.clear();
        this.connections.forEach(conn => conn.remove());
        this.connections = [];
        this.levelAngles.clear();
        
        // Clear node elements
        const nodeElements = this.graphContainer.querySelectorAll('.node');
        nodeElements.forEach(el => el.remove());
        
        // Clear connection elements
        const connectionElements = this.graphContainer.querySelectorAll('.connection');
        connectionElements.forEach(el => el.remove());
        
        // Clear sidebar
        this.nodeDetails.innerHTML = '<p>Click on a node to see its proof details and explanation.</p>';
    }
    
    updateStatus(message) {
        this.statusText.textContent = message;
    }
    
    updateProgress(percentage) {
        this.progressBar.style.width = `${percentage}%`;
    }
    
    toggleAnalyzeButton(analyzing) {
        this.analyzeBtn.disabled = analyzing;
        if (analyzing) {
            this.spinner.classList.add('active');
        } else {
            this.spinner.classList.remove('active');
        }
    }
    
    onAnalysisComplete() {
        this.isAnalyzing = false;
        this.toggleAnalyzeButton(false);
        this.updateStatus(`Analysis complete - ${this.nodes.size} nodes generated`);
        this.updateProgress(100);
        
        // Reset progress bar after a delay
        setTimeout(() => {
            this.updateProgress(0);
        }, 2000);
    }
    
    onError(message) {
        this.isAnalyzing = false;
        this.toggleAnalyzeButton(false);
        this.updateStatus(`Error: ${message}`);
        this.updateProgress(0);
    }
    
    async analyzeStatement(statement) {
        if (this.isAnalyzing || !statement.trim()) return;
        
        this.isAnalyzing = true;
        this.toggleAnalyzeButton(true);
        this.clearVisualization();
        
        // Connect to WebSocket if not connected
        if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            this.connectWebSocket();
            
            // Wait for connection
            await new Promise((resolve) => {
                const checkConnection = () => {
                    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                        resolve();
                    } else {
                        setTimeout(checkConnection, 100);
                    }
                };
                checkConnection();
            });
        }
        
        // Send statement for analysis
        this.websocket.send(JSON.stringify({
            statement: statement
        }));
        
        this.updateStatus('Starting analysis...');
        this.updateProgress(10);
    }
}

// Global instance
const visualizer = new ProofVisualizer();

// Global function for the button
async function analyzeStatement() {
    const statement = document.getElementById('statementInput').value.trim();
    if (!statement) {
        alert('Please enter a statement to analyze');
        return;
    }
    
    await visualizer.analyzeStatement(statement);
}

// Example statements for testing
const exampleStatements = [
    "The sum of angles in a triangle equals 180 degrees",
    "The area of a circle is π times the radius squared",
    "Objects fall at the same rate regardless of their weight",
    "The Pythagorean theorem: a² + b² = c²",
    "Parallel lines never meet"
];

// Add example statement functionality
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('statementInput');
    
    // Add placeholder cycling for better UX
    let placeholderIndex = 0;
    setInterval(() => {
        if (!input.value && document.activeElement !== input) {
            input.placeholder = `Try: "${exampleStatements[placeholderIndex]}"`;
            placeholderIndex = (placeholderIndex + 1) % exampleStatements.length;
        }
    }, 4000);
    
    // Allow Enter key to submit
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            analyzeStatement();
        }
    });
}); 