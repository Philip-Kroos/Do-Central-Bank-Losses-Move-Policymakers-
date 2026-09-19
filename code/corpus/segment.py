"""Sentence splitting and 5-sentence passages (as in Heinemann & Kemper 2026, for comparability).

Rule-based and language-agnostic enough for EN/DE/FR/IT/ES/NL central-bank prose. Protects
common abbreviations, initials and decimal numbers. Deterministic: no model downloads, so the
replication package runs offline.
"""
from __future__ import annotations
import re

ABBREVIATIONS = {
    # en
    "e.g", "i.e", "mr", "mrs", "ms", "dr", "prof", "vs", "etc", "no", "fig", "approx", "st", "jr", "inc", "co",
    # de
    "z.b", "bzw", "vgl", "ca", "mio", "mrd", "nr", "s", "u.a", "d.h", "usw", "dt", "abs", "art",
    # fr / it / es / nl
    "m", "mme", "cf", "sig", "dott", "sr", "sra", "dhr", "mevr", "blz", "art", "p", "pp",
}
_CANDIDATE = re.compile(r"([.!?])(\s+)(?=[\"'“„«(\[]?[A-ZÀ-ÖØ-Þ0-9])")


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    sentences, start = [], 0
    for m in _CANDIDATE.finditer(text):
        end = m.start(1) + 1
        chunk = text[start:end]
        last_token = re.split(r"[\s(]", chunk[:-1])[-1].lower() if m.group(1) == "." else ""
        if m.group(1) == "." and (last_token in ABBREVIATIONS or re.fullmatch(r"[a-zà-öø-þ]", last_token)):
            continue                                    # abbreviation or single initial
        if m.group(1) == "." and re.search(r"\d$", chunk[:-1]) and text[m.end():m.end() + 1].isdigit():
            continue                                    # decimal split across a space is unlikely; guard anyway
        sentences.append(chunk.strip())
        start = m.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def passages(text: str, size: int = 5) -> list[str]:
    sents = split_sentences(text)
    return [" ".join(sents[i:i + size]) for i in range(0, len(sents), size)]
