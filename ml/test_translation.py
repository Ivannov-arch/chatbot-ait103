#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

import time

# Ensure stdout supports UTF-8 on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

print("=" * 70)
print("  Gemini Translation & Preprocessing Test")
print("=" * 70)

# Check for Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your-gemini-api-key-here":
    print("\n[ERROR] GEMINI_API_KEY is not set in .env.")
    print("Please set it to run translation tests.")
    sys.exit(1)

# Import the chatbot
from chatbot_main import XMUMChatbot, ResponseFormatter

chatbot = XMUMChatbot()

# Test queries in different languages
test_cases = [
    {
        "query": "di mana letak perpustakaan dan kapan tutupnya?",
        "desc": "Indonesian query (should detect Indonesian, search in English, translate back)",
        "expected_keywords": ["library", "bibliotheca"]
    },
    {
        "query": "宿舍申请怎么做？",
        "desc": "Chinese query (should detect Chinese, search in English, translate back)",
        "expected_keywords": ["hostel", "accommodation", "dorm", "housing"]
    },
    {
        "query": "bagaimana cara sambung ke wifi kampus?",
        "desc": "Malay query (should detect Malay, search in English, translate back)",
        "expected_keywords": ["wi-fi", "wifi", "internet", "connection", "connect"]
    },
    {
        "query": "كيف يمكنني تقديم طلب للحصول على سكن الطلاب؟",
        "desc": "Arabic query (should detect Arabic, search in English, translate back)",
        "expected_keywords": ["hostel", "accommodation", "dorm", "housing"]
    },
    {
        "query": "где находится библиотека?",
        "desc": "Russian query (should detect Russian, search in English, translate back)",
        "expected_keywords": ["library", "bibliotheca"]
    },
    {
        "query": "hwo do i cnnect to the wify on campu",
        "desc": "English query with typos (should detect English, clean query, return in English)",
        "expected_keywords": ["wi-fi", "wifi", "internet", "connection", "connect"]
    }
]

passed = 0
for idx, tc in enumerate(test_cases, 1):
    query = tc["query"]
    print(f"\n[{idx}/{len(test_cases)}] Testing: {tc['desc']}")
    print(f"  Input Query: '{query}'")
    
    try:
        response = chatbot.process_message(query, session_id=f"test-{idx}", debug=True)
        
        print(f"  Detected Lang: {response.detected_language}")
        print(f"  Original Query: {response.original_query}")
        print(f"  Matched Q:      {response.matched_question}")
        print(f"  Answer:         {response.answer[:150]}...")
        if response.debug_info:
            print(f"  Debug Info:     {response.debug_info}")
        
        # Verify if it matched the correct concept
        # We check the debug info or the matched question to see if any expected keyword is present
        matched = False
        if response.matched_question:
            matched = any(kw.lower() in response.matched_question.lower() for kw in tc["expected_keywords"])
            
        status = "PASS" if matched else "FAIL"
        if matched:
            passed += 1
            
        print(f"  Status:         {status}")
    except Exception as e:
        print(f"  Error:          {str(e)}")

    # Add a delay to respect API rate limits
    if idx < len(test_cases):
        time.sleep(3.0)

print("\n" + "=" * 70)
print(f"Result: {passed}/{len(test_cases)} cases matched correctly.")
print("=" * 70)
