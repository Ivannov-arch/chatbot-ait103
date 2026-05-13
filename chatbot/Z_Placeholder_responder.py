# placeholder_responder.py
# chatbot/responder.py
#
# Responder — formats retrieved knowledge into a clean, readable reply.
#
# Responsibilities:
#   - Select the best result from Retriever output
#   - Format multi-item results with bullet points if needed
#   - Provide a graceful fallback if no result is found
#   - Optionally append a "Did you mean X?" suggestion
#
# TODO: implement Responder.format(results: list[dict], query: str) -> str
# TODO: define a fallback message when no results match.

FALLBACK_MESSAGE = (
    "Sorry, I couldn't find an answer to that question. "
    "Please try rephrasing, or contact the relevant XMUM office directly."
)


class Responder:
    """PLACEHOLDER — Format retriever results into a user-facing reply."""

    def format(self, results: list[dict], query: str) -> str:
        """
        Format a list of knowledge items into a response string.

        Args:
            results: List of knowledge item dicts from Retriever.
            query:   Original user query (used for fallback suggestions).

        Returns:
            A formatted string reply.
        """
        # PLACEHOLDER
        if not results:
            return FALLBACK_MESSAGE
        return f"[PLACEHOLDER] Found {len(results)} result(s) for: {query!r}"
