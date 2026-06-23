from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "demo"


def get_data_dir() -> Path:
    return Path(os.getenv("AULASENSE_DATA_DIR", str(DEFAULT_DATA_DIR))).expanduser().resolve()


def _candidate_paths(data_dir: Path, logical_name: str) -> list[Path]:
    names = [
        f"{logical_name}.csv",
        logical_name,
        f"{logical_name}_csv",
    ]
    paths: list[Path] = []
    for name in names:
        p = data_dir / name
        if p.exists():
            paths.append(p)
    # también buscar en subcarpetas exportadas por Spark
    for p in data_dir.rglob("*.csv"):
        if logical_name in str(p.parent.name) or logical_name in p.name:
            paths.append(p)
    # quitar duplicados manteniendo orden
    seen = set()
    unique = []
    for p in paths:
        key = str(p.resolve())
        if key not in seen:
            unique.append(p)
            seen.add(key)
    return unique


def read_csv_logical(logical_name: str, data_dir: Path | None = None) -> pd.DataFrame:
    data_dir = data_dir or get_data_dir()
    paths = _candidate_paths(data_dir, logical_name)
    frames: list[pd.DataFrame] = []

    for path in paths:
        if path.is_dir():
            csv_files = sorted([p for p in path.rglob("*.csv") if not p.name.startswith(".")])
        else:
            csv_files = [path]

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    frames.append(df)
            except Exception:
                continue

    if not frames:
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates()
    return out


def parse_datetime_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def classify_iaq(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "Sin dato"
    value = float(value)
    if value <= 50:
        return "Bueno"
    if value <= 100:
        return "Moderado"
    if value <= 150:
        return "Riesgo medio"
    return "Riesgo alto"


def recommend_action(value: float | int | None) -> str:
    state = classify_iaq(value)
    if state == "Bueno":
        return "Monitoreo normal"
    if state == "Moderado":
        return "Ventilación preventiva"
    if state == "Riesgo medio":
        return "Encender purificador/extractor"
    if state == "Riesgo alto":
        return "Alerta + extractor/purificador"
    return "Sin recomendación"

