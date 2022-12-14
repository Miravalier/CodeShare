from __future__ import annotations

import c_tools
import os
import statics
import hashlib
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from database import db
from utils import random_id
from hmac import compare_digest
from typing import Dict, Set


BASE_URL = os.environ.get("BASE_URL", "")
ADMIN_HASH = hashlib.sha256(os.environ.get("ADMIN_TOKEN", "").encode()).digest()


DOCUMENT_SUBSCRIBERS: Dict[str, Set[WebSocket]] = {}


app = FastAPI()


class JsonError(Exception):
    pass


@app.exception_handler(JsonError)
async def json_error_handler(request: Request, exc: JsonError):
    return JSONResponse(status_code=401, content={
        "status": "error",
        "reason": str(exc)
    })


class CListRequest(BaseModel):
    admin_token: str


@app.post("/list/c")
async def list_c(request: CListRequest):
    request_hash = hashlib.sha256(request.admin_token.encode()).digest()
    if not compare_digest(ADMIN_HASH, request_hash):
        raise JsonError("Invalid Admin Key")
    if not db.documents.c:
        db.documents.c = set()
    return {"status": "success", "documents": list(db.documents.c)}


class CCreateRequest(BaseModel):
    admin_token: str


@app.post("/create/c")
async def create_c(request: CCreateRequest):
    request_hash = hashlib.sha256(request.admin_token.encode()).digest()
    if not compare_digest(ADMIN_HASH, request_hash):
        raise JsonError("Invalid Admin Key")
    if not db.documents.c:
        db.documents.c = set()
    id = random_id()
    db.documents.c.add(id)
    db.save()
    return {"status": "success", "document": id}


@app.get("/editor/c/{document_id}")
async def editor_c(document_id: str):
    if not db.documents.c:
        db.documents.c = set()
    if document_id not in db.documents.c:
        raise JsonError("Invalid Document ID")
    return HTMLResponse(statics.apply_parameters(statics.C_EDITOR_HTML, {"document_id": document_id}))


class CRunRequest(BaseModel):
    document_id: str
    contents: str


@app.post("/run/c")
async def run_c(request: CRunRequest):
    if not db.documents.c:
        db.documents.c = set()
    if request.document_id not in db.documents.c:
        raise JsonError("Invalid Document ID")

    if request.document_id not in DOCUMENT_SUBSCRIBERS:
        DOCUMENT_SUBSCRIBERS[request.document_id] = set()

    compile_success, output, exe_path = await c_tools.compile(request.contents)
    if compile_success:
        run_success, output = await c_tools.run(exe_path)
        response = {"status": "success", "compile": True, "run": run_success, "output": output.decode()}
    else:
        response = {"status": "success", "compile": False, "run": False, "output": output.decode()}

    for websocket in tuple(DOCUMENT_SUBSCRIBERS[request.document_id]):
        try:
            await websocket.send_json(response)
        except:
            DOCUMENT_SUBSCRIBERS[request.document_id].discard(websocket)
    return response


@app.websocket("/subscribe/c/{document_id}")
async def subscribe_c(websocket: WebSocket, document_id: str):
    await websocket.accept()
    if document_id not in DOCUMENT_SUBSCRIBERS:
        DOCUMENT_SUBSCRIBERS[document_id] = set()
    DOCUMENT_SUBSCRIBERS[document_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        DOCUMENT_SUBSCRIBERS[document_id].discard(websocket)


@app.on_event("shutdown")
async def shutdown():
    print("Saving database ...")
    db.save()
