# Physics Before Newton - Proof Analyzer

A web application that analyzes mathematical and physics statements from the pre-Newtonian era (before 1727) by breaking them down into fundamental dependencies using AI. The system uses OpenAI's GPT-4 to recursively decompose complex statements into simpler ones until they reach a level understandable by a 5th grader.

## Features

- **Real-time Analysis**: Stream analysis results as nodes appear radially from the center
- **Recursive Dependency Breakdown**: Uses BFS (Breadth-First Search) to systematically analyze dependencies
- **Parallel Processing**: Multiple OpenAI API calls run simultaneously for efficiency
- **Interactive Visualization**: Click nodes to see detailed proofs and explanations
- **Historical Context**: Focuses on knowledge that could be proven before Newton's time
- **Visual Hierarchy**: Elementary concepts are highlighted in green

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Modern web browser with WebSocket support

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>  # or download the files
   cd physicsbeforenewton
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key**
   - Copy `env_example.txt` to `.env`
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   - Get an API key from: https://platform.openai.com/api-keys

4. **Run the server**
   ```bash
   cd backend
   python main.py
   ```

5. **Access the application**
   - Open your browser and go to: http://localhost:8000/static/index.html
   - Or use the API endpoints directly

## Usage

1. **Enter a Statement**: Type a mathematical or physics statement that could be proven before Newton's time (1727)

2. **Examples to try**:
   - "The sum of angles in a triangle equals 180 degrees"
   - "The area of a circle is π times the radius squared"
   - "The Pythagorean theorem: a² + b² = c²"
   - "Objects fall at the same rate regardless of their weight"
   - "Parallel lines never meet"

3. **Watch the Analysis**: Nodes will appear in real-time, radiating outward from your original statement

4. **Explore Dependencies**: Click on any node to see detailed explanations and proofs

5. **Color Coding**:
   - **Purple**: Original statement (center)
   - **Blue**: Complex statements being analyzed
   - **Green**: Elementary statements (5th grade level)

## Architecture

### Backend (Python/FastAPI)
- **WebSocket Connection**: Real-time streaming of analysis results
- **BFS Algorithm**: Systematic exploration of statement dependencies
- **OpenAI Integration**: GPT-4 analysis of mathematical/physics statements
- **Parallel Processing**: Multiple AI requests processed simultaneously

### Frontend (HTML/CSS/JavaScript)
- **Radial Visualization**: D3-like positioning without the library overhead
- **Real-time Updates**: WebSocket client for live data streaming
- **Interactive UI**: Click nodes for detailed information
- **Responsive Design**: Works on desktop and mobile devices

### Key Components

1. **ProofAnalyzer Class**: Core logic for statement analysis and BFS traversal
2. **ProofNode Class**: Data structure representing each statement in the proof tree
3. **ProofVisualizer Class**: Frontend visualization and interaction handling
4. **WebSocket Endpoint**: Real-time communication between frontend and backend

## API Endpoints

- `GET /`: Basic API information
- `WebSocket /ws/analyze`: Real-time proof analysis endpoint

### WebSocket Message Format

**Send to server**:
```json
{
  "statement": "Your mathematical statement here"
}
```

**Receive from server**:
```json
{
  "type": "node|node_update|complete|error",
  "data": {
    "id": "node-uuid",
    "statement": "The statement text",
    "level": 0,
    "parent_id": "parent-uuid",
    "is_elementary": false,
    "explanation": "AI explanation",
    "proof_text": "Proof details"
  }
}
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Customizable Parameters
- **Max Depth**: Change `self.max_level` in ProofAnalyzer class
- **Radial Distances**: Modify `levelRadius` array in ProofVisualizer
- **Concurrent Tasks**: Adjust limit in `process_proof_bfs` method

## Historical Context

The system focuses on mathematical and physics knowledge that would have been available before Isaac Newton's death in 1727. This includes:

- Classical geometry (Euclid, Archimedes)
- Basic algebra and arithmetic
- Observational astronomy (Kepler's laws)
- Simple mechanics and statics
- Classical optics
- Early calculus concepts

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if the server is running on port 8000
   - Verify no firewall blocking the connection

2. **OpenAI API Errors**
   - Verify your API key is correct in the .env file
   - Check your OpenAI account has sufficient credits
   - Ensure you have access to GPT-4 model

3. **No Nodes Appearing**
   - Check browser console for JavaScript errors
   - Verify WebSocket connection in browser dev tools
   - Check server logs for analysis errors

4. **Slow Analysis**
   - This is normal - AI analysis takes time
   - Multiple parallel requests are already optimized
   - Consider reducing max_level for faster results

## Development

### Adding New Features

1. **New Analysis Models**: Modify the prompt in `analyze_statement` method
2. **Different Visualizations**: Extend the ProofVisualizer class
3. **Additional Endpoints**: Add new FastAPI routes in main.py

### Testing

Test with various types of statements:
- Pure mathematics (geometry, algebra)
- Physics principles (mechanics, optics)
- Edge cases (very simple or complex statements)

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This application uses OpenAI's GPT-4 API, which requires an API key and may incur costs based on usage. Please monitor your OpenAI usage and set appropriate limits. 