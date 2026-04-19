"""FastAPI application, HTTP routes, WebSocket endpoint, and static file serving."""

import asyncio
import json
import os
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import meet_assistant.state as state
from meet_assistant.engines import AVAILABLE_ENGINES

app = FastAPI()

_web_dir = os.path.dirname(__file__)
_dist_dir = os.path.join(_web_dir, "dist")
_src_dir = os.path.join(_web_dir, "src")
_static_dir = _dist_dir if os.path.isdir(_dist_dir) else _src_dir

if os.path.isdir(os.path.join(_static_dir, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(_static_dir, "assets")), name="assets")


@app.on_event("startup")
async def startup():
    state.loop = asyncio.get_event_loop()


@app.get("/")
async def index():
    html_path = os.path.join(_static_dir, "index.html")
    return HTMLResponse(open(html_path).read())


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.clients.add(websocket)
    await websocket.send_json({
        "type": "init",
        "engine": state.current_engine_name,
        "engines": AVAILABLE_ENGINES,
        "language": state.current_language,
        "languages": state.SUPPORTED_LANGUAGES,
        "serverCapture": state.server_capture,
    })
    try:
        while True:
            msg = await websocket.receive()
            if "text" in msg:
                data = json.loads(msg["text"])
                action = data.get("action")
                if action == "set_language":
                    state.set_language(data.get("language"))
                elif action == "reset_speakers":
                    state.reset_speakers()
            elif "bytes" in msg:
                raw = msg["bytes"]
                if len(raw) > 44:
                    threading.Thread(
                        target=state.transcribe_browser_audio,
                        args=(bytes(raw),),
                        daemon=True,
                    ).start()
    except WebSocketDisconnect:
        state.clients.discard(websocket)
