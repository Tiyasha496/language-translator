from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from services.languages import (
    get_language_name,
    get_language_options,
    get_whisper_language,
    is_supported_language,
)
from services.transcriber import transcribe_audio
from services.translator import translate_text as run_translation


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI(title="Universal Language Translator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/languages")
def list_languages():
    return {"languages": get_language_options()}


@app.post("/api/translate")
def translate_text_route(payload: TranslationRequest):
    input_text = payload.text.strip()

    if not input_text:
        raise HTTPException(status_code=400, detail="Please enter text.")

    if not is_supported_language(payload.source_language):
        raise HTTPException(status_code=400, detail="Unsupported source language.")

    if not is_supported_language(payload.target_language):
        raise HTTPException(status_code=400, detail="Unsupported target language.")

    if payload.target_language == "auto":
        raise HTTPException(status_code=400, detail="Please choose a target language.")

    translated_text = run_translation(
        input_text,
        payload.source_language,
        payload.target_language,
    )

    return {
        "source_language": get_language_name(payload.source_language),
        "target_language": get_language_name(payload.target_language),
        "input_text": input_text,
        "translated_text": translated_text,
    }


@app.post("/api/transcribe-translate")
async def transcribe_and_translate_audio(
    source_language: str = Form(...),
    target_language: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Please upload an audio file.")

    if not is_supported_language(source_language):
        raise HTTPException(status_code=400, detail="Unsupported source language.")

    if not is_supported_language(target_language):
        raise HTTPException(status_code=400, detail="Unsupported target language.")

    if target_language == "auto":
        raise HTTPException(status_code=400, detail="Please choose a target language.")

    audio_bytes = await file.read()
    whisper_language = get_whisper_language(source_language)

    if whisper_language is None:
        raise HTTPException(
            status_code=400,
            detail="Audio transcription is not available for this source language.",
        )

    try:
        transcript = transcribe_audio(
            audio_bytes,
            file.filename or "audio",
            whisper_language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Could not transcribe this audio file: {exc}",
        ) from exc

    if not transcript.strip():
        raise HTTPException(status_code=422, detail="Could not transcribe the audio.")

    translated_text = run_translation(transcript, source_language, target_language)

    return {
        "source_language": get_language_name(source_language),
        "target_language": get_language_name(target_language),
        "transcript": transcript,
        "translated_text": translated_text,
    }
