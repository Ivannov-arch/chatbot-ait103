from fastapi import APIRouter, HTTPException, Request
from api.schemas.chat_schema import ChatRequest, ChatResponse, SuggestionsResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    chatbot = request.app.state.chatbot
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    from chatbot_main import ResponseFormatter
    response = chatbot.process_message(req.message.strip(), debug=req.debug)
    return ResponseFormatter.to_dict(response)


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(request: Request, module: str = None, limit: int = 10):
    chatbot = request.app.state.chatbot
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")

    if module:
        suggestions = chatbot.get_module_suggestions(module, limit)
    else:
        suggestions = []
        per_module = max(1, limit // 3)
        for mod in ["admin_directory", "campus_life", "academic_navigation"]:
            suggestions.extend(chatbot.get_module_suggestions(mod, per_module))
        suggestions = suggestions[:limit]

    return {"suggestions": suggestions}
