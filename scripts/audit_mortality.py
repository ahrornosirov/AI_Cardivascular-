"""Reproduce a pre-exclusion audit of CDC's 2019 NHANES linked mortality files.

This does not construct a model cohort: it has no baseline NHANES predictor data,
no age 40-79 restriction, and no prior-CVD exclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path
from urllib.request import urlopen

BASE = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality"
DEFAULT_CYCLES = (1999, 2001, 2003, 2005, 2007)
VALID_CAUSES = {f"{code:03d}" for code in range(1, 11)}
KNOWN_SHA256 = {
    1999: "562bd367107add0b2b40fed36a062d8b194fca31e11aab897a0efad4bebc8b26",
    2001: "2788c8c8a02995ea5686882b5fe65b4b9cd415016031525f8a3c1a3646c47f1b",
    2003: "639f6b3292a55b112fbfc842954af3d8d32bcce287cd8ae49319e5aca1c033c0",
    2005: "69388ea13a4f395f29d9d21bc51941b9759003490d4b00f6ff12a1bc5f8dba5c",
    2007: "75f89bd545a13ba726a7eb56de4d62f6dfc8f0f76d505dc18ced9752d5e2c77d",
}


def field(line: str, first: int, last: int) -> str:
    """Extract a one-based, inclusive, fixed-width field from a CDC record."""
    return line[first - 1 : last].strip()


def download(cycle: int, cache: Path) -> list[str]:
    filename = f"NHANES_{cycle}_{cycle + 1}_MORT_2019_PUBLIC.dat"
    path = cache / filename
    if not path.exists():
        cache.mkdir(parents=True, exist_ok=True)
        url = f"{BASE}/{filename}"
        for attempt in range(3):
            try:
                with urlopen(url, timeout=30) as response:
                    payload = response.read()
                if not payload:
                    raise ValueError(f"empty download: {url}")
                temporary = path.with_suffix(".part")
                temporary.write_bytes(payload)
                temporary.replace(path)
                break
            except (OSError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
    payload = path.read_bytes()
    if not payload.endswith(b"\n"):
        raise ValueError(f"incomplete final record in {path}; remove and download again")
    expected = KNOWN_SHA256.get(cycle)
    if expected and hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError(f"checksum mismatch for {path}; remove and download again")
    return payload.decode("ascii").splitlines()


def audit(lines: list[str]) -> tuple[int, int, int, int, int]:
    eligible = known = deaths = events = 0
    for line in lines:
        if field(line, 15, 15) != "1":  # ELIGSTAT: eligible adult
            continue
        eligible += 1
        months = field(line, 46, 48)  # PERMTH_EXM, not interview follow-up
        if not months.isdigit():
            continue
        elapsed = int(months)
        mortstat = field(line, 16, 16)
        if mortstat not in {"0", "1"}:
            continue
        if mortstat == "0" and elapsed < 120:
            continue  # Alive but less than the complete ten-year horizon
        cause = field(line, 17, 19)
        if mortstat == "1" and elapsed <= 120 and cause not in VALID_CAUSES:
            continue  # Early death with unknown cause has unknown target status
        known += 1
        if mortstat == "1":
            deaths += 1
            if elapsed <= 120 and cause in {"001", "005"}:
                events += 1
    return len(lines), eligible, known, deaths, events


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycles", type=int, nargs="+", default=DEFAULT_CYCLES)
    parser.add_argument("--cache", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    print("cycle,rows,eligible_adults,known_10y,all_deaths,cvd_deaths_10y,crude_pct", flush=True)
    for cycle in args.cycles:
        rows, eligible, known, deaths, events = audit(download(cycle, args.cache))
        print(f"{cycle}-{cycle + 1},{rows},{eligible},{known},{deaths},{events},{100 * events / known:.2f}", flush=True)


if __name__ == "__main__":
    main()
