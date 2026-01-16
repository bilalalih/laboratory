import csv
import hashlib
import json
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

BASE = Path(__file__).parent.resolve()
INBOX = BASE / "inbox"
OUTBOX = BASE / "outbox"
FAILED = BASE / "failed"
STATE_DIR = BASE / "state"
DB_PATH = "agent.db"
SEEN_PATH = STATE_DIR / "seen.json"

POLL_SECONDS = 2.0

# This functions returns the time now in ISO format
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"

# This function returns a 64 hex char string that can be used for integrity checks
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f: # Opens the file in binary mode
        for chunk in iter(lambda: f.read(1024*1024), b""): # Reads one MB chunks till b""(empty bytes)
            h.update(chunk)
    return h.hexdigest()

# This function loops over our four paths - and for each, create the folder, quietly skipping if it already exists
def ensure_dirs() -> None:
    for d in (INBOX, OUTBOX, FAILED, STATE_DIR):
        d.mkdir(parents=True, exist_ok=True)

# This function loads our JSON seen file
def load_seen() -> dict[str, Any]:
    if not SEEN_PATH.exists():
        return {}
    return json.loads(SEEN_PATH.read_text(encoding="utf-8"))

# This function saves a dist to the JSON file
def save_seen(seen: dict[Any, Any]) -> None:
    SEEN_PATH.write_text(json.dumps(seen, indent=2), encoding="utf-8")

# This function returns a connection to our .db file
def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            filename TEXT NOT NULL,
            filehash TEXT NOT NULL,
            status TEXT NOT NULL, -- queued | running | done | failed 
            error TEXT,
            UNIQUE(filename, filehash)
        )
        """)
    return conn

# This function logs messages 
def log(msg: str) -> None:
    print(f"[{now_iso()}] {msg}")

# Define schema
@dataclass
class Job:
    id: int
    filename: str
    filehash: str

# This function queues a new job if not already queued.
def enqueue_if_new(conn: sqlite3.Connection, path: Path, seen: dict[Any, Any]) -> None:
    # Avoid partial writes: only handle stable files (size unchanged for one poll)
    size_key = f"{path.name}::size"
    prev_size = seen.get(size_key)
    size = path.stat().st_size
    seen[size_key] = size
    if prev_size is None or prev_size != size:
        return # not stable yet
    
    # Unique identity: hash
    fhash = sha256_file(path)
    if seen.get(path.name) == fhash:
        return
    
    # Insert job
    cur = conn.execute(
        "INSERT OR IGNORE INTO jobs(created_at, updated_at, filename, filehash, status) VALUES(?, ?, ?, ?, ?)", 
        (now_iso(), now_iso(), path.name, fhash, "queued"),
    )

    conn.commit()
    job_id = cur.lastrowid
    
    if cur.rowcount == 0:  # remote duplicate
        return

    seen[path.name] = fhash
    log(f"Enqueued job #{job_id} for {path.name}") 

def fetch_next_job(conn: sqlite3.Connection) -> Optional[Job]:
    row = conn.execute("SELECT id, filename, filehash FROM jobs WHERE status='queued' ORDER BY id ASC LIMIT 1").fetchone()
    
    if not row:
        return None
    
    job_id, filename, filehash = row

    if job_id is None:
        raise RuntimeError(f"DB returned NULL id for row: {row}")
    conn.execute("UPDATE jobs SET status='running', updated_at=? WHERE id=?",(now_iso(), job_id))
    conn.commit()
    return Job(job_id, filename, filehash)

def mark_done(conn:sqlite3.Connection, job_id: int) -> None:
    conn.execute("UPDATE jobs SET status='done', updated_at=?, error=NULL WHERE id=?", (now_iso(), job_id))
    conn.commit()

def mark_failed(conn:sqlite3.Connection, job_id: int, error:str) -> None:
    conn.execute("UPDATE jobs SET status='failed', updated_at=?, error=? WHERE id=?", (now_iso(), error[:1000], job_id))
    conn.commit()

def clean_csv(input_path: Path, output_path: Path) -> dict[str, Any]:
    """
    Minimal 'data cleaning' pipeline:
    - trims whitespace in headers and values
    - drops completely empty rows
    - outputs cleaned CSV
    - returns a small report dict 
    """
    rows_in = 0
    rows_out = 0
    
    with input_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        all_rows = list(reader)

    if not all_rows:
        raise ValueError("Empty CSV")
    
    headers = [h.strip() for h in all_rows[0]]
    cleaned = [headers]

    for r in all_rows[1:]:
        rows_in += 1
        cells = [c.strip() for c in r]
        if all(c == "" for c in cells):
            continue
        # pad/truncate to head length
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))

        if len(cells) > len(headers):
            cells = cells[: len(headers)]

        cleaned.append(cells)
        rows_out += 1

        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(cleaned)

        return {
            "input_rows": rows_in,
            "output_rows": rows_out,
            "dropped_rows": rows_in - rows_out,
            "columns": len(headers),
        }
    
def process_job(conn: sqlite3.Connection, job:Job) -> None:
    src = INBOX / job.filename
    if not src.exists():
        raise FileNotFoundError(f"Missing file: {src}")
    
    # Verify hash to avoid mismatched files
    actual = sha256_file(src)
    if actual != job.filehash:
        raise ValueError("File changed since enqueue(hash mismatch)")
    stem = src.stem
    cleaned_csv = OUTBOX / f"{stem}.cleaned.csv"
    report_json = OUTBOX / f"{stem}.report.json"

    report = clean_csv(src, cleaned_csv)
    report["job_id"] = job.id
    report["filename"] = job.filename
    report["processed_at"] = now_iso()

    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    # archive original (move it out of inbox)
    archived = OUTBOX / f"{stem}.original{src.suffix}"
    shutil.move(str(src), str(archived))

    log(f"Job #{job.id} done -> {cleaned_csv.name}, {report_json.name}")

def main() -> None:
    ensure_dirs()
    seen = load_seen()
    conn = db_connect()

    log("Agent started. Drop CSV files into ./inbox")
    while True:
        try:
            # Scan Inbox and enqueue stable new files
            for p in sorted(INBOX.iterdir()):
                if p.is_file() and p.suffix.lower() == ".csv":
                    enqueue_if_new(conn, p, seen)
            
            save_seen(seen)

            # Execute one job per loop (keeps it simple)
            job = fetch_next_job(conn)
            if job is None:
                # No job found
                time.sleep(POLL_SECONDS)
                continue
            try:
                process_job(conn, job)
                mark_done(conn, job.id)
            except Exception as e:
                # Move bad input to failed
                src = INBOX / job.filename
                if src.exists():
                    shutil.move(str(src), str(FAILED / job.filename))
                mark_failed(conn, job.id, str(e))
                log(f"Job #{job.id} failed: {e}")
        
        except Exception as loop_err:
            log(f"Loop error (continuing): {loop_err}")
        
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()