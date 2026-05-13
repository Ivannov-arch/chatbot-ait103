# placeholder_seed.py
# database/seed.py
#
# Knowledge Base Seed Script
# Run with:  python -m database.seed
#
# What it does:
#   1. Reads JSON files from database/seeds/
#   2. Connects to Supabase using the SERVICE ROLE key (admin)
#   3. Upserts all knowledge items into the `knowledge_items` table
#
# JSON file format (each entry in the array):
#   {
#     "module":   "campus_life",
#     "question": "What time does the library close?",
#     "answer":   "The library closes at 9:00 PM on weekdays.",
#     "keywords": ["library", "hours", "close", "open"]
#   }
#
# TODO: implement load_seed_file(path) -> list[dict]
# TODO: implement upsert_knowledge_items(items: list[dict]) using admin client
# TODO: run seeding for all three modules

import json
import pathlib

SEEDS_DIR = pathlib.Path(__file__).parent / "seeds"
MODULES = ["admin_directory", "campus_life", "academic_navigation"]


def load_seed_file(module_name: str) -> list[dict]:
    """Load and parse a JSON seed file for a given module."""
    path = SEEDS_DIR / f"{module_name}.json"
    if not path.exists():
        print(f"  [WARN] Seed file not found: {path}")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def upsert_knowledge_items(items: list[dict]) -> None:
    """Insert or update knowledge items in Supabase."""
    # PLACEHOLDER — replace with real Supabase upsert
    # from database.client import get_admin_client
    # client = get_admin_client()
    # client.table("knowledge_items").upsert(items).execute()
    print(f"  [PLACEHOLDER] Would upsert {len(items)} item(s).")


def main():
    print("=== XMUM Chatbot — Seed Knowledge Base ===")
    for module in MODULES:
        print(f"\n[{module}]")
        items = load_seed_file(module)
        if items:
            upsert_knowledge_items(items)
            print(f"  Processed {len(items)} item(s).")
    print("\nDone.")


if __name__ == "__main__":
    main()
