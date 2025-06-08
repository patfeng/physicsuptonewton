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
import random

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
    def __init__(self, statement: str, level: int, parent_id: str = None, goal_statement: str = None):
        self.id = str(uuid.uuid4())
        self.statement = statement
        self.level = level
        self.parent_id = parent_id
        self.dependencies = []
        self.is_elementary = False
        self.proof_text = ""
        self.goal_statement = goal_statement  # The original statement we're trying to prove
        self.path_to_goal = []  # The path from this node to the goal

class ProofAnalyzer:
    def __init__(self):
        self.processed_statements: Set[str] = set()
        self.max_level = 10  # Maximum depth for BFS
        self.max_retries = 3  # Maximum number of retries
        self.base_delay = 1  # Base delay in seconds
        self.nodes = {}  # Store all nodes for path tracking
        
    async def analyze_statement(self, statement: str, parent_node: ProofNode = None) -> Dict:
        """Analyze a statement using OpenAI to determine if it's provable and get dependencies"""
        
        # Get the goal statement and current path from parent node
        goal_statement = parent_node.goal_statement if parent_node else statement
        current_path = parent_node.path_to_goal if parent_node else []
        print(statement)
        print(goal_statement)
        print(current_path)
        print("--------------------------------")

        system_prompt = """
        You are analyzing mathematical and physics statements to build a proof graph.

        Your task is to break down the statement into simpler dependencies that can be used to prove it. The current statement is the node that you are analyzing. The current path represents the nodes that have this statement as a dependency. The goal statement is the statement that the user has asked to prove. You are working downstream from this.
        The dependencies that you provide will be appended to the current path, and then a new request will be made with the new path as the current path.

        Please provide a JSON response with the following structure:
        {{
            "is_provable": boolean,
            "is_elementary": boolean,
            "explanation": "Brief explanation of the statement",
            "dependencies": ["list of simpler statements this depends on"],
            "proof_sketch": "Brief proof, should be rigorous but not too long"
        }}
        
        Guidelines:
        - is_provable: true if this could be proven with current knowledge and is true
        - is_elementary: true if an intelligent 5th grader could understand this with basic explanation, or if it is basic like "conservation of energy".
        - When evaluating the elementaryness of a statement, take into account the goal statement. If the goal is complex, then consider relatively complex statements as elementary, and if the goal is simple, only consider very simple statements as elementary.
        - If the Goal is the same as the Statement, NEVER mark it as elementary. This means that the user is asking you to prove that statement. It is disrespectful to the user to mark it as elementary.
        - dependencies: List up to 4 simpler statements that this depends on (empty if elementary)
        - Keep dependencies very specific to the statement, they should be an exact claim, not a concept.
        - Under NO CIRCUMSTANCES should you provide a vague dependency that is not a direct claim. Dependencies that start with "Understanding of" or "Defintion of" or "Concept of" are considered garbage and will not be tolerated.
        - Make dependencies progressively simpler and easier to understand.
        - Use the current path to goal to inform your choice of dependencies - they should help complete the path to the goal.
        - Paths should not exceed 4 statements. If you see that the current path is beginning to approach 4 statements, be MUCH more liberal with marking statements as elementary.
        """
        def format_prompt(statement, goal_statement, current_path):
            return f"""
            Statement: {statement}
            Goal: {goal_statement}
            Current path: {current_path}
            """
        few_shots = [
            [
                format_prompt("snells law", "snells law", []),
                """{
    "is_provable": true,
    "is_elementary": false,
    "explanation": "n1 sin(theta1) = n2 sin(theta2), where n1 and n2 are the refractive indices of the two media and theta1 and theta2 are the angles of incidence and refraction respectively",
    "dependencies": [
        "Light travels at different speeds in different media",
        "Fermat's principle states light takes the path of least time",
        "Minimizing a function by taking the derivative and setting it to 0"
    ],
    "proof_sketch": "Fermat's principle states that light takes the path of least time between two points. The light must \"balance\" the time it spends in each medium. If it bends the ray too much, it takes a longer path in the slower medium. If it bends too little, it spends too much distance in the slower region. By minimizing the sum of the time traveled in each medium, we can derive Snell's law."
}"""
            ],
            [
                format_prompt("Speed of light varies in different media", "snells law", ["snells law", "Light travels at different speeds in different media"]),
                """{
    "is_provable": true,
    "is_elementary": true,
    "explanation": "Light travels slower in denser media, with speed v = c/n where c is vacuum speed and n is refractive index",
    "dependencies": [],
    "proof_sketch": "This can be demonstrated through experiments measuring light speed in different media, and is a fundamental property of electromagnetic waves in matter."
}"""
            ],
            [
                format_prompt("Formula for the area of a triangle", "pythagorean theorem", ["pythagorean theorem"]),
                """{
    "is_provable": true,
    "is_elementary": true,
    "explanation": "The area of a triangle is 1/2 * base * height",
    "dependencies": [],
    "proof_sketch": "To prove the area of a triangle is 1/2 * base * height: 1) Draw a rectangle with the same base and height as the triangle. 2) The rectangle's area is base * height. 3) The triangle divides the rectangle into two equal parts. 4) Therefore, the triangle's area must be half of the rectangle's area."
}"""
            ],
            [
                format_prompt("1+2=3", "1+2=3", []),
                """{
    "is_provable": true,
    "is_elementary": false,
    "explanation": "1+2=3 is a basic mathematical statement that can be proven by adding 1 and 2",
    "dependencies": ["adding 2 numbers"],
    "proof_sketch": "1+1=2, 2+1=3, therefore 1+2=3"
}"""
            ]
        ]
        
        for attempt in range(self.max_retries):
            try:
                constructed_prompt = [{"role": "system", "content": system_prompt}]
                for shot in few_shots:
                    constructed_prompt.append({"role": "user", "content": shot[0]})
                    constructed_prompt.append({"role": "assistant", "content": shot[1]})
                constructed_prompt.append({"role": "user", "content": format_prompt(statement, goal_statement, current_path)})
                
                response = await client.chat.completions.create(
                    model="gpt-4",
                    messages=constructed_prompt,
                    temperature=0.3
                )
                
                content = response.choices[0].message.content
                # Try to extract JSON from the response
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                
                result = json.loads(content)
                return result
                
            except Exception as e:
                if attempt == self.max_retries - 1:  # Last attempt
                    print(f"Error analyzing statement after {self.max_retries} attempts: {e}")
                    return {
                        "is_provable": True,
                        "is_elementary": False,
                        "explanation": "Analysis failed after multiple retries",
                        "dependencies": [],
                        "proof_sketch": "Unable to analyze"
                    }
                
                # Calculate delay with exponential backoff and jitter
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed, retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)

    async def process_proof_bfs(self, initial_statement: str, websocket: WebSocket):
        """Process proof using BFS to break down dependencies"""
        
        # Initialize the queue with the root statement
        queue = deque()
        root_node = ProofNode(initial_statement, 0, goal_statement=initial_statement)
        self.nodes[root_node.id] = root_node
        queue.append(root_node)
        
        # Send the root node
        await websocket.send_json({
            "type": "node",
            "data": {
                "id": root_node.id,
                "statement": root_node.statement,
                "level": root_node.level,
                "parent_id": None,
                "is_elementary": False,
                "goal_statement": root_node.goal_statement,
                "path_to_goal": root_node.path_to_goal
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
                    task = self.analyze_statement(node.statement, node)
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
                    self.nodes[node.id] = node
                    
                    # Send updated node info
                    await websocket.send_json({
                        "type": "node_update",
                        "data": {
                            "id": node.id,
                            "is_elementary": node.is_elementary,
                            "proof_text": node.proof_text,
                            "explanation": result.get("explanation", ""),
                            "goal_statement": node.goal_statement,
                            "path_to_goal": node.path_to_goal
                        }
                    })
                    
                    # Create child nodes for dependencies if not elementary
                    if not node.is_elementary and result.get("dependencies"):
                        for dep in result["dependencies"]:
                            if dep.strip() and dep not in self.processed_statements:
                                # Create new path by adding current statement to parent's path
                                new_path = node.path_to_goal + [node.statement]
                                
                                child_node = ProofNode(
                                    dep.strip(), 
                                    node.level + 1, 
                                    node.id,
                                    goal_statement=node.goal_statement
                                )
                                child_node.path_to_goal = new_path
                                
                                node.dependencies.append(child_node.id)
                                self.nodes[child_node.id] = child_node
                                queue.append(child_node)
                                
                                # Send child node
                                await websocket.send_json({
                                    "type": "node",
                                    "data": {
                                        "id": child_node.id,
                                        "statement": child_node.statement,
                                        "level": child_node.level,
                                        "parent_id": child_node.parent_id,
                                        "is_elementary": False,
                                        "goal_statement": child_node.goal_statement,
                                        "path_to_goal": child_node.path_to_goal
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