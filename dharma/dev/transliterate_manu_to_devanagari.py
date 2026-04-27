#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / "dharma" / "manu.txt"
TARGET_PATH = REPO_ROOT / "dharma" / "dev" / "manu_dev.txt"


INDEPENDENT_VOWELS = {
    "aa": "आ",
    "ii": "ई",
    "uu": "ऊ",
    "ai": "ऐ",
    "au": "औ",
    "RR": "ॠ",
    "lRR": "ॡ",
    "lR": "ऌ",
    "A": "आ",
    "I": "ई",
    "U": "ऊ",
    "R": "ऋ",
    "e": "ए",
    "o": "ओ",
    "a": "अ",
    "i": "इ",
    "u": "उ",
}

VOWEL_SIGNS = {
    "aa": "ा",
    "ii": "ी",
    "uu": "ू",
    "ai": "ै",
    "au": "ौ",
    "RR": "ॄ",
    "lRR": "ॣ",
    "lR": "ॢ",
    "A": "ा",
    "I": "ी",
    "U": "ू",
    "R": "ृ",
    "e": "े",
    "o": "ो",
    "a": "",
    "i": "ि",
    "u": "ु",
}

CONSONANTS = {
    "kh": "ख",
    "gh": "घ",
    "ch": "छ",
    "jh": "झ",
    "Th": "ठ",
    "Dh": "ढ",
    "th": "थ",
    "dh": "ध",
    "ph": "फ",
    "bh": "भ",
    "k": "क",
    "g": "ग",
    "G": "ङ",
    "c": "च",
    "j": "ज",
    "J": "ञ",
    "T": "ट",
    "D": "ड",
    "N": "ण",
    "t": "त",
    "d": "द",
    "n": "न",
    "p": "प",
    "b": "ब",
    "m": "म",
    "y": "य",
    "r": "र",
    "l": "ल",
    "v": "व",
    "z": "श",
    "S": "ष",
    "s": "स",
    "h": "ह",
}

MARKS = {
    "M": "ं",
    "H": "ः",
}

VOWEL_TOKENS = sorted(VOWEL_SIGNS, key=len, reverse=True)
CONSONANT_TOKENS = sorted(CONSONANTS, key=len, reverse=True)
MARK_TOKENS = sorted(MARKS, key=len, reverse=True)
SANSKRIT_LINE_RE = re.compile(r"^([A-Za-z]?\d+\.\d+[a-z]/)(.*)$")


def _match_token(text: str, index: int, tokens: list[str]) -> str | None:
    for token in tokens:
        if text.startswith(token, index):
            return token
    return None


def transliterate_hk_to_devanagari(text: str) -> str:
    output: list[str] = []
    i = 0
    pending_consonant = False
    previous_was_phoneme = False

    while i < len(text):
        consonant = _match_token(text, i, CONSONANT_TOKENS)
        if consonant is not None:
            if pending_consonant:
                output.append("्")
            output.append(CONSONANTS[consonant])
            pending_consonant = True
            previous_was_phoneme = True
            i += len(consonant)
            continue

        vowel = _match_token(text, i, VOWEL_TOKENS)
        if vowel is not None:
            if pending_consonant:
                output.append(VOWEL_SIGNS[vowel])
            else:
                output.append(INDEPENDENT_VOWELS[vowel])
            pending_consonant = False
            previous_was_phoneme = True
            i += len(vowel)
            continue

        mark = _match_token(text, i, MARK_TOKENS)
        if mark is not None and previous_was_phoneme:
            if pending_consonant:
                output.append("्")
                pending_consonant = False
            output.append(MARKS[mark])
            previous_was_phoneme = True
            i += len(mark)
            continue

        ch = text[i]
        if ch == "'":
            if pending_consonant:
                output.append("्")
                pending_consonant = False
            output.append("ऽ")
            next_vowel = _match_token(text, i + 1, VOWEL_TOKENS)
            if next_vowel in {"a", "aa", "A"}:
                i += len(next_vowel)
        else:
            if pending_consonant:
                output.append("्")
                pending_consonant = False
            output.append(ch)
        previous_was_phoneme = False
        i += 1

    if pending_consonant:
        output.append("्")

    return "".join(output)


def convert_file() -> None:
    TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
    source_lines = SOURCE_PATH.read_text(encoding="utf-8").splitlines(keepends=True)

    converted_lines: list[str] = []
    for line in source_lines:
        stripped_newline = "\n" if line.endswith("\n") else ""
        core = line[:-1] if stripped_newline else line
        match = SANSKRIT_LINE_RE.match(core)
        if match:
            prefix, tail = match.groups()
            converted_tail = transliterate_hk_to_devanagari(tail)
            converted_lines.append(f"{prefix}{converted_tail}{stripped_newline}")
        else:
            converted_lines.append(line)

    TARGET_PATH.write_text("".join(converted_lines), encoding="utf-8")


if __name__ == "__main__":
    convert_file()
