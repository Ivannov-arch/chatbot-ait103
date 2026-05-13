# placeholder_test_intent_classifier.py
# tests/test_intent_classifier.py
#
# Unit tests for chatbot/intent_classifier.py
#
# Test cases to implement:
#   - "Where is the library?" → "campus_life"
#   - "How do I register for a course?" → "admin_directory"
#   - "How do I log in to the AC system?" → "academic_navigation"
#   - "Tell me a joke" → "unknown"
#   - Empty string → "unknown"
#   - All-whitespace string → "unknown"
#
# TODO: write actual test cases once IntentClassifier is implemented.

import pytest
from chatbot.intent_classifier import IntentClassifier


@pytest.fixture
def classifier():
    """Return a fresh IntentClassifier instance for each test."""
    return IntentClassifier()


class TestIntentClassifier:
    """PLACEHOLDER test suite for IntentClassifier."""

    def test_returns_string(self, classifier):
        """classify() should always return a string."""
        result = classifier.classify("hello")
        assert isinstance(result, str)

    def test_unknown_for_empty_input(self, classifier):
        """Empty input should return 'unknown'."""
        # PLACEHOLDER — update once implemented
        result = classifier.classify("")
        assert result == "unknown"

    # TODO: uncomment and complete once IntentClassifier is implemented
    # def test_campus_life_library(self, classifier):
    #     assert classifier.classify("Where is the library?") == "campus_life"

    # def test_admin_directory_registration(self, classifier):
    #     assert classifier.classify("How do I register for courses?") == "admin_directory"

    # def test_academic_navigation_ac_system(self, classifier):
    #     assert classifier.classify("How do I log in to the AC system?") == "academic_navigation"

    # def test_unknown_for_off_topic(self, classifier):
    #     assert classifier.classify("Tell me a joke") == "unknown"
