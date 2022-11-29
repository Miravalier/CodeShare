from __future__ import annotations

import c_tools
import os
import statics
import hashlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from database import db
from utils import random_id
from hmac import compare_digest


BASE_URL = os.environ.get("BASE_URL", "")
ADMIN_HASH = hashlib.sha256(os.environ.get("ADMIN_TOKEN", "").encode()).digest()


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

    success, output, exe_path = c_tools.compile(request.contents)
    if not success:
        return {"status": "success", "compile": False, "run": False, "output": output}

    success, output = c_tools.run(exe_path)
    return {"status": "success", "compile": True, "run": success, "output": output}


@app.on_event("shutdown")
async def shutdown():
    print("Saving database ...")
    db.save()
