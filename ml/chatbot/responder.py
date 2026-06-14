# responder.py
from chatbot_main import ChatbotResponse
import os
import random
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

class ResponseFormatter:
    """Format ChatbotResponse for different output targets."""
    
    @staticmethod
    def _to_dict(response: ChatbotResponse) -> Dict:
        """Convert response to dictionary (for JSON API)."""
        return {
            "answer": response.answer,
            "confidence": response.confidence_score,
            "matched_question": response.matched_question,
            "module": response.module,
            "sub_intent": response.sub_intent,
            "entities": response.extracted_entities,
            "debug": response.debug_info
        }

    @staticmethod
    def _to_json(response: ChatbotResponse) -> str:
        """Convert response to JSON string."""
        return json.dumps(ResponseFormatter._to_dict(response), indent=2)

    @staticmethod
    def _to_console(response: ChatbotResponse):
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

        

def log_unrecognized_query(raw_text):
    """
    [Responsibility 4: Unrecognised query logging]
    Automatically logs failed queries alongside a timestamp to a local file
    for administrators to review and patch knowledge gaps later.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] UNRECOGNIZED QUERY: {raw_text}\n"

    try:
        with open("failed_queries.txt", "a", encoding="utf-8") as file:
            file.write(log_entry)
        print("[System Log]: Unknown query successfully logged to 'failed_queries.txt'.")
    except Exception as e:
        print(f"[System Error]: Failed to write to log file: {e}")


def get_varied_fallback_phrase():
    """
    [Responsibility 3 & 6: Escalation prompt & Varied phrasing]
    Uses a randomized pool of responses so the chatbot avoids sounding repetitive.
    Includes an escalation clause directing the user to official campus channels.
    """
    fallback_pool = [
        "I didn't quite catch that. Could you please rephrase your campus-related question?",
        "I'm still learning the XMUM handbook! Could you try asking that another way?",
        "I'm sorry, I don't have information on that topic yet. If your issue is urgent, please contact the XMUM Academic Affairs Office directly."
    ]
    return random.choice(fallback_pool)


def generate_template_response(official_answer, user_name="Student"):
    """
    [Responsibility 5: Template-based response generation]
    Wraps the static CSV handbook answer inside a dynamic response template.
    Injects real-time system greetings, timestamps, and personalized names
    to fulfill the requirement of generating structured templates with dynamic data.
    """

    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    current_date = datetime.now().strftime("%Y-%m-%d")

    template = (
        "[{greeting}, {user}! (Processed on {date})]\n"
        "Here is the official handbook information regarding your query:\n"
        "--------------------------------------------------\n"
        "{answer}\n"
        "--------------------------------------------------"
    )

    return template.format(greeting=greeting, user=user_name, date=current_date, answer=official_answer)


def process_chatbot_output(confidence, matched_row, user_raw_input=""):
    """
    Core Pipeline Controller:
    Evaluates confidence scores to execute direct replies, close suggestions,
    or fallback/logging triggers.
    """
    CONFIDENCE_THRESHOLD = 0.50  # >= 50%: Highly confident, direct answer
    NEAR_MISS_THRESHOLD = 0.35  # 35% to 50%: Borderline confident, ask clarifying question

    # Scenario A: [Responsibility 1] Low confidence fallback
    if confidence < NEAR_MISS_THRESHOLD:
        log_unrecognized_query(user_raw_input)
        return get_varied_fallback_phrase()

    # Scenario B: [Responsibility 2] Closest suggestion prompt
    elif NEAR_MISS_THRESHOLD <= confidence < CONFIDENCE_THRESHOLD:
        if matched_row is not None and 'question' in matched_row:
            suggested_q = matched_row['question']
            return f"I'm not completely sure I understood, but did you mean: \"{suggested_q}\"?"
        else:
            return get_varied_fallback_phrase()

    # Scenario C: Successful intent match -> Dynamic template output
    else:
        if matched_row is not None and 'answer' in matched_row:
            official_ans = matched_row['answer']
            return generate_template_response(official_ans, user_name="Alex")
        else:
            return get_varied_fallback_phrase()


# [AUTOMATED TESTING SUITE]
if __name__ == "__main__":
    print("=" * 60)
    print("XMUM CHATBOT MODULE 5 - FULL PRODUCTION TEST RUN")
    print("=" * 60)

    # Try database/seeds first, then local directory
    csv_filename = os.path.join("database", "seeds", "xmum_handbook_ocr_qa.csv")
    if not os.path.exists(csv_filename):
        csv_filename = "xmum_handbook_ocr_qa.csv"

    # Safety Check: Verifies the database exists to prevent execution crashes
    if not os.path.exists(csv_filename):
        print(f"[CRITICAL ERROR]: Cannot find the database file '{csv_filename}' in this folder.")
        print("Please make sure you placed the uploaded CSV file into the exact same folder as this Python script!")
    else:
        print(f"[SUCCESS]: Found '{csv_filename}'. Loading database...")
        # Load the CSV handbook dataset
        df = pd.read_csv(csv_filename)
        print(f"Successfully loaded {len(df)} handbook QA pairs.\n")

        # Test 1: Perfect Match (Confidence = 0.95) -> Triggers Template Generation
        print("--- [TEST 1: HIGH CONFIDENCE MATCH (Motto Query)] ---")
        mock_row_1 = df.iloc[1]  # Extracts the row containing the university motto
        response_1 = process_chatbot_output(confidence=0.95, matched_row=mock_row_1)
        print(response_1)
        print("\n" + "-" * 50 + "\n")

        # Test 2: Vague Match (Confidence = 0.42) -> Triggers Closest Suggestion Prompt
        print("--- [TEST 2: WEAK MATCH (Vision Query Suggestion)] ---")
        mock_row_2 = df.iloc[2]  # Extracts the row containing the university vision statement
        response_2 = process_chatbot_output(confidence=0.42, matched_row=mock_row_2)
        print(f"[Bot Reply]: {response_2}")
        print("\n" + "-" * 50 + "\n")

        # Test 3: Complete Failure (Confidence = 0.12) -> Triggers Logging & Fallback
        print("--- [TEST 3: NO MATCH (Irrelevant Query)] ---")
        user_input_3 = "Can I order chicken rice through this chatbot?"
        response_3 = process_chatbot_output(confidence=0.12, matched_row=None, user_raw_input=user_input_3)
        print(f"[Bot Reply]: {response_3}")
        print("\n" + "-" * 50 + "\n")

        print("ALL TESTS COMPLETED SUCCESSFULLY WITHOUT ERROR.")
        print("Check your folder to see the newly generated 'failed_queries.txt' file!")