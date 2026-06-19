import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from services.gemini_service import GeminiService, GeminiServiceError, PROMPT_STYLES


BASE_DIR = Path(__file__).resolve().parent
FEEDBACK_FILE = BASE_DIR / "feedback.csv"


load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / "geminiapi.env")

app = Flask(__name__)


def read_api_key() -> str | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    legacy_key_file = BASE_DIR.parent / "geminiapi.env"
    if not legacy_key_file.exists():
        return None

    for line in legacy_key_file.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()
        if clean_line and not clean_line.startswith("#") and "=" not in clean_line:
            return clean_line

    return None


gemini_service = GeminiService(api_key=read_api_key())


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def ensure_feedback_file() -> None:
    if not FEEDBACK_FILE.exists():
        with FEEDBACK_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "function", "prompt_style", "feedback"])


@app.route("/")
def index():
    return render_template("index.html", prompt_styles=PROMPT_STYLES)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    assistant_function = data.get("function", "").strip()
    prompt_style = data.get("prompt_style", "").strip()
    user_input = data.get("user_input", "").strip()

    if not user_input:
        return jsonify({"error": "Please enter text before generating a response."}), 400

    if assistant_function not in PROMPT_STYLES:
        return jsonify({"error": "Invalid assistant function selected."}), 400

    if prompt_style not in PROMPT_STYLES[assistant_function]:
        return jsonify({"error": "Invalid prompt style selected."}), 400

    try:
        response_text = gemini_service.generate_response(
            assistant_function=assistant_function,
            prompt_style=prompt_style,
            user_input=user_input,
        )
        return jsonify({"response": response_text})
    except GeminiServiceError as error:
        return jsonify({"error": str(error)}), 502
    except Exception:
        app.logger.exception("Unexpected error while generating response")
        return jsonify({"error": "Something went wrong. Please try again."}), 500


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}
    assistant_function = data.get("function", "").strip()
    prompt_style = data.get("prompt_style", "").strip()
    feedback_value = data.get("feedback", "").strip().lower()

    if assistant_function not in PROMPT_STYLES:
        return jsonify({"error": "Invalid assistant function selected."}), 400

    if prompt_style not in PROMPT_STYLES[assistant_function]:
        return jsonify({"error": "Invalid prompt style selected."}), 400

    if feedback_value not in {"yes", "no"}:
        return jsonify({"error": "Feedback must be Yes or No."}), 400

    ensure_feedback_file()
    with FEEDBACK_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                assistant_function,
                prompt_style,
                feedback_value,
            ]
        )

    return jsonify({"message": "Feedback saved successfully."})


if __name__ == "__main__":
    ensure_feedback_file()
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=get_bool_env("FLASK_DEBUG"),
        use_reloader=False,
    )
