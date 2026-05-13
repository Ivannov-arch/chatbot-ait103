# placeholder_chat_schema.py
# api/schemas/chat_schema.py
#
# Pydantic Models for the /chat endpoint.
#
# FastAPI uses these to:
#   - Auto-validate incoming JSON request bodies
#   - Auto-generate OpenAPI / Swagger documentation
#   - Serialise response objects into JSON
#
# ChatRequest  — what the frontend sends to POST /chat
# ChatResponse — what the API returns to the frontend
#
# TODO: add field validators (e.g. max message length, session_id format)
# TODO: consider adding a `language` field for future multilingual support

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /chat."""

    session_id: str = Field(
        ...,
        description="Unique identifier for the user's chat session.",
        example="user-abc-123",
        min_length=1,
        max_length=128,
    )
    message: str = Field(
        ...,
        description="The user's message / question.",
        example="Where is the library and what time does it open?",
        min_length=1,
        max_length=1000,
    )


class ChatResponse(BaseModel):
    """Response body for POST /chat."""

    reply: str = Field(
        ...,
        description="The chatbot's answer to the user's message.",
        example="The XMUM library is at Block A. It opens at 8:30 AM on weekdays.",
    )
    module: str = Field(
        ...,
        description="The knowledge module that answered the query.",
        example="campus_life",
    )
    session_id: str = Field(
        ...,
        description="Echoed session ID for frontend tracking.",
        example="user-abc-123",
    )
