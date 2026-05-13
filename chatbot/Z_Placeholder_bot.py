# placeholder_bot.py
# chatbot/bot.py
#
# Main chatbot orchestrator.
# This class ties together all components of the pipeline:
#   1. ContextManager  — stores conversation history per session
#   2. IntentClassifier — maps user input to a knowledge module
#   3. Retriever        — queries Supabase for the best matching answer
#   4. Responder        — formats the raw result into a clean reply
#
# Usage:
#   bot = Bot()
#   reply = bot.chat(session_id="abc", message="Where is the canteen?")
#
# TODO: implement Bot.__init__ to wire up all components.
# TODO: implement Bot.chat(session_id, message) -> str
# TODO: implement Bot.reset(session_id) to clear context.

class Bot:
    """PLACEHOLDER — Main chatbot orchestrator."""

    def __init__(self):
        # TODO: initialise ContextManager, IntentClassifier, Retriever, Responder
        pass

    def chat(self, session_id: str, message: str) -> str:
        """Process a user message and return the chatbot reply."""
        # PLACEHOLDER
        return f"[PLACEHOLDER] Bot received: {message!r} for session {session_id!r}"

    def reset(self, session_id: str) -> None:
        """Clear the conversation context for a given session."""
        # PLACEHOLDER
        pass
