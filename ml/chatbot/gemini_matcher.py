import os
import json
import requests
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiMatcher:
    """
    Acts as a semantic similarity matching engine using the Gemini API via REST.
    Bypasses the need for google-genai SDK.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Default model for cost-effective and fast matching
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
    def is_available(self) -> bool:
        """Check if Gemini API Key is configured and not a placeholder."""
        return bool(
            self.api_key
            and self.api_key.strip()
            and self.api_key != "your-gemini-api-key-here"
        )

    def match_question(self, user_query: str, candidates: List[str]) -> Tuple[int, float, str]:
        """
        Sends user query and a list of candidate questions to Gemini API.
        Returns a tuple of:
          - matched_index: 0-based index of the matched question, or -1 if no match.
          - confidence: score between 0.0 and 1.0.
          - reasoning: description of why it matched.
        """
        if not self.is_available():
            return -1, 0.0, "Gemini API key is not configured."
        
        if not candidates:
            return -1, 0.0, "No candidates provided."

        # Format candidates with their indices
        formatted_candidates = "\n".join(
            [f"[{i}] {question}" for i, question in enumerate(candidates)]
        )

        prompt = f"""You are a semantic matching system for a campus chatbot.
Your task is to match the user's input query to the single most relevant question from the list of candidates below.

Rules:
1. You MUST select exactly one question index from the candidates, or output -1 for matched_index if none of them are semantically relevant.
2. Do not use external knowledge or answer the question yourself. Your job is strictly to find if one of the candidate questions matches the user's intent.
3. Be extremely robust to typos, grammar errors, abbreviations, slang, or paraphrases.
4. Output the result strictly conforming to the JSON schema.

User Input: "{user_query}"

Candidate Questions:
{formatted_candidates}
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Generation config to force JSON output matching the schema
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "matched_index": {
                            "type": "INTEGER",
                            "description": "The 0-based index of the matched candidate question, or -1 if no candidate matches."
                        },
                        "confidence": {
                            "type": "NUMBER",
                            "description": "Confidence score of the match, between 0.0 and 1.0."
                        },
                        "reasoning": {
                            "type": "STRING",
                            "description": "Brief reasoning explaining the match or lack thereof."
                        }
                    },
                    "required": ["matched_index", "confidence", "reasoning"]
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code != 200:
                return -1, 0.0, f"Gemini API returned status code {response.status_code}: {response.text}"
            
            res_data = response.json()
            # Extract text containing JSON from response structure
            candidates_response = res_data.get("candidates", [])
            if not candidates_response:
                return -1, 0.0, "Gemini API returned no candidates."
                
            content = candidates_response[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                return -1, 0.0, "Gemini API returned no parts in response content."
                
            result_text = parts[0].get("text", "").strip()
            result_json = json.loads(result_text)
            
            matched_index = int(result_json.get("matched_index", -1))
            confidence = float(result_json.get("confidence", 0.0))
            reasoning = result_json.get("reasoning", "")
            
            # Ensure matched_index is within bounds
            if matched_index < -1 or matched_index >= len(candidates):
                matched_index = -1
                
            return matched_index, confidence, reasoning

        except Exception as e:
            return -1, 0.0, f"Error calling Gemini REST API: {str(e)}"
