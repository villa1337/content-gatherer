import os
import time
import requests
import json
import ast
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")

def query_groq(prompt: str, model="llama3-70b-8192") -> str:
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "fractal-knowledge-explorer/1.0"
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2500
    }
    time.sleep(1)  # Delay to reduce risk of rate limiting
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=body,
            headers=headers
        )
        response.raise_for_status()
        try:
            final_response = response.json()["choices"][0]["message"]["content"]
            print(f"✅ Groq response: {final_response}")
            return final_response
        except json.JSONDecodeError as json_err:
            print(f"❌ JSONDecodeError: {json_err}")
            print(f"⚠️ Raw response text: {response.text}")
            raise
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ GROQ HTTP error occurred: {http_err}")
        if response.status_code == 429 and model != "llama3-70b-8192":
            print("🔁 Retrying with fallback model...")
            return query_groq(prompt, model="llama3-13b-4096")
        raise
    except requests.exceptions.RequestException as req_err:
        print(f"❌ RequestException occurred: {req_err}")
        raise
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        raise

def get_key_words(content) -> str:
    dirty_key_words = query_groq(f"""
    Generate 6 VISUAL keywords/phrases for image search from this article. Focus on:
    - Concrete objects, people, places, buildings
    - Visual scenes that can be photographed
    - Specific locations, landmarks, or recognizable things
    - Avoid abstract concepts like "reform", "conditions", "concepts"
    
    Article:
    Title: {content["title"]}
    Text: {content["text"][:800]}...
    
    Examples of GOOD visual keywords:
    - "prison cell bars", "courthouse building", "police officer", "New York skyline"
    - "hospital emergency room", "school classroom", "factory workers"
    
    Examples of BAD abstract keywords:
    - "justice system", "reform efforts", "policy changes", "social issues"
    
    Return only the array, nothing more, no explanation.
    """)
    return convert_to_list(dirty_key_words)

def get_summary(content: str) -> str:
    return query_groq(f""" give me a summary of the following article: {content["text"]} 
    
    Return only the summary, nothing more, no explanation, don't start with Here is a summary of the article: or any other text.
    """)

def get_youtube_title(content) -> str:
    """Generate a powerful YouTube Shorts title with selective CAPS for maximum clicks."""
    return query_groq(f"""
    Create a viral, edgy YouTube Shorts title for the following content:
    Title: {content["title"]}
    Summary: {content["text"][:500]}...

    Guidelines:
    - Keep it under 60 characters
    - Use emotionally charged words like SHOCKING, TRAGIC, BREAKING, BANNED, etc.
    - Use CAPS only on key emotional/action words (not the whole title), don't over use CAPS
    - Create urgency, mystery, or drama
    - Perfect for YouTube Shorts click-through

    Return only the title, no quotes or explanation.
    """)

def get_youtube_description(content) -> str:
    """Generate a short viral description with tiered hashtags for YouTube Shorts."""
    return query_groq(f"""
    Create a short, viral YouTube Shorts description for the following article:
    Title: {content["title"]}
    Summary: {content["text"][:300]}...

    Format:
    - 1 engaging sentence (no more than 100 characters)
    - End with 6-9 hashtags:
        - 2-3 broad/trending (#news, #breakingnews, #crime, etc.)
        - 2-3 mid-topic (#planekills, #chinaeconomy, #schooltragedy, etc.)
        - 2-3 niche-specific if relevant (#unesco2025, #idahomurders, etc.)
    - Total length must be under 150 characters

    Example style:
    A tragic crash leaves 33 dead at a school. #news #breaking #tragedy #aircrash #schoolkids #shocking

    Return only the description with hashtags, no extra text.
    """)

def convert_to_list(key_words):
    """Convert various string representations of lists into a Python list.
    
    Args:
        key_words: String that might contain a list representation
        
    Returns:
        list: List of keywords, or empty list if conversion fails
    """
    if not key_words or not isinstance(key_words, str):
        return []
    
    # Clean up the string
    key_words = key_words.strip()
    
    # Try direct JSON parsing first (most reliable)
    try:
        key_words_list = json.loads(key_words)
        if isinstance(key_words_list, list):
            return [str(item).strip('"\'') for item in key_words_list if item]
    except json.JSONDecodeError:
        pass
    
    # Try ast.literal_eval for Python-like lists
    try:
        import ast
        key_words_list = ast.literal_eval(key_words)
        if isinstance(key_words_list, list):
            return [str(item).strip('"\'') for item in key_words_list if item]
    except (ValueError, SyntaxError):
        pass
    
    # Try to extract keywords from bullet points or numbered lists
    lines = [line.strip(' -*•') for line in key_words.split('\n') if line.strip()]
    if lines:
        # Check if the first line is a header like "Here are the keywords:"
        if any(header in lines[0].lower() for header in ['keyword', 'here are', 'following']):
            lines = lines[1:]  # Skip the header line
        
        # Clean each line and filter out empty ones
        keywords = [line.strip('"\'') for line in lines if line.strip()]
        if keywords:
            return keywords
    
    # If all else fails, try to parse as comma-separated values
    if ',' in key_words:
        return [kw.strip('"\' ') for kw in key_words.split(',') if kw.strip()]
    
    # If it's a single word/phrase, return it in a list
    if key_words:
        return [key_words.strip('"\'')]
    
    return []