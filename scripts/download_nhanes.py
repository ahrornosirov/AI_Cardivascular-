"""Download baseline NHANES XPT files used for the cohort feasibility audit.

Run from the repository root with an HTTPS-capable Python installation. Raw files
are cached under data/raw and excluded from Git; a source manifest is written to
docs/nhanes_source_manifest.csv.
"""

from __future__ import annotations

import csv
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw"
MANIFEST = ROOT / "docs" / "nhanes_source_manifest.csv"
BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public"

FILES = {
    1999: ["DEMO", "BPX", "BMX", "LAB13", "MCQ", "SMQ", "DIQ", "BPQ"],
    2001: ["DEMO_B", "BPX_B", "BMX_B", "L13_B", "MCQ_B", "SMQ_B", "DIQ_B", "BPQ_B"],
    2003: ["DEMO_C", "BPX_C", "BMX_C", "L13_C", "MCQ_C", "SMQ_C", "DIQ_C", "BPQ_C"],
    2005: ["DEMO_D", "BPX_D", "BMX_D", "TCHOL_D", "HDL_D", "MCQ_D", "SMQ_D", "DIQ_D", "BPQ_D"],
    2007: ["DEMO_E", "BPX_E", "BMX_E", "TCHOL_E", "HDL_E", "MCQ_E", "SMQ_E", "DIQ_E", "BPQ_E"],
}


def fetch(year: int, stem: str) -> dict[str, str | int]:
    name = f"{stem}.xpt"
    path = CACHE / name
    url = f"{BASE}/{year}/DataFiles/{name}"
    if not path.exists():
        for attempt in range(3):
            try:
                with urlopen(url, timeout=60) as response:
                    data = response.read()
                    expected_length = response.headers.get("Content-Length")
                if expected_length and len(data) != int(expected_length):
                    raise ValueError(f"incomplete download: {url}")
                if len(data) < 80 or not data.startswith(b"HEADER RECORD"):
                    raise ValueError(f"unexpected XPT content: {url}")
                temporary = path.with_suffix(".part")
                temporary.write_bytes(data)
                temporary.replace(path)
                break
            except (OSError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(attempt + 1)
    data = path.read_bytes()
    if not data.startswith(b"HEADER RECORD"):
        raise ValueError(f"cached file is not XPT: {path}")
    return {
        "cycle": f"{year}-{year + 1}",
        "filename": name,
        "url": url,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    tasks = [(year, stem) for year, stems in FILES.items() for stem in stems]
    records = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fetch, year, stem): (year, stem) for year, stem in tasks}
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            print(f"{len(records):2}/{len(tasks)} {record['filename']} {record['bytes']} bytes", flush=True)
    records.sort(key=lambda record: (record["cycle"], record["filename"]))
    with MANIFEST.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=["cycle", "filename", "url", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(records)
    print(f"Source manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
