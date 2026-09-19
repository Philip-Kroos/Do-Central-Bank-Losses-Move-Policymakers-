"""Schema-tolerant loaders for the speech corpora.

The exact column layout of the BIS full-text extract and the CBS dataset is NOT yet verified
[UNVERIFIED]; the loader maps common aliases and fails loudly if a required field is missing,
printing the columns it found so the mapping can be fixed in one line.
"""
from __future__ import annotations
import io
import zipfile
from pathlib import Path
import pandas as pd

ALIASES = {
    "text": ["text", "content", "body", "speech_text", "full_text"],
    "date": ["date", "speech_date", "published", "pub_date"],
    "speaker": ["author", "speaker", "name", "central_banker"],
    "institution": ["institution", "central_bank", "cb", "country", "bank"],
    "title": ["title", "headline"],
    "url": ["url", "link", "source"],
}
REQUIRED = ("text", "date", "speaker")


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            members = [m for m in z.namelist() if m.lower().endswith((".csv", ".parquet", ".json", ".jsonl"))]
            if not members:
                raise ValueError(f"No tabular file inside {path}: {z.namelist()[:10]}")
            frames = [_read_bytes(m, z.read(m)) for m in members]
            return pd.concat(frames, ignore_index=True)
    return _read_bytes(path.name, path.read_bytes())


def _read_bytes(name: str, raw: bytes) -> pd.DataFrame:
    n = name.lower()
    if n.endswith(".parquet"):
        return pd.read_parquet(io.BytesIO(raw))
    if n.endswith((".json", ".jsonl")):
        return pd.read_json(io.BytesIO(raw), lines=n.endswith(".jsonl"))
    return pd.read_csv(io.BytesIO(raw), low_memory=False)


def standardise(df: pd.DataFrame, source: str) -> pd.DataFrame:
    lower = {c.lower().strip(): c for c in df.columns}
    out = {}
    for field, names in ALIASES.items():
        hit = next((lower[n] for n in names if n in lower), None)
        if hit is not None:
            out[field] = df[hit]
    missing = [f for f in REQUIRED if f not in out]
    if missing:
        raise KeyError(f"{source}: missing {missing}. Columns found: {list(df.columns)}")
    res = pd.DataFrame(out)
    res["date"] = pd.to_datetime(res["date"], errors="coerce")
    res["source"] = source
    return res.dropna(subset=["text", "date"])


def load_corpus(path: str | Path, source: str) -> pd.DataFrame:
    return standardise(_read_any(Path(path)), source)
