import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def generate_ai_response(prompt: str) -> str:
    """Sends a prompt to the Llama 3.3 70B Versatile model via Groq API."""
    # Check both standard names just in case Render environment configuration differs
    api_key = os.environ.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "Groq API Error: GROQ_API_KEY is missing from environment variables."
    
    try:
        # Initialize client fresh per request
        client = Groq(api_key=api_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        # This will return the exact internal error text so we can see what's failing on Render
        return f"Groq API Error: Connection error ({str(e)})"