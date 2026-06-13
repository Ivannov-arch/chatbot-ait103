# placeholder_api_reference.md
# docs/api_reference.md

# API Reference — XMUM Campus Chatbot

Base URL (development): `http://localhost:8000`

Interactive docs (auto-generated):
- Swagger UI → `http://localhost:8000/docs`
- ReDoc      → `http://localhost:8000/redoc`

---

## GET `/`

Root endpoint. Confirms the API is running.

**Response `200 OK`:**
```json
{
  "message": "XMUM Campus Chatbot API is running. Visit /docs for API reference."
}
```

---

## GET `/health`

Health check endpoint. Used by load balancers and monitoring tools.

**Response `200 OK`:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## POST `/chat`

Send a user message and receive the chatbot's reply.

**Request body:**
```json
{
  "session_id": "user-abc-123",
  "message": "Where is the library and what time does it open?"
}
```

| Field        | Type   | Required | Description                                    |
|--------------|--------|----------|------------------------------------------------|
| `session_id` | string | ✅       | Unique ID per user/browser session (max 128ch) |
| `message`    | string | ✅       | The user's question (max 1000 characters)      |

**Response `200 OK`:**
```json
{
  "reply": "The XMUM library is located at Block A. It opens at 8:30 AM on weekdays.",
  "module": "campus_life",
  "session_id": "user-abc-123"
}
```

| Field        | Type   | Description                                           |
|--------------|--------|-------------------------------------------------------|
| `reply`      | string | The chatbot's answer                                  |
| `module`     | string | Knowledge module that answered: `campus_life`, `admin_directory`, `academic_navigation`, or `unknown` |
| `session_id` | string | Echoed back for frontend tracking                     |

**Error responses:**

| Status | Reason                                         |
|--------|------------------------------------------------|
| `400`  | `message` field is missing or empty            |
| `422`  | Request body is malformed / fails validation   |
| `500`  | Internal server error                          |

---

## Next.js / React Integration Example

```typescript
// utils/chatbot.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function sendMessage(sessionId: string, message: string) {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json() as Promise<{
    reply: string;
    module: string;
    session_id: string;
  }>;
}
```

Add to your `.env.local` in the Next.js project:
```env
NEXT_PUBLIC_API_URL=https://your-deployed-api-url.railway.app
```

---

## CORS Notes

In development, CORS is open to all origins (`*`).  
**Before deploying to production**, restrict `allow_origins` in `api/app.py` to your frontend domain:

```python
allow_origins=["https://your-frontend.vercel.app"]
```
