import logging
from flask import Flask, render_template, request
from deepseek_api import generate_deepseek_text

# ---------------- Logging Setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    logger.info(f"Received {request.method} request at /")
    generated_text = ""
    subject = ""
    level = "B1"
    error = ""
    if request.method == "POST":
        subject = request.form.get("subject", "")
        level = request.form.get("level", "B1")
        logger.info(f"Form submitted. Subject: {subject}, Level: {level}")
        try:
            generated_text = generate_deepseek_text(subject, level)
        except Exception as e:
            error = str(e)
            logger.error(f"Error while generating text: {e}")
    return render_template("index.html", generated_text=generated_text, subject=subject, level=level, error=error)

if __name__ == "__main__":
    logger.info("Starting Flask app.")
    app.run(debug=True)
