# placeholder_modules.md
# docs/modules.md

# Knowledge Modules — XMUM Campus Chatbot

The chatbot's knowledge is divided into three focused modules.
Each module maps to a subset of rows in the `knowledge_items` Supabase table.

---

## Module 1 — Administrative & Campus Directory

**Module key:** `admin_directory`

| Topic                       | What it covers                                              |
|-----------------------------|-------------------------------------------------------------|
| International & Student Affairs | Office location, working hours, email/contact          |
| Registration & Payment      | Official portal links, payment methods, anti-scam tips      |
| Accommodation Services      | Housing office location, working hours, contact details     |

**Sample questions handled:**
- "Where is the International Affairs office?"
- "How do I register for a course?"
- "How do I pay my tuition fees?"
- "Where is the accommodation/housing office?"

---

## Module 2 — Daily Campus Life & Facilities

**Module key:** `campus_life`

| Topic                  | What it covers                                                       |
|------------------------|----------------------------------------------------------------------|
| Wi-Fi Connection       | SSID, captive portal login steps, troubleshooting                    |
| Canteen Guidance       | Locations, opening hours, food types (Chinese, Western, Halal, veg)  |
| Accommodation Guidance | Hostel rules, maintenance request SOP                                |
| Library Services       | Opening hours, borrowing rules, borrow/return SOP                    |

**Sample questions handled:**
- "How do I connect to campus Wi-Fi?"
- "Where is the canteen? What halal food is available?"
- "What are the hostel rules?"
- "How do I submit a maintenance request for my room?"
- "What time does the library open/close?"
- "How do I borrow a book from the library?"

---

## Module 3 — Academic Navigation

**Module key:** `academic_navigation`

| Topic             | What it covers                                                    |
|-------------------|-------------------------------------------------------------------|
| AC System         | Login instructions, main features (grades, timetable, courses)   |
| Leave Application | How to apply for leave; note: only accessible on campus network  |
| Academic Calendar | How to download the official school calendar (PDF)               |

**Sample questions handled:**
- "How do I log in to the AC system?"
- "How do I apply for leave?"
- "Where can I download the academic calendar?"

---

## Out of Scope

The chatbot does **not** handle:
- Complex or personalised academic consulting
- Financial aid calculations
- Grievance submissions
- Any topic outside the three modules above
- Non-English questions

When a question is out of scope, the chatbot responds with a polite fallback message directing the student to the relevant XMUM office.

---

## Adding New Knowledge

To add new Q&A pairs:
1. Open the relevant seed file in `database/seeds/`
2. Add a new JSON object with `module`, `question`, `answer`, and `keywords`
3. Re-run `python -m database.seed` to upsert the new data
