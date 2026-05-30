# scripts/check_urls.py
import requests

URLS = {
    "about_us": "https://www.xmu.edu.my/about-us",
    "contact_us": "https://www.xmu.edu.my/contact-us",
    "admission_faq": "https://www.xmu.edu.my/admissions/faq",
    "scholarship": "https://www.xmu.edu.my/admissions/scholarships-financial-aid",
    "foundation_programmes": "https://www.xmu.edu.my/foundation-programmes",
    "undergraduate_programmes": "https://www.xmu.edu.my/undergraduate-programmes",
    "postgraduate_programmes": "https://www.xmu.edu.my/postgraduate-programmes",
    "campus_life_eca": "https://www.xmu.edu.my/campus-life/eca",
    "clubs_societies": "https://www.xmu.edu.my/campus-life/eca/club-societies",
    "counseling": "https://www.xmu.edu.my/campus-life/counseling-centre",
    "accommodation": "https://www.xmu.edu.my/campus-life/accommodation-services",
    "accommodation_faq": "https://www.xmu.edu.my/campus-life/accommodation-services/accommodation-faq",
    "career_services": "https://www.xmu.edu.my/career-services",
    "student_helpdesk": "https://www.xmu.edu.my/campus-life/student-helpdesk",
    "student_handbook": "https://www.xmu.edu.my/campus-life/student-handbook",
    "library": "https://linc.xmu.edu.my/",
    "it_services": "https://linc.xmu.edu.my/it-service-policy/",
    "campus_id_ecard": "https://linc.xmu.edu.my/campus-id-ecard/",
    "campus_email": "https://linc.xmu.edu.my/campus-email/",
    "network_connectivity": "https://linc.xmu.edu.my/network-connectivity/"
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def check_url(name, url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        print(f"[{name}] Status: {res.status_code} | Final URL: {res.url} | Size: {len(res.text)} bytes")
    except Exception as e:
        print(f"[{name}] Error requesting {url}: {e}")

def main():
    print("Checking URL availability for XMUM Web Extract...")
    for name, url in URLS.items():
        check_url(name, url)

if __name__ == "__main__":
    main()
