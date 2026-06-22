from fastapi import APIRouter, HTTPException, Request
from api.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ResetChatRequest,
    SuggestionsResponse,
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    chatbot = request.app.state.chatbot
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    from chatbot_main import ResponseFormatter
    response = chatbot.process_message(
        req.message.strip(),
        session_id=req.session_id,
        debug=req.debug,
    )
    payload = ResponseFormatter.to_dict(response)
    payload["session_id"] = req.session_id
    return payload


@router.post("/chat/reset")
async def reset_chat(req: ResetChatRequest, request: Request):
    chatbot = request.app.state.chatbot
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    chatbot.reset(req.session_id)
    return {"session_id": req.session_id, "status": "cleared"}


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(request: Request, module: str = None, limit: int = 10):
    chatbot = request.app.state.chatbot
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    if module:
        suggestions = chatbot.get_module_suggestions(module, limit)
    else:
        suggestions = []
        for mod in ["admin_directory", "campus_life", "academic_navigation"]:
            suggestions.extend(chatbot.get_module_suggestions(mod, limit // 3))
        suggestions = suggestions[:limit]

    return {"suggestions": suggestions}
