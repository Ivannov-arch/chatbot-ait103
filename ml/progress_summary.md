# XMUM Campus Chatbot — Team Progress Summary
**Review Date:** 2026-06-14 | **Reviewed by:** Ivannov Kennedy

---

## 🟢 EvanChrs23 & guitarjun11-art — CGC-02 & CGC-06 · COMPLETE

### What was done
- **`chatbot/preprocessor.py`** (CGC-02) — fully implemented:
  - `normalize()`, `extract_keywords()`, `expand_synonyms()`, `build_search_terms()` all correct
  - `SYNONYM_MAP` has 30+ mappings (exceeds the 20 minimum)
  - Multi-word phrase expansion (`_iter_phrases`) and canonical chaining (`_canonicalize`) implemented
  - Interactive `__main__` block included
- **`scripts/validate_seeds.py`** (CGC-06) — all 4 checks implemented cleanly
- **JSON seed files** (`campus_life.json`, `academic_navigation.json`, `admin_directory.json`) — cleaned and verified
- **`database/client.py`** — `get_client()` and `get_admin_client()` implemented correctly

### Remaining action (1 item)
> **Re-upload seeds to Supabase** after all team fixes are confirmed:
> ```sql
> TRUNCATE TABLE knowledge_items;
> ```
> Then run: `python -m database.seed`

---

## 🟢 Marinoune — CGC-03 · COMPLETE (interface kept as-is)

### What was done
- **`chatbot/retriever.py`** — `KnowledgeRetriever` fully implemented with Supabase integration:
  - Loads from Supabase on `__init__`, indexes by module
  - Scoring: exact whole-word (+2.0), partial (+1.0), entity standard (+3.0), proper noun (+1.5)
  - `_is_whole_word_match()` using regex `\b`
  - `retrieve()` returns `(best_item, score, all_scores)` — tuple format
  - `retrieve_all_for_module()` for suggestions

> **Note:** The interface rename (`Retriever`, `search()`, `list[dict]` return) from the previous review was **not applied** — the current `bot.py` and `chatbot_main.py` already use `KnowledgeRetriever` and `retrieve()` directly. Changing the interface now would break both callers. The existing interface is kept and considered complete.

---

## 🟡 lai chun chyi — CGC-05 · PARTIAL

### What was done
- **`chatbot/responder.py`** — implemented with `ResponseFormatter` class:
  - `_to_dict()`, `_to_json()`, `_to_console()` — ✅ keep
  - `log_unrecognized_query()` — ✅ keep
  - `get_varied_fallback_phrase()` — ✅ keep
  - `generate_template_response()` — ✅ keep (fix: default `user_name="Student"`, not `"Alex"`)
  - `process_chatbot_output()` — ❌ remove, pipeline doesn't use confidence-score gating anymore
  - `import pandas as pd` — ❌ remove, not needed
  - `from chatbot_main import ChatbotResponse` — ✅ already fixed to `from chatbot.bot import ChatbotResponse`

- **`chatbot/bot.py`** — ✅ implemented with full pipeline:
  - `Bot.__init__` initializes `IntentClassifier`, `KnowledgeRetriever`, prints confirmation
  - `Bot.process_message()` runs: entity extraction → intent classify → retrieve → build response
  - Handles `unknown` intent, no-match, and success cases
  - `get_module_suggestions()` for UI quick-suggestions

- **`chatbot/main.py`** — ✅ implemented:
  - Interactive REPL loop with `Bot`
  - Import bug fixed: removed stale `from chatbot.intent_classifier import user_input`

### What still needs to be fixed (2 items)

**1. Fix `responder.py` — remove `process_chatbot_output` and `pandas` import:**
```python
# Remove:
import pandas as pd
# Remove:
def process_chatbot_output(confidence, matched_row, user_raw_input=""):
    ...
# Fix default:
def generate_template_response(official_answer, user_name="Student"):
```

**2. `chatbot/bot.py` does not use `context_manager` yet** — waiting on CGC-04.
Once `ContextManager` is available, add to `Bot.__init__` and `process_message()`.

---

## ❌ CGC-04 — context_manager.py · NOT STARTED · UNASSIGNED

> [!CAUTION]
> Still empty. `bot.py` works without it for now (no session memory), but multi-turn context is a rubric requirement. Must be completed before final integration test.

### Build from scratch:

```python
import os
from datetime import datetime

MAX_TURNS = int(os.getenv("MAX_TURNS", "5"))

class ContextManager:
    def __init__(self, max_turns: int = MAX_TURNS):
        self.max_turns = max_turns
        self._store: dict = {}

    def add_turn(self, session_id: str, role: str, message: str) -> None:
        if role not in ("user", "bot"):
            raise ValueError(f"role must be 'user' or 'bot', got {role!r}")
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        self._store[session_id] = self._store[session_id][-(self.max_turns * 2):]

    def get_history(self, session_id: str) -> list[dict]:
        return self._store.get(session_id, [])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
```

**Verify with:**
```
python -c "
from chatbot.context_manager import ContextManager
ctx = ContextManager(max_turns=2)
for i in range(3):
    ctx.add_turn('s1', 'user', f'msg {i}')
    ctx.add_turn('s1', 'bot', f'reply {i}')
h = ctx.get_history('s1')
assert len(h) == 4, f'Expected 4, got {len(h)}'
print('PASS —', len(h), 'messages retained')
"
```

---

## 🟢 Batch 3 — API Layer · COMPLETE

All API files implemented during migration from Flask to FastAPI:

- **`api/schemas/chat_schema.py`** — `ChatRequest`, `ChatResponse`, `SuggestionsResponse` (Pydantic v2)
- **`api/routes/chat.py`** — `POST /api/chat`, `GET /api/suggestions`
- **`api/routes/health.py`** — `GET /api/health`
- **`api/app.py`** — FastAPI app with lifespan (startup/shutdown), CORS middleware, router mounting

**Run server:**
```powershell
uvicorn api.app:app --reload --port 8000
```
Swagger docs at: `http://localhost:8000/docs`

---

## 📋 Action Priority Order

```
STEP 1 — CGC-04:        Implement context_manager.py          (BLOCKING multi-turn)
STEP 2 — lai chun chyi: Clean up responder.py                 (remove pandas + process_chatbot_output)
STEP 3 — guitarjun:     Re-upload seeds to Supabase           (TRUNCATE + python -m database.seed)
STEP 4 — Everyone:      python -m chatbot.main                (integration test terminal)
STEP 5 — Everyone:      uvicorn api.app:app --reload --port 8000 + test /docs
STEP 6 — Everyone:      pytest -v                             (all tests)
```

---

## 🔢 Completion Score

| Contributor | Ticket | Files | Status | % Done |
|---|---|---|---|---|
| EvanChrs23 | CGC-02 | `preprocessor.py` | ✅ Complete | 100% |
| guitarjun11-art | CGC-06 | `validate_seeds.py` + JSON + `client.py` | ✅ Complete (re-upload pending) | 95% |
| Marinoune | CGC-03 | `retriever.py` | ✅ Complete | 100% |
| lai chun chyi | CGC-05 | `responder.py` | ⚠️ Needs cleanup (pandas + old function) | 70% |
| lai chun chyi | CGC-05 | `bot.py` | ✅ Complete | 100% |
| lai chun chyi | CGC-05 | `main.py` | ✅ Complete | 100% |
| Ivannov | CGC-API | `api/app.py` + routes + schemas | ✅ Complete | 100% |
| *Unassigned* | CGC-04 | `context_manager.py` | ❌ Empty | 0% |
