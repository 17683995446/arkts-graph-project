
# ArkTS Knowledge Graph

A dynamic, real-time code analysis and visualization system for HarmonyOS ArkTS applications.

## Features

- **Real-time File Monitoring**: Automatically detects changes to ArkTS files
- **Incremental Updates**: Only processes changed files for optimal performance
- **SQLite Database**: Persistent storage of code analysis results
- **Interactive Visualization**: Beautiful, modern UI for exploring your codebase
- **Natural Language Query**: Ask questions about your code using plain English
- **WebSocket Updates**: Real-time UI updates as your code changes

## Tech Stack

### Backend
- Python 3.9+
- FastAPI
- SQLite
- watchdog (file watching)

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Lucide Icons

## Quick Start

### Prerequisites

Make sure you have the following installed:
- Python 3.9+
- Node.js 18+
- npm or yarn or pnpm

### Installation

1. **Install Backend Dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**

   ```bash
   cd frontend
   npm install
   ```

3. **Build Frontend**

   ```bash
   cd frontend
   npm run build
   ```

### Running the Application

1. **Start the Backend Server**

   ```bash
   cd backend
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open the Application**

   Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Project Structure

```
.
├── backend/                # Python backend
│   ├── main.py           # FastAPI application entry
│   ├── database.py       # SQLite database operations
│   ├── arkts_analyzer.py # ArkTS file parser
│   ├── file_monitor.py   # File system monitor
│   ├── llm_handler.py    # LLM query handler
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── api.ts        # API hooks
│   │   ├── types.ts      # TypeScript types
│   │   └── App.tsx       # Main app component
│   └── package.json
├── example_project/      # Example ArkTS files for testing
│   ├── Index.ets
│   └── GreetingCard.ets
└── README.md
```

## Usage

### Monitoring a Project

By default, the system monitors the `../example_project` directory. To monitor your own project, modify the `PROJECT_PATH` in `backend/main.py`.

### Exploring the UI

1. **Home**: Overview of the system and quick stats
2. **Graph**: Explore files, classes, and methods
3. **Architecture**: View system design and architecture
4. **Process**: Learn about the update workflow
5. **Status**: Real-time monitoring and status updates
6. **Query**: Ask questions about your codebase in natural language

### Design Principles

- **Atomic File Updates**: Each file is updated independently
- **Incremental Processing**: Only changed files are re-analyzed
- **Delete + Re-insert**: Simplified updates over complex diffing
- **Debounced Processing**: Batch rapid changes for efficiency

## Database Schema

The SQLite database contains the following tables:

- **files**: Source file metadata
- **classes**: Class/struct definitions
- **methods**: Function/method definitions
- **calls**: Method call relationships
- **components**: Component nesting relationships

## API Endpoints

- `GET /api/files`: Retrieve all files
- `GET /api/classes`: Retrieve all classes
- `GET /api/methods`: Retrieve all methods
- `GET /api/calls`: Retrieve call relationships
- `GET /api/components`: Retrieve component relationships
- `POST /api/query`: Natural language query
- `WebSocket /ws/status`: Real-time status updates

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

For frontend development with hot reload:

```bash
cd frontend
npm run dev
```

Note: You'll need to update the API base URL in `frontend/src/api.ts` to point to the backend server during development.

## License

MIT License - feel free to use this for your own projects!
