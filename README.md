# Extreme Sexual Challenges - Couples Edition

![Game Logo](static/images/logo.png)

This repository contains **Extreme Sexual Challenges - Couples Edition**, a Flask-based game that generates sexy and playful challenges for couples. The app interacts with the [OpenRouter API](https://openrouter.ai/) to generate personalized tasks based on selected levels and gender preferences.

## Features
- **Random Challenge Generation**: Select a level and get a randomly chosen challenge.
- **Nous Hermes & Grok AI Models**: Fetch AI-generated tasks tailored to the chosen difficulty.
- **Timer Integration**: Set a countdown timer (30 sec, 1 min, 1.5 min, or 2 min) for completing the challenge.
- **Audio Alert**: A sound notification plays when the timer ends.
- **Dynamic Admin Panel**: Modify system prompts through a simple web interface.

---

## Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/extreme-sexual-challenges.git
cd extreme-sexual-challenges
```

### 2. Set Up Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate  # For Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root and add:
```ini
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 5. Run the Application
```bash
python app.py
```

The app will start running on **`http://127.0.0.1:5000/`**.

---

## Usage
1. Open the app in a web browser.
2. Choose a level and let the app randomly pick a gender.
3. Click **"Get Task"** to receive a sexy challenge.
4. Set a timer and start the fun!

---

## Contributing
Feel free to submit pull requests for improvements, new features, or bug fixes!

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
