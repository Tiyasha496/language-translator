import html

import requests
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

from backend.services.roman_bengali import (
    looks_like_roman_bengali,
    roman_bengali_to_english,
)


GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


def translate_text(text: str, source_language_code: str, target_language_code: str) -> str:
    if source_language_code == "bn-rom" or (
        source_language_code == "bn" and looks_like_roman_bengali(text)
    ):
        english_text = roman_bengali_to_english(text)

        if target_language_code == "en":
            return english_text

        return translate_text(english_text, "en", target_language_code)

    if source_language_code == "bn-rom":
        source_language_code = "bn"

    response = requests.get(
        GOOGLE_TRANSLATE_URL,
        params={
            "client": "gtx",
            "sl": source_language_code,
            "tl": target_language_code,
            "dt": "t",
            "q": text,
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    translated_chunks = [chunk[0] for chunk in data[0] if chunk and chunk[0]]

    return html.unescape("".join(translated_chunks))
