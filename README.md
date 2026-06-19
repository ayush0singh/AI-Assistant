# AI Assistant

A complete web-based AI Assistant built for a Prompt Engineering internship assignment. It uses HTML, CSS, JavaScript, Flask, and the Google Gemini API.

## Features

- Question Answering with Short Answer, Teacher Explanation, and Detailed Expert modes
- Text Summarization with Short Summary, Bullet Point Summary, and Executive Summary modes
- Creative Content Generation with Story, Poem, and Creative Idea modes
- Dropdown-based function and prompt style selection
- Responsive card-based user interface
- Loading indicator and response display
- Feedback loop that stores Yes/No feedback in `feedback.csv`
- Modular Gemini integration in `services/gemini_service.py`

## Project Structure

```text
AI_Assistant/
├── app.py
├── services/
│   └── gemini_service.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── feedback.csv
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

1. Open a terminal in the project folder:

```bash
cd AI_Assistant
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Gemini API Setup

1. Create an API key from Google AI Studio.
2. Create a `.env` file in the `AI_Assistant` folder.
3. Add your API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The app also attempts to load `geminiapi.env` from the parent folder, so your existing assignment key file can work if it contains `GEMINI_API_KEY=...`.

The default model is `gemini-2.5-flash`, matching the internship assignment requirement.

## Running the Project

Start the Flask app:

```bash
python app.py
```

Open the local URL shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

## Routes

- `/` renders the main AI Assistant page.
- `/generate` accepts a JSON request and returns a Gemini-generated response.
- `/feedback` stores feedback in `feedback.csv`.

## Feedback CSV Format

Feedback is stored with these columns:

```csv
timestamp,function,prompt_style,feedback
```

## Notes

- Keep your Gemini API key private.
- Do not commit `.env` or any file containing real API keys.
- Use clear input text for the best AI responses.
- If you see `[WinError 10061]`, check that your system proxy is disabled or reachable. The app automatically ignores the common broken proxy value `127.0.0.1:9`.
