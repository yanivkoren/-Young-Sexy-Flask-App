import os
import json
import requests
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_SOMETHING_RANDOM"

# Read your OpenRouter API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_API_KEY_HERE")

# OpenRouter endpoint (change if needed)
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Configure file paths for system prompts
SYSTEM_PROMPT_FILES = {
    "level1": "system_prompt_level1.txt",
    "level2": "system_prompt_level2.txt",
    "level3": "system_prompt_level3.txt",
    "level4": "system_prompt_level4.txt",
    "translation": "system_prompt_translation.txt"
}

###############################################################################
# Utility functions
###############################################################################

def read_file_content(filepath):
    """Reads the content of a file. Returns empty string if file not found."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""  # Or handle as needed

def write_file_content(filepath, content):
    """Writes content to a file (overwrites)."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def call_openrouter_api(model_name, system_prompt, user_prompt):
    """
    Calls OpenRouter with the given model, system prompt, and user prompt.
    Returns the 'content' string from the response if successful.
    Raises an exception or returns None on error.
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

    try:
        resp = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=data, timeout=60)
        resp.raise_for_status()  # Raise an error if the request failed
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error calling OpenRouter API:", e)
        return None

###############################################################################
# Routes
###############################################################################

MAIN_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Young & Sexy App</title>
    <style>
        /* Simple "young & sexy" vibe (Customize this to your liking) */
        body {
            margin: 0;
            padding: 0;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(to right, #ff9966, #ff5e62);
            color: #FFFFFF;
            text-align: center;
        }
        h1, h2 {
            margin-top: 1em;
        }
        .container {
            max-width: 600px;
            margin: 2em auto;
            padding: 2em;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        select, button {
            padding: 1em;
            margin: 1em;
            border: none;
            border-radius: 8px;
            font-size: 1em;
        }
        select {
            background: #ffffff;
            color: #333;
        }
        .gender-button {
            background: #ffd700;
            color: #333;
            cursor: pointer;
            transition: 0.3s;
        }
        .gender-button:hover {
            background: #ffc107;
        }
        .submit-button {
            background: #8affc1;
            color: #333;
            cursor: pointer;
            transition: 0.3s;
        }
        .submit-button:hover {
            background: #7fffa8;
        }
        .response-container {
            margin-top: 2em;
            background: rgba(0,0,0,0.3);
            padding: 1em;
            border-radius: 8px;
            text-align: left;
        }
        .model-name {
            font-weight: bold;
            color: #fffdcc;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Young & Sexy App</h1>
        <h2>Select a Level and Gender</h2>
        <form method="POST" action="{{ url_for('process_request') }}">
            <!-- Level Selection -->
            <label for="level">Choose Level:</label><br>
            <select name="level" id="level">
                <option value="level1">Level-1</option>
                <option value="level2">Level-2</option>
                <option value="level3">Level-3</option>
                <option value="level4">Level-4</option>
            </select>
            <br><br>

            <!-- Gender Selection -->
            <button type="submit" name="gender" value="men" class="gender-button">MEN</button>
            <button type="submit" name="gender" value="women" class="gender-button">FEMALE</button>
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

    <p style="margin-top:3em;">
        <a href="{{ url_for('edit_prompts') }}" style="color:#FFF; text-decoration:underline;">
            Admin: Edit System Prompts
        </a>
    </p>

</body>
</html>
"""

EDIT_PROMPTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit Prompts</title>
    <style>
        body {
            font-family: sans-serif;
            background: #f5f5f5;
            margin: 0; padding: 0;
        }
        .container {
            max-width: 900px;
            margin: 2em auto;
            background: #ffffff;
            padding: 2em;
            border-radius: 8px;
        }
        h1 {
            text-align: center;
        }
        label {
            font-weight: bold;
        }
        textarea {
            width: 100%;
            height: 150px;
            margin-bottom: 1em;
        }
        button {
            padding: 0.75em 2em;
            background: #007bff;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        a {
            text-decoration: none;
            color: #007bff;
            margin-top: 1em;
            display: inline-block;
        }
        .flash-message {
            background: #f7c5c0;
            padding: 0.5em;
            margin-bottom: 1em;
            border-radius: 4px;
            color: #700;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Edit System Prompts</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="flash-message">
              {{ messages[0] }}
            </div>
          {% endif %}
        {% endwith %}
        <form method="POST">
            <label for="level1">System Prompt for Level 1:</label>
            <textarea name="level1" id="level1">{{ prompts['level1'] }}</textarea>

            <label for="level2">System Prompt for Level 2:</label>
            <textarea name="level2" id="level2">{{ prompts['level2'] }}</textarea>

            <label for="level3">System Prompt for Level 3:</label>
            <textarea name="level3" id="level3">{{ prompts['level3'] }}</textarea>

            <label for="level4">System Prompt for Level 4:</label>
            <textarea name="level4" id="level4">{{ prompts['level4'] }}</textarea>

            <label for="translation">System Prompt for Translation:</label>
            <textarea name="translation" id="translation">{{ prompts['translation'] }}</textarea>

            <button type="submit">Save</button>
        </form>
        <p><a href="{{ url_for('index') }}">Back to Main Page</a></p>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    # Render the main page
    return render_template_string(MAIN_PAGE_TEMPLATE)

@app.route("/", methods=["POST"])
def process_request():
    # Capture form data
    level = request.form.get("level")
    gender = request.form.get("gender")

    # Determine the file name for the system prompt
    system_prompt_file = SYSTEM_PROMPT_FILES.get(level, "system_prompt_level1.txt")
    system_prompt = read_file_content(system_prompt_file)

    # Construct user prompt
    if gender.lower() == "men":
        user_prompt = "Write task for men"
    else:
        user_prompt = "Write task for women"

    # 1) Call Nous Hermes
    hermes_response = call_openrouter_api(
        model_name="nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    # 2) Call Grok for translation
    grok_response = None
    if hermes_response:
        translation_system_prompt = read_file_content(SYSTEM_PROMPT_FILES["translation"])
        grok_response = call_openrouter_api(
            model_name="x-ai/grok-2-vision-1212",
            system_prompt=translation_system_prompt,
            user_prompt=hermes_response
        )

    return render_template_string(MAIN_PAGE_TEMPLATE,
                                  hermes_response=hermes_response,
                                  grok_response=grok_response)

@app.route("/edit-prompts", methods=["GET", "POST"])
def edit_prompts():
    if request.method == "POST":
        # Save the updated content
        new_level1 = request.form.get("level1", "")
        new_level2 = request.form.get("level2", "")
        new_level3 = request.form.get("level3", "")
        new_level4 = request.form.get("level4", "")
        new_translation = request.form.get("translation", "")

        write_file_content(SYSTEM_PROMPT_FILES["level1"], new_level1)
        write_file_content(SYSTEM_PROMPT_FILES["level2"], new_level2)
        write_file_content(SYSTEM_PROMPT_FILES["level3"], new_level3)
        write_file_content(SYSTEM_PROMPT_FILES["level4"], new_level4)
        write_file_content(SYSTEM_PROMPT_FILES["translation"], new_translation)

        flash("Prompts saved successfully!")
        return redirect(url_for("edit_prompts"))

    # If GET, load the current file content
    prompts = {
        "level1": read_file_content(SYSTEM_PROMPT_FILES["level1"]),
        "level2": read_file_content(SYSTEM_PROMPT_FILES["level2"]),
        "level3": read_file_content(SYSTEM_PROMPT_FILES["level3"]),
        "level4": read_file_content(SYSTEM_PROMPT_FILES["level4"]),
        "translation": read_file_content(SYSTEM_PROMPT_FILES["translation"])
    }
    return render_template_string(EDIT_PROMPTS_TEMPLATE, prompts=prompts)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
