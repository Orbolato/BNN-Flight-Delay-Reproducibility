"""Extract the exact SBRF-SBGR modeling slice from the archived SBGR table.

Usage:
    python scripts/prepare_route_dataset.py /path/to/final_data_sbgr.csv

The script writes data/final_data_sbrf_sbgr.csv and a deterministic gzip archive,
then prints SHA-256 checksums for both files.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import shutil
from pathlib import Path

import pandas as pd

ROUTE_CODE = 2
EXPECTED_ROWS = 14_956
EXPECTED_COLUMNS = 28
EXPECTED_CSV_SHA256 = "02990049e1307b352b369c0074719ce89d21fbc6aa6156bcd0dd32059819a0eb"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Archived final_data_sbgr.csv")
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    df = pd.read_csv(args.source)
    route = df.loc[df["sg_icao_origem"] == ROUTE_CODE].copy().reset_index(drop=True)

    if route.shape != (EXPECTED_ROWS, EXPECTED_COLUMNS):
        raise ValueError(
            f"Unexpected route slice shape {route.shape}; expected "
            f"({EXPECTED_ROWS}, {EXPECTED_COLUMNS})."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "final_data_sbrf_sbgr.csv"
    gz_path = args.output_dir / "final_data_sbrf_sbgr.csv.gz"

    route.to_csv(csv_path, index=False)
    csv_hash = sha256(csv_path)
    if csv_hash != EXPECTED_CSV_SHA256:
        raise ValueError(
            "The extracted CSV does not match the archived paper dataset. "
            f"Expected {EXPECTED_CSV_SHA256}, got {csv_hash}."
        )

    # Deterministic gzip: no stored filename and mtime=0.
    with csv_path.open("rb") as f_in, gz_path.open("wb") as raw_out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_out, compresslevel=9, mtime=0) as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f"Rows/columns: {route.shape}")
    print(f"CSV:    {csv_path}  sha256={sha256(csv_path)}")
    print(f"CSV.GZ: {gz_path}  sha256={sha256(gz_path)}")


if __name__ == "__main__":
    main()
