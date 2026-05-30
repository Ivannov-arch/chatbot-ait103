from chatbot.entity_recognizer import extract_entities

queries = [
    "Where can I find halal food?",
    "How do I connect to the campus wifi?",
    "Where is the library?",
    "How do I apply for leave on the AC System?",
    "List the vegetarian food options near the dormitory"
]

for query in queries:
    result = extract_entities(query)
    print(f"Query: {query}")
    print(f"Result: {result}")
    print("-" * 20)