import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import json
from typing import List, Dict, Set
from collections import deque
import uuid

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

class ProofRequest(BaseModel):
    statement: str

class ProofNode:
    def __init__(self, statement: str, level: int, parent_id: str = None):
        self.id = str(uuid.uuid4())
        self.statement = statement
        self.level = level
        self.parent_id = parent_id
        self.dependencies = []
        self.is_elementary = False
        self.proof_text = ""

class ProofAnalyzer:
    def __init__(self):
        self.processed_statements: Set[str] = set()
        self.max_level = 5  # Maximum depth for BFS
        
    async def analyze_statement(self, statement: str) -> Dict:
        """Analyze a statement using OpenAI to determine if it's provable and get dependencies"""
        
        prompt = f"""
        You are analyzing mathematical and physics statements that could be proven during Newton's time (before 1727).
        
        Statement: "{statement}"
        
        Please provide a JSON response with the following structure:
        {{
            "is_provable": boolean,
            "is_elementary": boolean,
            "explanation": "Brief explanation of the statement",
            "dependencies": ["list of simpler statements this depends on"],
            "proof_sketch": "Brief proof or explanation"
        }}
        
        Guidelines:
        - is_provable: true if this could be proven with knowledge available before Newton's death
        - is_elementary: true if a 5th grader could understand this with basic explanation
        - dependencies: List 2-4 simpler statements that this depends on (empty if elementary)
        - Keep dependencies focused on fundamental concepts
        - Make dependencies progressively simpler
        """
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            # Try to extract JSON from the response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"Error analyzing statement: {e}")
            return {
                "is_provable": True,
                "is_elementary": False,
                "explanation": "Analysis failed",
                "dependencies": [],
                "proof_sketch": "Unable to analyze"
            }

    async def process_proof_bfs(self, initial_statement: str, websocket: WebSocket):
        """Process proof using BFS to break down dependencies"""
        
        # Initialize the queue with the root statement
        queue = deque()
        root_node = ProofNode(initial_statement, 0)
        queue.append(root_node)
        
        # Send the root node
        await websocket.send_json({
            "type": "node",
            "data": {
                "id": root_node.id,
                "statement": root_node.statement,
                "level": root_node.level,
                "parent_id": None,
                "is_elementary": False
            }
        })
        
        # Track all nodes for parallel processing
        processing_tasks = []
        
        while queue and len(processing_tasks) < 20:  # Limit concurrent tasks
            current_level_nodes = []
            
            # Collect all nodes at current level
            current_level = queue[0].level if queue else 0
            while queue and queue[0].level == current_level:
                current_level_nodes.append(queue.popleft())
            
            if not current_level_nodes:
                break
                
            # Process current level nodes in parallel
            analysis_tasks = []
            for node in current_level_nodes:
                if node.statement not in self.processed_statements and node.level < self.max_level:
                    self.processed_statements.add(node.statement)
                    task = self.analyze_statement(node.statement)
                    analysis_tasks.append((node, task))
            
            if analysis_tasks:
                # Wait for all analyses to complete
                results = await asyncio.gather(*[task for _, task in analysis_tasks], return_exceptions=True)
                
                # Process results and create child nodes
                for (node, _), result in zip(analysis_tasks, results):
                    if isinstance(result, Exception):
                        continue
                        
                    node.is_elementary = result.get("is_elementary", False)
                    node.proof_text = result.get("proof_sketch", "")
                    
                    # Send updated node info
                    await websocket.send_json({
                        "type": "node_update",
                        "data": {
                            "id": node.id,
                            "is_elementary": node.is_elementary,
                            "proof_text": node.proof_text,
                            "explanation": result.get("explanation", "")
                        }
                    })
                    
                    # Create child nodes for dependencies if not elementary
                    if not node.is_elementary and result.get("dependencies"):
                        for dep in result["dependencies"]:
                            if dep.strip() and dep not in self.processed_statements:
                                child_node = ProofNode(dep.strip(), node.level + 1, node.id)
                                node.dependencies.append(child_node.id)
                                queue.append(child_node)
                                
                                # Send child node
                                await websocket.send_json({
                                    "type": "node",
                                    "data": {
                                        "id": child_node.id,
                                        "statement": child_node.statement,
                                        "level": child_node.level,
                                        "parent_id": child_node.parent_id,
                                        "is_elementary": False
                                    }
                                })
                                
                                await asyncio.sleep(0.1)  # Small delay for real-time effect
        
        # Send completion signal
        await websocket.send_json({
            "type": "complete",
            "data": {"message": "Proof analysis complete"}
        })

@app.websocket("/ws/analyze")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    analyzer = ProofAnalyzer()
    
    try:
        while True:
            # Wait for statement from frontend
            data = await websocket.receive_json()
            statement = data.get("statement", "").strip()
            
            if statement:
                await analyzer.process_proof_bfs(statement, websocket)
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })

@app.get("/")
async def get_index():
    """Serve the main page"""
    return {"message": "Physics Proof Analyzer API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 