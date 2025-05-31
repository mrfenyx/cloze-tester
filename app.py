import logging
import json
import re
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from deepseek_api import generate_deepseek_text
from cloze import process_text_with_inputs
from markupsafe import Markup

CONFIG_PATH = "cloze_config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    # Fallback defaults
    return {
        "default_cefr": "B1",
        "cloze_reveal_rules": [
            {"max_length": 5, "num_reveal": 1},
            {"max_length": 8, "num_reveal": 2},
            {"max_length": 11, "num_reveal": 3},
            {"max_length": 100, "num_reveal": 4}
        ]
    }

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "notsecure")

@app.route("/", methods=["GET", "POST"])
def index():
    config = load_config()
    cloze_html = ""
    blanks_info = []
    subject = ""
    level = config.get("default_cefr", "B1")
    error = ""
    generated_text = ""
    feedback_html = ""
    score_str = ""
    reveal_rules = config.get("cloze_reveal_rules", [])

    if request.method == "POST":
        if "generate" in request.form:
            subject = request.form.get("subject", "")
            level = request.form.get("level", config.get("default_cefr", "B1"))
            try:
                generated_text = generate_deepseek_text(subject, level)
                cloze_html, blanks_info = process_text_with_inputs(generated_text, reveal_rules)
            except Exception as e:
                error = str(e)
        elif "check" in request.form:
            generated_text = request.form.get("generated_text", "")
            blanks_info = json.loads(request.form.get("blanks_info", "[]"))
            total = len(blanks_info)
            correct = 0
            blank_pattern = re.compile(r'\[\[([^\]]+)\]\]')
            blank_id = 0
            flat_idx = 0

            def repl(m):
                nonlocal blank_id, correct, flat_idx
                info = blanks_info[blank_id]
                word = info['word']
                prefix = info['prefix']
                n_inputs = info['num_inputs']
                user_input = ''
                input_fields = ''
                is_correct = True
                for i in range(n_inputs):
                    val = request.form.get(f'blank_{flat_idx}', '')
                    user_input += val
                    if len(word[len(prefix):]) > i:
                        if val.lower() != word[len(prefix):][i].lower():
                            is_correct = False
                    else:
                        is_correct = False
                    input_fields += f'<input type="text" value="{val}" maxlength="1" readonly class="blank-input{" correct" if is_correct else " incorrect"}">'
                    flat_idx += 1
                if is_correct and user_input.lower() == word[len(prefix):].lower():
                    correct += 1
                    html = f'<span class="cloze-blank-group correct">{prefix}{input_fields}</span>'
                else:
                    html = f'<span class="cloze-blank-group incorrect">{prefix}{input_fields}</span> <span class="correct-answer">({word})</span>'
                blank_id += 1
                return html

            feedback_html = Markup(blank_pattern.sub(repl, generated_text))
            score_str = f"{correct}/{total} correct"

    return render_template(
        "index.html",
        subject=subject,
        level=level,
        cloze_html=cloze_html,
        feedback_html=feedback_html,
        error=error,
        generated_text=generated_text,
        blanks_info=json.dumps(blanks_info),
        score_str=score_str,
        config=config
    )

@app.route("/config", methods=["GET", "POST"])
def config():
    config = load_config()
    message = ""
    if request.method == "POST":
        default_cefr = request.form.get("default_cefr", "B1")
        # Process rules
        rules = []
        max_lengths = request.form.getlist("max_length")
        num_reveals = request.form.getlist("num_reveal")
        for m, n in zip(max_lengths, num_reveals):
            try:
                rules.append({"max_length": int(m), "num_reveal": int(n)})
            except Exception:
                continue
        # sort rules by max_length
        rules.sort(key=lambda r: r["max_length"])
        config = {"default_cefr": default_cefr, "cloze_reveal_rules": rules}
        save_config(config)
        message = "Configuration updated!"
    return render_template("config.html", config=config, message=message)

if __name__ == "__main__":
    logger.info("Starting Flask app.")
    app.run(host="0.0.0.0", port=5000, debug=False)
