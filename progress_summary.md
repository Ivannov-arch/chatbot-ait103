# XMUM Campus Chatbot — Team Progress Summary
**Review Date:** 2026-06-13 | **Reviewed by:** Ivannov Kennedy

---

## 🟢 EvanChrs 23 & guitarjun11-art — CGC-02 & CGC-06 · COMPLETE

### What was done
- **`chatbot/preprocessor.py`** (CGC-02) — fully implemented from scratch:
  - `normalize()`, `extract_keywords()`, `expand_synonyms()` all correct
  - `SYNONYM_MAP` has 30+ mappings (exceeds the 20 minimum)
  - Added bonus `build_search_terms()` that combines all three in one call
  - Interactive `__main__` block included
- **`scripts/validate_seeds.py`** (CGC-06) — all 4 checks implemented cleanly:
  - Structural integrity, keyword lowercase, cross-module conflicts, synonym compatibility
- **JSON seed files** (`campus_life.json`, `academic_navigation.json`, `admin_directory.json`) — cleaned:
  - Fixed incorrect `sub_intent` values (many were `"general_info"` incorrectly)
  - Replaced non-canonical keywords: `"wi-fi"` → `"wifi"`, `"email"` → `"student email"`, `"connection"` removed

### Remaining action (1 item)
> **Re-upload seeds to Supabase** after all team fixes are confirmed:
> ```sql
> TRUNCATE TABLE knowledge_items;
> ```
> Then run: `python -m database.seed`
> Verify row count matches local JSON count.

---

## 🟡 Marinoune — CGC-03 · NEEDS INTERFACE REVISION

### What was done (keep all of this)
- `KnowledgeRetriever` class with smart scoring algorithm:
  - Exact whole-word match: **+2.0 pts** (uses regex `\b` to avoid false positives like `"it"` matching `"kit"`)
  - Partial match: **+1.0 pt**
  - Entity match (standard): **+3.0 pts**
  - Entity match (proper noun): **+1.5 pts**
- `_is_whole_word_match()` helper
- `_score_item()` scoring method — the best part, do not touch
- Entity integration from `entity_recognizer.py` — correct direction

### What needs to be fixed (4 items)

> [!IMPORTANT]
> The scoring logic is correct. Only the **external interface** needs to change. Do not rewrite the internals.

**1. Rename the class:**
```python
# Before
class KnowledgeRetriever:

# After
class Retriever:
```

**2. Rename and fix the method signature:**
```python
# Before
def retrieve(self, module: str, user_message: str, extracted_entities=None):

# After
def search(self, module: str, keywords: list[str], top_k: int = 3,
           sub_intent: str = None, entities: dict = None) -> list[dict]:
    # Reconstruct query string internally: query = " ".join(keywords)
    # Pass entities through to _score_item() unchanged
```

**3. Fix the return type:**
```python
# Before — returns a Tuple
return best_item, best_score, scores

# After — returns list[dict], sorted desc by score, top_k only
return [
    {
        "question": item.question,
        "answer": item.answer,
        "keywords": item.keywords,
        "score": score
    }
    for item, score in scores[:top_k]
    if score > 0
]
```

**4. Switch data source to Supabase (keep CSV as fallback):**
```python
def __init__(self, csv_fallback_path=None):
    self.client = get_client()  # from database.client
    self.csv_fallback_path = csv_fallback_path
    # ... load from Supabase; if it fails and csv_fallback_path is set, load CSV
```

**Test command to verify:**
```
python -c "
from chatbot.retriever import Retriever
r = Retriever()
results = r.search('campus_life', ['library', 'borrow'])
print('Results:', len(results))
if results:
    print('Top:', results[0]['question'])
    print('Score:', results[0]['score'])
"
```

---

## 🟡 lai chun chyi — CGC-05 · PARTIAL

### What was done
- **`chatbot/responder.py`** — implemented, but with a different design:
  - `log_unrecognized_query()` — ✅ keep this
  - `get_varied_fallback_phrase()` — ✅ keep this
  - `generate_template_response()` — ✅ keep this (fix: default `user_name="Student"`, not hardcoded `"Alex"`)
  - `process_chatbot_output(confidence, matched_row)` — ❌ remove this, pipeline doesn't produce a confidence score

### What needs to be fixed (3 items)

**1. Revise `responder.py` — add `Responder` class, remove old function:**

```python
# Remove this:
def process_chatbot_output(confidence, matched_row, user_raw_input=""):
    ...

# Remove this import (not needed):
import pandas as pd

# Add this:
class Responder:
    def format(self, results: list[dict], query: str, module: str = "unknown") -> str:
        if not results:
            log_unrecognized_query(query)
            return self._fallback(module)
        reply = generate_template_response(results[0]["answer"])  # user_name defaults to "Student"
        if len(results) > 1:
            reply += f"\n\nRelated: {results[1]['question']}"
        return reply

    def _fallback(self, module: str) -> str:
        fallbacks = {
            "admin_directory":     "I couldn't find that info. Try contacting ISAO at isao@xmu.edu.my.",
            "campus_life":         "I couldn't find that info. Try the Student Affairs Office at student.affairs@xmu.edu.my.",
            "academic_navigation": "I couldn't find that. Contact your academic advisor or the Registrar's Office.",
        }
        return fallbacks.get(module,
            "I'm not sure what you're asking. Try asking about campus facilities, "
            "academic matters, or administrative services.")
```

**2. Implement `chatbot/bot.py` — currently empty:**

```python
from chatbot.intent_classifier import IntentClassifier
from chatbot.retriever import Retriever
from chatbot.context_manager import ContextManager
from chatbot.responder import Responder
from chatbot.preprocessor import normalize, extract_keywords, expand_synonyms

class Bot:
    def __init__(self):
        self.intent   = IntentClassifier()
        self.retriever = Retriever()
        self.context   = ContextManager()
        self.responder = Responder()

    def chat(self, session_id: str, message: str) -> str:
        self.context.add_turn(session_id, "user", message)
        module, sub_intent = self.intent.classify(message)      # returns TUPLE
        keywords = expand_synonyms(extract_keywords(normalize(message)))
        if module == "unknown" or not keywords:
            results = []
        else:
            results = self.retriever.search(module, keywords, sub_intent=sub_intent)
        reply = self.responder.format(results, message, module)
        self.context.add_turn(session_id, "bot", reply)
        return reply

    def reset(self, session_id: str) -> None:
        self.context.clear(session_id)
```

**3. Implement `chatbot/main.py` — currently empty:**

```python
import uuid
from chatbot.bot import Bot

def main():
    bot = Bot()
    session_id = str(uuid.uuid4())
    print("=" * 50)
    print("  XMUM Campus Chatbot")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 50)
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        reply = bot.chat(session_id, user_input)
        print(f"Bot: {reply}\n")

if __name__ == "__main__":
    main()
```

---

## ❌ CGC-04 — context_manager.py · NOT STARTED · UNASSIGNED

> [!CAUTION]
> This is the **#1 blocker**. `bot.py` cannot be implemented until this exists. No one appears to have been assigned this task. Whoever is available must complete this first.

### What needs to be built from scratch:

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
        # Trim to last max_turns * 2 messages
        self._store[session_id] = self._store[session_id][-(self.max_turns * 2):]

    def get_history(self, session_id: str) -> list[dict]:
        return self._store.get(session_id, [])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
```

**Test command:**
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

## 📋 Action Priority Order

```
STEP 1 — Everyone:  git pull origin main
STEP 2 — CGC-04:   Implement context_manager.py  (BLOCKING EVERYTHING)
STEP 3 — Marinoune: Fix retriever interface       (rename + return type + Supabase)
STEP 4 — lai chun chyi: Revise responder, implement bot.py + main.py
STEP 5 — guitarjun: Re-upload seeds to Supabase
STEP 6 — Everyone:  Run python -m chatbot.main to integration test
```

---

## 🔢 Completion Score

| Contributor | Ticket | Files | Status | % Done |
|---|---|---|---|---|
| Evanchrs23 | CGC-02 | `preprocessor.py` | ✅ Complete | 100% |
| guitarjun11-art | CGC-06 | `validate_seeds.py` + JSON | ✅ Complete (re-upload pending) | 95% |
| Marinoune | CGC-03 | `retriever.py` | ⚠️ Logic done, interface broken | 60% |
| lai chun chyi | CGC-05 | `responder.py` | ⚠️ Done differently | 40% |
| lai chun chyi | CGC-05 | `bot.py` | ❌ Empty | 0% |
| lai chun chyi | CGC-05 | `main.py` | ❌ Empty | 0% |
| *Unassigned* | CGC-04 | `context_manager.py` | ❌ Empty | 0% |
