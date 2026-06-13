# placeholder_retriever.py
# chatbot/retriever.py
#
# Retriever — searches the Supabase knowledge base for the best answer.
#
# Strategy:
#   Given a user message and a classified module, query the `knowledge_items`
#   table in Supabase using Lexical Search:
#   - PostgreSQL Full-Text Search (tsvector/tsquery) for accuracy.
#   - OR Pattern Matching (ILIKE '%keyword%') for simplicity.
#
# Supabase table expected: `knowledge_items`
#   - id          UUID
#   - module      TEXT  (e.g. "campus_life")
#   - question    TEXT  (canonical question)
#   - answer      TEXT  (the answer to return)
#   - keywords    TEXT[] (searchable keyword tags)
#   - created_at  TIMESTAMPTZ
#
# TODO: implement Retriever.search(module, query, top_k) -> list[dict]
# TODO: connect to Supabase via database.client
# TODO: handle empty results gracefully.

class Retriever:
    """PLACEHOLDER — Query Supabase knowledge base for relevant answers."""

    def __init__(self):
        # TODO: import and instantiate the Supabase client from database.client
        self.client = None

    def search(self, module: str, query: str, top_k: int = 3) -> list[dict]:
        """
        Search the knowledge base for answers matching the query.

        Args:
            module:  The knowledge module to search within.
            query:   The user's message / keywords.
            top_k:   Maximum number of results to return.

        Returns:
            A list of matching knowledge item dicts.
        """
        # PLACEHOLDER — returns empty list until implemented
        return []
