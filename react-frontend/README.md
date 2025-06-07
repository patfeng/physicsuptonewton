# Physics Up To Newton - React Frontend

This is a React-based frontend for the Physics Up To Newton proof analyzer application. It provides an interactive visualization of mathematical and physics proofs that could have been understood during Newton's time.

## Features

- **Interactive Proof Visualization**: Visual graph showing the dependency tree of mathematical proofs
- **Real-time WebSocket Connection**: Live updates as the AI analyzes statements
- **Node Details**: Click on any node to see detailed explanations and proofs
- **Responsive Design**: Works on desktop and mobile devices
- **Animated Interactions**: Smooth animations for node appearances and interactions

## Installation

1. Navigate to the react-frontend directory:
   ```bash
   cd react-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

1. Start the development server:
   ```bash
   npm start
   ```

2. The application will open in your browser at `http://localhost:3000`

## Building for Production

To create a production build:

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
src/
├── App.js              # Main application component
├── App.css             # Global styles
├── index.js            # Application entry point
└── components/
    ├── ProofGraph.js   # Main visualization component
    ├── Node.js         # Individual node component
    ├── Connection.js   # Connection line component
    ├── Sidebar.js      # Details sidebar component
    └── StatusBar.js    # Status and progress component
```

## How It Works

1. **Statement Input**: Enter a mathematical or physics statement in the text area
2. **WebSocket Connection**: The app connects to the backend WebSocket endpoint at `/ws/analyze`
3. **Real-time Visualization**: As the AI processes the statement, nodes appear in a radial layout
4. **Interactive Exploration**: Click nodes to see detailed proofs and explanations
5. **Responsive Layout**: The visualization adapts to different screen sizes

## Key React Features Used

- **Hooks**: useState, useEffect, useRef, useCallback for state management
- **Component Architecture**: Modular components for maintainability
- **WebSocket Integration**: Real-time communication with the backend
- **Dynamic Styling**: CSS classes and inline styles for animations
- **Event Handling**: User interactions and keyboard shortcuts

## Differences from Original

This React version maintains all the functionality of the original vanilla JavaScript version while providing:

- Better state management with React hooks
- Component-based architecture for maintainability
- More predictable re-rendering behavior
- Better separation of concerns
- Easier testing and debugging

## Backend Integration

This frontend expects a WebSocket server running at `/ws/analyze` that handles:

- `node` messages: New proof nodes to display
- `node_update` messages: Updates to existing nodes with proofs/explanations
- `complete` messages: Analysis completion
- `error` messages: Error handling

The frontend sends JSON messages with the statement to analyze:
```json
{
  "statement": "The sum of angles in a triangle equals 180 degrees"
}
``` 