# placeholder_route_chat.py
# api/routes/chat.py
#
# POST /chat  — Main chatbot endpoint
#
# Request body  (ChatRequest):
#   session_id  : str   — unique identifier per user/browser session
#   message     : str   — the user's message
#
# Response body (ChatResponse):
#   reply       : str   — the chatbot's answer
#   module      : str   — which knowledge module answered the query
#   session_id  : str   — echoed back for frontend tracking
#
# Flow:
#   1. Validate request with Pydantic (auto via FastAPI)
#   2. Pass message to Bot.chat(session_id, message)
#   3. Return structured ChatResponse
#
# TODO: instantiate Bot (consider dependency injection with Depends)
# TODO: handle exceptions and return appropriate HTTP error codes
# TODO: add rate limiting if needed

from fastapi import APIRouter, HTTPException

# from api.schemas.chat_schema import ChatRequest, ChatResponse
# from chatbot.bot import Bot

router = APIRouter()

# PLACEHOLDER — Bot instance (use FastAPI Depends for production)
# _bot = Bot()


@router.post("/")
def chat(body: dict):  # replace `dict` with ChatRequest once schema is ready
    """
    PLACEHOLDER — Send a message to the chatbot and receive a reply.

    Replace `body: dict` with `body: ChatRequest` after implementing schemas.
    """
    # PLACEHOLDER
    message = body.get("message", "")
    session_id = body.get("session_id", "default")

    if not message:
        raise HTTPException(status_code=400, detail="message field is required.")

    # reply = _bot.chat(session_id=session_id, message=message)
    reply = f"[PLACEHOLDER] Bot received: {message!r}"

    return {
        "reply": reply,
        "module": "unknown",
        "session_id": session_id,
    }
