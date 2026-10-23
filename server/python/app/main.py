from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

APP_NAME = "Synthetic Human Brain Research Server"
APP_VERSION = "0.1.0-alpha"
DEVELOPER = "ArkansasIo"

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("WEB_CLIENT_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    authenticated: bool
    username: str
    message: str


class JobRequest(BaseModel):
    operation: str
    payload: dict = {}


@app.get("/api/v1/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "synthetic-brain-python-api",
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/about")
async def about() -> dict:
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "developer": DEVELOPER,
        "role": "Public research API and orchestration layer",
        "platforms": ["windows", "macos", "linux"],
        "clients": ["desktop", "browser"],
    }


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    # Development endpoint only. Production authentication must use the MySQL
    # users table, Argon2id password hashes, sessions, RBAC and TLS.
    if not request.username or not request.password:
        return LoginResponse(authenticated=False, username=request.username, message="Credentials required")
    return LoginResponse(authenticated=False, username=request.username, message="Authentication service not configured")


@app.get("/api/v1/projects")
async def projects() -> dict:
    return {"items": [], "message": "Project repository is ready for database integration"}


@app.get("/api/v1/experiments")
async def experiments() -> dict:
    return {"items": []}


@app.post("/api/v1/jobs")
async def submit_job(request: JobRequest) -> dict:
    return {"accepted": True, "operation": request.operation, "payload": request.payload}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "connected", "service": "synthetic-brain-python-api"})
    while True:
        message = await websocket.receive_json()
        await websocket.send_json({"type": "ack", "message": message})
