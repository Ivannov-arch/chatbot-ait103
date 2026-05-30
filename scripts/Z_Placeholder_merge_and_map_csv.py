# scripts/merge_and_map_csv.py
import glob
import csv
import json
import os
import pathlib

def clean_value(val):
    if val is None:
        return ""
    # Strip whitespace and remove any zero-width spaces or odd characters
    return val.strip().replace('\u200b', '')

def map_module(row):
    original = row.get('module', '').strip()
    question = row.get('question', '').lower()
    
    # Special handling for mixed xmum_handbook_ocr
    if original == 'xmum_handbook_ocr':
        if any(w in question for w in ['motto', 'vision', 'mission', 'full name', 'history', 'chancellor', 'president']):
            return 'admin_directory'
        elif any(w in question for w in ['semester', 'exam', 'week', 'calendar', 'date', 'gpa', 'cgpa', 'credit', 'course', 'grade', 'admission', 'fee', 'register', 'orientation']):
            return 'academic_navigation'
        else:
            return 'campus_life'
            
    # General mapping based on filename-derived module
    mapping = {
        'about_xmum': 'admin_directory',
        'contact_us': 'admin_directory',
        'accommodation': 'campus_life',
        'accommodation_faq': 'campus_life',
        'career_services': 'campus_life',
        'clubs_societies': 'campus_life',
        'counseling': 'campus_life',
        'facilities': 'campus_life',
        'student_activities': 'campus_life',
        'student_affairs': 'campus_life',
        'student_card': 'campus_life',
        'student_email': 'campus_life',
        'it_policy': 'campus_life',
        'it_services': 'campus_life',
        'wifi_network': 'campus_life',
        'library': 'campus_life',
        'international_handbook': 'academic_navigation',
        'postgrad_handbook': 'academic_navigation',
        'programmes': 'academic_navigation',
        'scholarship': 'academic_navigation',
    }
    
    return mapping.get(original, 'campus_life')

def main():
    target_dir = "database/seeds"
    csv_files = glob.glob(os.path.join(target_dir, "*_qa.csv"))
    
    if not csv_files:
        print("No *_qa.csv files found!")
        return

    # Categorized lists for JSON
    data = {
        'admin_directory': [],
        'campus_life': [],
        'academic_navigation': []
    }
    
    total_processed = 0
    combined_rows = []
    
    for file_path in csv_files:
        # Avoid self-processing a combined CSV file
        if "combined" in os.path.basename(file_path):
            continue
            
        print(f"Processing: {file_path}")
        
        encodings = ['utf-8-sig', 'utf-16']
        content = None
        for enc in encodings:
            try:
                with open(file_path, mode='r', encoding=enc) as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    content = rows
                    break
            except Exception:
                continue
                
        if content is None:
            print(f"Failed to read: {file_path}")
            continue
            
        for row in content:
            # Skip rows without essential data
            if not row.get('question') or not row.get('answer'):
                continue
                
            mapped_mod = map_module(row)
            
            # Clean keywords
            keywords_raw = row.get('keywords', '')
            keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]
            
            # 1. Structure for JSON files
            item = {
                'module': mapped_mod,
                'question': clean_value(row['question']),
                'answer': clean_value(row['answer']),
                'keywords': keywords
            }
            data[mapped_mod].append(item)
            
            # 2. Structure for Combined CSV (with keywords kept as string)
            csv_item = {
                'module': mapped_mod,
                'question': clean_value(row['question']),
                'answer': clean_value(row['answer']),
                'keywords': ",".join(keywords)
            }
            combined_rows.append(csv_item)
            
            total_processed += 1

    # Save to individual JSON files (strictly matching the database schema modules)
    for module, items in data.items():
        out_path = os.path.join(target_dir, f"{module}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(items)} items to {out_path}")
        
    # Save combined CSV for direct Supabase Dashboard upload if needed
    combined_csv_path = os.path.join(target_dir, "combined_knowledge_items.csv")
    with open(combined_csv_path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['module', 'question', 'answer', 'keywords'])
        writer.writeheader()
        writer.writerows(combined_rows)
    print(f"Saved combined CSV to {combined_csv_path}")
        
    print(f"\nDone! Successfully processed and mapped {total_processed} Q&A items.")

if __name__ == "__main__":
    main()
