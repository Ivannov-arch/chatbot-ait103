# chatbot/intent_classifier.py
#
# Intent Classifier — maps a user message to one of three knowledge modules:
#   - "admin_directory"       (Module 1)
#   - "campus_life"           (Module 2)
#   - "academic_navigation"   (Module 3)
#   - "unknown"               (fallback)
#
# Approach:
#   Keyword / rule-based matching — most reliable for a pure retrieval chatbot.
#   Each keyword is checked as a whole word/phrase to avoid false positives
#   like "intern" matching inside "internet".
#   Keywords are unique across modules to prevent false positives.

import re

from chatbot.preprocessor import build_augmented_query, normalize

KNOWN_MODULES = [
    "admin_directory",
    "campus_life",
    "academic_navigation",
]


class IntentClassifier:
    def __init__(self):
        # Dictionary of keywords mapping to modules.
        # Format: { "module_name": [keyword1, keyword2, ...] }
        # Rules:
        #   - All keywords are LOWERCASE.
        #   - Each keyword must appear in ONLY ONE module (no duplicates across modules).
        #   - Modules are checked in order: admin → campus_life → academic.

        # Maps each fine-grained sub_intent to its parent module
        self.sub_intent_to_module = {
            # --- Module 1: Administrative & Campus Directory ---
            "about_xmum": "admin_directory",
            "contact_us": "admin_directory",
            
            # --- Module 2: Daily Campus Life & Facilities ---
            "hostel_rules_maintenance": "campus_life",
            "internship_career": "campus_life",
            "clubs_activities": "campus_life",
            "health_safety": "campus_life",
            "facilities_services": "campus_life",
            # "documents_identity": "campus_life",
            "it_connectivity": "campus_life",
            "library": "campus_life",
            "food_dining": "campus_life",
            "housing_application": "campus_life",
            
            # --- Module 3: Academic Navigation ---
            "visa_immigration": "academic_navigation",
            "postgrad_resources": "academic_navigation",
            "courses_syllabus": "academic_navigation",
            "finance_fees": "academic_navigation",
            "exams_grades": "academic_navigation",
            "leave_attendance": "academic_navigation",
            "admissions_enrollment": "academic_navigation",
            "internship_career": "academic_navigation",
            "documents_identity": "academic_navigation",
            
        }


        # Fine-grained keyword mapping targeting specific sub_intents
        self.keyword_map = {
            # about_xmum (Admin Directory)
            "about_xmum": [
                "about", "founder", "motto", "vision", "mission", "history", 
                "chancellor", "president", "established", "reciprocation", 
                "financial status", "not-for-profit"
            ],
            # contact_us (Admin Directory)
            "contact_us": [
                "contact", "phone", "email", "address", "call", "hotline", 
                "office location", "office number"
            ],
            # hostel_rules_maintenance (Campus Life)
            "hostel_rules_maintenance": [
                "hostel", "dorm", "dormitory", "room", "roommate", "warden", 
                "curfew", "laundry", "washing", "dryer", "hostel rule", 
                "aircond", "maintenance", "repair", "leak", "broken", "light", "plumbing"
            ],
            # internship_career (Campus Life)
            "internship_career": [
                "internship", "industrial", "practical", "intern", "placement", 
                "career", "job", "resume", "cv", "employment", "recruitment"
            ],
            # clubs_activities (Campus Life)
            "clubs_activities": [
                "club", "society", "event", "activities", "cultural", 
                "performance", "concert", "co-curricular", "student council", 
                "src", "student representative", "party", "gathering"
            ],
            # health_safety (Campus Life)
            "health_safety": [
                "clinic", "sick", "doctor", "nurse", "health", "emergency", 
                "ambulance", "accident", "safety", "security", "counseling", 
                "counselling", "mental", "stress", "therapist", "guard", "fire"
            ],
            # facilities_services (Campus Life)
            "facilities_services": [
                "gym", "fitness", "swimming", "pool", "sports", "court", 
                "atm", "bank", "money", "withdraw", "printing", "photocopy", 
                "print", "stationery", "surau", "mosque", "prayer", "parking", 
                "car", "motorcycle", "bicycle", "bike"
            ],
            # documents_identity (Campus Life)
            "documents_identity": [
                "student card", "matric", "id card", "lost card", "student id", 
                "replacement card"
            ],
            # it_connectivity (Campus Life)
            "it_connectivity": [
                "wifi", "wi-fi", "internet", "network", "hotspot", "portal", 
                "student email", "email account", "it helpdesk", "it services", 
                "wifi password", "captive portal"
            ],
            # library (Campus Life)
            "library": [
                "library", "book", "borrow", "journal", "e-resource", 
                "librarian", "study room", "return book"
            ],
            "food_dining": [
                "food", "eat", "canteen", "cafeteria", "cafe", "restaurant", 
                "meal", "halal", "vegetarian", "vegan", "drink", "hungry", 
                "menu", "breakfast", "lunch", "dinner", "chinese", "muslim",
                "korean", "japanese", "indian", "western", "muslim food",
                "korean food", "japanese food", "indian food", "western food",
            ],
            "housing_application": [
                "accommodation", "hostel application", "room application", "move in",
                "move out", "swap room", "move", "move to D", "Move to LY", "swap roommate"
            ],

            # visa_immigration (Academic Navigation)
            "visa_immigration": [
                "visa", "passport", "immigration", "emgs", "isao", "overstay", 
                "endorsement", "student pass", "international student office"
            ],
            # postgrad_resources (Academic Navigation)
            "postgrad_resources": [
                "postgraduate", "postgrad", "master", "phd", "doctorate", 
                "thesis", "dissertation", "supervisor", "research", "viva"
            ],
            # courses_syllabus (Academic Navigation)
            "courses_syllabus": [
                "course", "subject", "unit", "elective", "core", "credit", 
                "credit hour", "add drop", "drop course", "syllabus", 
                "programme", "department", "faculty", "curriculum"
            ],
            # finance_fees (Academic Navigation)
            "finance_fees": [
                "fees", "tuition", "payment", "invoice", "receipt", "pay", 
                "bursary", "scholarship", "financial aid", "refund", "ptptn", 
                "loan", "sponsor"
            ],
            # exams_grades (Academic Navigation)
            "exams_grades": [
                "exam", "final", "midterm", "quiz", "test", "assessment", 
                "barred", "grade", "result", "cgpa", "gpa", "pointer", 
                "pass", "fail", "repeat", "retake", "appeal", "dean", 
                "transcript", "degree", "certificate", "graduation", 
                "convocation", "convo"
            ],
            # leave_attendance (Academic Navigation)
            "leave_attendance": [
                "leave", "absent", "absence", "mc", "medical certificate", 
                "attendance", "attendance policy", "apply leave", "sick leave"
            ],
            # admissions_enrollment (Academic Navigation)
            "admissions_enrollment": [
                "admission", "enrollment", "registration", "enrol", 
                "register", "intake", "orientation"
            ]
        }
    # Teruskan sub_intent ke retriever
    def _normalize(self, text: str) -> str:
        return build_augmented_query(text)

    def _keyword_matches(self, keyword: str, normalized_message: str) -> bool:
        normalized_keyword = normalize(keyword)
        if not normalized_keyword:
            return False

        pattern = r"\b" + re.escape(normalized_keyword) + r"\b"
        return bool(re.search(pattern, normalized_message))

    def classify(self, message: str) -> tuple[str, str]:
        """
        Classify the user message and return the best matching module name.

        Args:
            message: The raw user input string.

        Returns:
            A (module, sub_intent) tuple. Module is one of KNOWN_MODULES or
            "unknown"; sub_intent is a fine-grained category or "unknown".
        """
        normalized = self._normalize(message)

        for sub_intent, keywords in self.keyword_map.items():
            for word in keywords:
                if self._keyword_matches(word, normalized):
                    module_name = self.sub_intent_to_module.get(sub_intent, "unknown")
                    return module_name, sub_intent

        return "unknown", "unknown"


if __name__ == "__main__":
    intent_classifier = IntentClassifier()

    print("Intent Classifier — Interactive Test")
    print("=====================================")
    print("Type your question. Type 'quit' or 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            break
        module, sub_intent = intent_classifier.classify(user_input)
        print(f"Module detected: {module}\n")
        print(f"Sub-intent detected: {sub_intent}\n")
    print("Exiting...")
