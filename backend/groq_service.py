import os
from dotenv import load_dotenv
from groq import Groq

# Load .env variables first so the client can find them immediately
load_dotenv()

# Initialize the Groq client using the environment variable
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_ai_response(prompt: str) -> str:
    """Sends a prompt to the Llama 3.3 70B Versatile model via Groq API."""
    try:
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