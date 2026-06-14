# ============================================================================
# chatbot/chatbot_main.py
#
# Main Chatbot Controller - orchestrates the full NLP pipeline:
#   1. Entity Recognition (entity_recognizer.py)
#   2. Intent Classification (intent_classifier.py)
#   3. Knowledge Retrieval (retriever.py)
#   4. Response Generation
#
# This is the entry point that ties all components together.
# ============================================================================

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

# Import your friends' modules from the chatbot package
from chatbot.entity_recognizer import extract_entities, print_entities
from chatbot.intent_classifier import IntentClassifier
from chatbot.retriever import KnowledgeRetriever, KnowledgeItem


@dataclass
class ChatbotResponse:
    """Structured response from the chatbot."""
    answer: str
    confidence_score: float
    matched_question: Optional[str] = None
    module: Optional[str] = None
    sub_intent: Optional[str] = None
    extracted_entities: Optional[Dict[str, List[str]]] = None
    top_alternatives: Optional[List[Tuple[str, float]]] = None
    debug_info: Optional[str] = None


class XMUMChatbot:
    """
    XMUMC Campus Assistant — main chatbot orchestrator.
    
    Pipeline:
    1. User sends message
    2. Extract entities (what are they asking about?)
    3. Classify intent (which module/category?)
    4. Retrieve matching answer from knowledge base
    5. Return structured response
    """
    
    def __init__(self):
        """
        Initialize the chatbot with all required components.
        Loads knowledge base from Supabase.
        """
        self.intent_classifier = IntentClassifier()
        self.retriever = KnowledgeRetriever()  # Loads from Supabase automatically
        print("[Chatbot] ✓ Initialized with intent classifier and Supabase knowledge base")
    
    def process_message(
        self,
        user_message: str,
        debug: bool = True
    ) -> ChatbotResponse:
        """
        Process a user message through the full pipeline.
        
        Args:
            user_message: Raw user input
            debug: Whether to include detailed debug info
        
        Returns:
            ChatbotResponse with answer and metadata
        """
        # ──────────────────────────────────────────────────────────────
        # Step 1: Extract Entities
        # ──────────────────────────────────────────────────────────────
        entities = extract_entities(user_message)
        
        # ──────────────────────────────────────────────────────────────
        # Step 2: Classify Intent
        # ──────────────────────────────────────────────────────────────
        module, sub_intent = self.intent_classifier.classify(user_message)
        
        # ──────────────────────────────────────────────────────────────
        # Step 3: Retrieve Answer
        # ──────────────────────────────────────────────────────────────
        if module == "unknown":
            return self._handle_unknown(
                user_message, entities, debug
            )
        
        best_item, confidence, all_scores = self.retriever.retrieve(
            module=module,
            user_message=user_message,
            extracted_entities=entities
        )
        
        # ──────────────────────────────────────────────────────────────
        # Step 4: Build Response
        # ──────────────────────────────────────────────────────────────
        if best_item and confidence > 0:
            return self._build_success_response(
                best_item, confidence, all_scores, module, sub_intent,
                entities, debug
            )
        else:
            return self._handle_no_match(module, entities, debug)
    
    def _build_success_response(
        self,
        best_item: KnowledgeItem,
        confidence: float,
        all_scores: List[Tuple[KnowledgeItem, float]],
        module: str,
        sub_intent: str,
        entities: Dict[str, List[str]],
        debug: bool
    ) -> ChatbotResponse:
        """Build a successful response with match found."""
        
        # Prepare top alternatives for scoring display
        top_alternatives = [
            (item.question, score)
            for item, score in all_scores[:5]
            if score > 0
        ]
        
        debug_info = ""
        if debug:
            debug_info = self._generate_debug_info(
                best_item, confidence, top_alternatives, entities,
                module, sub_intent
            )
        
        return ChatbotResponse(
            answer=best_item.answer,
            confidence_score=confidence,
            matched_question=best_item.question,
            module=module,
            sub_intent=sub_intent,
            extracted_entities=entities if entities else None,
            top_alternatives=top_alternatives,
            debug_info=debug_info
        )
    
    def _handle_no_match(
        self,
        module: str,
        entities: Dict[str, List[str]],
        debug: bool
    ) -> ChatbotResponse:
        """Handle case where no good match is found."""
        
        answer = (
            "Sorry, I couldn't find specific information about that. "
            "Try asking about: library hours, hostel rules, scholarship, "
            "course registration, WiFi, facilities, or academic calendars."
        )
        
        debug_info = ""
        if debug:
            debug_info = f"[Module: {module}] No high-confidence match found."
        
        return ChatbotResponse(
            answer=answer,
            confidence_score=0.0,
            module=module,
            sub_intent="unknown",
            extracted_entities=entities if entities else None,
            debug_info=debug_info
        )
    
    def _handle_unknown(
        self,
        user_message: str,
        entities: Dict[str, List[str]],
        debug: bool
    ) -> ChatbotResponse:
        """Handle case where intent cannot be classified."""
        
        answer = (
            "I'm not sure what you're asking about. "
            "I can help with: campus information, hostel, library, "
            "academic matters, scholarships, WiFi, and more. "
            "What would you like to know?"
        )
        
        debug_info = ""
        if debug:
            debug_info = "[Intent] Could not classify the user's intent."
        
        return ChatbotResponse(
            answer=answer,
            confidence_score=0.0,
            module="unknown",
            sub_intent="unknown",
            extracted_entities=entities if entities else None,
            debug_info=debug_info
        )
    
    def _generate_debug_info(
        self,
        best_item: KnowledgeItem,
        confidence: float,
        top_alternatives: List[Tuple[str, float]],
        entities: Dict[str, List[str]],
        module: str,
        sub_intent: str
    ) -> str:
        """Generate detailed debug information for response."""
        
        debug_lines = [
            f"[Module] {module}",
            f"[Sub-Intent] {sub_intent}",
            f"[Confidence] {confidence:.1f}",
            f"[Matched Question] {best_item.question}",
        ]
        
        if entities:
            entity_str = ", ".join(
                f"{k}:{','.join(v)}" for k, v in entities.items()
            )
            debug_lines.append(f"[Entities] {entity_str}")
        
        if top_alternatives:
            alt_str = " | ".join(
                f"{q[:30]}... ({s:.1f})"
                for q, s in top_alternatives[:3]
            )
            debug_lines.append(f"[Top Matches] {alt_str}")
        
        return " | ".join(debug_lines)
    
    def get_module_suggestions(self, module: str, limit: int = 5) -> List[str]:
        """
        Get suggestion questions for a specific module.
        Useful for UI quick-suggestions.
        """
        items = self.retriever.retrieve_all_for_module(module)
        return [item.question for item in items[:limit]]


# ============================================================================
# FORMATTER — Convert response to different outputs
# ============================================================================

class ResponseFormatter:
    """Format ChatbotResponse for different output targets."""
    
    @staticmethod
    def to_dict(response: ChatbotResponse) -> Dict:
        """Convert response to dictionary (for JSON API)."""
        return {
            "answer": response.answer,
            "confidence": response.confidence_score,
            "matched_question": response.matched_question,
            "module": response.module,
            "sub_intent": response.sub_intent,
            "entities": response.extracted_entities,
            "debug": response.debug_info if response.debug_info else None,
        }
    
    @staticmethod
    def to_json(response: ChatbotResponse) -> str:
        """Convert response to JSON string."""
        return json.dumps(ResponseFormatter.to_dict(response), indent=2)
    
    @staticmethod
    def to_console(response: ChatbotResponse) -> str:
        """Format for console/CLI output."""
        lines = [
            "=" * 70,
            f"🤖 XMUMC Assistant Response",
            "=" * 70,
            f"\nAnswer:\n{response.answer}",
            f"\n Confidence: {response.confidence_score:.1%}",
        ]
        
        if response.matched_question:
            lines.append(f" Matched Question: {response.matched_question}")
        
        if response.debug_info:
            lines.append(f"\n Debug Info:\n{response.debug_info}")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
    
    @staticmethod
    def to_html_debug(response: ChatbotResponse) -> str:
        """Format as HTML for embedding in web UI (like your original)."""
        html = f"""
        <div class="bot-response">
            <div class="answer">{response.answer}</div>
            <div class="debug-pill">
                <b>Best match:</b> "{response.matched_question}" 
                — confidence {response.confidence_score:.1f}
            </div>
        </div>
        """
        return html.strip()


# ============================================================================
# INTERACTIVE CLI MODE
# ============================================================================

def run_interactive_cli():
    """
    Run the chatbot in interactive CLI mode.
    Loads knowledge base from Supabase.
    """
    print("\n" + "=" * 70)
    print("  XMUMC Campus Assistant — Interactive Mode (Supabase)")
    print("=" * 70)
    print("Type your questions. Type 'quit' or 'exit' to stop.\n")
    
    chatbot = XMUMChatbot()  # Loads from Supabase automatically
    
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            print("\nGoodbye! ")
            break
        
        response = chatbot.process_message(user_input, debug=True)
        print(ResponseFormatter.to_console(response))
        print()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        run_interactive_cli()
    except Exception as e:
        print(f" Error: {e}")
        print(f"Make sure .env file has SUPABASE_URL and SUPABASE_ANON_KEY")
        import sys
        sys.exit(1)
