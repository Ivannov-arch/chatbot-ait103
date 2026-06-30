"""Compare old seed files (from git commit 3ee7aba) vs current seed files.
Outputs questions that are MISSING in the current version.
"""
import json
import pathlib
import subprocess
import sys

COMMIT = "3ee7aba"
MODULES = ["general", "admin_directory", "campus_life", "academic_navigation"]
SEEDS_DIR = pathlib.Path("database/seeds")

missing_all: dict[str, list[dict]] = {}

for module in MODULES:
    # Get old version from git (force UTF-8 output)
    result = subprocess.run(
        ["git", "show", f"{COMMIT}:ml/database/seeds/{module}.json"],
        capture_output=True,
    )
    old_data = json.loads(result.stdout.decode("utf-8", errors="replace"))
    old_questions = {
        r["question"].strip().lower(): r
        for r in old_data
        if r.get("question")
    }

    # Get current version
    current_data = json.loads(
        (SEEDS_DIR / f"{module}.json").read_text(encoding="utf-8")
    )
    current_questions = {
        r["question"].strip().lower()
        for r in current_data
        if r.get("question")
    }

    missing = {q: r for q, r in old_questions.items() if q not in current_questions}
    print(f"\n[{module}] OLD={len(old_questions)}, NOW={len(current_questions)}, MISSING={len(missing)}")
    for q in sorted(missing)[:10]:
        print(f"  - {missing[q]['question']}")
    if len(missing) > 10:
        print(f"  ... and {len(missing)-10} more")

    missing_all[module] = list(missing.values())

# Write missing questions to a restore file
restore_path = SEEDS_DIR / "_missing_to_restore.json"
with open(restore_path, "w", encoding="utf-8") as f:
    json.dump(missing_all, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in missing_all.values())
print(f"\nTotal missing across all modules: {total}")
print(f"Saved to: {restore_path}")
