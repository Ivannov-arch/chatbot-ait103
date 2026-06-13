# placeholder_architecture.md
# docs/architecture.md

# System Architecture — XMUM Campus Knowledge Chatbot

## Overview

The chatbot follows a **modular pipeline architecture**:

```
User Input
    │
    ▼
┌─────────────────────┐
│   ContextManager    │  ← stores conversation history per session
└────────┬────────────┘
         │ enriched message + history
         ▼
┌─────────────────────┐
│  IntentClassifier   │  ← maps input → knowledge module
└────────┬────────────┘
         │ module label ("campus_life" / "admin_directory" / ...)
         ▼
┌─────────────────────┐
│     Retriever       │  ← queries Supabase knowledge_items table
└────────┬────────────┘
         │ list of matching Q&A records
         ▼
┌─────────────────────┐
│     Responder       │  ← formats into readable reply string
└────────┬────────────┘
         │ final reply
         ▼
    User (Terminal or API)
```

## Deployment Modes

| Mode         | Entry Point              | Notes                              |
|--------------|--------------------------|------------------------------------|
| Terminal     | `python -m chatbot.main` | Interactive REPL loop              |
| REST API     | `uvicorn api.app:app`    | FastAPI server for web frontends   |

## Technology Stack

| Layer         | Technology          |
|---------------|---------------------|
| Language      | Python 3.11+        |
| Database      | Supabase (PostgreSQL) |
| API Framework | FastAPI + Uvicorn   |
| Validation    | Pydantic v2         |
| DB Client     | supabase-py v2      |

## Data Flow

1. User sends a message (terminal input or HTTP POST `/chat`)
2. `ContextManager` attaches the last N turns of conversation history
3. `IntentClassifier` determines which of the 3 knowledge modules to search
4. `Retriever` queries Supabase `knowledge_items` table using keyword or full-text search
5. `Responder` selects the best match and formats a clean reply
6. Reply is returned to the user (printed to terminal or sent as JSON response)

## TODO

- [ ] Decide on keyword dictionary for intent classification
- [ ] Finalize SQL Full-Text Search (FTS) queries in Supabase
- [ ] Design Supabase RLS policies for production
