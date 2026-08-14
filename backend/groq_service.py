import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def generate_ai_response(prompt: str) -> str:
    """Sends a prompt to the Llama 3.3 70B Versatile model via Groq API."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Groq API Error: GROQ_API_KEY is missing from environment variables."
    
    try:
        # Initialize client inside the function call so it grabs the environment variable fresh
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
        return f"Groq API Error: {str(e)}"