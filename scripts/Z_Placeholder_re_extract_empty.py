# scripts/re_extract_empty.py
import requests
from bs4 import BeautifulSoup
import os

URLS = {
    "admission_faq_raw.txt": "https://www.xmu.edu.my/admissions/faq",
    "scholarship_raw.txt": "https://www.xmu.edu.my/admissions/scholarships-financial-aid",
    "programmes_raw.txt": "https://www.xmu.edu.my/undergraduate-programmes",
    "student_activities_raw.txt": "https://www.xmu.edu.my/campus-life/eca",
    "it_services_raw.txt": "https://linc.xmu.edu.my/it-service-policy/",
    "facilities_raw.txt": "https://www.xmu.edu.my/about-us", # fallback to about-us for basic info if no specific facilities page
    "student_affairs_raw.txt": "https://www.xmu.edu.my/campus-life/student-helpdesk" # fallback to student helpdesk which contains student affairs info
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def extract_web_text(filename, url):
    dest_path = os.path.join("database/seeds", filename)
    print(f"Scraping: {url} -> {dest_path}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
            
        lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
        content = "\n".join(lines)
        
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Successfully wrote {len(content)} characters to {dest_path}")
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

def main():
    print("Starting re-extraction of empty web pages...")
    for filename, url in URLS.items():
        extract_web_text(filename, url)
    print("Done!")

if __name__ == "__main__":
    main()
