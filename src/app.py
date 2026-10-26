import os
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from src.pipeline.config import MAX_TEXT_LENGTH
from src.service.extractor import ner_service

app = FastAPI(
    title="Article Named-Entity Recognition Service",
    description="Layanan ekstraksi entitas bernama (NER) dari judul dan isi artikel berita.",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Permintaan tidak valid: format JSON cacat atau field bukan string."}
    )

@app.post("/extract-entities", status_code=status.HTTP_200_OK)
async def extract_entities_endpoint(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Format JSON tidak valid (malformed JSON)."}
        )

    if not isinstance(payload, dict) or "title" not in payload or "body" not in payload:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "JSON wajib memiliki field 'title' dan 'body'."}
        )

    title = payload.get("title")
    body = payload.get("body")

    if not isinstance(title, str) or not isinstance(body, str):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Field 'title' dan 'body' keduanya harus bertipe string."}
        )

    t_clean = title.strip()
    b_clean = body.strip()

    if not t_clean and not b_clean:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Judul (title) dan isi artikel (body) tidak boleh sama-sama kosong."}
        )

    combined_len = len(f"{t_clean}. {b_clean}" if (t_clean and b_clean) else (t_clean or b_clean))
    if combined_len > MAX_TEXT_LENGTH:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Panjang teks gabungan melebihi batas maksimum {MAX_TEXT_LENGTH} karakter."}
        )

    return ner_service.analyze(title, body)

@app.get("/")
async def serve_panel():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(base_dir, "static", "index.html"))
