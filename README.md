# Universal Language Transcription + Translation

This project converts one supported language into another supported language.

For text translation, it uses a Google-Translate-style web endpoint, so startup is much faster than loading a local AI model.

Audio transcription uses an internet-based speech recognition service and converts uploaded audio to WAV before transcription.

It supports two flows:

1. Text flow: source-language text -> target-language translation
2. Audio flow: source-language speech audio -> source-language transcription -> target-language translation

## Project Idea

Imagine one person writes or speaks in one language, but the listener understands another. This app acts as a language bridge.

Frontend:

- Text box for source text
- Audio upload for source speech
- Source and target language dropdowns
- Translation output panel
- React Native mobile frontend in `mobile-react-native/`

Backend:

- FastAPI REST API
- Google-Translate-style text translation request
- SpeechRecognition for uploaded audio transcription

## Algorithm

Text translation:

1. User selects source and target languages.
2. User enters text.
3. Frontend sends text and language codes to `POST /api/translate`.
4. Backend calls the translation service.
5. Backend returns translated text.
6. Frontend displays the result.

Audio transcription + translation:

1. User selects source and target languages.
2. User uploads source-language audio.
3. Frontend sends audio and language codes to `POST /api/transcribe-translate`.
4. Backend transcribes the speech into text.
5. Backend translates that text into the target language.
6. Frontend displays both the transcript and translation.

## Folder Structure

```text
transcriber/
  backend/
    main.py
    requirements.txt
    services/
      transcriber.py
      translator.py
  frontend/
    index.html
    styles.css
    app.js
  mobile-react-native/
    App.js
    package.json
```

## Setup

Use Python 3.11 or Python 3.12 for this project. Some AI packages do not install correctly on Python 3.14 yet.

Open a terminal in this folder:

```powershell
cd C:\Users\tiyas\OneDrive\Desktop\TIYASHA\transcriber
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r backend\requirements.txt
```

Run the app:

```powershell
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Important Notes

This version needs internet for translation and audio transcription, but it does not download huge AI model files.

## How Language Support Works

Text translation uses the NLLB model language list automatically. When the backend starts and `/api/languages` is called, it reads the model tokenizer and returns the available language codes.

Audio transcription needs a Whisper language name. Common languages are mapped in:

```text
backend/services/languages.py
```

If a language appears as `text only`, text translation works but audio upload is not configured for that source language yet.
