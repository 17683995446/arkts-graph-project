
import os
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

import database
from file_monitor import FileMonitorService
from llm_handler import LLMQueryHandler

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'example_project'))
DEBOUNCE_MS = 1000

monitor_service: FileMonitorService | None = None
llm_handler: LLMQueryHandler | None = None
active_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global monitor_service, llm_handler
    database.init_database()
    
    monitor_service = FileMonitorService(PROJECT_PATH, DEBOUNCE_MS)
    llm_handler = LLMQueryHandler()
    
    def status_callback(type: str, payload: Any):
        asyncio.create_task(broadcast_status(type, payload))
    
    monitor_service.start(status_callback)
    monitor_service.initial_sync()
    
    yield
    
    if monitor_service:
        monitor_service.stop()
    if llm_handler:
        await llm_handler.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

async def broadcast_status(type: str, payload: Any):
    for connection in active_connections:
        try:
            await connection.send_json({"type": type, "payload": payload})
        except Exception:
            pass

@app.get("/")
async def get_index():
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
    index_path = os.path.join(frontend_path, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "ArkTS Knowledge Graph API"}

@app.get("/api/files")
async def get_files():
    return database.get_all_files()

@app.get("/api/classes")
async def get_classes():
    return database.get_all_classes()

@app.get("/api/methods")
async def get_methods():
    return database.get_all_methods()

@app.get("/api/calls")
async def get_calls():
    return database.get_all_calls()

@app.get("/api/components")
async def get_components():
    return database.get_all_components()

@app.post("/api/query")
async def natural_language_query(request: QueryRequest):
    if not llm_handler:
        return {"sql": "", "result": []}
    
    sql = await llm_handler.natural_language_to_sql(request.question)
    try:
        result = database.execute_custom_query(sql)
        return {"sql": sql, "result": result}
    except Exception as e:
        return {"sql": sql, "result": [], "error": str(e)}

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
