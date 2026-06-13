# Supabase Setup & Fast Data Pipeline Guide

## Tahap 1 — Setup Supabase (15 menit)

### Step 1.1 — Buat Project Supabase
1. Pergi ke https://supabase.com → **New Project**
2. Isi: Project name: `xmum-chatbot`, Password (simpan!), Region: **Southeast Asia (Singapore)**
3. Tunggu ~2 menit sampai project siap

### Step 1.2 — Ambil Credentials
`Settings → API` → copy 3 nilai ini ke file `.env`:
```env
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...   # untuk seed script saja
```

### Step 1.3 — Jalankan Schema
`SQL Editor → New Query` → paste isi `database/Z_Placeholder_schema.sql` → **Run**

Verifikasi: `Table Editor` → pastikan tabel `knowledge_items` muncul. ✅

---

## Tahap 2 — Install Tools Ekstraksi Data

Tambahkan ke `requirements.txt`:
```
pdfplumber>=0.11.0        # ekstrak teks dari PDF handbook
requests>=2.32.0          # HTTP request ke website
beautifulsoup4>=4.12.0    # parse HTML website
lxml>=5.2.0               # HTML parser cepat untuk BS4
```

Install:
```bash
pip install -r requirements.txt
```

---

## Tahap 3 — Pipeline Ekstraksi Cepat

### 3A — Ekstrak dari PDF Handbook

Buat file: `scripts/extract_pdf.py`

```python
# scripts/extract_pdf.py
# Jalankan: python scripts/extract_pdf.py handbook.pdf campus_life
#
# Output: database/seeds/campus_life_raw.txt
# Anda tinggal edit file txt itu menjadi Q&A pairs

import sys
import pdfplumber
import pathlib

def extract_pdf_text(pdf_path: str, output_name: str):
    output_dir = pathlib.Path("database/seeds")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{output_name}_raw.txt"

    print(f"Membaca: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        all_text = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text.append(f"\n=== HALAMAN {i+1} ===\n{text}")

    raw = "\n".join(all_text)
    output_file.write_text(raw, encoding="utf-8")
    print(f"✅ Teks tersimpan di: {output_file}")
    print(f"   Total karakter: {len(raw):,}")

if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "handbook.pdf"
    output_name = sys.argv[2] if len(sys.argv) > 2 else "raw_output"
    extract_pdf_text(pdf_path, output_name)
```

**Cara pakai:**
```bash
# Taruh handbook PDF di root folder, lalu:
python scripts/extract_pdf.py "XMUM_Student_Handbook.pdf" campus_life
python scripts/extract_pdf.py "XMUM_Student_Handbook.pdf" admin_directory
```
Hasilnya adalah file teks mentah → buka di VS Code → **pilih bagian yang relevan** → susun menjadi Q&A.

---

### 3B — Ekstrak dari Website XMUM

Buat file: `scripts/extract_web.py`

```python
# scripts/extract_web.py
# Jalankan: python scripts/extract_web.py https://www.xmu.edu.my/some-page
#
# Cetak semua teks bersih dari halaman tersebut ke terminal

import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research bot for XMUM chatbot project)"}

def extract_web_text(url: str):
    print(f"Fetching: {url}")
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")

    # Hapus nav, footer, script yang tidak relevan
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Ambil semua teks
    text = soup.get_text(separator="\n")
    # Bersihkan baris kosong berlebih
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean = "\n".join(lines)

    print("\n" + "="*60)
    print(clean)
    print("="*60)
    print(f"\n✅ Total baris: {len(lines)}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.xmu.edu.my"
    extract_web_text(url)
```

**Cara pakai:**
```bash
# Ekstrak halaman library XMUM, redirect output ke file txt
python scripts/extract_web.py "https://www.xmu.edu.my/library" > database/seeds/library_raw.txt
python scripts/extract_web.py "https://www.xmu.edu.my/student-affairs" > database/seeds/student_affairs_raw.txt
```

---

### 3C — Konversi Teks Mentah ke JSON Cepat

Buat file: `scripts/text_to_json.py`

```python
# scripts/text_to_json.py
# 
# Alat bantu untuk mengubah Q&A yang ditulis manual di file .txt
# menjadi format JSON yang siap di-seed ke Supabase.
#
# Format input file .txt (buat sendiri dari hasil ekstraksi):
#   Q: Where is the library?
#   A: The library is located at Block A, Level 2.
#   K: library, location, block a
#   ---
#   Q: What time does the library open?
#   A: The library opens at 8:30 AM on weekdays.
#   K: library, open, hours, time
#   ---
#
# Jalankan:
#   python scripts/text_to_json.py campus_life database/seeds/campus_life_qa.txt

import sys
import json
import pathlib

def parse_qa_file(module: str, txt_path: str):
    path = pathlib.Path(txt_path)
    if not path.exists():
        print(f"ERROR: File tidak ditemukan: {txt_path}")
        return

    content = path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in content.split("---") if b.strip()]
    items = []

    for block in blocks:
        entry = {"module": module, "question": "", "answer": "", "keywords": []}
        for line in block.splitlines():
            if line.startswith("Q:"):
                entry["question"] = line[2:].strip()
            elif line.startswith("A:"):
                entry["answer"] = line[2:].strip()
            elif line.startswith("K:"):
                entry["keywords"] = [k.strip() for k in line[2:].split(",")]

        if entry["question"] and entry["answer"]:
            items.append(entry)
        else:
            print(f"  [SKIP] Block tidak lengkap: {block[:50]}...")

    output_path = pathlib.Path(f"database/seeds/{module}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(items)} Q&A disimpan ke {output_path}")

if __name__ == "__main__":
    module = sys.argv[1] if len(sys.argv) > 1 else "campus_life"
    txt_path = sys.argv[2] if len(sys.argv) > 2 else "database/seeds/campus_life_qa.txt"
    parse_qa_file(module, txt_path)
```

---

## Alur Kerja Lengkap (End-to-End)

```
PDF / Website
     │
     ▼
[extract_pdf.py / extract_web.py]
     │
     ▼
File _raw.txt  ← buka di VS Code, pilih bagian relevan
     │
     ▼
Tulis file _qa.txt  ← format Q:/A:/K: (paling cepat: 30 menit per modul)
     │
     ▼
[text_to_json.py]
     │
     ▼
File seeds/modul.json  ← JSON siap pakai
     │
     ▼
[python -m database.seed]
     │
     ▼
✅ Data masuk ke Supabase
```

---

## Cara Paling Cepat untuk Input Data

### Opsi A — Format Q:/A:/K: di VS Code *(Direkomendasikan)*
Bagi halaman _raw.txt menjadi dua jendela di VS Code (split editor).
Kiri: raw text dari handbook. Kanan: tulis file _qa.txt.
Rata-rata: **1 Q&A per 2 menit** = 1 modul (10 Q&A) selesai dalam 20 menit.

### Opsi B — Import CSV Langsung ke Supabase
Supabase mendukung import CSV langsung dari dashboard:
`Table Editor → knowledge_items → Import data → Upload CSV`

Format CSV:
```csv
module,question,answer,keywords
campus_life,"Where is the library?","The library is at Block A.","library,location,block"
campus_life,"What time does it open?","Opens at 8:30 AM on weekdays.","library,open,hours"
```

Ini berguna jika tim ingin mengisi data bersama-sama di **Google Sheets**
lalu export CSV dan import sekali klik.

### Opsi C — Google Sheets sebagai Collaborative Input
1. Buat Google Sheet dengan kolom: `module | question | answer | keywords`
2. Semua anggota tim mengisi bersama (paralel, real-time)
3. Saat selesai: `File → Download → CSV`
4. Import ke Supabase via dashboard, atau jalankan:
   ```bash
   python scripts/csv_to_seed.py knowledge_items.csv
   ```

---

## Dependency Baru untuk requirements.txt

```
pdfplumber>=0.11.0
requests>=2.32.0
beautifulsoup4>=4.12.0
lxml>=5.2.0
```
