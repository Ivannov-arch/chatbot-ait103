# ============================================================================
# chatbot/retriever.py
#
# Retriever - fetches answers from Supabase database based on:
#   1. Intent classification (module + sub_intent)
#   2. Entity extraction
#   3. Keyword/template matching
#
# Workflow:
#   1. Load knowledge base from Supabase
#   2. Score templates using keyword matching
#   3. Return best match with confidence score
# ============================================================================

import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()


@dataclass
class KnowledgeItem:
    """Represents a single Q&A entry from the knowledge base."""
    module: str
    question: str
    answer: str
    keywords: List[str]
    sub_intent: Optional[str] = None
    id: Optional[str] = None


class KnowledgeRetriever:
    """
    Loads and searches through the knowledge base.
    
    Attributes:
        knowledge_base: List of KnowledgeItem objects
        module_index: Dict mapping module names to items
    """
    
    def __init__(self):
        """
        Initialize retriever and load knowledge base from Supabase.
        """
        self.supabase: Optional[Client] = None
        self.knowledge_base: List[KnowledgeItem] = []
        self.module_index: Dict[str, List[KnowledgeItem]] = {}
        self._connect_supabase()
        self._load_from_supabase()
    
    def _connect_supabase(self) -> None:
        """Connect to Supabase using credentials from .env"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file"
            )
        
        self.supabase = create_client(supabase_url, supabase_key)
        print("[Retriever]  Connected to Supabase")
    
    def _load_from_supabase(self) -> None:
        """Load knowledge base from Supabase database."""
        try:
            # Fetch all rows from knowledge_items table
            response = self.supabase.table("knowledge_items").select("*").execute()
            
            data = response.data
            print(f"[Retriever]  Loaded {len(data)} items from Supabase")
            
            for row in data:
                module = row.get('module', '').lower()
                keywords = row.get('keywords', [])
                
                # Handle keywords - could be list or comma-separated string
                if isinstance(keywords, str):
                    keywords = [kw.strip().lower() for kw in keywords.split(',')]
                else:
                    keywords = [kw.lower() for kw in keywords]
                
                item = KnowledgeItem(
                    module=module,
                    question=row.get('question', ''),
                    answer=row.get('answer', ''),
                    keywords=keywords,
                    sub_intent=row.get('sub_intent'),
                    id=row.get('id')
                )
                
                self.knowledge_base.append(item)
                
                # Index by module for faster lookup
                if module not in self.module_index:
                    self.module_index[module] = []
                self.module_index[module].append(item)
        
        except Exception as e:
            print(f"[Retriever]  Error loading from Supabase: {e}")
            raise
    
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
        best_raw_score = scores[0][1] if scores else 0.0
    
        # Calculate max possible score and normalize to 0-100%
        max_possible = max([len(item.keywords) * 2.0 for item in candidates]) if candidates else 1.0
        best_score = min(100.0, (best_raw_score / max_possible) * 100) if max_possible > 0 else 0.0
    
        # Normalize all scores too
        normalized_scores = [
        (item, min(100.0, (raw_score / max_possible) * 100))
        for item, raw_score in scores
        ]
        
        return best_item, best_score, normalized_scores
    
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
# TEST BLOCK
# ============================================================================

if __name__ == "__main__":
    try:
        # Initialize retriever (loads from Supabase)
        retriever = KnowledgeRetriever()
        print(f"[Test]  Loaded {len(retriever.knowledge_base)} items from Supabase\n")
        
        # Test queries
        test_queries = [
            ("library", "campus_life"),
            ("makerspace", "campus_life"),
        ]
        
        for query, module in test_queries:
            print(f"Query: '{query}' (Module: {module})")
            best, score, all_scores = retriever.retrieve(module, query)
            
            if best:
                print(f" Best match: {best.question}")
                print(f"  Score: {score:.1f}")
                print(f"  Answer: {best.answer[:100]}...")
            else:
                print(" No match found")
            print()
    
    except Exception as e:
        print(f"Error during test: {e}")
        print("Make sure .env file exists with SUPABASE_URL and SUPABASE_ANON_KEY")
