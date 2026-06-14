from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    chatbot = request.app.state.chatbot
    return {
        "status": "ok",
        "version": "1.0.0",
        "knowledge_base_size": len(chatbot.retriever.knowledge_base) if chatbot else 0,
    }
