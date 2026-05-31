import tempfile
import subprocess
from pathlib import Path
from os import unlink

import imageio_ffmpeg
import speech_recognition as sr


def transcribe_audio(audio_bytes: bytes, original_filename: str, whisper_language: str) -> str:
    suffix = Path(original_filename).suffix or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as source_audio:
        source_audio.write(audio_bytes)
        source_audio_path = source_audio.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as converted_audio:
        converted_audio_path = converted_audio.name

    try:
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-i",
                source_audio_path,
                "-ar",
                "16000",
                "-ac",
                "1",
                converted_audio_path,
            ],
            check=True,
            capture_output=True,
        )

        recognizer = sr.Recognizer()
        with sr.AudioFile(converted_audio_path) as source:
            recording = recognizer.record(source)

        return recognizer.recognize_google(recording, language=whisper_language).strip()
    finally:
        for path in (source_audio_path, converted_audio_path):
            try:
                unlink(path)
            except FileNotFoundError:
                pass
