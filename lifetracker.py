import json
import os
from datetime import datetime, timezone, date
from pathlib import Path

DATA_FILE = Path.home() / ".lifetracker_data.json"

def load_data():
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        print("⚠️  Broken data file — starting fresh")
        return []
    
def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def today_str():
    return datetime.now(timezone.utc).date().strftime("%Y-%m-%d")

def add_entry():
    today = today_str()

    mood = input("What's your mood today(1-10)? ").strip()
    energy = input("What's your energy level today(1-10)? ").strip()
    note = input("One line note (optional): ").strip()

    try:
        mood = int(mood) if mood else None
        energy = int(energy) if energy else None
        if mood is not None and not (1 <= mood <= 10):
            mood = None
        if energy is not None and not (1 <= energy <= 10):
            energy = None
    except ValueError:
        mood = energy = None
    
    entry = {
        "date": today,
        "mood": mood,
        "energy": energy,
        "note": note or None,
    }

    entries = load_data()
    # Remove old entry for today if exists
    entries = [e for e in entries if e["date"] != today]
    entries.append(entry)
    entries.sort(key=lambda x: x["date"], reverse=True)

    save_data(entries)
    print("\n ✅ Entry saved for today.")

def show_last_days(n=7):
    entries = load_data()
    today = date.today()

    print(f"\nLast {n} days:\n")
    found = 0
    for entry in entries:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        days_ago = (today - entry_date).days

        if days_ago > n:
            break

        mood = f"{entry['mood']:2d}" if entry['mood'] else " "
        energy = f"{entry['energy']:2d}" if entry['energy'] else " "
        note = entry['note'] or ""

        print(f"{entry['date']} ({days_ago}d ago) Mood: {mood}  Energy: {energy}  {note}")
        found += 1
    if found == 0:
        print("No entries yet.")

def monthly_average():
    entries = load_data()
    if not entries:
        print("No data yet.")
        return

    this_month = datetime.now(timezone.utc).strftime("%Y-%m")
    moods = []
    energies = []

    for e in entries:
        if e["date"].startswith(this_month):
            if e["mood"] is not None:
                moods.append(e["mood"])
            if e["energy"] is not None:
                energies.append(e["energy"])
    
    if not moods and not energies:
        print("No rated entries this month yet.")
        return
    
    print(f"\n This month ({this_month}):")
    if moods:
        avg = sum(moods) / len(moods)
        print(f" • Average Mood: {avg:.1f} ({len(moods)} days)")

    if energies:
        avg = sum(energies) / len(energies)
        print(f" • Average Energy: {avg:.1f} ({len(energies)} days)")

def show_help():
    print("""
Commands:
  add       Add today's mood & note
  show      Show last 7 days
  month     Show this month's averages
  help      this help
  quit      exit
""")

def main():
    print("🧪 LifeTracker CLI v0.1 (mood + energy tracker)")
    show_help()

    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n Bye 👋")
            break

        if cmd in("q", "quit", "exit"):
            print("See you tomorrow hopefully 🌙")
            break
        elif cmd == "add":
            add_entry()
        elif cmd in ("show", "last", "ls"):
            show_last_days(7)
        elif cmd in ("month", "avg", "monthly"):
            monthly_average()
        elif cmd in ("help", "h", "?"):
            show_help()
        elif cmd == "":
            continue
        else:
            print(f"Unknown command: {cmd!r} (try 'help')")

if __name__ == "__main__":
    main()