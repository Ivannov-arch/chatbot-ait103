#!/usr/bin/env python3
# ============================================================================
# test_gemini_retriever.py
#
# Tests the Gemini-powered semantic matcher with typo/grammar-heavy queries.
# Verifies that the chatbot can still find the right answer despite bad input.
#
# Usage (from the ml/ directory):
#   python test_gemini_retriever.py
# ============================================================================

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("  Gemini Semantic Retriever Test")
print("=" * 70)

# Check for Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your-gemini-api-key-here":
    print("\n[SKIP] GEMINI_API_KEY is not set in .env.")
    print("  Set it to test Gemini-powered semantic matching.")
    print("  Get a free key at: https://aistudio.google.com/apikey")
    print("  Falling through to keyword-based retrieval only...\n")
else:
    print(f"\n[OK] GEMINI_API_KEY found ({api_key[:8]}...)\n")

# Import GeminiMatcher directly to test it
from chatbot.gemini_matcher import GeminiMatcher

matcher = GeminiMatcher()
print(f"Gemini available: {matcher.is_available()}")
print(f"Model:            {matcher.model}\n")

if matcher.is_available():
    # Quick sanity test of the matcher with some candidates
    print("[Test 1] Direct GeminiMatcher test:")
    candidates = [
        "What are the library opening hours?",
        "How do I connect to the campus Wi-Fi?",
        "What scholarships are available for students?",
        "Where is the hostel located?",
    ]
    typo_query = "whr cn i connnect to wify on campus??"
    print(f"  Query:   '{typo_query}'")
    idx, conf, reason = matcher.match_question(typo_query, candidates)
    if idx != -1:
        print(f"  Matched: [{idx}] '{candidates[idx]}'")
        print(f"  Confidence: {conf:.2f}")
        print(f"  Reasoning: {reason}")
    else:
        print(f"  No match found. Reason: {reason}")

print()

# Import the full chatbot and test end-to-end with typo queries
print("-" * 70)
print("[Test 2] End-to-end chatbot pipeline with typo-heavy queries:")
print("-" * 70)

from chatbot_main import XMUMChatbot

chatbot = XMUMChatbot()

# (typo query, expected keyword in answer to confirm it matched correctly)
typo_tests = [
    ("hwo do i cnnect to the wify on campu",       "wi-fi"),
    ("whr iz the lybary open till",                 "library"),
    ("cn student stay in dormitory hostle?",        "hostel"),
    ("how mny creditz do i need to graduat",        "credit"),
    ("wht is the schollrship for inter student",    "scholarship"),
]

passed = 0
for query, expected_keyword in typo_tests:
    response = chatbot.process_message(query, session_id="test", debug=False)
    answer_lower = response.answer.lower()
    matched = expected_keyword.lower() in answer_lower
    status = "PASS" if matched else "FAIL"
    if matched:
        passed += 1
    print(f"  [{status}] '{query}'")
    print(f"         → Confidence: {response.confidence_score:.2f}")
    print(f"         → Matched Q:  {response.matched_question}")
    print(f"         → Answer:     {response.answer[:80]}...")
    print()

print(f"Result: {passed}/{len(typo_tests)} typo queries matched correctly.\n")
print("=" * 70)
