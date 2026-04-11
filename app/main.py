from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .game import GameManager
from .question_bank import QuestionBank, QuestionBankError


BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"
QUESTION_BANK_PATH = BASE_DIR / "data" / "questions.json"

question_bank = QuestionBank(QUESTION_BANK_PATH)
manager = GameManager(question_bank)

app = FastAPI(title="Code Clash")


@app.on_event("startup")
async def startup() -> None:
    question_bank.load()
    manager.start_cleanup()


@app.get("/api/health")
async def health() -> dict[str, object]:
    return {"ok": True, "bank": question_bank.stats()}


@app.post("/api/admin/reload-questions")
async def reload_questions(x_admin_token: str | None = Header(default=None)) -> JSONResponse:
    admin_token = os.environ.get("ADMIN_TOKEN")
    if admin_token and x_admin_token != admin_token:
        return JSONResponse({"ok": False, "error": "Invalid admin token."}, status_code=403)

    try:
        stats = await manager.reload_questions()
    except (QuestionBankError, json.JSONDecodeError) as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    return JSONResponse({"ok": True, "bank": stats})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    conn = await manager.register(websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            if isinstance(payload, dict):
                await manager.handle(conn, payload)
            else:
                await manager.send_error(conn, "Messages must be JSON objects.")
    except WebSocketDisconnect:
        await manager.disconnect(conn)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/room/{room_id}")
async def room(room_id: str) -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
