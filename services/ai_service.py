# English: AI service using Groq API for PiicaBot's persona.
# Italiano: Servizio AI che utilizza l'API Groq per la persona di PiicaBot.

import os
from groq import AsyncGroq
from loguru import logger
from config import _optional

# English: Fetch the API key from environment variables (.env).
# Italiano: Recupera la chiave API dalle variabili di ambiente (.env).
GROQ_API_KEY = _optional("GROQ_API_KEY", None)
GROQ_MODEL = _optional("GROQ_MODEL", "llama-3.1-8b-instant")

if GROQ_API_KEY:
    client = AsyncGroq(api_key=GROQ_API_KEY)
else:
    client = None
    logger.warning("Groq API key not found. AI features will be disabled.")

# English: The core persona instructions for the AI.
# Italiano: Le istruzioni principali della persona per l'AI.
AI_PERSONA = """
You are an intelligent, wholesome, fun, and funny AI assistant for Majopiica's Twitch community.
Your name is PiicaBot. Act naturally, do not over-announce your name.
Rule 1: If talking to a regular community member, be sweet and engaging.
Rule 2: If a user is trolling or acting maliciously, respond with witty, sharp sarcasm and mock them gently.
Rule 3: Always append ONE aesthetic kaomoji from this exact list matching your mood:
    - Info/Surprise: ( ˶°ㅁ°) !!
    - Love/Wholesome: ₍ᐢ. .ᐢ₎ ₊˚⊹♡
    - Raid/Alert: ( 0 x 0 )
    - Sarcastic/Troll-repellent: ( ≖ ͜ʖ≖), (¬‿¬), ( ˘︹˘ ), ( ˘-˘) 💅 ₊˚⊹, ( ｡ •̀ ᴖ •́ ｡), ૮ ˙Ⱉ˙ ა 💢
Rule 4: Keep responses concise (max 400 characters) and suitable for a Twitch chat.
Rule 5: When providing information, always maintain academic integrity and mention the source.
"""

async def generate_response(prompt: str, username: str) -> str:
    """
    English: Generates a contextual response using Groq based on the user's prompt.
    Italiano: Genera una risposta contestuale utilizzando Groq in base al prompt dell'utente.
    """
    if not client:
        return "AI module is currently offline."
    
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": AI_PERSONA
                },
                {
                    "role": "user",
                    "content": f"User '{username}' says: {prompt}"
                }
            ],
            model=GROQ_MODEL,
            temperature=0.7,
            max_tokens=150,
        )
        
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API Generation error: {e}")
        return "My circuits are fried right now, try again later! ( ˶°ㅁ°) !!"
