import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("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")  # Use the env variable only

def is_safe_prompt(prompt):
    try:
        response = openai.moderations.create(input=prompt)
        flagged = response.results[0].flagged
        return not flagged
    except Exception:
        return True  # fallback: allow prompt if moderation check fails
