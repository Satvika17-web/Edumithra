import os
import httpx
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def generate_ai_response(prompt: str) -> str:
    """Sends a prompt to the Llama 3.3 70B Versatile model via Groq API."""
    api_key = os.environ.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "Groq API Error: GROQ_API_KEY is missing from environment variables."
    
    try:
        # Create an explicit transport layer that bypasses cloud container SSL blockages
        transport = httpx.HTTPTransport(verify=False)
        secure_client = httpx.Client(transport=transport, timeout=60.0)
        
        # Initialize Groq with the cloud-safe HTTP client, keeping the exact 70b model
        client = Groq(
            api_key=api_key,
            http_client=secure_client
        )
        
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
        return f"Groq API Error: Connection error ({str(e)})"