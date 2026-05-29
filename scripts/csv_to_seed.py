# scripts/csv_to_seed.py
# Import CSV (from Google Sheets) directly into Supabase as knowledge_items
# Run: python scripts/csv_to_seed.py knowledge_items.csv
#
# Expected CSV format (required columns):
# module,question,answer,keywords
# campus_life,"Where is the library?","The library is at Block A.","library,location"
#
# How to use with Google Sheets:
# 1. Create a Google Sheet with the columns: module | question | answer | keywords
# 2. All team members fill in together
# 3. File → Download → CSV
# 4. python scripts/csv_to_seed.py file_name.csv


from database import Z_Placeholder_client
import sys
import csv
import json
import pathlib

def csv_to_json(csv_path: str):
    path = pathlib.Path(csv_path)
    if not path.exists():
        print(f"ERROR: File tidak ditemukan: {csv_path}")
        sys.exit(1)
    
    #group by module
    modules: dict[str,list[dict]] = {}

    with open(path, encoding='utf-8-sig') as f: # utf-8-sig handles Excel BOM
        reader = csv.DictReader(f)
        rows = list(reader)
    
    for row in rows:
        module = row.get("module", "").strip()
        question = row.get("question", "").strip()
        answer = row.get("answer", "").strip()
        keywords_raw = row.get("keywords", "")
        #split by comma
        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

        #validate rows
        if not module or not question or not answer:
            print(f"[SKIP] Baris tidak lengkap: {row}")
            continue

        if module not in modules:
            modules[module] = []
        modules[module].append({
            "module": module,
            "question": question,
            "answer": answer,
            "keywords": keywords,
        })

    #save per module into JSON files inside database/seeds/
    output_dir = pathlib.Path("database/seeds")
    output_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for module, items in modules.items():
        out_path = output_dir / f"{module}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent = 2, ensure_ascii= True)
        print(f"✓ [{module}] {len(items)} items → {out_path}")
        total += len(items)
    
    print(f"\n🎉 Total: {total} items dari {len(modules)} modul siap di-seed.")
    print("Jalankan: python -m database.seed")
    
     
    if __name__ == "__main__":
        csv_path = sys.argv[1] if len(sys.argv) > 1 else "knowledge_items.csv"
        csv_to_json(csv_path)