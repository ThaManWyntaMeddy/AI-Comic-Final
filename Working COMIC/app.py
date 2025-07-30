from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check if prompt violates OpenAI policy
def is_safe_prompt(prompt):
    try:
        response = openai.moderations.create(input=prompt)
        return not response.results[0].flagged
    except Exception:
        return True  # allow if check fails

# Check prompt for sensitive or bias-related keywords
def check_prompt_for_bias(prompt):
    keywords = ["Black", "Latino", "Latina", "Asian", "White", "Native", "Brown", "African", "race", "ethnicity", "person of color"]
    return any(word.lower() in prompt.lower() for word in keywords)

# Use GPT to break prompt into 6 panels
def split_into_panels(story_prompt):
    instruction = f"""
You are a comic writer. Break this story into 6 short numbered comic panel descriptions. 
Make it creative, safe, family-friendly, and avoid violence, hate, stereotypes, or politics.

Story: "{story_prompt}"
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": instruction}],
            temperature=0.8
        )
        result = response.choices[0].message.content.strip()
        return [line for line in result.split("\n") if line.strip()]
    except Exception as e:
        return [f"⚠️ Error splitting panels: {e}"] * 6

# Generate 6 images from panel descriptions
def generate_comic_panels(panel_texts):
    image_urls = []
    for i, panel_prompt in enumerate(panel_texts):
        full_prompt = f"Comic panel {i+1} of 6: {panel_prompt}"
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_urls.append(response.data[0].url)
        except openai.OpenAIError as e:
            if "content_policy_violation" in str(e).lower():
                image_urls.append("⚠️ Panel blocked due to OpenAI content policy.")
            else:
                image_urls.append(f"⚠️ Error generating image: {e}")
    return image_urls

# Main route
@app.route("/", methods=["GET", "POST"])
def index():
    user_prompt = ""
    safety_message = ""
    bias_message = ""
    image_urls = []

    if request.method == "POST":
        user_prompt = request.form.get("prompt", "").strip()

        # Step 1: Check for safety violation
        if not is_safe_prompt(user_prompt):
            safety_message = "🚫 This prompt violates OpenAI's policy. Try something more creative and safe."

        # Step 2: Check for sensitive keywords (but still allow)
        if check_prompt_for_bias(user_prompt):
            bias_message = "⚠️ This prompt might include sensitive or bias-related topics."

        # Step 3: If allowed, generate comic
        if not safety_message:
            panels = split_into_panels(user_prompt)
            image_urls = generate_comic_panels(panels)

    return render_template("index.html",
                           user_prompt=user_prompt,
                           safety_message=safety_message,
                           bias_message=bias_message,
                           image_urls=image_urls)

if __name__ == "__main__":
    app.run(debug=True)
