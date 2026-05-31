# XMUM Campus Chatbot — Linear Project Plan

## Overview

6 Roles → 4 Batches (Sprints) → ~30 Linear Issues

Each team member is assigned a main role (based on the rubric) and a main technical file for which they are fully responsible.
The `Z_Placeholder_` file remains available for reference — not for copying and pasting,
but for understanding the flow and rewriting with your own understanding.

---

## 👥 Role → Member → Main File Mapping

| # | Role (Rubrik) | Owned Main File |
|---|----------------------------------------------------------------------------|---------------------------------------------------------------------|
| 1 | **Intent Recognition** | `chatbot/intent_classifier.py` |
| 2 | **Entity Extraction** | `chatbot/preprocessor.py` *(new file)* |
| 3 | **Response Matching & Retrieval** | `chatbot/retriever.py`, `database/client.py`, `database/schema.sql` |
| 4 | **Context & Session Management** | `chatbot/context_manager.py` |
| 5 | **Fallback Handling & Response Generation** | `chatbot/responder.py`, `chatbot/bot.py`, `chatbot/main.py` |
| 6 | **NLP & Text Preprocessing** | `database/seeds/*.json`, `database/seed.py`, keyword normalization |

---

## 🗂️ Dataset: Who is Responsible?

> **Dataset Lead: Role 6 — NLP & Text Preprocessing**

### Why Role 6?
Since this chatbot is **Pure Retrieval-Based**, the quality of the dataset (`.json` file in `database/seeds/`) is the most critical component. It's not the model, but the data that determines the bot's intelligence. Role 6 best understands:
- How keywords should be normalized for easy matching.
- The correct JSON format for processing by `seed.py`.
- Consistency of data structures across modules.

### Each Member's Contribution to the Dataset:
While Role 6 **leads and curates**, each member is **required to contribute content** from their module area:

| Who | Contributes Content to |
|---------------------------------------|
| Role 1 (Intent) | List of keywords per module for the `intent_classifier.py` file |
| Role 2 (Entity) | List of synonyms (e.g., "wifi" = "internet" = "network") |
| Role 3 (Retrieval) | Ensure JSON seed is compatible with Supabase queries |
| Role 4 (Context) | Example multi-turn Q&A to test the context |
| Role 5 (Fallback) | List of questions that should trigger the fallback |
| Role 6 (NLP Lead) | **Final curation, formatting, review, and upload to Supabase** |

---

## 🚀 Batch 0 — Setup & Onboarding *(All Members, Week 1)*

Everyone completes this in **parallel** and **independently**.
This is a *pre-condition* before Batch 1 can begin.

### Linear Issues (Assigned to Everyone):

```
[SETUP-1] Clone the repo and create a Python virtual environment
[SETUP-2] Create a .env file from .env.example, fill it with your Supabase team key
[SETUP-3] Install requirements.txt and verify there are no errors
[SETUP-4] Read your own Z_Placeholder_ file (30 minutes)
[SETUP-5] Read README.md from start to finish
[SETUP-6] Create a Supabase account (if you don't have one) and join the project
```

> ⚠️ **CRITICAL**: Batch 1 must not start until everyone has completed SETUP.

---

## 🏗️ Batch 1 — Foundation Layer *(Weeks 1-2)*

This batch builds the database foundation. **Role 3 and Role 6 are the leaders.**
Other members may begin researching and designing their module logic on paper.

### Role 3 — Response Matching & Retrieval

```
[DB-1] Read and understand Z_Placeholder_schema.sql
[DB-2] Write schema.sql from scratch (knowledge_items + conversation_logs tables)
[DB-3] Run schema.sql in Supabase SQL Editor and screenshot the results
[DB-4] Read and understand Z_Placeholder_client.py
[DB-5] Implement database/client.py (get_client() function)
[DB-6] Test Supabase connection: python -c "from database.client import get_client; print(get_client())"
```

### Role 6 — NLP & Text Preprocessing (Dataset Lead)

```
[DATA-1] Collect Module 1 (Admin Directory) information from Student Handbook XMUM
[DATA-2] Collect Module 2 (Campus Life) information from Student Handbook XMUM
[DATA-3] Gather information for Module 3 (Academic Navigation) from the official XMUM website
[DATA-4] Write admin_directory.json (min. 8 Q&A pairs, complete with keywords)
[DATA-5] Write campus_life.json (min. 10 Q&A pairs)
[DATA-6] Write academic_navigation.json (min. 6 Q&A pairs)
[DATA-7] Read and understand Z_Placeholder_seed.py
[DATA-8] Implement database/seed.py
[DATA-9] Test: python -m database.seed → verify data entry into Supabase
```

### Other Members (Batch 1 Side Task):
```
[PLAN-1] Role 1: Draft a keyword dictionary for the 3 modules (on paper/Notion)
[PLAN-2] Role 2: Draft a list of synonyms for keywords (wifi=internet, hostel=dorm, etc.)
[PLAN-3] Role 4: Design the session data structure (dict format to be saved)
[PLAN-4] Role 5: Design the fallback message and final response format to the user
```

---

## ⚙️ Batch 2 — Core Logic *(Weeks 2-3)*

This batch builds the database foundation. **Roles 3 and 6 are the leaders.**
Other members may begin research and design their module logic on paper.

### Role 3 — Response Matching & Retrieval

```
[DB-1] Read and understand Z_Placeholder_schema.sql
[DB-2] Write schema.sql from scratch (knowledge_items + conversation_logs tables)
[DB-3] Run schema.sql in Supabase SQL Editor and screenshot the results
[DB-4] Read and understand Z_Placeholder_client.py
[DB-5] Implement database/client.py (get_client() function)
[DB-6] Test Supabase connection: python -c "from database.client import get_client; print(get_client())"
```

### Role 6 — NLP & Text Preprocessing (Dataset Lead)

```
[DATA-1] Collect Module 1 (Admin Directory) information from Student Handbook XMUM
[DATA-2] Collect Module 2 (Campus Life) information from Student Handbook XMUM
[DATA-3] Gather information for Module 3 (Academic Navigation) from the official XMUM website
[DATA-4] Write admin_directory.json (min. 8 Q&A pairs, complete with keywords)
[DATA-5] Write campus_life.json (min. 10 Q&A pairs)
[DATA-6] Write academic_navigation.json (min. 6 Q&A pairs)
[DATA-7] Read and understand Z_Placeholder_seed.py
[DATA-8] Implement database/seed.py
[DATA-9] Test: python -m database.seed → verify data entry into Supabase
```

### Other Members (Batch 1 Side Task):
```
[PLAN-1] Role 1: Draft a keyword dictionary for the 3 modules (on paper/Notion)
[PLAN-2] Role 2: Draft a list of synonyms for keywords (wifi=internet, hostel=dorm, etc.)
[PLAN-3] Role 4: Design the session data structure (dict format to be saved)
[PLAN-4] Role 5: Design the fallback message and final response format to the user
```

---

## ⚙️ Batch 2 — Core Logic *(Weeks 2-3)*

This batch is the heart of the project. Everyone works on their core files in parallel.

There are no direct dependencies between roles in this batch, except for Role 5, which requires output from Roles 1, 2, and 3.

### Role 1 — Intent Recognition

```
[INTENT-1] Read Z_Placeholder_intent_classifier.py and understand the flow.
[INTENT-2] Define the dictionary KEYWORD_MAP: {module_name: [list of keywords]}
Use the draft from PLAN-1 as a basis.
[INTENT-3] Implement the function classify(message: str) -> str
Logic: lowercase input → check each word → return matching module → fallback "unknown"
[INTENT-4] Manual test in the terminal:
python -c "from chatbot.intent_classifier import IntentClassifier; ic = IntentClassifier(); print(ic.classify('where is the library'))"
[INTENT-5] Ensure the test is tests/test_intent_classifier.py passed (uncomment & run pytest)
```

### Role 2 — Entity Extraction

```
[ENTITY-1] Create a new file: chatbot/preprocessor.py (no Z_Placeholder, this is original!)
[ENTITY-2] Implement the function normalize(text: str) -> str
(lowercase, strip whitespace, remove punctuation)
[ENTITY-3] Implement the function extract_keywords(text: str) -> list[str]
(break the sentence into relevant keywords, remove stopwords)
[ENTITY-4] Create a SYNONYM_MAP from the draft PLAN-2:
{"internet": "wifi", "dorm": "hostel", "borrow": "loan", ...}
[ENTITY-5] Implement the function expand_synonyms(keywords: list[str]) -> list[str]
[ENTITY-6] Manual test: verify "how do I connect to the internet" → ["wifi", "connect", "campus"]
```

### Role 3 — Response Matching & Retrieval

```
[RETRIEVAL-1] Read Z_Placeholder_retriever.py and understand the ILIKE vs. FTS strategy
[RETRIEVAL-2] Implement Retriever.search() using ILIKE matching first
(simple: search in the 'keywords' or 'question' column)
[RETRIEVAL-3] Test search with seeded data:
python -c "from chatbot.retriever import Retriever; r = Retriever(); print(r.search('campus_life', 'library'))"
[RETRIEVAL-4] (Bonus) Upgrade to PostgreSQL Full-Text Search if ILIKE is inaccurate
[RETRIEVAL-5] Uncomment and run tests/test_retriever.py
```

### Role 4 — Context & Session Management

```
[CTX-1] Read Z_Placeholder_context_manager.py and understand the session concept
[CTX-2] Implement ContextManager.__init__ with an in-memory dict
[CTX-3] Implement add_turn(session_id, role, message)
[CTX-4] Implement get_history(session_id) → list[dict]
[CTX-5] Implement clear(session_id)
[CTX-6] Ensure MAX_TURNS is read from .env (use os.getenv)
[CTX-7] Manual test: add 3 turns, get history, verify correct order
```

### Role 5 — Fallback Handling & Response Generation

```
[RESP-1] Read Z_Placeholder_responder.py
[RESP-2] Implement Responder.format() → select the best result from the list, return a clean string
[RESP-3] Define a friendly and informative FALLBACK_MESSAGE
[RESP-4] Read Z_Placeholder_bot.py — this is the main integration file!
[RESP-5] Implement Bot.__init__ (initialize all components)
[RESP-6] Implement Bot.chat(session_id, message) → complete pipeline:
preprocessor → intent_classifier → retriever → responder
[RESP-7] Read Z_Placeholder_main.py
[RESP-8] Implement the terminal REPL loop in ma
```

---

## 🔗 Batch 3 — Integration & API *(Week 3-4)*

This batch combines all modules into an API layer.
**Role 5 leads** because they already know bot.py.
**Role 3 assists** because they are familiar with the database layer.

```
[API-1] Role 5: Read Z_Placeholder_app.py
[API-2] Role 5: Implement api/app.py (FastAPI instance + CORS middleware)
[API-3] Role 3: Implement api/schemas/chat_schema.py (ChatRequest + ChatResponse Pydantic)
[API-4] Role 3: Implement api/routes/health.py (GET /health)
[API-5] Role 5: Implement api/routes/chat.py (POST /chat using Bot.chat())
[API-6] Role 5: Mount all routers in app.py
[API-7] Role 4: Update api/routes/chat.py to include session management
[API-8] ALL: Integration test — run server & test with curl or Postman:
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{"session_id":"test-1","message":"where is the library?"}'
```

---

## ✅ Batch 4 — Testing & Polishing *(Week 4)*

```
[TEST-1] Role 1: Complete & run tests/test_intent_classifier.py
[TEST-2] Role 3: Complete & run tests/test_retriever.py
[TEST-3] Role 5: Complete & run tests/test_responder.py
[TEST-4] Role 3: Complete & run tests/test_api.py
[TEST-5] Role 6: Review all seed data — are there any inaccurate answers?
[TEST-6] Role 2: End-to-end synonym testing — can "internet" find the answer to wifi?
[TEST-7] Role 4: Test multi-turn conversation — is context maintained between questions?
[TEST-8] Role 5: Test fallback — ensure out-of-scope questions are answered correctly
[TEST-9] ALL: Run pytest for all tests
[DOC-1] ALL: Update README.md with team members and final information
```

---

## 📊 Workload Summary per Role

| Role | Batch 0 | Batch 1 | Batch 2 | Batch 3 | Batch 4 | Est. Issues |
|------|----------|---------|---------|---------|---------|---------|
| Intent Recognition | ✅ | Design | 5 issues | - | 1 issue | ~8 |
| Entity Extraction | ✅ | Design | 6 issues | - | 1 issue | ~9 |
| Response Matching & Retrieval | ✅ | 6 issues | 5 issues | 2 issues | 1 issue | ~16 |
| Context & Session Management | ✅ | Design | 7 issues | 1 issue | 1 issue | ~11 |
| Fallback & Response Generation | ✅ | Design | 9 issues | 3 issues | 2 issues | ~16 |
| NLP & Text Preprocessing | ✅ | 9 issues | 6 issues | - | 2 issues | ~19 |

---

## 🗓️ Recommended Linear Timeline (4 Weeks)

| Cycles | Batches | Deadlines |
|-------|----------|----------|
| Sprint 1 | Batch 0 + Batch 1 | End of Week 1 |
| Sprint 2 | Batch 2 (all roles parallel) | End of Week 3 |
| Sprint 3 | Batch 3 + Batch 4 | End of Week 4 |

---

## 💡 Tips for Linear Setup

1. **Project**: Create a project named `XMUM Campus Chatbot`
2. **Labels**: Create labels per role: `intent`, `entity`, `retrieval`, `context`, `fallback`, `nlp-data`
3. **States**: `Backlog → Todo → In Progress → In Review → Done`
4. **Priority**: Set all issues in Batch 1 (DB-1 to DATA-9) to **Urgent**
5. **Cycles**: Create 3 cycles according to the timeline above