# scripts/extract_pdf.py
# Extract the raw text from the PDF handbook to a .txt file
# Run: python scripts/extract_pdf.py "XMUM_Handbook.pdf" campus_life

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
                all_text.append(f"\n=== HALAMAN {i + 1} ===\n{text}")

    raw = "\n".join(all_text)
    output_file.write_text(raw, encoding="utf-8")
    print(f"✅ Tersimpan: {output_file}  ({len(raw):,} karakter)")


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "handbook.pdf"
    output_name = sys.argv[2] if len(sys.argv) > 2 else "raw_output"
    extract_pdf_text(pdf_path, output_name)
