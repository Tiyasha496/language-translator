import re


PHRASES = {
    "kire ki korchis": "Hey, what are you doing?",
    "kire ki korcho": "Hey, what are you doing?",
    "ki korchis": "What are you doing?",
    "ki korcho": "What are you doing?",
    "kemon achis": "How are you?",
    "kemon acho": "How are you?",
    "ami bhalo achi": "I am fine.",
    "tui kothay": "Where are you?",
    "tumi kothay": "Where are you?",
    "ami tomake bhalobashi": "I love you.",
    "dhonnobad": "Thank you.",
}

WORDS = {
    "ami": "I",
    "tumi": "you",
    "tui": "you",
    "apni": "you",
    "ki": "what",
    "kire": "hey",
    "kothay": "where",
    "keno": "why",
    "kokhon": "when",
    "bhalo": "good",
    "kharap": "bad",
    "achi": "am",
    "acho": "are",
    "achis": "are",
    "korchi": "am doing",
    "korcho": "are doing",
    "korchis": "are doing",
    "khabo": "will eat",
    "khabar": "food",
    "pani": "water",
    "jol": "water",
    "bari": "home",
    "school": "school",
    "college": "college",
}


def looks_like_roman_bengali(text: str) -> bool:
    if re.search(r"[\u0980-\u09ff]", text):
        return False

    normalized = normalize_roman_text(text)
    return any(phrase in normalized for phrase in PHRASES) or any(
        word in WORDS for word in normalized.split()
    )


def normalize_roman_text(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"[^a-z\s]", " ", normalized)
    normalized = re.sub(r"(.)\1{2,}", r"\1", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def roman_bengali_to_english(text: str) -> str:
    normalized = normalize_roman_text(text)

    for phrase, meaning in PHRASES.items():
        if phrase in normalized:
            return meaning

    translated_words = [WORDS.get(word, word) for word in normalized.split()]
    translated = " ".join(translated_words).strip()

    return translated or text

