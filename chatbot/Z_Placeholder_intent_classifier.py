# placeholder_intent_classifier.py
# chatbot/intent_classifier.py
#
# Intent Classifier — maps a user message to one of three knowledge modules:
#   - "admin_directory"       (Module 1)
#   - "campus_life"           (Module 2)
#   - "academic_navigation"   (Module 3)
#   - "unknown"               (fallback)
#
# Approach:
#   Keyword / rule-based matching (The most reliable for pure retrieval).
#   Maps specific words (e.g., "wifi", "hostel", "AC") to their respective modules.
#
# TODO: implement classify(message: str) -> str
# TODO: define dictionary of keywords per module.

KNOWN_MODULES = [
    "admin_directory",
    "campus_life",
    "academic_navigation",
]


class IntentClassifier:
    """PLACEHOLDER — Classify user intent into a knowledge module."""

    def classify(self, message: str) -> str:
        """
        Classify the user message and return the best matching module name.

        Args:
            message: The raw user input string.

        Returns:
            One of KNOWN_MODULES or "unknown".
        """
        # PLACEHOLDER — always returns unknown until implemented
        return "unknown"
