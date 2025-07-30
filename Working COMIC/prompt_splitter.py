import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("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")  # Be sure this matches your .env key name

def split_into_panels(story_prompt):
    instruction = f"""
    Break this story into 6 numbered short scene descriptions for a comic strip.
    Each panel must build on the last to create a clear, connected narrative arc.
    Keep each panel's description concise, visual, and creative.

    Story: "{story_prompt}"
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": instruction}],
            temperature=0.75
        )
        result = response.choices[0].message.content.strip()
        # Return just the 6 descriptions
        panels = [line.strip() for line in result.split("\n") if line.strip()]
        return panels[:6] if len(panels) >= 6 else panels + ["(Empty)"] * (6 - len(panels))
    except Exception as e:
        return [f"Error: {e}"] * 6
