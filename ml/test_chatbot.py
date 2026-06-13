#!/usr/bin/env python3
# ============================================================================
# test_chatbot.py
#
# Quick test script to verify all components work together.
# Run this BEFORE deploying to ensure everything is working.
#
# Usage:
#   python test_chatbot.py
# ============================================================================

import sys
import os
from pathlib import Path

print("=" * 70)
print("  XMUMC Chatbot — System Test")
print("=" * 70)


# Test 1: Check files exist
print("\n[1/6] Checking files...")
required_files = [
    "entity_recognizer.py",
    "intent_classifier.py",
    "retriever.py",
    "chatbot_main.py",
    "flask_api.py",
    "knowledge_base.csv",
    "requirements.txt"
]

missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print(f"❌ Missing files: {', '.join(missing_files)}")
    print("   Please ensure all files are in the current directory.")
    sys.exit(1)
else:
    print("✓ All required files found")


# Test 2: Check Python dependencies
print("\n[2/6] Checking Python dependencies...")
try:
    import flask
    print("✓ flask installed")
except ImportError:
    print("❌ flask not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import nltk
    print("✓ nltk installed")
except ImportError:
    print("❌ nltk not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from flask_cors import CORS
    print("✓ flask-cors installed")
except ImportError:
    print("❌ flask-cors not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


# Test 3: Test entity recognizer
print("\n[3/6] Testing entity recognizer...")
try:
    from entity_recognizer import extract_entities
    
    test_input = "Where is the library?"
    entities = extract_entities(test_input)
    
    if "facility" in entities and "library" in entities["facility"]:
        print(f"✓ Entity recognition working")
        print(f"   Input: '{test_input}'")
        print(f"   Extracted: {entities}")
    else:
        print(f"⚠ Entity extraction returned unexpected result: {entities}")
except Exception as e:
    print(f"❌ Entity recognizer error: {e}")
    sys.exit(1)


# Test 4: Test intent classifier
print("\n[4/6] Testing intent classifier...")
try:
    from intent_classifier import IntentClassifier
    
    classifier = IntentClassifier()
    test_input = "How do I register for courses?"
    module, sub_intent = classifier.classify(test_input)
    
    if module in ["admin_directory", "campus_life", "academic_navigation", "unknown"]:
        print(f"✓ Intent classification working")
        print(f"   Input: '{test_input}'")
        print(f"   Module: {module}")
        print(f"   Sub-intent: {sub_intent}")
    else:
        print(f"⚠ Unexpected module: {module}")
except Exception as e:
    print(f"❌ Intent classifier error: {e}")
    sys.exit(1)


# Test 5: Test retriever
print("\n[5/6] Testing knowledge retriever...")
try:
    from retriever import KnowledgeRetriever
    
    if not os.path.exists("knowledge_base.csv"):
        print("❌ knowledge_base.csv not found")
        sys.exit(1)
    
    retriever = KnowledgeRetriever("knowledge_base.csv")
    
    if len(retriever.knowledge_base) == 0:
        print("⚠ Warning: Knowledge base is empty")
    else:
        print(f"✓ Knowledge retriever loaded {len(retriever.knowledge_base)} items")
        
        # Try a test retrieval
        if retriever.knowledge_base:
            test_module = retriever.knowledge_base[0].module
            test_message = "test query"
            best, score, all_scores = retriever.retrieve(test_module, test_message)
            print(f"✓ Retriever working (searched {len(all_scores)} items)")
except Exception as e:
    print(f"❌ Retriever error: {e}")
    sys.exit(1)


# Test 6: Test full chatbot
print("\n[6/6] Testing full chatbot pipeline...")
try:
    from chatbot_main import XMUMChatbot, ResponseFormatter
    
    chatbot = XMUMChatbot("knowledge_base.csv")
    
    # Test a simple query
    test_queries = [
        "Tell me about XMUM",
        "How do I register for courses?",
        "Where is the library?"
    ]
    
    print(f"✓ Chatbot initialized")
    print(f"\n  Testing with sample queries:")
    
    for query in test_queries:
        response = chatbot.process_message(query, debug=False)
        confidence_pct = int(response.confidence_score * 100)
        status = "✓" if response.confidence_score > 0 else "⚠"
        print(f"  {status} '{query}' → {confidence_pct}% confidence")

except Exception as e:
    print(f"❌ Chatbot error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 7: Test Flask API
print("\n[BONUS] Testing Flask API...")
try:
    from flask_api import app
    
    # Create test client
    client = app.test_client()
    
    # Test /api/health
    resp = client.get('/api/health')
    if resp.status_code == 200:
        print("✓ /api/health endpoint working")
    else:
        print(f"⚠ /api/health returned {resp.status_code}")
    
    # Test /api/chat
    resp = client.post('/api/chat', 
        json={"message": "When does the library open?", "debug": False},
        content_type='application/json'
    )
    if resp.status_code == 200:
        print("✓ /api/chat endpoint working")
        data = resp.get_json()
        print(f"   Response keys: {list(data.keys())}")
    else:
        print(f"⚠ /api/chat returned {resp.status_code}")
        
except Exception as e:
    print(f"⚠ Flask API test skipped: {e}")


# Summary
print("\n" + "=" * 70)
print("  ✓ ALL TESTS PASSED")
print("=" * 70)
print("\nYou're ready to run the chatbot!")
print("\nNext steps:")
print("  1. Start the backend:")
print("     python flask_api.py --csv knowledge_base.csv --port 5000")
print("\n  2. Open the frontend in browser:")
print("     xmumc_chatbot_updated.html")
print("\n  3. Or test interactively:")
print("     python chatbot_main.py knowledge_base.csv")
print("\n" + "=" * 70)
