import os
import json
import requests
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiTranslator:
    """
    Handles translation and grammar correction of user queries (preprocessing)
    and translating the retrieved answer back to the user's language (postprocessing)
    using the Gemini API via REST.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def is_available(self) -> bool:
        """Check if Gemini API Key is configured."""
        return bool(
            self.api_key
            and self.api_key.strip()
            and self.api_key != "your-gemini-api-key-here"
        )

    def preprocess_query(self, user_query: str) -> Dict[str, Any]:
        """
        Detects the language of the user query, translates it to English if necessary,
        and corrects any grammar or spelling mistakes.
        
        Returns:
            A dictionary containing:
            - detected_language: str (e.g., 'Indonesian', 'Chinese', 'Malay', 'English')
            - is_english: bool
            - cleaned_english_query: str (the English version with meaning optimized for DB retrieval)
        """
        if not self.is_available():
            return {
                "detected_language": "English",
                "is_english": True,
                "cleaned_english_query": user_query
            }

        prompt = f"""You are a multilingual preprocessing assistant for a campus chatbot.
Your task is to analyze the user's input query and perform the following:
1. Detect the language of the query.
2. Translate the query to English if it is in another language (like Malay, Chinese, Indonesian, Arabic, Russian, Tamil, Hindi, etc.).
3. Correct any grammar, spelling, and typo mistakes to produce a clean, grammatically correct English query.
4. Ensure the cleaned English query represents the core semantic meaning of the user's intent, phrased in a way that matches a database of campus FAQs (e.g. using standard terms like "library hours", "hostel application", "wifi connection", etc.).

Output the result strictly conforming to the JSON schema.

User Input: "{user_query}"
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
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
                        "detected_language": {
                            "type": "STRING",
                            "description": "The name of the detected language (e.g., 'Indonesian', 'Chinese', 'Malay', 'Arabic', 'Russian', 'English')."
                        },
                        "is_english": {
                            "type": "BOOLEAN",
                            "description": "True if the original input was already in English, False otherwise."
                        },
                        "cleaned_english_query": {
                            "type": "STRING",
                            "description": "The corrected, translated, and cleaned English query representing the core semantic meaning of the user's intent."
                        }
                    },
                    "required": ["detected_language", "is_english", "cleaned_english_query"]
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code != 200:
                print(f"[Translator] Gemini API error: {response.status_code} - {response.text}")
                return {
                    "detected_language": "English",
                    "is_english": True,
                    "cleaned_english_query": user_query
                }
            
            res_data = response.json()
            candidates = res_data.get("candidates", [])
            if not candidates:
                return {
                    "detected_language": "English",
                    "is_english": True,
                    "cleaned_english_query": user_query
                }
                
            result_text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
            result_json = json.loads(result_text)
            
            return {
                "detected_language": result_json.get("detected_language", "English"),
                "is_english": bool(result_json.get("is_english", True)),
                "cleaned_english_query": result_json.get("cleaned_english_query", user_query)
            }

        except Exception as e:
            print(f"[Translator] Error preprocessing query: {str(e)}")
            return {
                "detected_language": "English",
                "is_english": True,
                "cleaned_english_query": user_query
            }

    def translate_response(self, english_answer: str, target_language: str) -> str:
        """
        Translates the English answer from the knowledge base back to the target language.
        
        Args:
            english_answer: The answer text from the knowledge base (in English)
            target_language: The language to translate to (e.g., 'Indonesian', 'Chinese')
            
        Returns:
            The translated answer string.
        """
        if not self.is_available() or not target_language or target_language.lower() == "english":
            return english_answer

        prompt = f"""You are a professional translator.
Translate the following campus chatbot answer from English into {target_language}.
Ensure the translation is natural, polite, accurate, and retains all original details (like hours, links, emails, phone numbers, and formatting).
Do not add any introductory or concluding remarks. Output only the translated text.

English Answer:
{english_answer}
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
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
                        "translated_text": {
                            "type": "STRING",
                            "description": "The translated text."
                        }
                    },
                    "required": ["translated_text"]
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code != 200:
                print(f"[Translator] Gemini translation API error: {response.status_code}")
                return english_answer
            
            res_data = response.json()
            candidates = res_data.get("candidates", [])
            if not candidates:
                return english_answer
                
            result_text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
            result_json = json.loads(result_text)
            return result_json.get("translated_text", english_answer)

        except Exception as e:
            print(f"[Translator] Error translating response: {str(e)}")
            return english_answer
