import os
import json
import requests
import logging
from flask import Flask, render_template_string, request, redirect, url_for, flash
# from flask_markdown import Markdown
from flask import Markup
import mistune
import random
from flask import send_file

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_SOMETHING_RANDOM"
# את זה יש להוסיף אחרי יצירת האובייקט של Flask
# Markdown(app)

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
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            background: linear-gradient(to right, black, red, black); /* רקע מעוצב */
            color: white;
        }

        /* עיצוב הספינר */
        .loading-spinner {
            display: none; /* מוסתר כברירת מחדל */
            width: 50px;
            height: 50px;
            border: 5px solid rgba(255, 255, 255, 0.3);
            border-top: 5px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }

        /* אנימציה של הסיבוב */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>

</head>
<body>
    <div class="container">
        <div id="loadingSpinner" class="loading-spinner"></div>
        <button class="settings-icon" onclick="window.location.href='/edit_prompts'">⚙️</button>
        <h1>Young & Sexy Flask App</h1>
        <h2>Select a Level and Choose Randomly</h2>
        <form method="POST" action="{{ url_for('choose_randomly') }}">
            <label for="level">Choose Level:</label><br>
            <select name="level" id="level">
                <option value="level1" {% if level == "level1" %}selected{% endif %}>Level-1</option>
                <option value="level2" {% if level == "level2" %}selected{% endif %}>Level-2</option>
                <option value="level3" {% if level == "level3" %}selected{% endif %}>Level-3</option>
                <option value="level4" {% if level == "level4" %}selected{% endif %}>Level-4</option>
            </select>
            <br><br>
            <button type="submit">Choose Randomly</button>
        </form>

        {% if gender %}
            <h3>Selected Gender: {{ gender | upper }}</h3>
            <form method="POST" action="{{ url_for('process_request') }}" onsubmit="showLoading()">
                <input type="hidden" name="gender" value="{{ gender }}">
                <input type="hidden" name="level" value="{{ level }}">
                <button type="submit" id="getTaskButton">Get Task</button>
            </form>
        {% endif %}

        {% if hermes_response and grok_response %}
        <div class="response-container">
            <div class="model-name" style="text-align: left; direction: ltr;">Nous Hermes Response:</div>
            <div style="text-align: left; direction: ltr;">{{ hermes_response }}</div>
            <br>
            <div class="model-name" style="text-align: right; direction: rtl;">Grok Response:</div>
            <div style="text-align: right; direction: rtl;">{{ grok_response }}</div>
        </div>

        <!-- טיימר -->
        <div class="timer-container">
            <h3>Set Timer:</h3>
            <select id="timerDuration">
                <option value="30">30 seconds</option>
                <option value="60" selected>1 minute</option>
                <option value="90">1.5 minutes</option>
                <option value="120">2 minutes</option>
            </select>
            <br><br>
            <button onclick="startTimer()">Start Timer</button>
            <h3 id="timerDisplay">Time Left: --:--</h3>
        </div>

        <!-- אלמנט להפקת צליל -->
        <audio id="alarmSound" src="/alarm.mp3"></audio>

        <script>
            // הסתרת הספינר כאשר הנתונים מוצגים
            document.addEventListener("DOMContentLoaded", function() {
                document.getElementById("loadingSpinner").style.display = "none"; 
            });

            let timer;
            let audio = document.getElementById("alarmSound");

            // פונקציה שמאפשרת לדפדפן "לאשר" השמעת צליל
            function enableAudio() {
                audio.play().then(() => {
                    audio.pause();
                    audio.currentTime = 0;  // מחזיר להתחלה אחרי ההפעלה הראשונה
                }).catch(error => {
                    console.error("Audio play blocked:", error);
                });

                document.removeEventListener("click", enableAudio);
            }

            // מאזין שמאפשר אודיו כאשר המשתמש לוחץ על המסך
            document.addEventListener("click", enableAudio);

            function startTimer() {
                let duration = parseInt(document.getElementById("timerDuration").value);
                let display = document.getElementById("timerDisplay");

                clearInterval(timer);  // איפוס טיימר קודם
                let timeLeft = duration;

                function updateDisplay() {
                    let minutes = Math.floor(timeLeft / 60);
                    let seconds = timeLeft % 60;
                    display.innerHTML = `Time Left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
                }

                updateDisplay();  // עדכון ראשוני
                timer = setInterval(() => {
                    if (timeLeft > 0) {
                        timeLeft--;
                        updateDisplay();
                    } else {
                        clearInterval(timer);
                        audio.play();  // עכשיו הצליל יפעל
                        display.innerHTML = "Time's up!";
                    }
                }, 1000);
            }
        </script>
        {% endif %}



    </div>
    <script>
        function showLoading() {
            var getTaskButton = document.getElementById("getTaskButton");
            var loadingSpinner = document.getElementById("loadingSpinner");

            if (getTaskButton) getTaskButton.style.display = "none";  // הסתרת הכפתור
            if (loadingSpinner) loadingSpinner.style.display = "block"; // הצגת הספינר
        }
    </script>
</body>
</html>
"""
EDIT_PROMPTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit System Prompts</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: #f4f4f4;
            color: #333;
        }

        .container {
            max-width: 90%; /* במקום רוחב קבוע */
            width: 600px;
            margin: 2em auto;
            padding: 2em;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            position: relative;
        }

        textarea {
            width: 100%;
            height: 150px;
            margin-top: 10px;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }

        button {
            padding: 10px 20px;
            margin-top: 10px;
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
            font-size: 1rem;  /* קובע גודל טקסט יחסי */
            width: 100%;  /* מתאים את הכפתור למסכים קטנים */
            max-width: 300px;  /* מגביל את הרוחב המקסימלי */
            transition: background 0.3s ease-in-out; /* מעבר חלק בצבע */
        }

        button:hover {
            background: #0056b3;
        }


    </style>
    <script>
        function loadFileContent() {
            var selectedFile = document.getElementById("filename").value;
            window.location.href = "/edit_prompts?filename=" + selectedFile;
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Edit System Prompts</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <label for="filename">Select Prompt File:</label>
            <select id="filename" name="filename" onchange="loadFileContent()">
                {% for name, path in files.items() %}
                    <option value="{{ path }}" {% if selected_file == path %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
            </select>
            <br><br>
            <label>Edit Content:</label>
            <textarea name="content">{{ file_content }}</textarea>
            <br>
            <button type="submit">Save Changes</button>
        </form>
        <br>
        <a href="/">Back to Home</a>
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

@app.route("/choose_randomly", methods=["POST"])
def choose_randomly():
    level = request.form.get("level")  # מקבל את הערך מהטופס *ללא שינוי*
    gender = random.choice(["men", "women"])  # בחירה אקראית בין גבר לאישה

    return render_template_string(
        MAIN_PAGE_TEMPLATE, 
        gender=gender, 
        level=level,  # משמר את הרמה שנבחרה
        hermes_response=None, 
        grok_response=None
    )



@app.route("/", methods=["POST"])
def process_request():
    level = request.form.get("level", "level1")  # שמירה על רמת המשימה
    gender = request.form.get("gender")  # שמירה על המגדר שנבחר

    logging.info(f"Received form submission: Level={level}, Gender={gender}")

    if not level or not gender:
        logging.error("Form submission is missing required fields!")
        flash("Please select a level and gender.", "error")
        return redirect(url_for("index"))

    system_prompt_file = SYSTEM_PROMPT_FILES.get(level, "system_prompt_level1.txt")
    system_prompt = read_file_content(system_prompt_file)
    user_prompt = "Write task for men" if gender.lower() == "men" else "Write task for women"

    hermes_response = call_openrouter_api(
        model_name="nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    if not hermes_response:
        flash("Error retrieving response from Nous Hermes.", "error")
        return redirect(url_for("index"))

    translation_system_prompt = read_file_content(SYSTEM_PROMPT_FILES["translation"])
    grok_response = call_openrouter_api(
        model_name="x-ai/grok-2-vision-1212",
        system_prompt=translation_system_prompt,
        user_prompt=hermes_response
    )

    if not grok_response:
        flash("Error retrieving response from Grok model.", "error")
        return redirect(url_for("index"))

    logging.info(f"Hermes Response: {hermes_response[:200]}")  # לוג לקיצור פלט
    logging.info(f"Grok Response: {grok_response[:200]}")

    # 📌 עיבוד Markdown בפייתון לפני שליחת הנתונים ל-HTML
    hermes_response_html = Markup(mistune.markdown(hermes_response))
    grok_response_html = Markup(mistune.markdown(grok_response))

    return render_template_string(MAIN_PAGE_TEMPLATE,
                                  hermes_response=hermes_response_html,
                                  grok_response=grok_response_html,
                                  gender=gender,
                                  level=level)



@app.route('/alarm.mp3')
def serve_audio():
    return send_file("alarm.mp3", mimetype="audio/mpeg")

@app.route("/edit_prompts", methods=["GET", "POST"])
def edit_prompts():
    """Allows the user to edit system prompt files dynamically."""
    selected_file = request.args.get("filename", "system_prompt_level1.txt")  # Default to level1
    file_content = read_file_content(selected_file)

    if request.method == "POST":
        new_filename = request.form.get("filename")
        new_content = request.form.get("content")

        if new_filename not in SYSTEM_PROMPT_FILES.values():
            flash("Invalid file selection!", "error")
            return redirect(url_for("edit_prompts", filename=selected_file))

        write_file_content(new_filename, new_content)
        flash(f"Updated {new_filename} successfully!", "success")

        # Reload the updated content
        return redirect(url_for("edit_prompts", filename=new_filename))

    return render_template_string(EDIT_PROMPTS_TEMPLATE, selected_file=selected_file, file_content=file_content, files=SYSTEM_PROMPT_FILES)

###############################################################################
# Run the Flask App
###############################################################################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
