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

from chatbot.preprocessor import build_augmented_query, build_search_terms, normalize

KNOWN_MODULES = [
    "general",
    "admin_directory",
    "campus_life",
    "academic_navigation",
]

LOW_SIGNAL_CLASSIFIER_TERMS = {
    "answer",
    "answers",
    "chatbot",
    "current",
    "data",
    "information",
    "location",
    "question",
    "questions",
    "source",
    "support",
}


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
            # --- General / chatbot self-service ---
            "bot_identity": "general",
            "bot_capabilities": "general",
            "bot_functionality": "general",
            "bot_nature": "general",
            "bot_scope": "general",
            "bot_limitations": "general",
            "bot_official_status": "general",
            "bot_information_source": "general",
            "bot_accuracy": "general",
            "bot_action_limitations": "general",
            "bot_privacy": "general",
            "bot_version": "general",
            "help_request": "general",
            "clarification_request": "general",
            "language_capability": "general",
            "answer_feedback": "general",

            # --- Module 1: Administrative & Campus Directory ---
            "about_xmum": "admin_directory",
            "contact_us": "admin_directory",
            
            # --- Module 2: Daily Campus Life & Facilities ---
            "hostel_rules_maintenance": "campus_life",
            "clubs_activities": "campus_life",
            "health_safety": "campus_life",
            "facilities_services": "campus_life",
            "documents_identity": "campus_life",
            "it_connectivity": "campus_life",
            "library": "campus_life",
            "food_dining": "campus_life",
            "housing_application": "campus_life",
            
            # --- Module 3: Academic Navigation ---
            "academic_system": "academic_navigation",
            "visa_immigration": "academic_navigation",
            "postgrad_resources": "academic_navigation",
            "academic_calendar": "academic_navigation",
            "courses_syllabus": "academic_navigation",
            "finance_fees": "academic_navigation",
            "exams_grades": "academic_navigation",
            "leave_attendance": "academic_navigation",
            "admissions_enrollment": "academic_navigation",
            "internship_career": "academic_navigation",
            "programme_transfer": "academic_navigation",
            
        }


        # Fine-grained keyword mapping targeting specific sub_intents
        self.keyword_map = {
            "bot_identity": [
                "who are you", "what are you", "what is your name",
                "your name", "introduce yourself", "tell me about yourself",
                "about yourself", "xmum campus assistant"
            ],
            "bot_capabilities": [
                "what can you do", "what do you do", "how can you help",
                "capabilities", "features", "help me", "what can this chatbot do",
                "what can the chatbot do", "chatbot information",
                "chatbot info", "about this chatbot", "about the chatbot",
                "chatbot help"
            ],
            "bot_scope": [
                "what topics can you answer", "topics can you answer",
                "what can i ask about", "covered topics", "available topics",
                "chatbot scope", "answer topics", "questions can i ask",
                "main categories of questions", "categories of questions",
                "main categories", "designed to handle",
                "hostel exams food offices",
                "can you help with non-campus questions",
                "can you help with non campus questions",
                "non-campus questions", "non campus questions",
                "outside campus questions", "off topic questions",
                "general questions not about xmum", "non xmum questions"
            ],
            "bot_limitations": [
                "what can you not do", "what can't you do", "cannot do",
                "cant do", "limitations", "chatbot limitations",
                "not able to do", "things you cannot do"
            ],
            "bot_functionality": [
                "how do you work", "how does this work", "how are you built",
                "how are you made", "how does the chatbot work",
                "how does this chatbot work"
            ],
            "bot_nature": [
                "robot", "bot", "chatbot", "ai", "artificial intelligence",
                "are you human", "are you a person", "real person"
            ],
            "bot_official_status": [
                "are you an official xmum chatbot", "official xmum chatbot",
                "official chatbot", "are you official", "official assistant",
                "official source", "official xmum assistant"
            ],
            "bot_information_source": [
                "where does your information come from",
                "where do you get your information", "information source",
                "data source", "knowledge source", "source of information",
                "knowledge base", "where is your data from"
            ],
            "bot_accuracy": [
                "is your information accurate", "is your information up to date",
                "accurate information", "up to date information",
                "is your answer accurate", "are you updated",
                "how accurate are you", "current information"
            ],
            "bot_action_limitations": [
                "can you contact offices for me", "contact offices for me",
                "contact office for me", "can you contact the office",
                "can you call the office", "call office for me",
                "email office for me", "message office for me",
                "can you make bookings", "make bookings", "make a booking",
                "can you book", "book for me", "reserve for me",
                "can you reserve", "confirm reservation",
                "can you submit forms", "can you submit a form",
                "submit forms for me", "submit form for me",
                "submit application for me", "file form for me",
                "send form for me", "submit documents for me"
            ],
            "bot_privacy": [
                "can you remember my data", "remember my data",
                "remember my information", "remember me", "store my data",
                "save my data", "personal memory", "will you remember me",
                "what data do you collect", "data do you collect",
                "what information do you collect", "do you collect data",
                "privacy", "personal data", "collect my data", "chat logs"
            ],
            "bot_version": [
                "what version are you", "version", "chatbot version",
                "which version", "build version", "dataset version",
                "release version"
            ],
            "help_request": [
                "i need help", "assist me", "need assistance", "support"
            ],
            "clarification_request": [
                "i don't understand", "don't get it", "confused", "not sure",
                "unclear", "what do you mean"
            ],
            "language_capability": [
                "speak malay", "bahasa melayu", "boleh cakap melayu",
                "speak chinese", "mandarin", "putonghua", "cantonese",
                "do you support malay and chinese",
                "support malay and chinese", "support bahasa and chinese",
                "support bahasa melayu", "support chinese",
                "support mandarin", "malay and chinese",
                "multilingual support", "can i ask in chinese",
                "ask in chinese", "ask chinese", "can i use chinese",
                "can i type chinese", "can i ask in mandarin",
                "ask in mandarin", "use mandarin"
            ],
            "answer_feedback": [
                "how do i report a wrong answer", "report a wrong answer",
                "report wrong answer", "wrong answer feedback",
                "incorrect answer feedback", "report chatbot mistake",
                "report error", "feedback about answer",
                "what should i do if your answer is wrong",
                "if your answer is wrong", "your answer is wrong",
                "answer is incorrect", "wrong response",
                "incorrect response", "chatbot answer wrong",
                "what if you are wrong"
            ],
            # about_xmum (Admin Directory)
            "about_xmum": [
                "about", "founder", "motto", "vision", "mission", "history", 
                "chancellor", "president", "established", "reciprocation", 
                "financial status", "not-for-profit"
            ],
            # contact_us (Admin Directory)
            "contact_us": [
                "contact", "phone", "address", "call", "hotline", 
                "office location", "office number", "contact email",
                "office email",
                "official office hours",
                "official hours",
                "where can i find official office hours",
                "working hours",
                "counter hours",
                "parent call xmum",
                "parents contact",
                "campus visit arrangements",
                "admission fees campus visit",
                "official contact admission fees",
                "admissions contact"
            ],
            # hostel_rules_maintenance (Campus Life)
            "hostel_rules_maintenance": [
                "hostel", "dorm", "dormitory", "roommate", "warden", 
                "curfew", "laundry", "washing", "dryer", "hostel rule", 
                "aircond", "maintenance", "repair", "leak", "broken", "light", "plumbing",
                "midnight", "after midnight", "guardhouse", "room key",
                "key replacement", "room unlock", "defect", "maintenance hotline",
                "public refrigerator", "residence rule", "residence rules",
                "maintenance request", "repair request", "repair form",
                "maintenance form", "aska maintenance", "report defect",
                "maintenance website", "maintenance webpage",
                "aska",
                "laundry room",
                "where is laundry room",
                "laundry facilities",
                "public refrigerators",
                "common pantry",
                "hostel refrigerator",
                "residence refrigerator"
            ],
            # internship_career (Campus Life)
            "internship_career": [
                "internship", "industrial", "practical", "intern", "placement", 
                "career", "job", "resume", "cv", "employment", "recruitment",
                "career services", "career services office",
                "career service office", "cso",
                "career services appointment",
                "career service appointment",
                "make an appointment with the career services office",
                "appointment with the career services office",
                "career coaching appointment"
            ],
            # clubs_activities (Campus Life)
            "clubs_activities": [
                "club", "society", "event", "activities", "cultural", 
                "performance", "concert", "co-curricular", "student council", 
                "src", "student representative", "party", "gathering",
                "community", "communities", "clubs", "societies",
                "sports club", "sports clubs", "club societies",
                "club category", "club categories", "eca club",
                "performing arts", "service volunteerism",
                "international communities"
            ],
            # health_safety (Campus Life)
            "health_safety": [
                "clinic", "sick", "doctor", "nurse", "health", "emergency", 
                "ambulance", "accident", "safety", "security", "counseling", 
                "counselling", "mental", "stress", "therapist", "guard", "fire",
                "police", "helpline", "emergency helpline", "smoke", "medical",
                "medical assistance", "plux", "hospital", "insurance",
                "need help", "help on campus", "urgent help", "emergency help",
                "medical issue", "security emergency",
                "student fainted",
                "fainted",
                "student collapsed",
                "medical emergency",
                "campus emergency",
                "call security",
                "contact campus security",
                "campus security",
                "security hotline",
                "stress counselling",
                "stress counseling",
                "cannot focus",
                "mental health support",
                "counselling appointment",
                "counseling appointment"
            ],
            # facilities_services (Campus Life)
            "facilities_services": [
                "gym", "fitness", "swimming", "pool", "sport", "sports", "court", 
                "atm", "bank", "money", "withdraw", "printing", "photocopy", 
                "print", "stationery", "surau", "mosque", "prayer", "parking", 
                "car", "motorcycle", "bicycle", "bike", "gymnasium",
                "swimming pool", "sports facilities", "basketball", "badminton",
                "football", "table tennis", "tennis", "volleyball", "yoga",
                "student activity centre", "activity centre", "lifeguard",
                "student activity center", "activity center", "gym location",
                "gym hours", "gym operating hours", "operating hours",
                "gym equipment", "treadmill", "treadmills", "weights",
                "weight machines", "indoor sport centre",
                "indoor sports centre", "indoor sport center",
                "indoor sports center", "sports centre", "sports center",
                "stadium", "running track", "court booking",
                "basketball court", "badminton court", "sports equipment",
                "equipment rental", "equipment loan", "yoga room",
                "space booking", "room booking", "e-services", "linc",
                "parking sticker", "vehicle registration", "visitor parking",
                "facility", "facilities", "campus facilities",
                "use facilities", "facility information", "booking",
                "reservation", "book facility", "book space",
                "print shop", "a1-g", "atm", "atms", "maybank", "public bank",
                "icbc", "banking", "ablution", "prayer room",
                "vehicle parking"
            ],
            # documents_identity (Campus Life)
            "documents_identity": [
                "student card", "matric", "id card", "lost card", "student id", 
                "replacement card", "campus ecard", "ecard", "campus id",
                "student verification", "lost and found", "campus id password",
                "campus id card", "student id card", "ecard replacement",
                "replacement fee", "b1-107", "student affairs office",
                "parcel", "parcel collection", "collect parcel",
                "mail collection", "delivery", "student card"
            ],
            # it_connectivity (Campus Life)
            "it_connectivity": [
                "wifi", "wi-fi", "internet", "network", "hotspot", "portal", 
                "student email", "email account", "it helpdesk", "it services", 
                "wifi password", "captive portal", "campus email", "outlook",
                "teams", "office 365", "moodle", "aska", "cas",
                "password reset", "forgot password", "reset password",
                "account password", "email password",
                "wifi connection problem",
                "wi-fi connection problem",
                "student id wifi",
                "campus id wifi",
                "student wifi problem",
                "network login",
                "student email login",
                "login student email",
                "campus email login",
                "microsoft 365",
                "microsoft office portal"
            ],
            # library (Campus Life)
            "library": [
                "library", "borrow book", "borrow books", "journal", "e-resource", 
                "librarian", "study room", "return book", "return books",
                "opac", "makerspace", "document delivery", "printing", "print",
                "computer", "turnitin", "discussion room",
                "renew borrowed book",
                "renew a borrowed book",
                "renew book",
                "library renewal",
                "borrowed book renewal",
                "extend book loan"
            ],
            "food_dining": [
                "food", "eat", "canteen", "cafeteria", "cafe", "restaurant", 
                "meal", "halal", "vegetarian", "vegan", "drink", "hungry", 
                "menu", "breakfast", "lunch", "dinner", "chinese", "muslim",
                "korean", "japanese", "indian", "western", "muslim food",
                "korean food", "japanese food", "indian food", "western food",
                "food stall", "dining hall", "where to eat", "cafeteria feedback",
                "order food", "food order", "meal order", "chicken rice",
                "middle east", "middle eastern", "central asian", "asian cuisine",
                "malaysian food", "local food", "thai food", "nyonya", "sichuan",
                "hong kong food", "muslim friendly", "muslim-friendly",
                "pork free", "pork-free", "lanzhou", "ramen", "sushi", "bento",
                "poke bowl", "hot plate", "korean cuisine", "mala", "hotpot",
                "hot pot", "wanton mee", "wantan mee", "pan mee", "rice noodles",
                "dimsum", "dim sum", "yong taufu", "malatang", "bbq", "bakery",
                "dessert", "coffee", "milk tea", "fruit", "juice", "snack",
                "snacks", "under tree", "canteen hours", "cafeteria hours",
                "operation hours", "opening hours", "business hours",
                "off day", "closed day", "canteen location",
                "cafeteria location", "stall location", "food court",
                "dining", "food recommendation", "recommend food",
                "chinese food recommendation", "western food recommendation",
                "japanese food recommendation", "korean food recommendation",
                "middle eastern food", "halal food", "muslim-friendly food",
                "vegetarian food", "coffee shop", "dessert shop",
                "lunch suggestion",
                "dinner suggestion",
                "eat lunch",
                "eat dinner",
                "canteen meal",
                "cafeteria meal"
            ],
            "housing_application": [
                "accommodation", "hostel application", "room application", "move in",
                "move out", "swap room", "move", "move to d", "move to ly",
                "swap roommate", "room type", "twin sharing", "block d",
                "block ly", "rental", "residence application",
                "student residence", "student residences", "residence booking",
                "booking fee", "residence booking fee"
            ],

            # academic_system (Academic Navigation)
            "academic_system": [
                "ac system", "academic affairs online system",
                "academic online system", "academic system",
                "student portal", "xmum portal", "campus id",
                "campusid", "central authentication service", "cas",
                "academic services", "student profile", "academic records",
                "degree progress", "student handbook", "student handbooks",
                "download handbook", "system login", "login ac",
                "ac login", "forgot password", "password reset",
                "reset campus id", "reset campusid", "campusid service platform"
            ],
            # visa_immigration (Academic Navigation)
            "visa_immigration": [
                "visa", "passport", "immigration", "emgs", "isao", "overstay", 
                "endorsement", "student pass", "international student office",
                "international student", "international students", "eval",
                "visa approval letter", "sev", "evisa", "student visa",
                "i-kad", "ikad", "mdac", "medical screening",
                "part-time work", "work part-time", "checkout memo",
                "com", "visa cancellation", "visa renewal",
                "emgs status",
                "emgs status stuck",
                "emgs status has not moved",
                "student pass expiry",
                "visa status delayed"
            ],
            # postgrad_resources (Academic Navigation)
            "postgrad_resources": [
                "postgraduate", "postgrad", "master", "phd", "doctorate", 
                "ph d", "thesis", "dissertation", "supervisor", "research",
                "viva", "viva voce", "psu", "proposal defence",
                "mixed mode", "coursework mode"
            ],
            # academic_calendar (Academic Navigation)
            "academic_calendar": [
                "academic calendar", "calendar", "semester calendar",
                "semester break", "sem break", "term break", "term dates",
                "semester dates", "semester", "teaching week",
                "revision week", "study week", "examination week",
                "exam week", "registration days", "orientation day",
                "february semester", "april semester", "september semester",
                "sep semester"
            ],
            # courses_syllabus (Academic Navigation)
            "courses_syllabus": [
                "course", "subject", "unit", "elective", "core", "credit", 
                "credit hour", "add drop", "drop course", "syllabus", 
                "course registration", "course enrollment", "course enrolment",
                "register course", "register courses", "add course",
                "add courses", "drop courses", "add/drop", "add or drop",
                "course offering", "course offerings", "class schedule",
                "study plan", "academic advisor", "academic coordinator",
                "programme", "department", "faculty", "curriculum",
                "credit hours",
                "credit hours needed",
                "how many credit hours do i need",
                "course handbook",
                "programme handbook",
                "study plan credit hours"
            ],
            # finance_fees (Academic Navigation)
            "finance_fees": [
                "fees", "tuition", "payment", "invoice", "receipt", "pay", 
                "bursary", "scholarship", "financial aid", "refund", "ptptn", 
                "loan", "sponsor",
                "tuition fees",
                "pay tuition fees",
                "tuition payment",
                "fee payment",
                "payment methods",
                "apply scholarship",
                "scholarship application",
                "ptptn loan",
                "ptptn application",
                "ptptn enquiries"
            ],
            # exams_grades (Academic Navigation)
            "exams_grades": [
                "exam", "final", "midterm", "quiz", "test", "assessment", 
                "barred", "grade", "result", "cgpa", "gpa", "pointer", 
                "pass", "fail", "repeat", "retake", "appeal", "dean", 
                "transcript", "degree", "certificate", "graduation", 
                "convocation", "convo", "exam timetable", "exam schedule",
                "final assessment deferment", "defer exam", "deferment form",
                "appeal form", "review of marks", "exam emergency"
            ],
            # leave_attendance (Academic Navigation)
            "leave_attendance": [
                "leave", "absent", "absence", "mc", "medical certificate", 
                "attendance", "attendance policy", "apply leave", "sick leave",
                "leave application", "e-services", "eservices",
                "supporting documents", "death certificate", "family emergency",
                "attendance record", "digital attendance", "attendance sheet",
                "facial recognition", "location scanning"
            ],
            # admissions_enrollment (Academic Navigation)
            "admissions_enrollment": [
                "admission", "enrollment", "registration", "enrol", 
                "register", "intake", "orientation",
                "intakes",
                "available intakes",
                "what intakes are available",
                "offer letter",
                "offer letter next steps",
                "received offer letter",
                "after offer letter",
                "acceptance form",
                "new student registration"
            ],
            # programme_transfer (Academic Navigation)
            "programme_transfer": [
                "change programme", "change program", "change course",
                "programme transfer", "program transfer", "transfer programme",
                "transfer program", "switch programme", "switch program",
                "change study programme", "new programme", "new program",
                "credit transfer", "entry requirements"
            ]
        }
    # Pass sub_intent through to the retriever.
    def _normalize(self, text: str) -> str:
        return build_augmented_query(text)

    def _keyword_matches(self, keyword: str, normalized_message: str) -> bool:
        normalized_keyword = normalize(keyword)
        if not normalized_keyword:
            return False

        pattern = r"\b" + re.escape(normalized_keyword) + r"\b"
        return bool(re.search(pattern, normalized_message))

    def _keyword_score(
        self,
        keyword: str,
        normalized_message: str,
        search_terms: set[str],
    ) -> float:
        """Score one configured keyword against the whole user message."""
        normalized_keyword = normalize(keyword)
        if not normalized_keyword:
            return 0.0

        if self._keyword_matches(normalized_keyword, normalized_message):
            token_count = len(normalized_keyword.split())
            return 3.0 + (0.5 * max(token_count - 1, 0))

        keyword_terms = {
            term for term in build_search_terms(normalized_keyword)
            if term not in LOW_SIGNAL_CLASSIFIER_TERMS
        }
        search_terms = {
            term for term in search_terms
            if term not in LOW_SIGNAL_CLASSIFIER_TERMS
        }
        overlap = keyword_terms & search_terms
        if not overlap:
            return 0.0

        # Partial overlap is useful for long natural-language questions, but
        # should not overpower exact phrase matches such as "student card".
        return 0.75 * len(overlap)

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
        search_terms = set(build_search_terms(message))

        if normalize(message) == "aska":
            return "campus_life", "hostel_rules_maintenance"

        best_sub_intent = "unknown"
        best_score = 0.0

        for sub_intent, keywords in self.keyword_map.items():
            score = sum(
                self._keyword_score(word, normalized, search_terms)
                for word in keywords
            )
            if score > best_score:
                best_score = score
                best_sub_intent = sub_intent

        if best_score > 0:
            module_name = self.sub_intent_to_module.get(best_sub_intent, "unknown")
            return module_name, best_sub_intent

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
