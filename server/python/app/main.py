from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import settings
from .security import create_access_token, hash_password, verify_password

app = FastAPI(title=settings.app_name, version=settings.version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Temporary in-process repository. The next repository layer maps these records
# to the MySQL schema in db/migrations/002_auth_projects.sql.
_USERS: dict[str, dict] = {}
_PROJECTS: dict[str, dict] = {}
_JOBS: dict[str, dict] = {}


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=512)
    client_id: str = Field(default="browser", max_length=128)
    platform: str = Field(default="browser", max_length=32)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    visibility: str = "private"


@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": settings.version}


@app.get("/api/v1/about")
async def about() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "developer": settings.developer,
        "role": "Public research API and orchestration layer",
        "platforms": ["windows", "macos", "linux"],
        "clients": ["desktop", "browser"],
        "protocols": ["HTTPS", "WSS"],
    }


@app.post("/api/v1/auth/register")
async def register(request: LoginRequest) -> dict:
    if request.username in _USERS:
        raise HTTPException(status_code=409, detail="Username already exists")
    user_id = str(uuid4())
    session_id = str(uuid4())
    _USERS[request.username] = {
        "id": user_id,
        "username": request.username,
        "display_name": request.username,
        "password_hash": hash_password(request.password),
        "roles": ["researcher"],
    }
    token = create_access_token(user_id, session_id)
    safe_user = {key: value for key, value in _USERS[request.username].items() if key != "password_hash"}
    return {"access_token": token, "token_type": "bearer", "session_id": session_id, "user": safe_user}


@app.post("/api/v1/auth/login")
async def login(request: LoginRequest) -> dict:
    user = _USERS.get(request.username)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session_id = str(uuid4())
    token = create_access_token(user["id"], session_id)
    safe_user = {key: value for key, value in user.items() if key != "password_hash"}
    return {"access_token": token, "token_type": "bearer", "session_id": session_id, "user": safe_user}


@app.get("/api/v1/projects")
async def projects() -> dict:
    return {"items": list(_PROJECTS.values())}


@app.post("/api/v1/projects")
async def create_project(project: ProjectCreate) -> dict:
    project_id = str(uuid4())
    record = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "visibility": project.visibility,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _PROJECTS[project_id] = record
    return record


@app.get("/api/v1/jobs")
async def jobs() -> dict:
    return {"items": list(_JOBS.values())}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"message_type": "server.connected", "timestamp": datetime.now(timezone.utc).isoformat()})
    try:
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({
                "message_type": "server.ack",
                "request_id": message.get("request_id"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {"received": True},
            })
    except WebSocketDisconnect:
        return
