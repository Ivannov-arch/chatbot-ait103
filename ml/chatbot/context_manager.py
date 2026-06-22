
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
class ContextManager:

    def __init__(self) -> None:

        self.sessions: dict[str, list[dict[str, str]]] = {}

    def add_turn(
        self,
        session_id: str,
        role: str,
        message: str,
    ) -> None:

        if session_id not in self.sessions:
            self.sessions[session_id] = []


        utc_timestamp: str = datetime.now(tz=timezone.utc).isoformat()

        message_record: dict[str, str] = {
            "role":      role,
            "message":   message,
            "timestamp": utc_timestamp,
        }

        self.sessions[session_id].append(message_record)


        self._prune_history(session_id)

    def get_history(self, session_id: str) -> list[dict[str, str]]:

        return self.sessions.get(session_id, [])

    def clear(self, session_id: str) -> None:

        self.sessions.pop(session_id, None)


    def _prune_history(self, session_id: str) -> None:

        if session_id not in self.sessions:
            return

        raw_max_turns: str = os.getenv("MAX_TURNS", "5")

        try:
            configured_turn_limit: int = int(raw_max_turns)
        except ValueError:

            configured_turn_limit = 5

        max_individual_messages: int = configured_turn_limit * 2

        current_history: list[dict[str, str]] = self.sessions[session_id]
        current_message_count: int = len(current_history)

        if current_message_count > max_individual_messages:

            self.sessions[session_id] = current_history[-max_individual_messages:]


if __name__ == "__main__":

    os.environ["MAX_TURNS"] = "2"

    print("=" * 60)
    print("CGC-03  ContextManager — manual verification")
    print(f"  MAX_TURNS env var set to: {os.environ['MAX_TURNS']}")
    print(f"  Effective message cap   : {int(os.environ['MAX_TURNS']) * 2}")
    print("=" * 60)

    dialogue_memory = ContextManager()
    test_session_identifier: str = "campus-orientation-session-001"

    print("\nAdding 6 messages to the session (3 user + 3 bot)…\n")

    dialogue_memory.add_turn(test_session_identifier, "user", "Where is the library?")
    dialogue_memory.add_turn(test_session_identifier, "bot",  "The library is in Block A, Level 2.")
    dialogue_memory.add_turn(test_session_identifier, "user", "What are the opening hours?")
    dialogue_memory.add_turn(test_session_identifier, "bot",  "The library is open Mon–Fri, 8 AM to 10 PM.")
    dialogue_memory.add_turn(test_session_identifier, "user", "Is there a student lounge nearby?")
    dialogue_memory.add_turn(test_session_identifier, "bot",  "Yes, the student lounge is on Level 3 of Block A.")


    retained_messages: list[dict[str, str]] = dialogue_memory.get_history(
        test_session_identifier
    )

    print(f"Messages retained after pruning : {len(retained_messages)}  (expected: 4)\n")

    for position, record in enumerate(retained_messages, start=1):
        print(
            f"  [{position}] role={record['role']:<10}  "
            f"ts={record['timestamp']}  "
            f"msg={record['message']!r}"
        )


    assert len(retained_messages) == 4, (
        f"Pruning failed: expected 4 messages but got {len(retained_messages)}"
    )
    print("\n✅  Pruning verified — 4 most recent messages retained, 2 oldest discarded.")


    print("\nClearing session…")
    dialogue_memory.clear(test_session_identifier)

    post_clear_history: list[dict[str, str]] = dialogue_memory.get_history(
        test_session_identifier
    )
    print(f"History length after clear_session: {len(post_clear_history)}  (expected: 0)")

    assert len(post_clear_history) == 0, (
        "clear_session failed: history should be empty but is not"
    )
    print("✅  clear_session verified — history length is 0.")

    dialogue_memory.clear("session-that-never-existed")
    print("✅  Speculative clear_session on unknown ID raised no error.")

    print("\n" + "=" * 60)
    print("All manual checks passed.  context_manager.py is working correctly.")
    print("=" * 60)
