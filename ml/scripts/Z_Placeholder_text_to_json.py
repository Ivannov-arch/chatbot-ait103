# scripts/text_to_json.py
# Konversi file Q&A format .txt ke JSON siap seed ke Supabase
# Jalankan: python scripts/text_to_json.py campus_life database/seeds/campus_life_qa.txt
#
# Format file .txt input:
#   Q: Where is the library?
#   A: The library is located at Block A, Level 2.
#   K: library, location, block a
#   ---
#   Q: What time does the library open?
#   A: Opens at 8:30 AM on weekdays, 9:00 AM on Saturdays.
#   K: library, open, hours, time, weekday
#   ---

import sys
import json
import pathlib


def parse_qa_file(module: str, txt_path: str):
    path = pathlib.Path(txt_path)
    if not path.exists():
        print(f"ERROR: File tidak ditemukan: {txt_path}")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in content.split("---") if b.strip()]
    items = []
    skipped = 0

    for block in blocks:
        entry = {"module": module, "question": "", "answer": "", "keywords": []}
        for line in block.splitlines():
            if line.startswith("Q:"):
                entry["question"] = line[2:].strip()
            elif line.startswith("A:"):
                entry["answer"] = line[2:].strip()
            elif line.startswith("K:"):
                entry["keywords"] = [k.strip() for k in line[2:].split(",") if k.strip()]

        if entry["question"] and entry["answer"]:
            items.append(entry)
        else:
            skipped += 1
            print(f"  [SKIP] Block tidak lengkap (Q atau A kosong)")

    output_path = pathlib.Path(f"database/seeds/{module}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(items)} Q&A pairs disimpan ke {output_path}")
    if skipped:
        print(f"   ({skipped} block diskip karena tidak lengkap)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/text_to_json.py <module_name> <qa_txt_file>")
        print("Example: python scripts/text_to_json.py campus_life database/seeds/campus_life_qa.txt")
        sys.exit(1)
    parse_qa_file(module=sys.argv[1], txt_path=sys.argv[2])
