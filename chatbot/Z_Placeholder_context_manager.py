# placeholder_context_manager.py
# chatbot/context_manager.py
#
# ContextManager — tracks multi-turn conversation history per session.
#
# Purpose:
#   Allows the bot to understand follow-up questions like:
#     User: "Where is the library?"
#     Bot:  "The library is at Block A."
#     User: "What time does it close?"  ← needs previous context
#
# Storage options:
#   A) In-memory dict (simple, resets on server restart)
#   B) Supabase `conversation_sessions` table (persistent)
#
# TODO: implement add_turn(session_id, role, message)
# TODO: implement get_history(session_id) -> list[dict]
# TODO: implement clear(session_id)
# TODO: enforce MAX_TURNS window to avoid unbounded memory growth.

MAX_TURNS = 5  # read from env in final implementation


class ContextManager:
    """PLACEHOLDER — In-memory conversation context store."""

    def __init__(self, max_turns: int = MAX_TURNS):
        self.max_turns = max_turns
        self._store: dict[str, list[dict]] = {}

    def add_turn(self, session_id: str, role: str, message: str) -> None:
        """Append a message turn to the session history."""
        # PLACEHOLDER
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append({"role": role, "message": message})
        # Trim to max_turns window
        self._store[session_id] = self._store[session_id][-self.max_turns * 2:]

    def get_history(self, session_id: str) -> list[dict]:
        """Return the conversation history for a session."""
        return self._store.get(session_id, [])

    def clear(self, session_id: str) -> None:
        """Erase all history for a session."""
        self._store.pop(session_id, None)
