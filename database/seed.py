# database/seed.py
#
# Knowledge Base Seed Script
# Run with: python -m database.seed
#
# Reads all JSON files from database/seeds/ and inserts them into Supabase.
# Uses SERVICE ROLE KEY (admin) to bypass RLS during seeding.
#
# JSON format expected per entry:
#   {
#     "module":   "campus_life",
#     "question": "What time does the library close?",
#     "answer":   "The library closes at 9:00 PM on weekdays.",
#     "keywords": ["library", "hours", "close", "open"]
#   }

import json
import pathlib
from database.client import get_admin_client

SEEDS_DIR = pathlib.Path(__file__).parent / "seeds"
MODULES = ["admin_directory", "campus_life", "academic_navigation"]

# How many rows to insert per API call (Supabase recommends <= 500)
BATCH_SIZE = 100


def load_seed_file(module_name: str) -> list[dict]:
    """Load and parse the JSON seed file for a given module."""
    path = SEEDS_DIR / f"{module_name}.json"
    if not path.exists():
        print(f"  [SKIP] Seed file not found: {path.name}")
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print(f"  Loaded {len(data)} rows from {path.name}")
    return data


def insert_in_batches(client, items: list[dict], module_name: str) -> int:
    """Insert rows into Supabase in batches. Returns total rows inserted."""
    total = 0
    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i : i + BATCH_SIZE]
        response = client.table("knowledge_items").insert(batch).execute()
        total += len(batch)
        print(f"  Inserted batch {i // BATCH_SIZE + 1}: {len(batch)} rows")
    return total


def main():
    print("=" * 55)
    print("  XMUM Chatbot — Seed Knowledge Base")
    print("=" * 55)

    print("\nConnecting to Supabase...")
    client = get_admin_client()
    print("Connection OK.")

    grand_total = 0
    for module in MODULES:
        print(f"\n[MODULE: {module}]")
        items = load_seed_file(module)
        if not items:
            continue
        inserted = insert_in_batches(client, items, module)
        grand_total += inserted
        print(f"  Done: {inserted} rows inserted for '{module}'.")

    print("\n" + "=" * 55)
    print(f"  Seeding complete. Total rows inserted: {grand_total}")
    print("=" * 55)


if __name__ == "__main__":
    main()
