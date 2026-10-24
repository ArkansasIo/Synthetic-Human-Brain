"""Verify WebSocket rejection behaviour (error 1006/1008 fix)."""

import asyncio
import json
import sys

import httpx
import websockets

BASE = "http://127.0.0.1:8787"
WS = "ws://127.0.0.1:8787"


async def main() -> None:
    token = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json={"username": "researcher1", "password": "TestPass123!"},
    ).json()["access_token"]

    # 1. Valid token → accepted, greeting received.
    async with websockets.connect(f"{WS}/ws?token={token}") as ws:
        greeting = json.loads(await ws.recv())
        payload = greeting.get("payload", greeting)
        kind = greeting.get("type") or payload.get("type") or ("connected" if "session_id" in greeting else greeting)
        print("1. valid token: accepted, greeting =", kind)

    # 2. Garbage token → readable rejection message, not a bare 1008.
    try:
        async with websockets.connect(f"{WS}/ws?token=garbage") as ws:
            message = json.loads(await ws.recv())
            print("2. garbage token: rejected with detail =", message.get("detail"))
    except websockets.exceptions.ConnectionClosed as exc:
        print("2. garbage token: closed", exc.code, "reason:", exc.reason)

    # 3. No token → readable rejection.
    try:
        async with websockets.connect(f"{WS}/ws") as ws:
            message = json.loads(await ws.recv())
            print("3. no token: rejected with detail =", message.get("detail"))
    except websockets.exceptions.ConnectionClosed as exc:
        print("3. no token: closed", exc.code, "reason:", exc.reason)

    # 4. Hardware stream with unknown device → readable rejection.
    try:
        async with websockets.connect(f"{WS}/ws/hardware/no-such-device?token={token}") as ws:
            message = json.loads(await ws.recv())
            print("4. unknown device: rejected with detail =", message.get("detail"))
    except websockets.exceptions.ConnectionClosed as exc:
        print("4. unknown device: closed", exc.code, "reason:", exc.reason)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
