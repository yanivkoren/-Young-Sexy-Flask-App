import os
import json
import requests
import logging
from flask import Flask, render_template_string, request, redirect, url_for, flash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_SOMETHING_RANDOM"

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to logging.INFO to reduce verbosity
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Read OpenRouter API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_API_KEY_HERE")

# OpenRouter endpoint
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# System prompt file locations
SYSTEM_PROMPT_FILES = {
    "level1": "system_prompt_level1.txt",
    "level2": "system_prompt_level2.txt",
    "level3": "system_prompt_level3.txt",
    "level4": "system_prompt_level4.txt",
    "translation": "system_prompt_translation.txt"
}

###############################################################################
# HTML Template (Main Page)
###############################################################################

MAIN_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Young & Sexy Flask App</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: linear-gradient(to right, #ff9966, #ff5e62); color: white; }
        .container { max-width: 600px; margin: 2em auto; padding: 2em; background: rgba(255,255,255,0.1); border-radius: 10px; }
        select, button { padding: 10px; margin: 10px; border-radius: 5px; font-size: 16px; }
        .response-container { margin-top: 2em; background: rgba(0,0,0,0.3); padding: 1em; border-radius: 8px; }
        .model-name { font-weight: bold; color: #fffdcc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Young & Sexy Flask App</h1>
        <h2>Select a Level and Gender</h2>
        <form method="POST" action="{{ url_for('process_request') }}">
            <label for="level">Choose Level:</label><br>
            <select name="level" id="level">
                <option value="level1">Level-1</option>
                <option value="level2">Level-2</option>
                <option value="level3">Level-3</option>
                <option value="level4">Level-4</option>
            </select>
            <br><br>
            <button type="submit" name="gender" value="men">MEN</button>
            <button type="submit" name="gender" value="women">FEMALE</button>
        </form>
        {% if hermes_response and grok_response %}
        <div class="response-container">
            <div class="model-name">Nous Hermes Response:</div>
            <div>{{ hermes_response }}</div>
            <br>
            <div class="model-name">Grok Response:</div>
            <div>{{ grok_response }}</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

###############################################################################
# Utility Functions
###############################################################################

def read_file_content(filepath):
    """Reads the content of a file and logs it."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            logging.info(f"Read system prompt from {filepath}")
            return content
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return ""

def write_file_content(filepath, content):
    """Writes content to a file and logs the action."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        logging.info(f"Updated system prompt in {filepath}")

def call_openrouter_api(model_name, system_prompt, user_prompt):
    """
    Calls OpenRouter API and logs the response.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    logging.debug(f"Sending request to OpenRouter: {model_name} with user prompt: {user_prompt}")

    try:
        resp = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        response_content = result["choices"][0]["message"]["content"]
        logging.info(f"Received response from {model_name}: {response_content[:200]}...")  # Log first 200 chars
        return response_content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling OpenRouter API: {e}")
        return None

###############################################################################
# Routes
###############################################################################

@app.route("/", methods=["GET"])
def index():
    logging.info("Rendering main page.")
    return render_template_string(MAIN_PAGE_TEMPLATE)

@app.route("/", methods=["POST"])
def process_request():
    level = request.form.get("level")
    gender = request.form.get("gender")

    logging.info(f"Received form submission: Level={level}, Gender={gender}")

    if not level or not gender:
        logging.error("Form submission is missing required fields!")
        flash("Please select a level and gender.", "error")
        return redirect(url_for("index"))

    # Read system prompt file
    system_prompt_file = SYSTEM_PROMPT_FILES.get(level, "system_prompt_level1.txt")
    system_prompt = read_file_content(system_prompt_file)

    user_prompt = "Write task for men" if gender.lower() == "men" else "Write task for women"

    # Call Nous Hermes model
    hermes_response = call_openrouter_api(
        model_name="nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    if not hermes_response:
        flash("Error retrieving response from Nous Hermes.", "error")
        return redirect(url_for("index"))

    # Call Grok model for translation
    translation_system_prompt = read_file_content(SYSTEM_PROMPT_FILES["translation"])
    grok_response = call_openrouter_api(
        model_name="x-ai/grok-2-vision-1212",
        system_prompt=translation_system_prompt,
        user_prompt=hermes_response
    )

    if not grok_response:
        flash("Error retrieving response from Grok model.", "error")
        return redirect(url_for("index"))

    logging.info("Successfully retrieved responses from both models.")

    return render_template_string(MAIN_PAGE_TEMPLATE,
                                  hermes_response=hermes_response,
                                  grok_response=grok_response)

###############################################################################
# Run the Flask App
###############################################################################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
