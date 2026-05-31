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
#   Each keyword is checked via substring search (e.g. "market" matches "supermarket").
#   Keywords are unique across modules to prevent false positives.

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
        self.keyword_map = {

            # --- Module 1: Administrative & Official Processes ---
            # Covers: visa, registration, fees, insurance, lost card, official letters
            "admin_directory": [
                # visa & immigration
                "visa", "passport", "immigration", "emgs", "isao",
                "overstay", "endorsement", "student pass",
                # registration & enrollment
                "register", "registration", "registrar", "enrollment",
                "enrolled", "admission", "admissions", "admit", "application",
                # fees & payments
                "fees", "tuition", "payment", "invoice", "receipt", "pay",
                "bursary", "scholarship", "financial aid", "refund",
                # student id & official documents
                "student card", "matric", "id card", "lost card",
                "official letter", "verification", "attestation", "clearance",
                # accommodation application (official process, not daily life)
                "accommodation", "hostel application", "room application",
                # insurance
                "insurance", "coverage", "claim",
                # offices & staff contacts
                "admin", "administration", "staff", "employee",
                "directory", "contact", "international office",
                # withdrawal & deferment
                "withdrawal", "defer", "deferment", "terminate",
            ],

            # --- Module 2: Daily Campus Life ---
            # Covers: wifi, food, dorm daily life, transport, facilities, activities
            "campus_life": [
                # connectivity
                "wifi", "wi-fi", "internet", "network", "hotspot",
                # food & dining
                "food", "eat", "canteen", "cafeteria", "cafe", "restaurant",
                "meal", "halal", "vegetarian", "vegan", "drink", "hungry",
                "menu", "breakfast", "lunch", "dinner",
                # hostel & dorm daily life
                "hostel", "dorm", "dormitory", "room", "roommate", "warden",
                "curfew", "laundry", "washing", "dryer", "hostel rule",
                # transport
                "bus", "shuttle", "transport", "travel", "pickup",
                "grab", "taxi", "ride", "station",
                # shopping & outings
                "supermarket", "minimarket", "market", "mall", "shopping",
                "grocery", "outing", "entertainment", "nearby",
                # sports & fitness facilities
                "gym", "fitness", "swimming", "pool", "sports", "court",
                # money & services
                "atm", "bank", "money", "withdraw",
                "printing", "photocopy", "print", "stationery",
                # religious facilities
                "surau", "mosque", "prayer",
                # parking
                "parking", "car", "motorcycle", "bicycle", "bike",
                # health & emergency
                "clinic", "sick", "doctor", "nurse", "health",
                "emergency", "ambulance", "accident", "safety", "security",
                # activities & social life
                "club", "society", "event", "activities",
                "cultural", "performance", "concert",
            ],

            # --- Module 3: Academic Navigation ---
            # Covers: courses, exams, grades, leave, schedule, graduation
            "academic_navigation": [
                # courses & credit
                "course", "subject", "unit", "elective", "core",
                "credit", "credit hour", "add drop", "drop course",
                # timetable & schedule
                "timetable", "schedule", "class", "lecture", "tutorial", "lab",
                "academic calendar", "semester", "trimester", "term",
                # exams & assessments
                "exam", "final", "midterm", "quiz", "test", "assessment",
                "barred", "attendance",
                # grades & results
                "grade", "result", "cgpa", "gpa", "pointer", "pass", "fail",
                "repeat", "retake", "appeal", "dean",
                # assignments & submissions
                "assignment", "homework", "project", "report", "thesis",
                "dissertation", "submission", "deadline", "plagiarism",
                # academic staff
                "lecturer", "professor", "tutor", "instructor", "supervisor",
                "coordinator", "advisor",
                # library (as academic resource)
                "library", "book", "borrow", "journal", "e-resource",
                # academic leave
                "leave", "absent", "absence", "mc",
                # graduation & completion
                "graduate", "graduation", "convocation", "convo",
                "transcript", "degree", "certificate", "major", "minor",
                # internship
                "internship", "industrial", "practical", "intern", "placement",
                # department / faculty
                "department", "faculty", "syllabus", "programme",
            ],
        }

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def classify(self, message: str) -> str:
        """
        Classify the user message and return the best matching module name.

        Args:
            message: The raw user input string.

        Returns:
            One of KNOWN_MODULES or "unknown".
        """
        normalized = self._normalize(message)

        for module_name, keywords in self.keyword_map.items():
            for word in keywords:
                if word in normalized:
                    return module_name

        return "unknown"


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
        module = intent_classifier.classify(user_input)
        print(f"Module detected: {module}\n")

    print("Exiting...")