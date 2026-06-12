# retriever.py
# ============================================================================
# chatbot/retriever.py
#
# Retriever — fetches answers from the knowledge base (CSV) based on:
#   1. Intent classification (module + sub_intent)
#   2. Entity extraction
#   3. Keyword/template matching
#
# Workflow:
#   1. Load knowledge base from CSV
#   2. Score templates using keyword matching
#   3. Return best match with confidence score
# ============================================================================

import csv
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class KnowledgeItem:
    """Represents a single Q&A entry from the knowledge base."""
    module: str
    question: str
    answer: str
    keywords: List[str]


class KnowledgeRetriever:
    """
    Loads and searches through the knowledge base.
    
    Attributes:
        knowledge_base: List of KnowledgeItem objects
        module_index: Dict mapping module names to items
    """
    
    def __init__(self, csv_path: str):
        """
        Initialize retriever and load knowledge base from CSV.
        
        Args:
            csv_path: Path to the CSV file (module, question, answer, keywords)
        """
        self.knowledge_base: List[KnowledgeItem] = []
        self.module_index: Dict[str, List[KnowledgeItem]] = {}
        self._load_csv(csv_path)
    
    def _load_csv(self, csv_path: str) -> None:
        """Load and parse the CSV knowledge base."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Knowledge base not found: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                module = row['module'].strip()
                question = row['question'].strip()
                answer = row['answer'].strip()
                
                # Parse keywords (comma-separated)
                keywords = [kw.strip().lower() for kw in row['keywords'].split(',')]
                
                item = KnowledgeItem(
                    module=module,
                    question=question,
                    answer=answer,
                    keywords=keywords
                )
                
                self.knowledge_base.append(item)
                
                # Index by module for faster lookup
                if module not in self.module_index:
                    self.module_index[module] = []
                self.module_index[module].append(item)
    
    def retrieve(
        self,
        module: str,
        user_message: str,
        extracted_entities: Optional[Dict[str, List[str]]] = None
    ) -> Tuple[Optional[KnowledgeItem], float, List[Tuple[KnowledgeItem, float]]]:
        """
        Retrieve the best matching answer for a user query.
        
        Args:
            module: The classified module (from intent_classifier)
            user_message: The raw user input
            extracted_entities: Optional entities extracted by entity_recognizer
        
        Returns:
            A tuple of:
            - best_item: The top matching KnowledgeItem (or None)
            - best_score: Confidence score of the best match
            - all_scores: List of (item, score) sorted by score descending
        """
        # Get items from the relevant module
        candidates = self.module_index.get(module, [])
        
        if not candidates:
            return None, 0.0, []
        
        # Score each candidate
        scores = []
        for item in candidates:
            score = self._score_item(user_message, item, extracted_entities)
            scores.append((item, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        best_item = scores[0][0] if scores else None
        best_score = scores[0][1] if scores else 0.0
        
        return best_item, best_score, scores
    
    def _score_item(
        self,
        user_message: str,
        item: KnowledgeItem,
        extracted_entities: Optional[Dict[str, List[str]]] = None
    ) -> float:
        """
        Score a knowledge item against the user message.
        
        Scoring strategy:
        1. Exact keyword matches in user message (+2 points each)
        2. Partial keyword matches (+1 point each)
        3. Entity matches from entity_recognizer (+3 points each)
        
        Args:
            user_message: The raw user input
            item: The KnowledgeItem to score
            extracted_entities: Extracted entities from entity_recognizer
        
        Returns:
            A numeric score (higher = better match)
        """
        score = 0.0
        message_lower = user_message.lower()
        matched_keywords = []
        
        # Strategy 1: Exact and partial keyword matches
        for keyword in item.keywords:
            # Exact match (higher weight)
            if keyword in message_lower:
                # Check if it's a whole word, not substring
                if self._is_whole_word_match(keyword, message_lower):
                    score += 2.0
                    matched_keywords.append(keyword)
            # Partial match (lower weight)
            elif keyword in message_lower or any(
                part in keyword for part in message_lower.split()
            ):
                score += 1.0
                matched_keywords.append(f"{keyword}(~)")
        
        # Strategy 2: Entity-based scoring
        if extracted_entities:
            # Give extra weight to entity matches
            for entity_type, entities in extracted_entities.items():
                if entity_type in ["pos_nouns"]:
                    # Proper nouns are less reliable, lower weight
                    for entity in entities:
                        if entity.lower() in message_lower:
                            score += 1.5
                else:
                    # Standard entities (facility, office, academic, etc.)
                    for entity in entities:
                        entity_lower = entity.lower()
                        if entity_lower in message_lower:
                            score += 3.0
        
        return score
    
    def _is_whole_word_match(self, word: str, text: str) -> bool:
        """Check if a word appears as a whole word in text."""
        import re
        pattern = r'\b' + re.escape(word) + r'\b'
        return bool(re.search(pattern, text))
    
    def retrieve_all_for_module(self, module: str) -> List[KnowledgeItem]:
        """Get all items for a specific module (for fallback/suggestions)."""
        return self.module_index.get(module, [])


# ============================================================================
# 5. TEST BLOCK
# ============================================================================

if __name__ == "__main__":
    # Test with a sample CSV (create one first if needed)
    csv_path = "knowledge_base.csv"
    
    # Create a sample CSV for testing if it doesn't exist
    if not os.path.exists(csv_path):
        print("Creating sample knowledge_base.csv for testing...")
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['module', 'question', 'answer', 'keywords'])
            writer.writerow([
                'about_xmum',
                'Who founded Xiamen University (XMU)?',
                'Xiamen University (XMU) was founded by the Malayan Chinese Mr. Tan Kah Kee.',
                'founder, XMU, Tan Kah Kee'
            ])
            writer.writerow([
                'campus_life',
                'When does the library open?',
                'The library is open Monday to Friday 8am-8pm, Saturday 9am-5pm, closed Sundays.',
                'library, hours, open, close'
            ])
    
    # Initialize retriever
    retriever = KnowledgeRetriever(csv_path)
    print(f"✓ Loaded {len(retriever.knowledge_base)} items from knowledge base\n")
    
    # Test queries
    test_queries = [
        ("founder of xmu", "about_xmum"),
        ("library opening hours", "campus_life"),
    ]
    
    for query, module in test_queries:
        print(f"Query: '{query}' (Module: {module})")
        best, score, all_scores = retriever.retrieve(module, query)
        
        if best:
            print(f"✓ Best match: {best.question}")
            print(f"  Score: {score:.1f}")
            print(f"  Answer: {best.answer[:80]}...")
        else:
            print("✗ No match found")
        print()

