# scripts/auto_qna_gemini.py
import os
import sys
import pathlib

try:
    from google import genai
except ImportError:
    print("ERROR: google-genai library is not installed.")
    print("Run: pip install google-genai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def convert_text_to_csv(input_file, output_file, module_name):
    # Ensure API Key is present
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable is not set!")
        print("In terminal (Powershell), run:")
        print('$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"')
        return False

    client = genai.Client()
    
    # Try reading the file, handling powershell utf-16le redirection if necessary
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except UnicodeDecodeError:
        try:
            with open(input_file, "r", encoding="utf-16") as f:
                raw_text = f.read()
        except Exception as e:
            print(f"Failed to read file {input_file}: {e}")
            return False
    except Exception as e:
        print(f"Failed to read file {input_file}: {e}")
        return False
        
    # Check if the file is empty to save API quota
    if not raw_text.strip():
        print(f"[SKIP] File {input_file} is empty! Skipping Gemini request to save quota.")
        # Create an empty CSV file so the next steps don't break
        with open(output_file, "w", encoding="utf-8-sig") as f:
            f.write("module,question,answer,keywords\n")
        return True
        
    prompt = f"""
    Analyze the following raw text from a university website and extract all important factual information into a comprehensive list of Question and Answer (Q&A) pairs.
    Format the output EXACTLY as a CSV without markdown code blocks, with the following header:
    module,question,answer,keywords
    
    Rules:
    1. The 'module' column must be exactly: {module_name}
    2. 'keywords' must be 3-4 comma-separated words enclosed in double quotes (e.g. "library, hours, open").
    3. Both 'question' and 'answer' must be enclosed in double quotes to prevent comma issues.
    4. Provide as many relevant Q&A pairs as possible (aim for at least 5-10 if the text is long).
    5. Do NOT output any conversational text or markdown like ```csv, JUST the raw CSV data.
    
    Here is the raw text:
    {raw_text}
    """
    
    print(f"[PROCESSING] Sending text ({len(raw_text)} characters) to Gemini API...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        output_text = response.text.strip()
        # Clean up markdown backticks if AI outputs them
        if output_text.startswith("```csv"):
            output_text = output_text[6:].strip()
        elif output_text.startswith("```"):
            output_text = output_text[3:].strip()
        if output_text.endswith("```"):
            output_text = output_text[:-3].strip()

        with open(output_file, "w", encoding="utf-8-sig") as f:
            f.write(output_text)
            
        print(f"[SUCCESS] Q&A successfully saved in CSV format at: {output_file}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to process data: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/auto_qna_gemini.py <file_raw.txt>")
        print("Example: python scripts/auto_qna_gemini.py database/seeds/clubs_societies_raw.txt")
        sys.exit(1)
        
    target_file = sys.argv[1]
    
    # Automate module naming
    # example: database/seeds/clubs_societies_raw.txt -> module: clubs_societies, output: ..._qa.csv
    base_name = pathlib.Path(target_file).stem
    module_name = base_name.replace("_raw", "")
    
    output_dir = pathlib.Path(target_file).parent
    output_csv = output_dir / f"{module_name}_qa.csv"
    
    success = convert_text_to_csv(target_file, output_csv, module_name)
    if not success:
        sys.exit(1)

