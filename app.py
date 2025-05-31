import logging
from flask import Flask, render_template, request
from deepseek_api import generate_deepseek_text
from cloze import process_text

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    logger.info(f"Received {request.method} request at /")
    cloze_result = []
    subject = ""
    level = "B1"
    error = ""
    generated_text = ""
    if request.method == "POST":
        subject = request.form.get("subject", "")
        level = request.form.get("level", "B1")
        logger.info(f"Form submitted. Subject: {subject}, Level: {level}")
        try:
            generated_text = generate_deepseek_text(subject, level)
            cloze_result = process_text(generated_text)
        except Exception as e:
            error = str(e)
            logger.error(f"Error while generating text: {e}")
    return render_template(
        "index.html",
        subject=subject,
        level=level,
        cloze_result=cloze_result,
        error=error,
        generated_text=generated_text
    )

if __name__ == "__main__":
    logger.info("Starting Flask app.")
    app.run(debug=True)
